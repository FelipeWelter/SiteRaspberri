# app/routes_users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from functools import wraps

from .models import db, User, UserClass
from .forms import UserForm, UserPasswordForm
from .utils import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role != "admin":
            flash("Ação restrita a administradores.", "danger")
            return redirect(url_for("main.dashboard"))
        return fn(*args, **kwargs)
    return wrapper

def class_required(classe: str):
    classe = (classe or "").strip().upper()
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.can_access(classe):
             return redirect(url_for("main.dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@bp.get("/users")
@admin_required
def users_list():
    q = request.args.get("q","").strip()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.username.ilike(like), User.full_name.ilike(like), User.role.ilike(like)))
    users = query.order_by(User.username.asc()).all()
    return render_template("users_list.html", users=users, q=q)

@bp.route("/users/new", methods=["GET","POST"])
@admin_required
def users_new():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Usuário já existe.", "warning")
            return render_template("users_form.html", form=form, mode="new")

        u = User(
            full_name=form.full_name.data,
            username=form.username.data,
            identity=form.identity.data,
            role=form.role.data,
            active=getattr(form, "active", None).data if hasattr(form, "active") else True,
        )
        if form.password.data:
            u.set_password(form.password.data)

        u.classes = []
        if u.role == "user":
            for c in (form.classes.data or []):
                u.classes.append(UserClass(classe=c))

        db.session.add(u)
        db.session.commit()

        flash("Usuário criado.", "success")
        return redirect(url_for("admin.users_list"))
    return render_template("users_form.html", form=form, mode="new")

@bp.route("/users/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def users_edit(id):
    u = User.query.get_or_404(id)

    form = UserForm(
        full_name=u.full_name,
        username=u.username,
        identity=u.identity,
        role=u.role,
        active=u.active,
        classes=[c.classe for c in u.classes],
    )
    if form.validate_on_submit():
        # impedir duplicar username em outro usuário
        if User.query.filter(User.username == form.username.data, User.id != u.id).first():
            flash("Login já utilizado por outro usuário.", "warning")
            return render_template("users_form.html", form=form, mode="edit", user=u)

        u.full_name = form.full_name.data
        u.username  = form.username.data
        u.identity  = form.identity.data
        u.role      = form.role.data
        u.active    = bool(form.active.data)
        if form.password.data:
            u.set_password(form.password.data)

        u.classes.clear()
        if u.role == "user":
            for c in (form.classes.data or []):
                u.classes.append(UserClass(classe=c))

        db.session.commit()
        flash("Usuário atualizado.", "success")
        return redirect(url_for("admin.users_list"))

    # Pré-popula checkboxes de classes
    form.classes.data = [c.classe for c in u.classes]
    return render_template("users_form.html", form=form, mode="edit", user=u)

@bp.route("/users/<int:id>/password", methods=["GET","POST"])
@admin_required
def users_password(id):
    u = User.query.get_or_404(id)
    form = UserPasswordForm()
    if form.validate_on_submit():
        u.set_password(form.password.data)
        db.session.commit()
        flash("Senha atualizada.", "success")
        return redirect(url_for("admin.users_list"))
    return render_template("users_password.html", form=form, user=u)

@bp.post("/users/<int:id>/delete")
@admin_required
def users_delete(id):
    u = User.query.get_or_404(id)
    if u.id == current_user.id:
        flash("Você não pode excluir a própria conta logada.", "warning")
        return redirect(url_for("admin.users_list"))
    db.session.delete(u)
    db.session.commit()
    flash("Usuário removido.", "warning")
    return redirect(url_for("admin.users_list"))
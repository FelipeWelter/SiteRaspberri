from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from .models import db, User
from .forms import RegisterForm

bp = Blueprint("auth", __name__, url_prefix="")

@bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        user = User.query.filter_by(username=u, active=True).first()
        if user and user.check_password(p):
            login_user(user, remember=False)
            return redirect(url_for("main.dashboard"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        # checa username duplicado
        if User.query.filter_by(username=form.username.data).first():
            flash("Este login já está em uso.", "warning")
            return render_template("register.html", form=form)

        u = User(
            full_name=form.full_name.data,
            username=form.username.data,
            identity=form.identity.data or None,
            role="user",
            active=False,  # exige aprovação do admin
        )
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()

        flash("Conta criada com sucesso! Aguarde aprovação do administrador.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)
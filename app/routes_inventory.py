# app/routes_inventory.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from .models import db, CL2, CL6
from .forms import CL2Form, CL6Form

bp = Blueprint("inv", __name__, url_prefix="/inv")

# ---- CL2 ----
@bp.get("/cl2")
@login_required
def cl2_list():
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    query = CL2.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(CL2.item_id.ilike(like), CL2.nome.ilike(like), CL2.situacao.ilike(like)))
    items = query.order_by(CL2.atualizado_em.desc()).paginate(page=page, per_page=12)
    return render_template("cl2_list.html", items=items, q=q)

@bp.route("/cl2/new", methods=["GET","POST"])
@login_required
def cl2_new():
    form = CL2Form()
    if form.validate_on_submit():
        item = CL2(**{f.name: f.data for f in form})
        db.session.add(item); db.session.commit()
        flash("CL2 cadastrado.", "success")
        return redirect(url_for("inv.cl2_list"))
    return render_template("cl2_form.html", form=form, mode="new")

@bp.route("/cl2/<int:id>/edit", methods=["GET","POST"])
@login_required
def cl2_edit(id):
    item = CL2.query.get_or_404(id)
    form = CL2Form(obj=item)
    if form.validate_on_submit():
        for f in form: 
            if f.name not in ("csrf_token","submit"): setattr(item, f.name, f.data)
        db.session.commit()
        flash("CL2 atualizado.", "success")
        return redirect(url_for("inv.cl2_list"))
    return render_template("cl2_form.html", form=form, mode="edit", item=item)

@bp.post("/cl2/<int:id>/delete")
@login_required
def cl2_delete(id):
    item = CL2.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash("CL2 removido.", "warning")
    return redirect(url_for("inv.cl2_list"))

# ---- CL6 ----
@bp.get("/cl6")
@login_required
def cl6_list():
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    query = CL6.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            CL6.item_id.ilike(like), CL6.nome.ilike(like),
            CL6.numero_serie.ilike(like), CL6.numero_patrimonio.ilike(like),
            CL6.marca.ilike(like), CL6.modelo.ilike(like),
        ))
    items = query.order_by(CL6.atualizado_em.desc()).paginate(page=page, per_page=12)
    return render_template("cl6_list.html", items=items, q=q)

@bp.route("/cl6/new", methods=["GET","POST"])
@login_required
def cl6_new():
    form = CL6Form()
    if form.validate_on_submit():
        item = CL6(**{f.name: f.data for f in form})
        db.session.add(item); db.session.commit()
        flash("CL6 cadastrado.", "success")
        return redirect(url_for("inv.cl6_list"))
    return render_template("cl6_form.html", form=form, mode="new")

@bp.route("/cl6/<int:id>/edit", methods=["GET","POST"])
@login_required
def cl6_edit(id):
    item = CL6.query.get_or_404(id)
    form = CL6Form(obj=item)
    if form.validate_on_submit():
        for f in form:
            if f.name not in ("csrf_token","submit"): setattr(item, f.name, f.data)
        db.session.commit()
        flash("CL6 atualizado.", "success")
        return redirect(url_for("inv.cl6_list"))
    return render_template("cl6_form.html", form=form, mode="edit", item=item)

@bp.post("/cl6/<int:id>/delete")
@login_required
def cl6_delete(id):
    item = CL6.query.get_or_404(id)
    db.session.delete(item); db.session.commit()
    flash("CL6 removido.", "warning")
    return redirect(url_for("inv.cl6_list"))

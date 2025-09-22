# app/routes_inventory.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import or_
from .models import db, CL2, CL6
from .forms import CL2Form, CL6Form

bp = Blueprint("inv", __name__, url_prefix="/inv")

# -------- CL2 ----------
@bp.get("/cl2")
@login_required
def cl2_list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = CL2.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(CL2.nome.ilike(like), CL2.situacao.ilike(like)))
    items = query.order_by(CL2.atualizado_em.desc()).paginate(page=page, per_page=10)
    return render_template("cl2_list.html", items=items, q=q)

@bp.route("/cl2/new", methods=["GET", "POST"])
@login_required
def cl2_new():
    form = CL2Form()
    if form.validate_on_submit():
        it = CL2(
            nome=form.nome.data,
            situacao=form.situacao.data or "OK",
            qtd_prevista=form.qtd_prevista.data or 0,
            qtd_disp=form.qtd_disp.data or 0,
            qtd_indisp=form.qtd_indisp.data or 0,
        )
        db.session.add(it); db.session.commit()
        flash("Item CL2 cadastrado.", "success")
        return redirect(url_for("inv.cl2_list"))
    return render_template("cl2_form.html", form=form, mode="new")

@bp.route("/cl2/<int:id>/edit", methods=["GET", "POST"])
@login_required
def cl2_edit(id):
    it = CL2.query.get_or_404(id)
    form = CL2Form(obj=it)
    if form.validate_on_submit():
        form.populate_obj(it)
        db.session.commit()
        flash("Item CL2 atualizado.", "success")
        return redirect(url_for("inv.cl2_list"))
    return render_template("cl2_form.html", form=form, mode="edit", item=it)

@bp.post("/cl2/<int:id>/delete")
@login_required
def cl2_delete(id):
    it = CL2.query.get_or_404(id)
    db.session.delete(it); db.session.commit()
    flash("Item CL2 removido.", "warning")
    return redirect(url_for("inv.cl2_list"))

# -------- CL6 ----------
@bp.get("/cl6")
@login_required
def cl6_list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = CL6.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            CL6.nome.ilike(like), CL6.situacao.ilike(like),
            CL6.numero_patrimonio.ilike(like), CL6.numero_serie.ilike(like),
            CL6.marca.ilike(like), CL6.modelo.ilike(like),
        ))
    items = query.order_by(CL6.atualizado_em.desc()).paginate(page=page, per_page=10)
    return render_template("cl6_list.html", items=items, q=q)

@bp.route("/cl6/new", methods=["GET", "POST"])
@login_required
def cl6_new():
    form = CL6Form()
    if form.validate_on_submit():
        it = CL6(
            nome=form.nome.data,
            situacao=form.situacao.data or "OK",
            qtd_prevista=form.qtd_prevista.data or 0,
            qtd_disp=form.qtd_disp.data or 0,
            qtd_indisp=form.qtd_indisp.data or 0,
            valor=form.valor.data or 0,
            observacao=form.observacao.data,
            numero_serie=form.numero_serie.data,
            numero_patrimonio=form.numero_patrimonio.data,
            modelo=form.modelo.data,
            marca=form.marca.data,
        )
        db.session.add(it); db.session.commit()
        flash("Item CL6 cadastrado.", "success")
        return redirect(url_for("inv.cl6_list"))
    return render_template("cl6_form.html", form=form, mode="new")

@bp.route("/cl6/<int:id>/edit", methods=["GET", "POST"])
@login_required
def cl6_edit(id):
    it = CL6.query.get_or_404(id)
    form = CL6Form(obj=it)
    if form.validate_on_submit():
        form.populate_obj(it)
        db.session.commit()
        flash("Item CL6 atualizado.", "success")
        return redirect(url_for("inv.cl6_list"))
    return render_template("cl6_form.html", form=form, mode="edit", item=it)

@bp.post("/cl6/<int:id>/delete")
@login_required
def cl6_delete(id):
    it = CL6.query.get_or_404(id)
    db.session.delete(it); db.session.commit()
    flash("Item CL6 removido.", "warning")
    return redirect(url_for("inv.cl6_list"))

# app/routes_inventory.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from sqlalchemy import func, or_, case
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
import io

from .utils import class_required  # << agora vem do utils.py
from .models import db, CL2, CL6, CL7
from .forms import CL2Form, CL6Form, CL7Form

bp = Blueprint("inv", __name__, url_prefix="/inv")

# ------------------------
# Helpers
# ------------------------
def normalize_situacao(raw: str | None) -> str:
    """Normaliza texto de situação para valores canônicos."""
    s = (raw or "OK").strip().lower()
    if s in {"ok", "livre", "disponivel", "disponível"}:
        return "DISPONÍVEL"
    if s in {"defeito", "manutencao", "manutenção", "indisponivel", "indisponível"}:
        return "INDISPONÍVEL"
    if s in {"cautelado", "emprestado"}:
        return "CAUTELADO"
    return (raw or "OK").upper()

# -------- CL2 ----------
@bp.get("/cl2")
@class_required("CL2")
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
@class_required("CL2")
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
        db.session.add(it)
        db.session.commit()
        flash("Item CL2 cadastrado.", "success")
        return redirect(url_for("inv.cl2_list"))
    return render_template("cl2_form.html", form=form, mode="new")

@bp.route("/cl2/<int:id>/edit", methods=["GET", "POST"])
@class_required("CL2")
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
@class_required("CL2")
def cl2_delete(id):
    it = CL2.query.get_or_404(id)
    db.session.delete(it)
    db.session.commit()
    flash("Item CL2 removido.", "warning")
    return redirect(url_for("inv.cl2_list"))

# -------- CL6 ----------
@bp.get("/cl6")
@class_required("CL6")
def cl6_list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = CL6.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                CL6.nome.ilike(like),
                CL6.situacao.ilike(like),
                CL6.numero_patrimonio.ilike(like),
                CL6.numero_serie.ilike(like),
                CL6.marca.ilike(like),
                CL6.modelo.ilike(like),
            )
        )
    items = query.order_by(CL6.atualizado_em.desc()).paginate(page=page, per_page=10)
    return render_template("cl6_list.html", items=items, q=q)

@bp.route("/cl6/new", methods=["GET", "POST"])
@class_required("CL6")
def cl6_new():
    form = CL6Form()
    if form.validate_on_submit():
        raw_val = request.form.get("valor")
        if raw_val:
            raw_val = raw_val.replace(",", ".")  # aceita vírgula também
            try:
                valor = float(raw_val)
            except ValueError:
                valor = 0.0
        else:
            valor = 0.0

        it = CL6(
            nome=form.nome.data,
            situacao=form.situacao.data or "OK",
            qtd_prevista=form.qtd_prevista.data or 0,
            qtd_disp=form.qtd_disp.data or 0,
            qtd_indisp=form.qtd_indisp.data or 0,
            valor=valor,
            observacao=form.observacao.data,
            numero_serie=form.numero_serie.data,
            numero_patrimonio=form.numero_patrimonio.data,
            modelo=form.modelo.data,
            marca=form.marca.data,
        )
        db.session.add(it)
        db.session.commit()
        flash("Item CL6 cadastrado.", "success")
        return redirect(url_for("inv.cl6_list"))
    return render_template("cl6_form.html", form=form, mode="new")

@bp.route("/cl6/<int:id>/edit", methods=["GET", "POST"])
@class_required("CL6")
def cl6_edit(id):
    it = CL6.query.get_or_404(id)
    form = CL6Form(obj=it)
    if form.validate_on_submit():
        raw_val = request.form.get("valor")
        if raw_val:
            raw_val = raw_val.replace(",", ".")
            try:
                valor = float(raw_val)
            except ValueError:
                valor = 0.0
        else:
            valor = 0.0

        form.populate_obj(it)
        it.valor = valor
        db.session.commit()
        flash("Item CL6 atualizado.", "success")
        return redirect(url_for("inv.cl6_list"))
    return render_template("cl6_form.html", form=form, mode="edit", item=it)

@bp.post("/cl6/<int:id>/delete")
@class_required("CL6")
def cl6_delete(id):
    it = CL6.query.get_or_404(id)
    db.session.delete(it)
    db.session.commit()
    flash("Item CL6 removido.", "warning")
    return redirect(url_for("inv.cl6_list"))

# -------- CL7 ---------- (Classe VII para rádios)
@bp.get("/cl7")
@class_required("CL7")
def cl7_list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    # filtros usados na listagem e no resumo
    filters = []
    if q:
        like = f"%{q}%"
        filters.append(
            or_(
                CL7.material.ilike(like),
                CL7.marca.ilike(like),
                CL7.modelo.ilike(like),
                CL7.numero_serie.ilike(like),
                CL7.situacao.ilike(like),
                CL7.observacao.ilike(like),
            )
        )

    # listagem
    query = CL7.query.filter(*filters)
    items = query.order_by(CL7.atualizado_em.desc()).paginate(page=page, per_page=10)

    # resumo por situação (respeita filtros) — usa UPPER para cobrir acentos
    s = func.upper(func.trim(CL7.situacao))

    disp = func.coalesce(
        func.sum(
            case(
                (s.in_(["DISPONIVEL", "DISPONÍVEL", "OK", "LIVRE"]), 1),
                else_=0,
            )
        ),
        0,
    )
    indisp = func.coalesce(
        func.sum(
            case(
                (s.in_(["INDISPONIVEL", "INDISPONÍVEL", "DEFEITO", "MANUTENCAO", "MANUTENÇÃO"]), 1),
                else_=0,
            )
        ),
        0,
    )
    caut = func.coalesce(
        func.sum(case((s.in_(["CAUTELADO", "EMPRESTADO"]), 1), else_=0)),
        0,
    )
    total = func.count(CL7.id)

    sums = db.session.query(
        disp.label("disp"),
        indisp.label("indisp"),
        caut.label("caut"),
        total.label("total"),
    ).filter(*filters).one()

    return render_template("cl7_list.html", items=items, q=q, sums=sums)

@bp.route("/cl7/new", methods=["GET", "POST"])
@class_required("CL7")
def cl7_new():
    form = CL7Form()
    if form.validate_on_submit():
        it = CL7(
            material=form.material.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            numero_serie=form.numero_serie.data,
            situacao=normalize_situacao(form.situacao.data),
            observacao=form.observacao.data,
        )
        db.session.add(it)
        db.session.commit()
        flash("Item cadastrado.", "success")
        return redirect(url_for("inv.cl7_list"))
    return render_template("cl7_form.html", form=form, mode="new")

@bp.route("/cl7/<int:id>/edit", methods=["GET", "POST"])
@class_required("CL7")
def cl7_edit(id):
    it = CL7.query.get_or_404(id)
    form = CL7Form(obj=it)
    if form.validate_on_submit():
        it.material = form.material.data
        it.marca = form.marca.data
        it.modelo = form.modelo.data
        it.numero_serie = form.numero_serie.data
        it.situacao = normalize_situacao(form.situacao.data)
        it.observacao = form.observacao.data
        db.session.commit()
        flash("Item CL7 atualizado.", "success")
        return redirect(url_for("inv.cl7_list"))
    return render_template("cl7_form.html", form=form, mode="edit", item=it)

@bp.post("/cl7/<int:id>/delete")
@class_required("CL7")
def cl7_delete(id):
    it = CL7.query.get_or_404(id)
    db.session.delete(it)
    db.session.commit()
    flash("Item CL7 removido.", "warning")
    return redirect(url_for("inv.cl7_list"))

# -------- Impressão PDF CL7 --------
@bp.get("/cl7/print-pdf")
@class_required("CL7")
def cl7_print_pdf():
    """Gera PDF com TABELA de CL7 + resumo (respeita filtro ?q=)."""
    q = request.args.get("q", "").strip()

    # filtros iguais aos da listagem
    filters = []
    if q:
        like = f"%{q}%"
        filters.append(or_(
            CL7.material.ilike(like),
            CL7.marca.ilike(like),
            CL7.modelo.ilike(like),
            CL7.numero_serie.ilike(like),
            CL7.situacao.ilike(like),
            CL7.observacao.ilike(like),
        ))

    # busca dos itens
    items = (
        CL7.query.filter(*filters)
        .order_by(CL7.atualizado_em.desc())
        .all()
    )

    # agregação (mesma lógica da tela)
    s = func.upper(func.trim(CL7.situacao))
    disp = func.coalesce(func.sum(case((s.in_(["DISPONIVEL", "DISPONÍVEL", "OK", "LIVRE"]), 1), else_=0)), 0)
    indisp = func.coalesce(func.sum(case((s.in_(["INDISPONIVEL", "INDISPONÍVEL", "DEFEITO", "MANUTENCAO", "MANUTENÇÃO"]), 1), else_=0)), 0)
    caut = func.coalesce(func.sum(case((s.in_(["CAUTELADO", "EMPRESTADO"]), 1), else_=0)), 0)
    total = func.count(CL7.id)
    sums = db.session.query(
        disp.label("disp"),
        indisp.label("indisp"),
        caut.label("caut"),
        total.label("total"),
    ).filter(*filters).one()

    # monta o PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="Resumo CL7"
    )

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        spaceAfter=6,
    )
    Normal = styles["Normal"]

    story = []
    # Cabeçalho
    story.append(Paragraph("Resumo CL7 — Rádios", H1))
    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q:
        cab += f" &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Filtro: <b>{q}</b>"
    story.append(Paragraph(cab, Normal))
    story.append(Spacer(1, 8))

    # Tabela de itens
    data = [["ID", "Material", "Marca", "Modelo", "Nº Série", "Situação", "Observação"]]
    for it in items:
        data.append([
            it.id,
            it.material or "-",
            it.marca or "-",
            it.modelo or "-",
            it.numero_serie or "-",
            it.situacao or "-",
            it.observacao or "-",
        ])

    col_widths = [14*mm, 36*mm, 26*mm, 26*mm, 26*mm, 24*mm, 60*mm]

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),

        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7F7F7")]),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    # Resumo final
    resumo_data = [
        ["Disponíveis", str(sums.disp)],
        ["Indisponíveis", str(sums.indisp)],
        ["Cautelados", str(sums.caut)],
        ["TOTAL", str(sums.total)],
    ]
    resumo_tbl = Table(resumo_data, colWidths=[40*mm, 20*mm])
    resumo_tbl.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-2), "Helvetica"),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 11),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("LINEBELOW", (0,-2), (-1,-2), 0.5, colors.black),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(resumo_tbl)

    doc.build(story)
    pdf = io.BytesIO(buffer.getvalue()).getvalue()
    buffer.close()

    resp = make_response(pdf)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = "inline; filename=resumo_cl7.pdf"
    return resp

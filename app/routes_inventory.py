# app/routes_inventory.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from sqlalchemy import func, or_, case
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
import io

from .utils import class_required  # segue vindo do utils.py
from .models import db, CL2, CL6, CL7
from .forms import CL2Form, CL6Form, CL7Form

bp = Blueprint("inv", __name__, url_prefix="/inv")

# ------------------------
# Helpers
# ------------------------
def normalize_situacao(raw: str | None) -> str:
    """Normaliza texto de situação para valores canônicos (salva em maiúsculo)."""
    s = (raw or "OK").strip().lower()
    if s in {"ok", "livre", "disponivel", "disponível"}:
        return "DISPONÍVEL"
    if s in {"defeito", "manutencao", "manutenção", "indisponivel", "indisponível"}:
        return "INDISPONÍVEL"
    if s in {"cautelado", "emprestado"}:
        return "CAUTELADO"
    return (raw or "OK").upper()

# Classe 1 - RAÇÕES 

@bp.get("/cl1", endpoint="cl1_list")
@class_required("CL1")
def cl1_list():
    rows = CL1.query.order_by(CL1.atualizado_em.desc()).all()
    return render_template("inventory/cl1_list.html", rows=rows)

# Novo
@bp.route("/cl1/new", methods=["GET", "POST"], endpoint="cl1_new")
@class_required("CL1")
def cl1_new():
    form = CL1Form()
    if form.validate_on_submit():
        item = CL1(
            tipo=form.tipo.data,
            quantidade=form.quantidade.data,
            validade=form.validade.data,
        )
        db.session.add(item)
        db.session.commit()
        flash("Ração cadastrada com sucesso!", "success")
        return redirect(url_for("inv.cl1_list"))
    return render_template("inventory/cl1_form.html", form=form, title="Nova Ração")

# Editar
@bp.route("/cl1/<int:id>/edit", methods=["GET", "POST"], endpoint="cl1_edit")
@class_required("CL1")
def cl1_edit(id):
    item = CL1.query.get_or_404(id)
    form = CL1Form(obj=item)
    if form.validate_on_submit():
        item.tipo = form.tipo.data
        item.quantidade = form.quantidade.data
        item.validade = form.validade.data
        db.session.commit()
        flash("Ração atualizada com sucesso!", "success")
        return redirect(url_for("inv.cl1_list"))
    return render_template("inventory/cl1_form.html", form=form, title="Editar Ração")

# Deletar
@bp.post("/cl1/<int:id>/delete", endpoint="cl1_delete")
@class_required("CL1")
def cl1_delete(id):
    item = CL1.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Ração removida com sucesso!", "success")
    return redirect(url_for("inv.cl1_list"))


# CL2 =====================================================================================
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

# -------- Impressão PDF CL2 --------
@bp.get("/cl2/print-pdf", endpoint="cl2_print_pdf")
@class_required("CL2")
def cl2_print_pdf():
    """Gera PDF com listagem de CL2 (respeita ?q= e ?m=)."""
    q = request.args.get("q", "").strip()
    m = request.args.get("m", "").strip()

    filters = []
    if q:
        like = f"%{q}%"
        filters.append(or_(CL2.nome.ilike(like), CL2.situacao.ilike(like)))
    if m:
        filters.append(CL2.nome == m)

    rows = CL2.query.filter(*filters).order_by(CL2.atualizado_em.desc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="Resumo CL2"
    )
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, spaceAfter=6)
    Normal = styles["Normal"]

    story = []
    story.append(Paragraph("Resumo CL2", H1))
    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q or m:
        filtros_txt = []
        if q: filtros_txt.append(f"Busca: <b>{q}</b>")
        if m: filtros_txt.append(f"Material: <b>{m}</b>")
        cab += " &nbsp;&nbsp;|&nbsp;&nbsp; " + " · ".join(filtros_txt)
    story.append(Paragraph(cab, Normal))
    story.append(Spacer(1, 8))

    data = [["ID", "Material", "Situação", "Prevista", "Disp.", "Indisp."]]
    for it in rows:
        data.append([
            it.id, it.nome or "-", it.situacao or "-",
            it.qtd_prevista or 0, it.qtd_disp or 0, it.qtd_indisp or 0
        ])

    tbl = Table(data, colWidths=[12*mm, 50*mm, 30*mm, 20*mm, 20*mm, 22*mm], repeatRows=1)
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

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    resp = make_response(pdf)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = "inline; filename=resumo_cl2.pdf"
    return resp


# =====================================================================================
# CL6 (inalterado)
# =====================================================================================
# app/routes_inventory.py (trechos CL6)


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
                CL6.situacao_patrimonial.ilike(like),
                CL6.codot_item_material.ilike(like),
                CL6.numero_patrimonio_material.ilike(like),
                CL6.localizacao_atual.ilike(like),
                CL6.marca.ilike(like),
                CL6.modelo.ilike(like),
                CL6.numero_serie.ilike(like),
                CL6.categoria.ilike(like),
                CL6.disponibilidade.ilike(like),
            )
        )


    items = query.order_by(CL6.atualizado_em.desc()).paginate(page=page, per_page=10)
    return render_template("cl6_list.html", items=items, q=q)

@bp.route("/cl6/new", methods=["GET", "POST"])
@class_required("CL6")
def cl6_new():
    form = CL6Form()
    if form.validate_on_submit():
        it = CL6(
            situacao_patrimonial=form.situacao_patrimonial.data,
            codot_item_material=form.codot_item_material.data,
            numero_patrimonio_material=form.numero_patrimonio_material.data,
            ano_fabricacao=form.ano_fabricacao.data,
            disponibilidade=form.disponibilidade.data,
            categoria=form.categoria.data,
            valor_inclusao_carga=(form.valor_inclusao_carga.data or 0),
            localizacao_atual=form.localizacao_atual.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            numero_serie=form.numero_serie.data,
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
        form.populate_obj(it)
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

@bp.get("/cl6/print-pdf", endpoint="cl6_print_pdf")
@class_required("CL6")
def cl6_print_pdf():
    """Gera PDF com listagem de CL6 (respeita ?q=)."""
    q = request.args.get("q", "").strip()

    filters = []
    if q:
        like = f"%{q}%"
        filters.append(or_(
            CL6.situacao_patrimonial.ilike(like),
            CL6.codot_item_material.ilike(like),
            CL6.numero_patrimonio_material.ilike(like),
            CL6.localizacao_atual.ilike(like),
            CL6.marca.ilike(like),
            CL6.modelo.ilike(like),
            CL6.numero_serie.ilike(like),
            CL6.categoria.ilike(like),
            CL6.disponibilidade.ilike(like),
        ))

    rows = CL6.query.filter(*filters).order_by(CL6.atualizado_em.desc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="Resumo Materiais Classe VI"
    )
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"],
                        fontName="Helvetica-Bold", fontSize=16, spaceAfter=6)
    Normal = ParagraphStyle("Normal", parent=styles["Normal"], fontSize=9, leading=12)

    story = [Paragraph("Resumo CL6", H1)]

    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q:
        cab += f" &nbsp;&nbsp;|&nbsp;&nbsp; Busca: <b>{q}</b>"
    story.append(Paragraph(cab, Normal))
    story.append(Spacer(1, 6))

    # Cabeçalho / Tabela
    data = [[
        "ID", "Situação", "CODOT", "Nº Patr. (mat)",
        "Ano", "Disp.", "Categoria", "Valor (inc. carga)", "Localização",
        "Marca", "Modelo", "Nº Série"
    ]]

    def _fmt_valor(v):
        try:
            return f"R$ {float(v):.2f}"
        except (TypeError, ValueError):
            return "-"

    if rows:
        for it in rows:
            data.append([
                it.id,
                it.situacao_patrimonial or "-",
                it.codot_item_material or "-",
                it.numero_patrimonio_material or "-",
                it.ano_fabricacao or "-",
                it.disponibilidade or "-",
                it.categoria or "-",
                _fmt_valor(it.valor_inclusao_carga),
                it.localizacao_atual or "-",
                it.marca or "-",
                it.modelo or "-",
                it.numero_serie or "-",
            ])
    else:
        # Linha “vazia” amigável: evita parecer página em branco
        data.append(["— Sem registros —"] + ["-"] * 12)

    # Larguras pensadas para caber em A4 com margens
    col_widths = [
        10*mm, 22*mm, 28*mm, 22*mm, 30*mm,
        12*mm, 16*mm, 20*mm, 26*mm, 28*mm, 20*mm, 22*mm, 26*mm
    ]

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE", (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7F7F7")]),
    ]))

    story.append(tbl)
    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    resp = make_response(pdf)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = "inline; filename=resumo_cl6.pdf"
    return resp


# =====================================================================================
# CL7 — HUB + páginas separadas por Pelotão (NOVO) — sem mexer no fluxo de CL2/CL6
# =====================================================================================

# HUB: só mostra dois botões (1º e 2º Pelotão). Não interfere nas outras classes.
@bp.get("/cl7")
@class_required("CL7")
def cl7_hub():
    return render_template("cl7_hub.html")  # crie este template com 2 botões

# ----- utilidades internas para reuso -----
def _summary_query(filters):
    """Retorna agregados (disp/indisp/caut/total) com mesma lógica da tela."""
    s = func.upper(func.trim(CL7.situacao))
    disp = func.coalesce(
        func.sum(case((s.in_(["DISPONIVEL", "DISPONÍVEL", "OK", "LIVRE"]), 1), else_=0)),
        0,
    )
    indisp = func.coalesce(
        func.sum(case((s.in_(["INDISPONIVEL", "INDISPONÍVEL", "DEFEITO", "MANUTENCAO", "MANUTENÇÃO"]), 1), else_=0)),
        0,
    )
    caut = func.coalesce(
        func.sum(case((s.in_(["CAUTELADO", "EMPRESTADO"]), 1), else_=0)),
        0,
    )
    total = func.count(CL7.id)
    return db.session.query(
        disp.label("disp"),
        indisp.label("indisp"),
        caut.label("caut"),
        total.label("total"),
    ).filter(*filters).one()

def _list_core(pelotao_val: str):
    """Core: devolve items paginados, termo q e resumo, filtrando pelo pelotão informado."""
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    filters = [CL7.pelotao == pelotao_val]
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

    query = CL7.query.filter(*filters)
    items = query.order_by(CL7.atualizado_em.desc()).paginate(page=page, per_page=10)
    sums = _summary_query(filters)
    return items, q, sums

def _create_core(form: CL7Form, pelotao_val: str) -> bool:
    """Core: cria registro em CL7 já fixando o pelotão (form não exibe pelotão)."""
    if form.validate_on_submit():
        it = CL7(
            material=form.material.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            numero_serie=form.numero_serie.data,
            situacao=normalize_situacao(form.situacao.data),
            observacao=form.observacao.data,
            pelotao=pelotao_val,
        )
        db.session.add(it)
        db.session.commit()
        flash("Item cadastrado.", "success")
        return True
    return False

def _update_core(form: CL7Form, it: CL7, pelotao_val: str) -> bool:
    """Core: atualiza registro, garantindo consistência de pelotão."""
    if form.validate_on_submit():
        it.material = form.material.data
        it.marca = form.marca.data
        it.modelo = form.modelo.data
        it.numero_serie = form.numero_serie.data
        it.situacao = normalize_situacao(form.situacao.data)
        it.observacao = form.observacao.data
        it.pelotao = pelotao_val
        db.session.commit()
        flash("Item CL7 atualizado.", "success")
        return True
    return False

# ---------------- 1º PELOTÃO ----------------
@bp.get("/cl7/p1")
@class_required("CL7")
def cl7_p1_list():
    items, q, sums = _list_core("1º PELOTAO")
    return render_template(
        "cl7_list_sep.html",
        items=items, q=q, sums=sums,
        pel_label="1º PELOTÃO",
        create_endpoint="inv.cl7_p1_new",
        edit_endpoint="inv.cl7_p1_edit",
        delete_endpoint="inv.cl7_p1_delete",
        print_endpoint="inv.cl7_p1_print",
    )

@bp.route("/cl7/p1/new", methods=["GET", "POST"])
@class_required("CL7")
def cl7_p1_new():
    form = CL7Form()
    if _create_core(form, "1º PELOTAO"):
        return redirect(url_for("inv.cl7_p1_list"))
    return render_template("cl7_form_sep.html", form=form, mode="new", pel_label="1º PELOTÃO", back_endpoint="inv.cl7_p1_list")

@bp.route("/cl7/p1/<int:id>/edit", methods=["GET", "POST"])
@class_required("CL7")
def cl7_p1_edit(id):
    it = CL7.query.get_or_404(id)
    if it.pelotao != "1º PELOTAO":
        flash("Registro não pertence ao 1º Pelotão.", "warning")
        return redirect(url_for("inv.cl7_p1_list"))
    form = CL7Form(obj=it)
    if _update_core(form, it, "1º PELOTAO"):
        return redirect(url_for("inv.cl7_p1_list"))
    return render_template("cl7_form_sep.html", form=form, mode="edit", item=it, pel_label="1º PELOTÃO", back_endpoint="inv.cl7_p1_list")

@bp.post("/cl7/p1/<int:id>/delete")
@class_required("CL7")
def cl7_p1_delete(id):
    it = CL7.query.get_or_404(id)
    if it.pelotao != "1º PELOTAO":
        flash("Registro não pertence ao 1º Pelotão.", "warning")
        return redirect(url_for("inv.cl7_p1_list"))
    db.session.delete(it)
    db.session.commit()
    flash("Item CL7 removido.", "warning")
    return redirect(url_for("inv.cl7_p1_list"))

@bp.get("/cl7/p1/print-pdf")
@class_required("CL7")
def cl7_p1_print():
    return _cl7_print_pdf_core("1º PELOTAO", "CL7 — 1º Pelotão")

# ---------------- 2º PELOTÃO ----------------
@bp.get("/cl7/p2")
@class_required("CL7")
def cl7_p2_list():
    items, q, sums = _list_core("2º PELOTAO")
    return render_template(
        "cl7_list_sep.html",
        items=items, q=q, sums=sums,
        pel_label="2º PELOTÃO",
        create_endpoint="inv.cl7_p2_new",
        edit_endpoint="inv.cl7_p2_edit",
        delete_endpoint="inv.cl7_p2_delete",
        print_endpoint="inv.cl7_p2_print",
    )

@bp.route("/cl7/p2/new", methods=["GET", "POST"])
@class_required("CL7")
def cl7_p2_new():
    form = CL7Form()
    if _create_core(form, "2º PELOTAO"):
        return redirect(url_for("inv.cl7_p2_list"))
    return render_template("cl7_form_sep.html", form=form, mode="new", pel_label="2º PELOTÃO", back_endpoint="inv.cl7_p2_list")

@bp.route("/cl7/p2/<int:id>/edit", methods=["GET", "POST"])
@class_required("CL7")
def cl7_p2_edit(id):
    it = CL7.query.get_or_404(id)
    if it.pelotao != "2º PELOTAO":
        flash("Registro não pertence ao 2º Pelotão.", "warning")
        return redirect(url_for("inv.cl7_p2_list"))
    form = CL7Form(obj=it)
    if _update_core(form, it, "2º PELOTAO"):
        return redirect(url_for("inv.cl7_p2_list"))
    return render_template("cl7_form_sep.html", form=form, mode="edit", item=it, pel_label="2º PELOTÃO", back_endpoint="inv.cl7_p2_list")

@bp.post("/cl7/p2/<int:id>/delete")
@class_required("CL7")
def cl7_p2_delete(id):
    it = CL7.query.get_or_404(id)
    if it.pelotao != "2º PELOTAO":
        flash("Registro não pertence ao 2º Pelotão.", "warning")
        return redirect(url_for("inv.cl7_p2_list"))
    db.session.delete(it)
    db.session.commit()
    flash("Item CL7 removido.", "warning")
    return redirect(url_for("inv.cl7_p2_list"))

@bp.get("/cl7/p2/print-pdf")
@class_required("CL7")
def cl7_p2_print():
    return _cl7_print_pdf_core("2º PELOTAO", "CL7 — 2º Pelotão")

# ----- Impressão PDF reusável por pelotão -----
def _cl7_print_pdf_core(pelotao_val: str, titulo: str):
    filters = [CL7.pelotao == pelotao_val]
    items = CL7.query.filter(*filters).order_by(CL7.atualizado_em.desc()).all()
    sums = _summary_query(filters)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title=titulo
    )
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, spaceAfter=6)
    Normal = styles["Normal"]

    story = []
    story.append(Paragraph(titulo, H1))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", Normal))
    story.append(Spacer(1, 8))

    data = [["ID", "Material", "Marca", "Modelo", "Nº Série", "Situação", "Observação"]]
    for it in items:
        data.append([
            it.id, it.material or "-", it.marca or "-", it.modelo or "-",
            it.numero_serie or "-", it.situacao or "-", it.observacao or "-",
        ])

    tbl = Table(
        data,
        colWidths=[14*mm, 36*mm, 26*mm, 26*mm, 26*mm, 24*mm, 60*mm],
        repeatRows=1
    )
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
    pdf = buffer.getvalue()
    buffer.close()

    resp = make_response(pdf)
    resp.headers["Content-Type"] = "application/pdf"
    filename = "cl7_p1.pdf" if pelotao_val.startswith("1") else "cl7_p2.pdf"
    resp.headers["Content-Disposition"] = f"inline; filename={filename}"
    return resp

# =====================================================================================
# Impressão PDF CL7 (geral, mantém sua rota antiga para não quebrar links existentes)
# =====================================================================================
@bp.get("/cl7/print-pdf")
@class_required("CL7")
def cl7_print_pdf():
    """PDF geral de CL7 (todos os pelotões). Mantida para compatibilidade."""
    q = request.args.get("q", "").strip()

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

    items = CL7.query.filter(*filters).order_by(CL7.atualizado_em.desc()).all()
    sums = _summary_query(filters)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="Resumo CL7 (Geral)"
    )
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, spaceAfter=6)
    Normal = styles["Normal"]

    story = []
    story.append(Paragraph("Resumo CL7 — Geral", H1))
    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q:
        cab += f" &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Filtro: <b>{q}</b>"
    story.append(Paragraph(cab, Normal))
    story.append(Spacer(1, 8))

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

    tbl = Table(data, colWidths=[14*mm, 36*mm, 26*mm, 26*mm, 26*mm, 24*mm, 60*mm], repeatRows=1)
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

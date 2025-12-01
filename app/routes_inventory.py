# app/routes_inventory.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import current_user
from sqlalchemy import func, or_, case
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
import io

from .utils import class_required  # segue vindo do utils.py
from .models import db, CL2, CL6, CL7, CL1, CL1Log
from .forms import CL2Form, CL6Form, CL7Form, CL1Form

bp = Blueprint("inv", __name__, url_prefix="/inv")

# ------------------------
# Helpers
# ------------------------
def normalize_situacao(raw: str | None) -> str:
    """Normaliza texto de situação para valores canônicos (salva em maiúsculo)."""
    s = (raw or "ok").strip().lower()
    if s in {"ok", "livre", "disponivel", "disponível", "s/a"}:
        return "DISPONÍVEL"
    if s in {"defeito", "manutencao", "manutenção", "indisponivel", "indisponível", "baixado", "bxd"}:
        return "INDISPONÍVEL"
    if s in {"cautelado", "emprestado"}:
        return "CAUTELADO"
    return (raw or "OK").upper()

# Classe 1 - RAÇÕES 

@bp.get("/cl1", endpoint="cl1_list")
@class_required("CL1")
def cl1_list():
    rows = CL1.query.order_by(CL1.atualizado_em.desc()).all()
    return render_template("cl1_list.html", rows=rows)

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
            cardapio1=form.cardapio1.data,
            cardapio2=form.cardapio2.data,
            cardapio3=form.cardapio3.data,
            cardapio4=form.cardapio4.data,
            menu_atual=form.menu_atual.data,
            lote=form.lote.data,
        )
        db.session.add(item)
        db.session.commit()
        flash("Ração cadastrada com sucesso!", "success")
        return redirect(url_for("inv.cl1_list"))
    return render_template("cl1_form.html", form=form, title="Nova Ração", mode="new")

# Editar
@bp.route("/cl1/<int:id>/edit", methods=["GET", "POST"], endpoint="cl1_edit")
@class_required("CL1")
def cl1_edit(id):
    item = CL1.query.get_or_404(id)
    form = CL1Form(obj=item)
    if request.method == "GET" and (
        not item.menu_atual or item.menu_atual not in [c[0] for c in form.menu_atual.choices]
    ):
        form.menu_atual.data = form.menu_atual.default
    if form.validate_on_submit():
        if not form.motivo_edicao.data:
            flash("Informe o motivo da edição.", "warning")
            return render_template("cl1_form.html", form=form, title="Editar Ração", mode="edit")

        snapshot_antes = {
            "tipo": item.tipo,
            "quantidade": item.quantidade,
            "validade": item.validade.isoformat() if item.validade else None,
            "cardapio1": item.cardapio1,
            "cardapio2": item.cardapio2,
            "cardapio3": item.cardapio3,
            "cardapio4": item.cardapio4,
            "menu_atual": item.menu_atual,
            "lote": item.lote,
        }

        item.tipo = form.tipo.data
        item.quantidade = form.quantidade.data
        item.validade = form.validade.data
        item.cardapio1 = form.cardapio1.data
        item.cardapio2 = form.cardapio2.data
        item.cardapio3 = form.cardapio3.data
        item.cardapio4 = form.cardapio4.data
        item.menu_atual = form.menu_atual.data
        item.lote = form.lote.data

        snapshot_depois = {
            "tipo": item.tipo,
            "quantidade": item.quantidade,
            "validade": item.validade.isoformat() if item.validade else None,
            "cardapio1": item.cardapio1,
            "cardapio2": item.cardapio2,
            "cardapio3": item.cardapio3,
            "cardapio4": item.cardapio4,
            "menu_atual": item.menu_atual,
            "lote": item.lote,
        }

        log_entry = CL1Log(
            cl1=item,
            user_id=current_user.id if current_user and current_user.is_authenticated else None,
            user_name=(current_user.full_name or current_user.username)
            if current_user and current_user.is_authenticated
            else None,
            motivo=form.motivo_edicao.data,
            dados_antes=snapshot_antes,
            dados_depois=snapshot_depois,
        )
        db.session.add(log_entry)
        db.session.commit()
        flash("Ração atualizada com sucesso!", "success")
        return redirect(url_for("inv.cl1_list"))
    return render_template("cl1_form.html", form=form, title="Editar Ração", mode="edit")

# Deletar
@bp.post("/cl1/<int:id>/delete", endpoint="cl1_delete")
@class_required("CL1")
def cl1_delete(id):
    item = CL1.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Ração removida com sucesso!", "success")
    return redirect(url_for("inv.cl1_list"))


@bp.get("/cl1/<int:id>/logs", endpoint="cl1_logs")
@class_required("CL1")
def cl1_logs(id):
    item = CL1.query.get_or_404(id)
    logs = (
        CL1Log.query.filter_by(cl1_id=id)
        .order_by(CL1Log.criado_em.desc())
        .all()
    )
    return render_template("cl1_history.html", item=item, logs=logs)


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
            necessidade=form.necessidade.data or 0,
            qtd_cautelada=form.qtd_cautelada.data or 0,
            observacoes=form.observacoes.data,
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
        title="Resumo Classe 2"
    )
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, spaceAfter=6)
    Normal = styles["Normal"]

    CellStyle = ParagraphStyle(
        name="CellStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        wordWrap="CJK" # QUEBRA DE LINHA AUTOMATICA
    )

    story = []
    story.append(Paragraph("Relação Material Classe II", H1))
    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q or m:
        filtros_txt = []
        if q: filtros_txt.append(f"Busca: <b>{q}</b>")
        if m: filtros_txt.append(f"Material: <b>{m}</b>")
        cab += " &nbsp;&nbsp;|&nbsp;&nbsp; " + " · ".join(filtros_txt)
    story.append(Paragraph(cab, Normal))
    story.append(Spacer(1, 8))

    data = [[
        "ID",
        "Material",
        "Situação",
        "Necessidade",
        "Prevista",
        "Disp.",
        "Cautelada",
        "Indisp.",
        "Total",
        "Observações",
    ]]

    for it in rows:
        data.append([
            it.id,
            Paragraph(it.nome or "-", CellStyle),
            Paragraph(it.situacao or "-", CellStyle),
            it.necessidade or 0,
            it.qtd_prevista or 0,
            it.qtd_disp or 0,
            it.qtd_cautelada or 0,
            it.qtd_indisp or 0,
            (it.qtd_disp or 0) + (it.qtd_cautelada or 0) + (it.qtd_indisp or 0),
            Paragraph(it.observacoes or "-", CellStyle),
        ])

    tbl = Table(
        data,
        colWidths=[
            12*mm,
            35*mm,
            20*mm,
            15*mm,
            15*mm,
            15*mm,
            15*mm,
            15*mm,
            15*mm,
            17*mm,
        ],
        repeatRows=1,
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
                CL6.material.ilike(like),
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
            material=form.material.data,
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
            CL6.material.ilike(like),
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

    # ===== Helpers =====
    def br_moeda(v):
        try:
            n = float(v)
        except (TypeError, ValueError):
            return "-"
        # Formata estilo pt-BR sem depender de locale do SO
        s = f"{n:,.2f}"
        return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

    total_itens = len(rows)
    soma_valores = sum(float(getattr(r, "valor_inclusao_carga") or 0) for r in rows)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=12*mm, rightMargin=12*mm,
        topMargin=14*mm, bottomMargin=14*mm,
        title="Resumo Materiais Classe VI",
    )

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"],
                        fontName="Helvetica-Bold", fontSize=16, spaceAfter=4)
    Small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, leading=10)
    Normal = ParagraphStyle("Normal9", parent=styles["Normal"], fontSize=9, leading=12)
    Cell = ParagraphStyle("Cell", parent=styles["Normal"], fontName="Helvetica",
                          fontSize=8, leading=10, wordWrap="CJK")

    story = []
    story.append(Paragraph("Relação Material Classe VI", H1))

    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q:
        cab += f" &nbsp;&nbsp;|&nbsp;&nbsp; Busca: <b>{q}</b>"
    story.append(Paragraph(cab, Small))
    story.append(Spacer(1, 4))

    # Resumo
    resumo = f"Itens: <b>{total_itens}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Soma dos valores: <b>{br_moeda(soma_valores)}</b>"
    story.append(Paragraph(resumo, Normal))
    story.append(Spacer(1, 6))

    # Cabeçalho e dados
    headers = [
        "ID", "Material", "Situação", "CODOT", "Nº Patr.",
        "Ano", "Disp.", "Categoria", "Valor (R$)", "Localização",
        "Marca", "Modelo", "Nº Série",
    ]
    data = [headers]

    if rows:
        for it in rows:
            data.append([
                it.id,
                Paragraph(it.material or "-", Cell),
                Paragraph(it.situacao_patrimonial or "-", Cell),
                Paragraph(it.codot_item_material or "-", Cell),
                Paragraph(it.numero_patrimonio_material or "-", Cell),
                Paragraph(str(it.ano_fabricacao or "-"), Cell),
                Paragraph(it.disponibilidade or "-", Cell),
                Paragraph(it.categoria or "-", Cell),
                Paragraph(br_moeda(it.valor_inclusao_carga), Cell),
                Paragraph(it.localizacao_atual or "-", Cell),
                Paragraph(it.marca or "-", Cell),
                Paragraph(it.modelo or "-", Cell),
                Paragraph(it.numero_serie or "-", Cell),
            ])
    else:
        # Corrigido: usa o mesmo nº de colunas
        data.append(["— Sem registros —"] + ["-"] * (len(headers) - 1))

    # Larguras otimizadas p/ A4 paisagem
    col_widths = [
        10*mm, 38*mm, 24*mm, 28*mm, 24*mm,
        14*mm, 16*mm, 24*mm, 22*mm,
        36*mm, 28*mm, 32*mm, 26*mm
    ]

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    ts = [
        # Cabeçalho
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        # Grade e tipografia
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
        ("LEADING", (0, 1), (-1, -1), 10),
        # Alinhamentos por coluna
        ("ALIGN", (0, 1), (0, -1), "CENTER"),   # ID
        ("ALIGN", (4, 1), (4, -1), "CENTER"),   # Ano
        ("ALIGN", (5, 1), (5, -1), "CENTER"),   # Disp.
        ("ALIGN", (7, 1), (7, -1), "RIGHT"),    # Valor
    ]
    # Em caso de "Sem registros", mantém alinhamento central
    if not rows:
        ts.append(("ALIGN", (0, 1), (-1, 1), "CENTER"))

    tbl.setStyle(TableStyle(ts))
    story.append(tbl)

    # ===== Cabeçalho/Rodapé por página =====
    def _header_footer(canvas, doc_):
        canvas.saveState()
        w, h = landscape(A4)
        # Título leve no topo
        canvas.setFont("Helvetica", 8)
        canvas.drawString(doc_.leftMargin, h - 10*mm, "CL6 • Relatório de Materiais")
        # Numeração de páginas
        page_txt = f"Página {canvas.getPageNumber()}"
        canvas.drawRightString(w - doc_.rightMargin, 10*mm, page_txt)
        canvas.restoreState()

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)

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
        func.sum(case((s.in_(["INDISPONIVEL", "INDISPONÍVEL", "DEFEITO", "MANUTENCAO", "MANUTENÇÃO", "BAIXADO"]), 1), else_=0)),
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
    q = request.args.get("q", "").strip()

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

    CellStyle = ParagraphStyle(
        name="CellStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        wordWrap="CJK"  # habilita quebra automática
    )

    story = []
    story.append(Paragraph(titulo, H1))
    cab = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if q:
        cab += f" &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Filtro: <b>{q}</b>"
    story.append(Paragraph(cab, Normal))
    story.append(Spacer(1, 8))

    data = [["ID", "Material", "Marca", "Modelo", "Nº Série", "Situação", "Observação"]]

    for it in items:
        data.append([
            it.id,
            Paragraph(it.material or "-", CellStyle),
            Paragraph(it.marca or "-", CellStyle),
            Paragraph(it.modelo or "-", CellStyle),
            Paragraph(it.numero_serie or "-", CellStyle),
            Paragraph(it.situacao or "-", CellStyle),
            Paragraph(it.observacao or "-", CellStyle),
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
        title="Relação Classe VII - Geral"
    )
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, spaceAfter=6)
    Normal = styles["Normal"]

    CellStyle = ParagraphStyle(
        name="CellStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        wordWrap="CJK"  # habilita quebra automática
    )

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
            Paragraph(it.material or "-", CellStyle),
            Paragraph(it.marca or "-", CellStyle),
            Paragraph(it.modelo or "-", CellStyle),
            Paragraph(it.numero_serie or "-", CellStyle),
            Paragraph(it.situacao or "-", CellStyle),
            Paragraph(it.observacao or "-", CellStyle),
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

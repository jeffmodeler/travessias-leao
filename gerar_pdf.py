# coding: utf-8
"""
TRAVESSIAS — Gerador de PDF (eBook editorial)
==============================================
Lê src/cartas.js e gera travessias.pdf com diagramação editorial profissional.

Estrutura do livro:
1.  Capa
2.  Folha de rosto (título limpo)
3.  Ficha técnica / colofão de abertura
4.  Sumário
5.  Para cada entrada (12 ao todo):
    a. Página de abertura da carta (foto + label + nome + epígrafe)
    b. Páginas de texto com header sutil + numeração de página
    c. Fechamento (ornamento + assinatura)
6.  Colofão final

Formato: A5 retrato (148×210 mm) — proporção de livro de leitura.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


# --------------------------------------------------------------------------
# PALETA DE CORES DO PROJETO
# --------------------------------------------------------------------------

CREME = HexColor("#FAF7F2")
TINTA = HexColor("#1E2A38")
TINTA_SUAVE = HexColor("#2C3849")
TERRA = HexColor("#A84A2A")
MEL = HexColor("#C89B4A")
OLIVA = HexColor("#5C6B4E")
CARVAO = HexColor("#3A3A3A")
CINZA = HexColor("#8A8578")

# --------------------------------------------------------------------------
# DIMENSÕES E FONTES
# --------------------------------------------------------------------------

PG_W, PG_H = A5  # 148 × 210 mm
MARGIN_OUTER = 18 * mm   # margem externa (laterais)
MARGIN_TOP = 22 * mm
MARGIN_BOTTOM = 18 * mm

# ReportLab embute Times/Helvetica/Courier. Manter consistência editorial.
FONTE_TITULO = "Times-Roman"
FONTE_TITULO_ITAL = "Times-Italic"
FONTE_TITULO_BOLD = "Times-Bold"
FONTE_TEXTO = "Times-Roman"
FONTE_TEXTO_ITAL = "Times-Italic"
FONTE_META = "Helvetica"
FONTE_META_BOLD = "Helvetica-Bold"


# --------------------------------------------------------------------------
# DATACLASSES
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Carta:
    """Representa uma entrada do livro (autora, prefácio ou carta)."""

    id: str
    numero: str
    label: str
    tipo: str
    nome: str
    saudacao: str
    idade: str
    cidade: str
    foto: str
    epigrafe: str
    assinatura: str
    paginas: tuple[str, ...]

    @property
    def eh_carta(self) -> bool:
        """True se for uma carta numerada (não abertura nem prefácio)."""
        return bool(self.numero)

    @property
    def rotulo(self) -> str:
        """Rótulo legível: 'Carta I' ou 'Autora' ou 'Prefácio'."""
        if self.numero:
            return f"Carta {self.numero}"
        return self.label or "Abertura"


# --------------------------------------------------------------------------
# PARSER DE cartas.js
# --------------------------------------------------------------------------


def _extrair_paginas(arr_content: str) -> list[str]:
    """Extrai cada string entre backticks do array paginas: [...]."""
    pages: list[str] = []
    i = 0
    n = len(arr_content)
    while i < n:
        while i < n and arr_content[i] != "`":
            i += 1
        if i >= n:
            break
        i += 1
        start = i
        while i < n and arr_content[i] != "`":
            i += 1
        pages.append(arr_content[start:i])
        i += 1
    return pages


def extrair_cartas(path: str = "src/cartas.js") -> list[Carta]:
    """Lê cartas.js e devolve a lista de Carta na ordem do arquivo."""
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    array_match = re.search(r"const CARTAS\s*=\s*\[(.*?)\n\];", src, re.DOTALL)
    if not array_match:
        raise RuntimeError("Não encontrei const CARTAS = [...] em " + path)
    body = array_match.group(1)

    # Captura cada objeto { ... } no nível raiz do array
    objs: list[str] = []
    depth = 0
    start = None
    for i, ch in enumerate(body):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objs.append(body[start : i + 1])

    cartas: list[Carta] = []
    for obj_text in objs:
        campos: dict[str, str] = {}
        for campo in (
            "id", "numero", "label", "tipo", "nome",
            "saudacao", "idade", "cidade", "foto",
            "epigrafe", "assinatura",
        ):
            m = re.search(rf'{campo}:\s*"((?:[^"\\]|\\.)*)"', obj_text)
            campos[campo] = m.group(1) if m else ""

        pag_m = re.search(r"paginas:\s*\[(.*?)\n\s*\]", obj_text, re.DOTALL)
        paginas = tuple(_extrair_paginas(pag_m.group(1))) if pag_m else ()

        cartas.append(
            Carta(
                id=campos["id"],
                numero=campos["numero"],
                label=campos["label"],
                tipo=campos["tipo"],
                nome=campos["nome"],
                saudacao=campos["saudacao"],
                idade=campos["idade"],
                cidade=campos["cidade"],
                foto=campos["foto"],
                epigrafe=campos["epigrafe"],
                assinatura=campos["assinatura"],
                paginas=paginas,
            )
        )

    return cartas


# --------------------------------------------------------------------------
# CONVERSÃO HTML → reportlab Paragraph
# --------------------------------------------------------------------------


def _limpar_inline(html: str) -> str:
    """Converte tags inline HTML para o subset suportado pelo Paragraph."""
    # Tags inline equivalentes
    html = re.sub(r"<em\b[^>]*>", "<i>", html)
    html = re.sub(r"</em>", "</i>", html)
    html = re.sub(r"<strong\b[^>]*>", "<b>", html)
    html = re.sub(r"</strong>", "</b>", html)
    html = re.sub(r"<br\s*/?>", "<br/>", html)
    # Links viram apenas o texto (sem destaque) — PDF não tem hyperlinks aqui
    html = re.sub(r'<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', r"\1", html)
    # Remove tags desconhecidas mas preserva o texto
    html = re.sub(r"<(?!/?(?:i|b|br|font|sup|sub)\b)[^>]+>", "", html)
    # Entidades comuns
    return (
        html.replace("&ldquo;", "“")
        .replace("&rdquo;", "”")
        .replace("&lsquo;", "‘")
        .replace("&rsquo;", "’")
        .replace("&hellip;", "…")
        .replace("&mdash;", "—")
        .replace("&ndash;", "–")
        .replace("&nbsp;", " ")
        .strip()
    )


def html_to_flowables(html: str, styles: dict[str, ParagraphStyle]) -> list:
    """Converte uma string HTML em uma sequência de flowables do reportlab."""
    flow: list = []
    blocos = re.split(r"(?=<(?:p|blockquote|div)[\s>])", html)
    for blk in blocos:
        blk = blk.strip()
        if not blk:
            continue

        # blockquote class="citacao"
        if re.match(r'<blockquote[^>]*class="citacao"', blk):
            inner = re.sub(r"<blockquote[^>]*>", "", blk)
            inner = re.sub(r"</blockquote>\s*$", "", inner)
            attrib_m = re.search(
                r'<span[^>]*class="citacao-atribuicao"[^>]*>(.*?)</span>', inner
            )
            atribuicao = attrib_m.group(1).strip() if attrib_m else ""
            if attrib_m:
                inner = inner.replace(attrib_m.group(0), "").strip()
            flow.append(Paragraph(_limpar_inline(inner), styles["citacao"]))
            if atribuicao:
                flow.append(Paragraph(_limpar_inline(atribuicao), styles["atribuicao"]))
            flow.append(Spacer(1, 6))
            continue

        # div class="dialogo"
        if re.match(r'<div[^>]*class="dialogo"', blk):
            inner = re.sub(r"<div[^>]*>", "", blk, count=1)
            inner = re.sub(r"</div>\s*$", "", inner)
            flow.append(Paragraph(_limpar_inline(inner), styles["dialogo"]))
            continue

        # <p> normal ou sem-indent
        m_p = re.match(r"<p([^>]*)>(.*)</p>\s*$", blk, re.DOTALL)
        if m_p:
            attrs, content = m_p.group(1), m_p.group(2)
            sem_indent = "sem-indent" in attrs
            style = styles["p_sem_indent"] if sem_indent else styles["p"]
            flow.append(Paragraph(_limpar_inline(content), style))
            continue

    return flow


# --------------------------------------------------------------------------
# ESTILOS EDITORIAIS
# --------------------------------------------------------------------------


def montar_estilos() -> dict[str, ParagraphStyle]:
    """Devolve o dicionário de estilos editoriais usados no PDF."""

    s: dict[str, ParagraphStyle] = {}

    # --- Capa ---
    s["capa_marca"] = ParagraphStyle(
        "capa_marca",
        fontName=FONTE_META_BOLD,
        fontSize=10,
        leading=14,
        textColor=MEL,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    s["capa_titulo"] = ParagraphStyle(
        "capa_titulo",
        fontName=FONTE_TITULO_ITAL,
        fontSize=52,
        leading=56,
        textColor=CREME,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    s["capa_subtitulo"] = ParagraphStyle(
        "capa_subtitulo",
        fontName=FONTE_TITULO_ITAL,
        fontSize=17,
        leading=22,
        textColor=MEL,
        alignment=TA_CENTER,
        spaceAfter=40,
    )
    s["capa_autora"] = ParagraphStyle(
        "capa_autora",
        fontName=FONTE_META,
        fontSize=11,
        leading=15,
        textColor=CREME,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    s["capa_ano"] = ParagraphStyle(
        "capa_ano",
        fontName=FONTE_META,
        fontSize=10,
        leading=14,
        textColor=MEL,
        alignment=TA_CENTER,
    )

    # --- Folha de rosto e ficha técnica ---
    s["rosto_titulo"] = ParagraphStyle(
        "rosto_titulo",
        fontName=FONTE_TITULO_ITAL,
        fontSize=40,
        leading=44,
        textColor=TINTA,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    s["rosto_subtitulo"] = ParagraphStyle(
        "rosto_subtitulo",
        fontName=FONTE_TITULO_ITAL,
        fontSize=15,
        leading=18,
        textColor=TERRA,
        alignment=TA_CENTER,
        spaceAfter=40,
    )
    s["rosto_autora"] = ParagraphStyle(
        "rosto_autora",
        fontName=FONTE_META,
        fontSize=10,
        leading=14,
        textColor=CINZA,
        alignment=TA_CENTER,
    )
    s["colofao"] = ParagraphStyle(
        "colofao",
        fontName=FONTE_META,
        fontSize=8.5,
        leading=14,
        textColor=CARVAO,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    s["colofao_label"] = ParagraphStyle(
        "colofao_label",
        fontName=FONTE_META_BOLD,
        fontSize=7.5,
        leading=12,
        textColor=MEL,
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    # --- Sumário ---
    s["toc_titulo"] = ParagraphStyle(
        "toc_titulo",
        fontName=FONTE_TITULO_ITAL,
        fontSize=26,
        leading=30,
        textColor=TINTA,
        alignment=TA_CENTER,
        spaceAfter=24,
    )
    s["toc_item_rotulo"] = ParagraphStyle(
        "toc_item_rotulo",
        fontName=FONTE_META_BOLD,
        fontSize=8,
        leading=12,
        textColor=MEL,
        alignment=TA_LEFT,
    )
    s["toc_item_nome"] = ParagraphStyle(
        "toc_item_nome",
        fontName=FONTE_TITULO_ITAL,
        fontSize=15,
        leading=20,
        textColor=TINTA,
        alignment=TA_LEFT,
        spaceAfter=10,
    )

    # --- Abertura de cada carta ---
    s["carta_rotulo"] = ParagraphStyle(
        "carta_rotulo",
        fontName=FONTE_META_BOLD,
        fontSize=10,
        leading=14,
        textColor=MEL,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    s["carta_saudacao"] = ParagraphStyle(
        "carta_saudacao",
        fontName=FONTE_TITULO_ITAL,
        fontSize=30,
        leading=34,
        textColor=CREME,
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    s["carta_epigrafe"] = ParagraphStyle(
        "carta_epigrafe",
        fontName=FONTE_TEXTO_ITAL,
        fontSize=11.5,
        leading=17,
        textColor=CREME,
        alignment=TA_CENTER,
        leftIndent=24,
        rightIndent=24,
        spaceAfter=12,
    )
    s["carta_meta"] = ParagraphStyle(
        "carta_meta",
        fontName=FONTE_META,
        fontSize=8.5,
        leading=13,
        textColor=MEL,
        alignment=TA_CENTER,
    )

    # --- Corpo da carta (texto) ---
    s["p"] = ParagraphStyle(
        "p",
        fontName=FONTE_TEXTO,
        fontSize=10.5,
        leading=16.5,
        textColor=TINTA,
        alignment=TA_JUSTIFY,
        firstLineIndent=14,
        spaceAfter=2,
    )
    s["p_sem_indent"] = ParagraphStyle(
        "p_sem_indent",
        parent=s["p"],
        firstLineIndent=0,
        spaceBefore=4,
    )
    s["citacao"] = ParagraphStyle(
        "citacao",
        fontName=FONTE_TEXTO_ITAL,
        fontSize=11.5,
        leading=17,
        textColor=TINTA,
        alignment=TA_LEFT,
        leftIndent=22,
        rightIndent=22,
        spaceBefore=12,
        spaceAfter=4,
    )
    s["atribuicao"] = ParagraphStyle(
        "atribuicao",
        fontName=FONTE_META,
        fontSize=8,
        leading=11,
        textColor=CINZA,
        alignment=TA_RIGHT,
        leftIndent=22,
        rightIndent=22,
        spaceAfter=10,
    )
    s["dialogo"] = ParagraphStyle(
        "dialogo",
        fontName=FONTE_TEXTO,
        fontSize=10,
        leading=15,
        textColor=OLIVA,
        alignment=TA_LEFT,
        leftIndent=16,
        spaceBefore=6,
        spaceAfter=10,
    )

    # --- Fechamento da carta ---
    s["ornamento"] = ParagraphStyle(
        "ornamento",
        fontName=FONTE_META,
        fontSize=10,
        leading=14,
        textColor=MEL,
        alignment=TA_CENTER,
        spaceBefore=14,
        spaceAfter=8,
    )
    s["assinatura"] = ParagraphStyle(
        "assinatura",
        fontName=FONTE_TITULO_ITAL,
        fontSize=20,
        leading=24,
        textColor=TINTA,
        alignment=TA_RIGHT,
        spaceBefore=4,
    )
    s["assinatura_meta"] = ParagraphStyle(
        "assinatura_meta",
        fontName=FONTE_META,
        fontSize=7.5,
        leading=12,
        textColor=CINZA,
        alignment=TA_RIGHT,
    )

    return s


# --------------------------------------------------------------------------
# DESENHOS DE FUNDO (page templates)
# --------------------------------------------------------------------------


# Estado mutável compartilhado com os handlers de página (que o reportlab
# chama com (canvas, doc), sem closure). Cada handler lê de _ctx.
_ctx: dict[str, str] = {"carta_atual": ""}


def fundo_capa_livro(c, _doc) -> None:
    """Fundo tinta + ornamento de capa do livro."""
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    # filete mel decorativo no topo
    c.setStrokeColor(MEL)
    c.setLineWidth(0.6)
    c.line(MARGIN_OUTER, PG_H - 30 * mm, PG_W - MARGIN_OUTER, PG_H - 30 * mm)
    # filete inferior também
    c.line(PG_W / 2 - 20 * mm, 22 * mm, PG_W / 2 + 20 * mm, 22 * mm)
    c.restoreState()


def fundo_capa_carta(c, _doc) -> None:
    """Fundo tinta para a página de abertura de cada carta."""
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()


def fundo_texto(c, _doc) -> None:
    """Fundo creme + header sutil com nome da carta + número de página."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)

    nome_carta = _ctx.get("carta_atual", "")
    if nome_carta:
        # Header: nome da carta em versaletes pequeninhos
        c.setFont(FONTE_META, 7)
        c.setFillColor(CINZA)
        c.drawCentredString(PG_W / 2, PG_H - 12 * mm, nome_carta.upper())
        # filete fino abaixo do header
        c.setStrokeColor(MEL)
        c.setLineWidth(0.3)
        c.line(
            PG_W / 2 - 12 * mm, PG_H - 14 * mm,
            PG_W / 2 + 12 * mm, PG_H - 14 * mm,
        )

    # Footer: número de página
    c.setFont(FONTE_META, 7.5)
    c.setFillColor(CINZA)
    c.drawCentredString(PG_W / 2, 10 * mm, str(c.getPageNumber()))

    c.restoreState()


def fundo_rosto(c, _doc) -> None:
    """Folha de rosto / sumário / colofão — creme com ornamentos sutis."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)

    # Filete decorativo central no topo
    c.setStrokeColor(MEL)
    c.setLineWidth(0.4)
    c.line(PG_W / 2 - 15 * mm, PG_H - 30 * mm, PG_W / 2 + 15 * mm, PG_H - 30 * mm)

    # Número de página no rodapé (exceto na folha de rosto que é "i")
    c.setFont(FONTE_META, 7.5)
    c.setFillColor(CINZA)
    c.drawCentredString(PG_W / 2, 10 * mm, str(c.getPageNumber()))

    c.restoreState()


# --------------------------------------------------------------------------
# CONSTRUÇÃO DO PDF
# --------------------------------------------------------------------------


def _foto_disponivel(carta: Carta) -> Optional[str]:
    """Devolve o caminho da foto se existir; None caso contrário."""
    if carta.foto and os.path.exists(carta.foto):
        return carta.foto
    return None


def construir_pdf(cartas: list[Carta], saida: str = "travessias.pdf") -> str:
    """Monta o PDF editorial completo e devolve o caminho do arquivo gerado."""

    styles = montar_estilos()

    doc = BaseDocTemplate(
        saida,
        pagesize=A5,
        leftMargin=MARGIN_OUTER,
        rightMargin=MARGIN_OUTER,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Travessias — cartas de mulheres reais",
        author="Renata Leão",
        subject="eBook · Cartas autobiográficas de dez mulheres reais",
        keywords="travessias, mulheres, cartas, fotografia, Renata Leão",
        allowSplitting=1,
    )

    frame_full = Frame(
        0, 0, PG_W, PG_H,
        leftPadding=MARGIN_OUTER, rightPadding=MARGIN_OUTER,
        topPadding=MARGIN_TOP, bottomPadding=MARGIN_BOTTOM,
        id="full",
    )
    frame_texto = Frame(
        MARGIN_OUTER, MARGIN_BOTTOM,
        PG_W - 2 * MARGIN_OUTER, PG_H - MARGIN_TOP - MARGIN_BOTTOM,
        leftPadding=0, rightPadding=0,
        topPadding=4 * mm, bottomPadding=4 * mm,
        id="texto",
    )

    doc.addPageTemplates([
        PageTemplate(id="capa-livro",  frames=[frame_full],  onPage=fundo_capa_livro),
        PageTemplate(id="capa-carta",  frames=[frame_full],  onPage=fundo_capa_carta),
        PageTemplate(id="rosto",       frames=[frame_full],  onPage=fundo_rosto),
        PageTemplate(id="texto",       frames=[frame_texto], onPage=fundo_texto),
    ])

    story: list = []

    # ----- BLOCO 1: CAPA DO LIVRO -----
    story.append(NextPageTemplate("capa-livro"))
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("CARTAS DE MULHERES REAIS", styles["capa_marca"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Travessias", styles["capa_titulo"]))

    # Foto da Renata centralizada na capa
    foto_renata = _foto_disponivel(
        Carta(
            id="renata", numero="", label="", tipo="abertura", nome="Renata Leão",
            saudacao="", idade="", cidade="",
            foto="fotos/renata_leao.jpg",
            epigrafe="", assinatura="", paginas=(),
        )
    )
    if foto_renata:
        img = Image(foto_renata, width=55 * mm, height=72 * mm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 14 * mm))
    else:
        story.append(Spacer(1, 50 * mm))

    story.append(Paragraph("Por <b>RENATA LEÃO</b>", styles["capa_autora"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Volume 01 · 2025", styles["capa_ano"]))
    story.append(PageBreak())

    # ----- BLOCO 2: FOLHA DE ROSTO -----
    story.append(NextPageTemplate("rosto"))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("Travessias", styles["rosto_titulo"]))
    story.append(Paragraph("cartas de mulheres reais", styles["rosto_subtitulo"]))
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("Por", styles["rosto_autora"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>RENATA LEÃO</b>", styles["rosto_autora"]))
    story.append(PageBreak())

    # ----- BLOCO 3: FICHA TÉCNICA / COLOFÃO DE ABERTURA -----
    story.append(Spacer(1, 60 * mm))
    story.append(Paragraph("FICHA TÉCNICA", styles["colofao_label"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>Travessias — cartas de mulheres reais</b>", styles["colofao"]))
    story.append(Paragraph("Volume 01 · Edição 2025", styles["colofao"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Idealização, fotografia e palavra", styles["colofao_label"]))
    story.append(Paragraph("Renata Leão", styles["colofao"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Prefácio", styles["colofao_label"]))
    story.append(Paragraph("Nicole Pelosi", styles["colofao"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Origem", styles["colofao_label"]))
    story.append(Paragraph(
        "Entrevistas realizadas durante a 1ª edição do Festival MEL — Mulheres em Lutas, em 2025.",
        styles["colofao"],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Contato", styles["colofao_label"]))
    story.append(Paragraph("@renataleaofotografia · renataleaofotografia@gmail.com", styles["colofao"]))
    story.append(PageBreak())

    # ----- BLOCO 4: SUMÁRIO -----
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("Sumário", styles["toc_titulo"]))
    story.append(Spacer(1, 6 * mm))
    for carta in cartas:
        story.append(Paragraph(carta.rotulo.upper(), styles["toc_item_rotulo"]))
        story.append(Paragraph(carta.nome, styles["toc_item_nome"]))
    story.append(PageBreak())

    # ----- BLOCO 5: CADA ENTRADA (12 ao todo) -----
    for carta in cartas:
        # 5a · Página de abertura: foto + label + nome + epígrafe
        story.append(NextPageTemplate("capa-carta"))
        # Limpa header da próxima página
        _ctx["carta_atual"] = ""

        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph(carta.rotulo.upper(), styles["carta_rotulo"]))

        foto = _foto_disponivel(carta)
        if foto:
            img = Image(foto, width=58 * mm, height=82 * mm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 8 * mm))

        story.append(Paragraph(carta.saudacao, styles["carta_saudacao"]))

        if carta.epigrafe:
            story.append(Paragraph(f"“{carta.epigrafe}”", styles["carta_epigrafe"]))

        meta = " · ".join(p for p in (carta.idade, carta.cidade) if p)
        if meta:
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph(meta, styles["carta_meta"]))

        story.append(PageBreak())

        # 5b · Páginas de texto — define o header com o nome
        story.append(NextPageTemplate("texto"))
        _ctx["carta_atual"] = carta.nome

        for pHtml in carta.paginas:
            story.extend(html_to_flowables(pHtml, styles))

        # 5c · Fechamento — ornamento + assinatura + data + autoria
        story.append(Paragraph("· · ·", styles["ornamento"]))
        story.append(Paragraph(carta.assinatura, styles["assinatura"]))

        data = "Abril · 2025" if carta.eh_carta else "2025"
        if carta.eh_carta:
            assinatura_meta = f"{data}<br/>Por Renata Leão"
        else:
            assinatura_meta = data
        story.append(Paragraph(assinatura_meta, styles["assinatura_meta"]))

        story.append(PageBreak())

    # ----- BLOCO 6: COLOFÃO FINAL -----
    story.append(NextPageTemplate("rosto"))
    story.append(Spacer(1, 70 * mm))
    story.append(Paragraph("· · ·", styles["ornamento"]))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "Travessias é sobre mulheres que seguem,<br/>que atravessam a própria vida.",
        styles["colofao"],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "<i>Mulheres que sustentam outras mulheres. Mulheres que, juntas,<br/>"
        "criam abrigo enquanto buscam abrigo em outras travessias.</i>",
        styles["colofao"],
    ))
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("RENATA LEÃO · 2025", styles["colofao_label"]))

    doc.build(story)
    return saida


# --------------------------------------------------------------------------
# ENTRADA PRINCIPAL
# --------------------------------------------------------------------------


def main() -> int:
    """Carrega cartas.js, monta o PDF e imprime estatísticas."""
    cartas = extrair_cartas("src/cartas.js")
    print(f"Carregadas {len(cartas)} entradas:")
    total_pgs = 0
    for c in cartas:
        total_pgs += len(c.paginas)
        rotulo = c.rotulo
        print(f"  - {rotulo:13} {c.nome:24} {len(c.paginas):>2} pgs")

    saida = construir_pdf(cartas, "travessias.pdf")
    tamanho = os.path.getsize(saida)
    print(f"\nPDF gerado: {saida} ({tamanho // 1024} KB)")
    print(f"Conteúdo: {total_pgs} páginas de texto + capa + rosto + colofão + sumário + 12 aberturas")
    return 0


if __name__ == "__main__":
    sys.exit(main())

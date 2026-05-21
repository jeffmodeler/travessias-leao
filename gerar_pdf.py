# coding: utf-8
"""
TRAVESSIAS — Gerador de PDF (eBook editorial)
==============================================

Diagramação no estilo de livro de fotografia/literário, formato 6×9 polegadas
(formato padrão de paperback de trade nos EUA, comum em livros-arte e ensaios).

Sequência editorial:

    1. Capa
    2. Folha de rosto (limpa, com ornamento)
    3. Ficha técnica (duas colunas refinadas)
    4. Sumário com três seções tipográficas:
         · ABERTURA  · PREFÁCIO  · AS CARTAS
       Nomes alinhados à esquerda e ano à direita (sem números de
       página — convenção de eBook moderno).
    5. Para cada uma das 12 entradas:
         a. Página de meia-portada (label "CARTA III" + grande)
         b. Página retratada (foto + nome + epígrafe centralizada)
         c. Corpo da carta (texto justificado, drop-cap no primeiro
            parágrafo, header com nome em versaletes + filete mel)
         d. Fechamento (ornamento + assinatura à direita)
    6. Colofão final (citação síntese + crédito + ornamento de cauda)

Refatoração técnica em PEP-8 com type hints; estrutura em camadas
(parser → modelo → estilos → desenho de página → composição).
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ==========================================================================
# PALETA DE CORES (igual ao site)
# ==========================================================================

CREME = HexColor("#FAF7F2")
TINTA = HexColor("#1E2A38")
TINTA_SUAVE = HexColor("#2C3849")
TERRA = HexColor("#A84A2A")
MEL = HexColor("#C89B4A")
OLIVA = HexColor("#5C6B4E")
CARVAO = HexColor("#3A3A3A")
CINZA = HexColor("#8A8578")


# ==========================================================================
# DIMENSÕES E FONTES
# ==========================================================================

# 6 × 9 polegadas — formato de paperback de trade (152.4 × 228.6 mm)
PG_W, PG_H = 6 * inch, 9 * inch
MARGIN_OUTER = 20 * mm
MARGIN_INNER = 22 * mm   # margem interna ligeiramente maior (lombada)
MARGIN_TOP = 24 * mm
MARGIN_BOTTOM = 22 * mm

FONTE_TITULO = "Times-Roman"
FONTE_TITULO_ITAL = "Times-Italic"
FONTE_TITULO_BOLD = "Times-Bold"
FONTE_TEXTO = "Times-Roman"
FONTE_TEXTO_ITAL = "Times-Italic"
FONTE_TEXTO_BOLD = "Times-Bold"
FONTE_META = "Helvetica"
FONTE_META_BOLD = "Helvetica-Bold"


# ==========================================================================
# MODELO
# ==========================================================================


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
        return bool(self.numero)

    @property
    def rotulo(self) -> str:
        if self.numero:
            return f"Carta {self.numero}"
        return self.label or "Abertura"

    @property
    def autoria_credito(self) -> str:
        """Por quem foi escrita esta entrada — 'Renata Leão' ou 'Nicole Pelosi'."""
        if self.tipo == "prefacio":
            return "Nicole Pelosi"
        return "Renata Leão"


# ==========================================================================
# PARSER de cartas.js
# ==========================================================================


def _extrair_paginas_array(arr_content: str) -> list[str]:
    pages: list[str] = []
    i, n = 0, len(arr_content)
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
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    array_match = re.search(r"const CARTAS\s*=\s*\[(.*?)\n\];", src, re.DOTALL)
    if not array_match:
        raise RuntimeError(f"const CARTAS = [...] não encontrado em {path}")
    body = array_match.group(1)

    objs: list[str] = []
    depth, start = 0, None
    for i, ch in enumerate(body):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objs.append(body[start : i + 1])

    campos_obrigatorios = (
        "id", "numero", "label", "tipo", "nome",
        "saudacao", "idade", "cidade", "foto", "epigrafe", "assinatura",
    )

    cartas: list[Carta] = []
    for obj_text in objs:
        valores = {}
        for campo in campos_obrigatorios:
            m = re.search(rf'{campo}:\s*"((?:[^"\\]|\\.)*)"', obj_text)
            valores[campo] = m.group(1) if m else ""
        pag_m = re.search(r"paginas:\s*\[(.*?)\n\s*\]", obj_text, re.DOTALL)
        paginas = tuple(_extrair_paginas_array(pag_m.group(1))) if pag_m else ()
        cartas.append(Carta(**valores, paginas=paginas))
    return cartas


# ==========================================================================
# HTML → flowables
# ==========================================================================


def _limpar_inline(html: str) -> str:
    html = re.sub(r"<em\b[^>]*>", "<i>", html)
    html = re.sub(r"</em>", "</i>", html)
    html = re.sub(r"<strong\b[^>]*>", "<b>", html)
    html = re.sub(r"</strong>", "</b>", html)
    html = re.sub(r"<br\s*/?>", "<br/>", html)
    html = re.sub(r'<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', r"\1", html)
    html = re.sub(r"<(?!/?(?:i|b|br|font|sup|sub)\b)[^>]+>", "", html)
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


def _aplicar_drop_cap(texto: str) -> str:
    """Insere drop-cap inline (primeira letra maior em terra)."""
    texto = texto.lstrip()
    if not texto:
        return texto
    # encontra a primeira letra real (pula tags abertas)
    m = re.match(r"^(<[^>]+>)*([A-Za-zÁÉÍÓÚÀÂÊÔÃÕÇáéíóúàâêôãõç])", texto)
    if not m:
        return texto
    abre = m.group(1) or ""
    letra = m.group(2)
    resto = texto[m.end():]
    return (
        f'{abre}<font size="32" color="#A84A2A" face="Times-Roman">{letra}</font>'
        f'{resto}'
    )


def html_to_flowables(
    html: str,
    styles: dict[str, ParagraphStyle],
    *,
    com_drop_cap: bool = False,
) -> list:
    flow: list = []
    blocos = re.split(r"(?=<(?:p|blockquote|div)[\s>])", html)
    primeiro_p_ja_aplicado = False

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
            flow.append(Spacer(1, 4))
            continue

        # div class="dialogo"
        if re.match(r'<div[^>]*class="dialogo"', blk):
            inner = re.sub(r"<div[^>]*>", "", blk, count=1)
            inner = re.sub(r"</div>\s*$", "", inner)
            flow.append(Paragraph(_limpar_inline(inner), styles["dialogo"]))
            continue

        # <p>
        m_p = re.match(r"<p([^>]*)>(.*)</p>\s*$", blk, re.DOTALL)
        if m_p:
            attrs, content = m_p.group(1), m_p.group(2)
            sem_indent = "sem-indent" in attrs
            content_limpo = _limpar_inline(content)

            if com_drop_cap and not primeiro_p_ja_aplicado and sem_indent:
                content_limpo = _aplicar_drop_cap(content_limpo)
                primeiro_p_ja_aplicado = True
                style = styles["p_drop_cap"]
            else:
                style = styles["p_sem_indent"] if sem_indent else styles["p"]

            flow.append(Paragraph(content_limpo, style))
            continue

    return flow


# ==========================================================================
# ESTILOS EDITORIAIS
# ==========================================================================


def montar_estilos() -> dict[str, ParagraphStyle]:
    s: dict[str, ParagraphStyle] = {}

    # ---- Capa ----
    s["capa_marca"] = ParagraphStyle(
        "capa_marca", fontName=FONTE_META_BOLD, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER, spaceAfter=8,
    )
    s["capa_titulo"] = ParagraphStyle(
        "capa_titulo", fontName=FONTE_TITULO_ITAL, fontSize=64,
        leading=68, textColor=CREME, alignment=TA_CENTER, spaceAfter=14,
    )
    s["capa_subtitulo"] = ParagraphStyle(
        "capa_subtitulo", fontName=FONTE_TITULO_ITAL, fontSize=18,
        leading=24, textColor=MEL, alignment=TA_CENTER, spaceAfter=8,
    )
    s["capa_autora"] = ParagraphStyle(
        "capa_autora", fontName=FONTE_META, fontSize=10,
        leading=14, textColor=CREME, alignment=TA_CENTER,
    )
    s["capa_ano"] = ParagraphStyle(
        "capa_ano", fontName=FONTE_META_BOLD, fontSize=8,
        leading=12, textColor=MEL, alignment=TA_CENTER,
    )

    # ---- Folha de rosto ----
    s["rosto_titulo"] = ParagraphStyle(
        "rosto_titulo", fontName=FONTE_TITULO_ITAL, fontSize=46,
        leading=50, textColor=TINTA, alignment=TA_CENTER, spaceAfter=10,
    )
    s["rosto_subtitulo"] = ParagraphStyle(
        "rosto_subtitulo", fontName=FONTE_TITULO_ITAL, fontSize=16,
        leading=20, textColor=TERRA, alignment=TA_CENTER, spaceAfter=48,
    )
    s["rosto_autora"] = ParagraphStyle(
        "rosto_autora", fontName=FONTE_META, fontSize=11,
        leading=16, textColor=CARVAO, alignment=TA_CENTER,
    )

    # ---- Ficha técnica ----
    s["ficha_secao"] = ParagraphStyle(
        "ficha_secao", fontName=FONTE_META_BOLD, fontSize=7.5,
        leading=11, textColor=MEL, alignment=TA_LEFT, spaceAfter=2,
    )
    s["ficha_valor"] = ParagraphStyle(
        "ficha_valor", fontName=FONTE_TEXTO, fontSize=9.5,
        leading=14, textColor=CARVAO, alignment=TA_LEFT, spaceAfter=10,
    )

    # ---- Sumário ----
    s["sum_titulo"] = ParagraphStyle(
        "sum_titulo", fontName=FONTE_TITULO_ITAL, fontSize=30,
        leading=34, textColor=TINTA, alignment=TA_CENTER, spaceAfter=10,
    )
    s["sum_secao"] = ParagraphStyle(
        "sum_secao", fontName=FONTE_META_BOLD, fontSize=8.5,
        leading=12, textColor=MEL, alignment=TA_LEFT, spaceAfter=2,
    )
    s["sum_item_rotulo"] = ParagraphStyle(
        "sum_item_rotulo", fontName=FONTE_META, fontSize=8,
        leading=11, textColor=CINZA, alignment=TA_LEFT,
    )
    s["sum_item_nome"] = ParagraphStyle(
        "sum_item_nome", fontName=FONTE_TITULO_ITAL, fontSize=15,
        leading=20, textColor=TINTA, alignment=TA_LEFT,
    )
    s["sum_item_epigrafe"] = ParagraphStyle(
        "sum_item_epigrafe", fontName=FONTE_TEXTO_ITAL, fontSize=9,
        leading=13, textColor=CARVAO, alignment=TA_LEFT, spaceAfter=10,
    )
    s["sum_item_autor"] = ParagraphStyle(
        "sum_item_autor", fontName=FONTE_META, fontSize=8,
        leading=11, textColor=CINZA, alignment=TA_RIGHT,
    )

    # ---- Meia-portada (página antes da carta) ----
    s["meia_portada_rotulo"] = ParagraphStyle(
        "meia_portada_rotulo", fontName=FONTE_META_BOLD, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER, spaceAfter=12,
    )
    s["meia_portada_nome"] = ParagraphStyle(
        "meia_portada_nome", fontName=FONTE_TITULO_ITAL, fontSize=48,
        leading=54, textColor=TINTA, alignment=TA_CENTER, spaceAfter=18,
    )
    s["meia_portada_epigrafe"] = ParagraphStyle(
        "meia_portada_epigrafe", fontName=FONTE_TEXTO_ITAL, fontSize=12,
        leading=18, textColor=CARVAO, alignment=TA_CENTER,
        leftIndent=30, rightIndent=30, spaceAfter=4,
    )

    # ---- Página retratada (foto + saudação) ----
    s["retrato_rotulo"] = ParagraphStyle(
        "retrato_rotulo", fontName=FONTE_META_BOLD, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER, spaceAfter=10,
    )
    s["retrato_saudacao"] = ParagraphStyle(
        "retrato_saudacao", fontName=FONTE_TITULO_ITAL, fontSize=32,
        leading=36, textColor=CREME, alignment=TA_CENTER, spaceAfter=12,
    )
    s["retrato_meta"] = ParagraphStyle(
        "retrato_meta", fontName=FONTE_META, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER,
    )

    # ---- Corpo do texto ----
    s["p"] = ParagraphStyle(
        "p", fontName=FONTE_TEXTO, fontSize=10.5, leading=16.5,
        textColor=TINTA, alignment=TA_JUSTIFY,
        firstLineIndent=16, spaceAfter=2,
    )
    s["p_sem_indent"] = ParagraphStyle(
        "p_sem_indent", parent=s["p"],
        firstLineIndent=0, spaceBefore=4,
    )
    s["p_drop_cap"] = ParagraphStyle(
        "p_drop_cap", parent=s["p_sem_indent"],
        leading=18,  # leading maior pra acomodar o tamanho da letra inicial
    )
    s["citacao"] = ParagraphStyle(
        "citacao", fontName=FONTE_TEXTO_ITAL, fontSize=11.5,
        leading=17, textColor=TINTA, alignment=TA_LEFT,
        leftIndent=24, rightIndent=24, spaceBefore=12, spaceAfter=4,
    )
    s["atribuicao"] = ParagraphStyle(
        "atribuicao", fontName=FONTE_META, fontSize=8,
        leading=11, textColor=CINZA, alignment=TA_RIGHT,
        leftIndent=24, rightIndent=24, spaceAfter=10,
    )
    s["dialogo"] = ParagraphStyle(
        "dialogo", fontName=FONTE_TEXTO, fontSize=10,
        leading=15, textColor=OLIVA, alignment=TA_LEFT,
        leftIndent=18, spaceBefore=6, spaceAfter=10,
    )

    # ---- Fechamento ----
    s["ornamento"] = ParagraphStyle(
        "ornamento", fontName=FONTE_META, fontSize=11,
        leading=14, textColor=MEL, alignment=TA_CENTER,
        spaceBefore=16, spaceAfter=10,
    )
    s["assinatura"] = ParagraphStyle(
        "assinatura", fontName=FONTE_TITULO_ITAL, fontSize=22,
        leading=26, textColor=TINTA, alignment=TA_RIGHT, spaceBefore=6,
    )
    s["assinatura_meta"] = ParagraphStyle(
        "assinatura_meta", fontName=FONTE_META, fontSize=8,
        leading=13, textColor=CINZA, alignment=TA_RIGHT,
    )

    # ---- Colofão final ----
    s["colofao_citacao"] = ParagraphStyle(
        "colofao_citacao", fontName=FONTE_TITULO_ITAL, fontSize=14,
        leading=22, textColor=TINTA, alignment=TA_CENTER,
        leftIndent=24, rightIndent=24, spaceAfter=8,
    )
    s["colofao_credito"] = ParagraphStyle(
        "colofao_credito", fontName=FONTE_META_BOLD, fontSize=8,
        leading=12, textColor=MEL, alignment=TA_CENTER,
    )

    return s


# ==========================================================================
# DESENHOS DE FUNDO E HEADER/FOOTER
# ==========================================================================


_ctx: dict[str, str] = {"carta_atual": "", "pagina_atual_rotulo": ""}


def _desenhar_filete(c, x1: float, x2: float, y: float, cor=MEL, espessura: float = 0.4) -> None:
    c.saveState()
    c.setStrokeColor(cor)
    c.setLineWidth(espessura)
    c.line(x1, y, x2, y)
    c.restoreState()


def fundo_capa(c, _doc) -> None:
    """Capa do livro: tinta + dois filetes mel decorativos."""
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()
    _desenhar_filete(c, MARGIN_OUTER, PG_W - MARGIN_OUTER, PG_H - 30 * mm)
    _desenhar_filete(c, PG_W / 2 - 18 * mm, PG_W / 2 + 18 * mm, 20 * mm)


def fundo_carta_retrato(c, _doc) -> None:
    """Fundo tinta da página retratada (foto + saudação)."""
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()


def fundo_rosto(c, _doc) -> None:
    """Folhas creme sem header/footer (rosto, ficha, sumário, meia-portada)."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()
    # Filete delicado no topo
    _desenhar_filete(c, PG_W / 2 - 14 * mm, PG_W / 2 + 14 * mm, PG_H - 18 * mm, MEL, 0.3)


def fundo_texto(c, _doc) -> None:
    """Páginas de corpo: header com nome da carta, footer com número."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)

    nome = _ctx.get("carta_atual", "")
    if nome:
        c.setFont(FONTE_META, 7)
        c.setFillColor(CINZA)
        c.drawCentredString(PG_W / 2, PG_H - 14 * mm, nome.upper())
        _desenhar_filete(
            c,
            PG_W / 2 - 14 * mm, PG_W / 2 + 14 * mm,
            PG_H - 17 * mm, MEL, 0.3,
        )

    c.setFont(FONTE_META, 7.5)
    c.setFillColor(CINZA)
    c.drawCentredString(PG_W / 2, 12 * mm, str(c.getPageNumber()))

    c.restoreState()


# ==========================================================================
# CONSTRUÇÃO DO PDF
# ==========================================================================


def _foto_existe(caminho: str) -> Optional[str]:
    return caminho if caminho and os.path.exists(caminho) else None


def _tabela_ficha(linhas: list[tuple[str, str]], styles: dict[str, ParagraphStyle]) -> Table:
    """Monta a ficha técnica como tabela de duas colunas (label / valor)."""
    data = []
    for label, valor in linhas:
        data.append([
            Paragraph(label.upper(), styles["ficha_secao"]),
            Paragraph(valor, styles["ficha_valor"]),
        ])
    t = Table(data, colWidths=[38 * mm, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _bloco_sumario(
    cartas: list[Carta], styles: dict[str, ParagraphStyle]
) -> list:
    """Sumário editorial com três seções e nome do autor à direita."""

    flow: list = []

    def secao(titulo: str, entradas: list[Carta]) -> None:
        flow.append(Spacer(1, 6 * mm))
        flow.append(Paragraph(titulo.upper(), styles["sum_secao"]))
        flow.append(Spacer(1, 1 * mm))

        for c in entradas:
            esquerda_html = (
                f'<font color="#8A8578">{c.rotulo.upper()}</font><br/>'
                f'<font name="Times-Italic" size="14" color="#1E2A38">{c.nome}</font>'
            )
            esquerda = Paragraph(esquerda_html, styles["sum_item_rotulo"])
            direita = Paragraph(c.autoria_credito, styles["sum_item_autor"])

            t = Table(
                [[esquerda, direita]],
                colWidths=[None, 36 * mm],
                style=TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.3, MEL),
                ]),
            )
            flow.append(t)
            if c.epigrafe:
                flow.append(Spacer(1, 1 * mm))
                flow.append(Paragraph(
                    f'<i>“{c.epigrafe}”</i>', styles["sum_item_epigrafe"]
                ))

    aberturas = [c for c in cartas if c.tipo == "abertura"]
    prefacios = [c for c in cartas if c.tipo == "prefacio"]
    numeradas = [c for c in cartas if c.eh_carta]

    if aberturas:
        secao("Abertura", aberturas)
    if prefacios:
        secao("Prefácio", prefacios)
    if numeradas:
        secao("As cartas", numeradas)

    return flow


def construir_pdf(
    cartas: list[Carta],
    saida: str = "travessias.pdf",
) -> str:
    styles = montar_estilos()

    doc = BaseDocTemplate(
        saida, pagesize=(PG_W, PG_H),
        leftMargin=MARGIN_INNER, rightMargin=MARGIN_OUTER,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        title="Travessias — cartas de mulheres reais",
        author="Renata Leão",
        subject="eBook · cartas autobiográficas de dez mulheres reais",
        keywords="travessias, mulheres, cartas, fotografia, Renata Leão",
        creator="Travessias — gerar_pdf.py",
        allowSplitting=1,
    )

    frame_full = Frame(
        0, 0, PG_W, PG_H,
        leftPadding=MARGIN_INNER, rightPadding=MARGIN_OUTER,
        topPadding=MARGIN_TOP, bottomPadding=MARGIN_BOTTOM,
        id="full",
    )
    frame_texto = Frame(
        MARGIN_INNER, MARGIN_BOTTOM,
        PG_W - MARGIN_INNER - MARGIN_OUTER,
        PG_H - MARGIN_TOP - MARGIN_BOTTOM,
        leftPadding=0, rightPadding=0,
        topPadding=4 * mm, bottomPadding=4 * mm,
        id="texto",
    )

    doc.addPageTemplates([
        PageTemplate(id="capa",          frames=[frame_full],  onPage=fundo_capa),
        PageTemplate(id="rosto",         frames=[frame_full],  onPage=fundo_rosto),
        PageTemplate(id="carta-retrato", frames=[frame_full],  onPage=fundo_carta_retrato),
        PageTemplate(id="texto",         frames=[frame_texto], onPage=fundo_texto),
    ])

    story: list = []

    # -------- 1. CAPA --------
    story.append(NextPageTemplate("capa"))
    story.append(Spacer(1, 16 * mm))
    story.append(Paragraph("CARTAS DE MULHERES REAIS", styles["capa_marca"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Travessias", styles["capa_titulo"]))

    foto_renata = _foto_existe("fotos/renata_leao.jpg")
    if foto_renata:
        img = Image(foto_renata, width=68 * mm, height=92 * mm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 12 * mm))
    else:
        story.append(Spacer(1, 60 * mm))

    story.append(Paragraph("Por <b>RENATA LEÃO</b>", styles["capa_autora"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("VOLUME 01 · 2025", styles["capa_ano"]))
    story.append(PageBreak())

    # -------- 2. FOLHA DE ROSTO --------
    story.append(NextPageTemplate("rosto"))
    story.append(Spacer(1, 50 * mm))
    story.append(Paragraph("Travessias", styles["rosto_titulo"]))
    story.append(Paragraph("cartas de mulheres reais", styles["rosto_subtitulo"]))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("Por", styles["rosto_autora"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>RENATA LEÃO</b>", styles["rosto_autora"]))
    story.append(PageBreak())

    # -------- 3. FICHA TÉCNICA --------
    story.append(Spacer(1, 40 * mm))
    story.append(_tabela_ficha([
        ("Obra", "<b>Travessias — cartas de mulheres reais</b><br/>Volume 01 · Edição 2025"),
        ("Idealização", "Renata Leão"),
        ("Fotografia e palavra", "Renata Leão"),
        ("Prefácio", "Nicole Pelosi"),
        ("Origem", "Entrevistas realizadas durante a 1ª edição do Festival MEL — Mulheres em Lutas, em 2025."),
        ("Contato", "@renataleaofotografia<br/>renataleaofotografia@gmail.com"),
    ], styles))
    story.append(PageBreak())

    # -------- 4. SUMÁRIO --------
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("Sumário", styles["sum_titulo"]))
    story.append(Spacer(1, 6 * mm))
    story.extend(_bloco_sumario(cartas, styles))
    story.append(PageBreak())

    # -------- 5. CADA ENTRADA --------
    for carta in cartas:
        # 5a · Página retratada (foto sobre fundo tinta)
        story.append(NextPageTemplate("carta-retrato"))
        _ctx["carta_atual"] = ""

        story.append(Spacer(1, 16 * mm))
        story.append(Paragraph(carta.rotulo.upper(), styles["retrato_rotulo"]))

        foto = _foto_existe(carta.foto)
        if foto:
            img = Image(foto, width=72 * mm, height=104 * mm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 12 * mm))

        story.append(Paragraph(carta.saudacao, styles["retrato_saudacao"]))

        meta = " · ".join(p for p in (carta.idade, carta.cidade) if p)
        if meta:
            story.append(Paragraph(meta, styles["retrato_meta"]))

        story.append(PageBreak())

        # 5b · Meia-portada (em creme) com o nome em grande e a epígrafe
        story.append(NextPageTemplate("rosto"))
        story.append(Spacer(1, 60 * mm))
        story.append(Paragraph(carta.rotulo.upper(), styles["meia_portada_rotulo"]))
        story.append(Paragraph(carta.nome, styles["meia_portada_nome"]))
        if carta.epigrafe:
            story.append(Paragraph(f"“{carta.epigrafe}”", styles["meia_portada_epigrafe"]))
        story.append(PageBreak())

        # 5c · Páginas de texto
        story.append(NextPageTemplate("texto"))
        _ctx["carta_atual"] = carta.nome

        for i, pHtml in enumerate(carta.paginas):
            story.extend(html_to_flowables(
                pHtml, styles, com_drop_cap=(i == 0),
            ))

        # 5d · Fechamento (ornamento + assinatura à direita)
        story.append(Paragraph("· · ·", styles["ornamento"]))
        story.append(Paragraph(carta.assinatura, styles["assinatura"]))

        if carta.eh_carta:
            assinatura_meta = "Abril · 2025<br/>Por Renata Leão"
        elif carta.tipo == "prefacio":
            assinatura_meta = "2025<br/>Por Nicole Pelosi"
        else:
            assinatura_meta = "2025"
        story.append(Paragraph(assinatura_meta, styles["assinatura_meta"]))

        story.append(PageBreak())

    # -------- 6. COLOFÃO FINAL --------
    story.append(NextPageTemplate("rosto"))
    story.append(Spacer(1, 70 * mm))
    story.append(Paragraph("· · ·", styles["ornamento"]))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "Travessias é sobre mulheres que seguem,<br/>"
        "que atravessam a própria vida.",
        styles["colofao_citacao"],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "Mulheres que sustentam outras mulheres.<br/>"
        "Mulheres que, juntas, criam abrigo<br/>"
        "enquanto buscam abrigo em outras travessias.",
        styles["colofao_citacao"],
    ))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("RENATA LEÃO · VOLUME 01 · 2025", styles["colofao_credito"]))

    doc.build(story)
    return saida


# ==========================================================================
# ENTRADA PRINCIPAL
# ==========================================================================


def main() -> int:
    cartas = extrair_cartas("src/cartas.js")
    print(f"Carregadas {len(cartas)} entradas:")
    total_pgs = 0
    for c in cartas:
        total_pgs += len(c.paginas)
        print(f"  {c.rotulo:14}  {c.nome:24}  {len(c.paginas):>2} pgs")
    saida = construir_pdf(cartas, "travessias.pdf")
    tamanho_kb = os.path.getsize(saida) // 1024
    print(f"\nPDF: {saida} · {tamanho_kb} KB")
    print(f"Formato: 6×9 polegadas (paperback de trade)")
    print(f"Conteúdo: {total_pgs} pgs de texto + capa + rosto + ficha + sumário + 12 retratos + 12 meias-portadas + colofão")
    return 0


if __name__ == "__main__":
    sys.exit(main())

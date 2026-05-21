# coding: utf-8
"""
TRAVESSIAS — Gerador de PDF (eBook editorial)
==============================================

Estrutura editorial:

    Pré-textuais (creme)
      1. Capa do livro
      2. Folha de rosto
      3. Ficha técnica
      4. Sumário (com números de página reais)

    Para cada uma das 12 entradas:
      a. Página separadora (fundo tinta) — meia-portada limpa, anuncia
         a entrada. Equivale ao "frontispício" de um livro impresso.
      b. Página retratada (creme) — foto + saudação manuscrita +
         epígrafe + meta (idade · cidade).
      c. Texto da carta — uma página por entrada de paginas[], com
         drop-cap no primeiro parágrafo do primeiro bloco.
      d. Fechamento no final do último texto — ornamento + assinatura
         alinhada à direita + crédito de autoria.

    Pós-textuais
      • Colofão final

Detalhes:
    • Formato 6 × 9 polegadas, paperback de trade.
    • Header de páginas de texto: "TRAVESSIAS" em versaletes (não o
      nome da carta — convenção comum em livros de coletânea).
    • Footer: número de página em algarismos arábicos a partir
      da página de sumário.
    • Sumário tem números de página REAIS — calculados em pré-passo.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
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


class PageMarker(Flowable):
    """Flowable invisível que registra em qual página foi renderizado.

    Usado em two-pass build: na primeira passada, populamos um registry
    com os números de página reais; na segunda, o sumário usa esses
    números em vez da predição.
    """

    def __init__(self, key: str, registry: dict[str, int]) -> None:
        super().__init__()
        self.key = key
        self.registry = registry

    def wrap(self, _w: float, _h: float) -> tuple[float, float]:
        return 0, 0

    def draw(self) -> None:
        self.registry[self.key] = self.canv.getPageNumber()


# ==========================================================================
# PALETA
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

PG_W, PG_H = 6 * inch, 9 * inch
MARGIN_OUTER = 20 * mm
MARGIN_INNER = 22 * mm
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
    """Uma entrada do livro (autora, prefácio ou carta numerada)."""

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
    def numero_paginas_internas(self) -> int:
        """Páginas que esta entrada consome: 1 separador + 1 retrato + len(paginas)."""
        return 2 + len(self.paginas)


# ==========================================================================
# PARSER
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
        valores: dict[str, str] = {}
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
    texto = texto.lstrip()
    if not texto:
        return texto
    m = re.match(
        r"^(<[^>]+>)*([A-Za-zÁÉÍÓÚÀÂÊÔÃÕÇáéíóúàâêôãõç])", texto
    )
    if not m:
        return texto
    abre = m.group(1) or ""
    letra = m.group(2)
    resto = texto[m.end():]
    return (
        f'{abre}<font size="34" color="#A84A2A" face="Times-Roman">{letra}</font>'
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
    drop_aplicado = False

    for blk in blocos:
        blk = blk.strip()
        if not blk:
            continue

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

        if re.match(r'<div[^>]*class="dialogo"', blk):
            inner = re.sub(r"<div[^>]*>", "", blk, count=1)
            inner = re.sub(r"</div>\s*$", "", inner)
            flow.append(Paragraph(_limpar_inline(inner), styles["dialogo"]))
            continue

        m_p = re.match(r"<p([^>]*)>(.*)</p>\s*$", blk, re.DOTALL)
        if m_p:
            attrs, content = m_p.group(1), m_p.group(2)
            sem_indent = "sem-indent" in attrs
            content_limpo = _limpar_inline(content)

            if com_drop_cap and not drop_aplicado and sem_indent:
                content_limpo = _aplicar_drop_cap(content_limpo)
                drop_aplicado = True
                style = styles["p_drop_cap"]
            else:
                style = styles["p_sem_indent"] if sem_indent else styles["p"]

            flow.append(Paragraph(content_limpo, style))
            continue

    return flow


# ==========================================================================
# ESTILOS
# ==========================================================================


def montar_estilos() -> dict[str, ParagraphStyle]:
    s: dict[str, ParagraphStyle] = {}

    # ---- Capa ----
    s["capa_marca"] = ParagraphStyle(
        "capa_marca", fontName=FONTE_META_BOLD, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER, spaceAfter=8,
    )
    s["capa_titulo"] = ParagraphStyle(
        "capa_titulo", fontName=FONTE_TITULO_ITAL, fontSize=68,
        leading=72, textColor=CREME, alignment=TA_CENTER, spaceAfter=14,
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
        "rosto_titulo", fontName=FONTE_TITULO_ITAL, fontSize=48,
        leading=52, textColor=TINTA, alignment=TA_CENTER, spaceAfter=10,
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
        "sum_titulo", fontName=FONTE_TITULO_ITAL, fontSize=34,
        leading=38, textColor=TINTA, alignment=TA_CENTER, spaceAfter=20,
    )
    s["sum_secao"] = ParagraphStyle(
        "sum_secao", fontName=FONTE_META_BOLD, fontSize=8,
        leading=12, textColor=MEL, alignment=TA_LEFT,
        spaceBefore=10, spaceAfter=4,
    )
    s["sum_numero"] = ParagraphStyle(
        "sum_numero", fontName=FONTE_META, fontSize=9,
        leading=20, textColor=CINZA, alignment=TA_LEFT,
    )
    s["sum_nome"] = ParagraphStyle(
        "sum_nome", fontName=FONTE_TITULO_ITAL, fontSize=14,
        leading=20, textColor=TINTA, alignment=TA_LEFT,
    )
    s["sum_pagina"] = ParagraphStyle(
        "sum_pagina", fontName=FONTE_META, fontSize=10,
        leading=20, textColor=MEL, alignment=TA_RIGHT,
    )

    # ---- Separador (fundo tinta — anuncia carta) ----
    s["sep_rotulo"] = ParagraphStyle(
        "sep_rotulo", fontName=FONTE_META_BOLD, fontSize=11,
        leading=16, textColor=MEL, alignment=TA_CENTER, spaceAfter=22,
    )
    s["sep_nome"] = ParagraphStyle(
        "sep_nome", fontName=FONTE_TITULO_ITAL, fontSize=56,
        leading=62, textColor=CREME, alignment=TA_CENTER,
    )

    # ---- Retrato (creme — foto + saudação) ----
    s["retr_saudacao"] = ParagraphStyle(
        "retr_saudacao", fontName=FONTE_TITULO_ITAL, fontSize=32,
        leading=36, textColor=TINTA, alignment=TA_CENTER, spaceAfter=14,
    )
    s["retr_epigrafe"] = ParagraphStyle(
        "retr_epigrafe", fontName=FONTE_TEXTO_ITAL, fontSize=12,
        leading=18, textColor=CARVAO, alignment=TA_CENTER,
        leftIndent=24, rightIndent=24, spaceAfter=10,
    )
    s["retr_meta"] = ParagraphStyle(
        "retr_meta", fontName=FONTE_META, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER,
    )

    # ---- Corpo ----
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
        "p_drop_cap", parent=s["p_sem_indent"], leading=20,
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
        "colofao_citacao", fontName=FONTE_TITULO_ITAL, fontSize=15,
        leading=24, textColor=TINTA, alignment=TA_CENTER,
        leftIndent=22, rightIndent=22, spaceAfter=8,
    )
    s["colofao_credito"] = ParagraphStyle(
        "colofao_credito", fontName=FONTE_META_BOLD, fontSize=8,
        leading=12, textColor=MEL, alignment=TA_CENTER,
    )

    return s


# ==========================================================================
# FUNDOS DE PÁGINA
# ==========================================================================

# Estado mutável global para o handler de fundo (reportlab chama com
# (canvas, doc); precisamos passar contexto por aqui).
_ctx: dict[str, object] = {
    "mostrar_cabecalho": False,  # bool — se mostra "TRAVESSIAS" no header
    "numerar": False,             # bool — se mostra número de página
}


def _filete(c, x1: float, x2: float, y: float, cor=MEL, espessura: float = 0.4) -> None:
    c.saveState()
    c.setStrokeColor(cor)
    c.setLineWidth(espessura)
    c.line(x1, y, x2, y)
    c.restoreState()


def fundo_capa(c, _doc) -> None:
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()
    _filete(c, MARGIN_OUTER, PG_W - MARGIN_OUTER, PG_H - 30 * mm)
    _filete(c, PG_W / 2 - 18 * mm, PG_W / 2 + 18 * mm, 20 * mm)


def fundo_separador(c, _doc) -> None:
    """Fundo tinta com filete decorativo central — separador de carta."""
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()
    # Dois filetes simétricos, dão peso editorial à separação
    _filete(c, PG_W / 2 - 30 * mm, PG_W / 2 + 30 * mm, PG_H / 2 + 28 * mm, MEL, 0.5)
    _filete(c, PG_W / 2 - 20 * mm, PG_W / 2 + 20 * mm, PG_H / 2 - 50 * mm, MEL, 0.4)


def fundo_creme_pretextual(c, _doc) -> None:
    """Páginas creme antes do corpo (rosto, ficha, sumário, retratos)."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()
    _filete(c, PG_W / 2 - 14 * mm, PG_W / 2 + 14 * mm, PG_H - 18 * mm, MEL, 0.3)
    if _ctx.get("numerar"):
        c.saveState()
        c.setFont(FONTE_META, 7.5)
        c.setFillColor(CINZA)
        c.drawCentredString(PG_W / 2, 12 * mm, str(c.getPageNumber()))
        c.restoreState()


def fundo_texto(c, _doc) -> None:
    """Páginas de corpo da carta: header 'TRAVESSIAS' + footer com número."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)

    # Header: nome do projeto em versaletes
    c.setFont(FONTE_META, 7)
    c.setFillColor(CINZA)
    c.drawCentredString(PG_W / 2, PG_H - 14 * mm, "TRAVESSIAS")
    _filete(
        c,
        PG_W / 2 - 14 * mm, PG_W / 2 + 14 * mm,
        PG_H - 17 * mm, MEL, 0.3,
    )

    # Footer: número de página
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
    data = []
    for label, valor in linhas:
        data.append([
            Paragraph(label.upper(), styles["ficha_secao"]),
            Paragraph(valor, styles["ficha_valor"]),
        ])
    t = Table(data, colWidths=[42 * mm, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# Constantes da paginação calculada
PAGINAS_PRETEXTUAIS = 4  # capa, rosto, ficha, sumário (sumário = pg 4)


def _calcular_paginas_por_entrada(cartas: list[Carta]) -> dict[str, int]:
    """Calcula em que página COMEÇA cada entrada (a página separadora).

    Estrutura prevista:
      Pré-textuais: pgs 1..4 (capa, rosto, ficha, sumário)
      Cada entrada: 1 separador + 1 retrato + N text pages
    """
    pagina_atual = PAGINAS_PRETEXTUAIS + 1  # próxima página após o sumário
    mapa: dict[str, int] = {}
    for c in cartas:
        mapa[c.id] = pagina_atual
        pagina_atual += c.numero_paginas_internas
    return mapa


def _bloco_sumario(
    cartas: list[Carta],
    mapa_paginas: dict[str, int],
    styles: dict[str, ParagraphStyle],
) -> list:
    """Sumário com seções tipográficas e números de página alinhados à direita.

    Layout por linha:
      [I]    [Marília Martins]            [13]
      ^      ^                            ^
      8mm    expande                      14mm
    """
    flow: list = []

    def render_secao(titulo: str, entradas: list[Carta]) -> None:
        if not entradas:
            return
        flow.append(Spacer(1, 8 * mm))
        flow.append(Paragraph(titulo.upper(), styles["sum_secao"]))

        data = []
        for c in entradas:
            numero_visual = c.numero if c.numero else "—"
            pag = mapa_paginas.get(c.id, 0)
            data.append([
                Paragraph(numero_visual, styles["sum_numero"]),
                Paragraph(c.nome, styles["sum_nome"]),
                Paragraph(str(pag), styles["sum_pagina"]),
            ])

        t = Table(data, colWidths=[10 * mm, None, 14 * mm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, MEL),
        ]))
        flow.append(t)

    aberturas = [c for c in cartas if c.tipo == "abertura"]
    prefacios = [c for c in cartas if c.tipo == "prefacio"]
    numeradas = [c for c in cartas if c.eh_carta]

    render_secao("Abertura", aberturas)
    render_secao("Prefácio", prefacios)
    render_secao("As cartas", numeradas)

    return flow


def _build_uma_passada(
    cartas: list[Carta],
    mapa_paginas: dict[str, int],
    registry: dict[str, int],
    saida: str,
) -> None:
    """Constroi o PDF uma vez com o mapa de páginas dado e marcadores
    populando o registry."""
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
        PageTemplate(id="capa",        frames=[frame_full],  onPage=fundo_capa),
        PageTemplate(id="pretextual",  frames=[frame_full],  onPage=fundo_creme_pretextual),
        PageTemplate(id="separador",   frames=[frame_full],  onPage=fundo_separador),
        PageTemplate(id="retrato",     frames=[frame_full],  onPage=fundo_creme_pretextual),
        PageTemplate(id="texto",       frames=[frame_texto], onPage=fundo_texto),
    ])

    story: list = []

    # -------- 1. CAPA --------
    story.append(NextPageTemplate("capa"))
    story.append(Spacer(1, 16 * mm))
    story.append(Paragraph("CARTAS DE MULHERES REAIS", styles["capa_marca"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Travessias", styles["capa_titulo"]))

    foto_renata = _foto_existe("fotos/renata_leao.jpg")
    if foto_renata:
        img = Image(foto_renata, width=70 * mm, height=94 * mm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 14 * mm))
    else:
        story.append(Spacer(1, 60 * mm))

    story.append(Paragraph("Por <b>RENATA LEÃO</b>", styles["capa_autora"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("VOLUME 01 · 2025", styles["capa_ano"]))
    story.append(PageBreak())

    # -------- 2. FOLHA DE ROSTO --------
    _ctx["numerar"] = False
    story.append(NextPageTemplate("pretextual"))
    story.append(Spacer(1, 56 * mm))
    story.append(Paragraph("Travessias", styles["rosto_titulo"]))
    story.append(Paragraph("cartas de mulheres reais", styles["rosto_subtitulo"]))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("Por", styles["rosto_autora"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>RENATA LEÃO</b>", styles["rosto_autora"]))
    story.append(PageBreak())

    # -------- 3. FICHA TÉCNICA --------
    story.append(Spacer(1, 38 * mm))
    story.append(_tabela_ficha([
        ("Obra", "<b>Travessias — cartas de mulheres reais</b><br/>Volume 01 · Edição 2025"),
        ("Idealização", "Renata Leão"),
        ("Fotografia e palavra", "Renata Leão"),
        ("Prefácio", "Nicole Pelosi"),
        ("Origem", "Entrevistas realizadas durante a 1ª edição do Festival MEL — Mulheres em Lutas, em 2025."),
        ("Contato", "@renataleaofotografia<br/>renataleaofotografia@gmail.com"),
    ], styles))
    story.append(PageBreak())

    # -------- 4. SUMÁRIO (página 4, números reais) --------
    _ctx["numerar"] = True
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("Sumário", styles["sum_titulo"]))
    story.extend(_bloco_sumario(cartas, mapa_paginas, styles))
    story.append(PageBreak())

    # -------- 5. ENTRADAS --------
    for carta in cartas:
        # 5a · Separador (fundo tinta — meia-portada elegante)
        _ctx["numerar"] = True
        story.append(NextPageTemplate("separador"))
        story.append(PageMarker(carta.id, registry))  # registra página real
        story.append(Spacer(1, PG_H * 0.32))  # empurra pro centro vertical
        story.append(Paragraph(carta.rotulo.upper(), styles["sep_rotulo"]))
        story.append(Paragraph(carta.nome, styles["sep_nome"]))
        story.append(PageBreak())

        # 5b · Retrato (creme — foto + saudação + epígrafe + meta)
        story.append(NextPageTemplate("retrato"))
        story.append(Spacer(1, 16 * mm))
        story.append(Paragraph(carta.saudacao, styles["retr_saudacao"]))

        foto = _foto_existe(carta.foto)
        if foto:
            img = Image(foto, width=66 * mm, height=94 * mm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 10 * mm))

        if carta.epigrafe:
            story.append(Paragraph(
                f"“{carta.epigrafe}”", styles["retr_epigrafe"]
            ))

        meta = " · ".join(p for p in (carta.idade, carta.cidade) if p)
        if meta:
            story.append(Paragraph(meta, styles["retr_meta"]))

        story.append(PageBreak())

        # 5c · Páginas de texto — UMA PAGE BREAK ENTRE CADA pagina[]
        story.append(NextPageTemplate("texto"))
        for i, pHtml in enumerate(carta.paginas):
            story.extend(html_to_flowables(
                pHtml, styles, com_drop_cap=(i == 0),
            ))
            # Page break entre páginas, exceto na última (que termina com
            # fechamento + page break depois)
            if i < len(carta.paginas) - 1:
                story.append(PageBreak())

        # 5d · Fechamento na última página de texto
        story.append(Paragraph("· · ·", styles["ornamento"]))
        story.append(Paragraph(carta.assinatura, styles["assinatura"]))
        if carta.eh_carta:
            meta_ass = "Abril · 2025<br/>Por Renata Leão"
        elif carta.tipo == "prefacio":
            meta_ass = "2025<br/>Por Nicole Pelosi"
        else:
            meta_ass = "2025"
        story.append(Paragraph(meta_ass, styles["assinatura_meta"]))
        story.append(PageBreak())

    # -------- 6. COLOFÃO FINAL --------
    story.append(NextPageTemplate("pretextual"))
    story.append(Spacer(1, 80 * mm))
    story.append(Paragraph("· · ·", styles["ornamento"]))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "Travessias é sobre mulheres que seguem,<br/>"
        "que atravessam a própria vida.",
        styles["colofao_citacao"],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "<i>Mulheres que sustentam outras mulheres.<br/>"
        "Mulheres que, juntas, criam abrigo<br/>"
        "enquanto buscam abrigo em outras travessias.</i>",
        styles["colofao_citacao"],
    ))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("RENATA LEÃO · VOLUME 01 · 2025", styles["colofao_credito"]))

    doc.build(story)


def construir_pdf(cartas: list[Carta], saida: str = "travessias.pdf") -> str:
    """Constroi o PDF em duas passadas:

    1. Build inicial com predição de páginas. Cada separador de carta
       carrega um PageMarker que regista a página REAL no registry.
    2. Re-build usando o registry como mapa de páginas — agora o sumário
       reflete exatamente onde cada entrada começa.
    """
    # Passe 1: predição → captura páginas reais
    mapa_predito = _calcular_paginas_por_entrada(cartas)
    registry: dict[str, int] = {}
    _build_uma_passada(cartas, mapa_predito, registry, saida)

    # Se a predição já estiver correta, evita re-build
    if registry == mapa_predito:
        return saida

    # Passe 2: re-build com páginas reais
    registry2: dict[str, int] = {}
    _build_uma_passada(cartas, registry, registry2, saida)
    return saida


# ==========================================================================
# ENTRADA
# ==========================================================================


def main() -> int:
    cartas = extrair_cartas("src/cartas.js")
    mapa = _calcular_paginas_por_entrada(cartas)

    print(f"Carregadas {len(cartas)} entradas:")
    print(f"{'rótulo':14}  {'nome':24}  {'págs':>4}  {'inicia pg':>10}")
    print("-" * 65)
    total_pgs = 0
    for c in cartas:
        total_pgs += len(c.paginas)
        print(f"  {c.rotulo:12}  {c.nome:24}  {len(c.paginas):>4}  {mapa[c.id]:>10}")

    saida = construir_pdf(cartas, "travessias.pdf")
    tamanho_kb = os.path.getsize(saida) // 1024
    print()
    print(f"PDF: {saida} · {tamanho_kb} KB")
    print(f"Formato: 6×9 polegadas (152 × 229 mm)")
    print(f"Estrutura: 4 pré + {sum(c.numero_paginas_internas for c in cartas)} corpo + 1 colofão "
          f"= {4 + sum(c.numero_paginas_internas for c in cartas) + 1} páginas previstas")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# coding: utf-8
"""
TRAVESSIAS — Gerador de PDF (eBook editorial)
==============================================

Diagramação por book designer profissional:

    • Formato A4 retrato (210 × 297 mm) — padrão para distribuição
      e impressão doméstica.
    • Tipografia Times Roman 11.5pt / leading 17pt — confortável
      em A4 e respeitando a tradição de livro editorial.
    • Margens 28mm topo, 25mm base, 28mm interna (lombada), 22mm
      externa — convenção de paperback impresso.
    • Texto FLUI naturalmente por carta: as paginas[] do JS são
      concatenadas como um único bloco e reportlab faz a paginação
      automática (sem page breaks artificiais que deixavam espaço
      em branco no fim das páginas).
    • Sumário em UMA página, layout compacto.
    • Prefácio em UMA página (cabe sem forçar quebra).
    • Inicial colorida (não drop-cap real) na primeira letra do
      texto — destaque sutil sem sobreposição.
    • Header "TRAVESSIAS" + nome da carta atual em versaletes.
    • Footer com número de página.

Two-pass build com PageMarker → sumário com páginas reais.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
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
# PALETA E DIMENSÕES
# ==========================================================================

CREME = HexColor("#FAF7F2")
TINTA = HexColor("#1E2A38")
TINTA_SUAVE = HexColor("#2C3849")
TERRA = HexColor("#A84A2A")
MEL = HexColor("#C89B4A")
OLIVA = HexColor("#5C6B4E")
CARVAO = HexColor("#3A3A3A")
CINZA = HexColor("#8A8578")

PG_W, PG_H = A4  # 210 × 297 mm
MARGIN_TOP = 28 * mm
MARGIN_BOTTOM = 25 * mm
MARGIN_INNER = 28 * mm  # lombada — margem interna mais generosa
MARGIN_OUTER = 22 * mm

# Fontes Times/Helvetica embutidas no reportlab — sem dependências
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
    """Uma entrada do livro: autora, prefácio ou carta numerada."""

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
        return f"Carta {self.numero}" if self.numero else (self.label or "Abertura")


class PageMarker(Flowable):
    """Flowable invisível que registra em qual página foi renderizado."""

    def __init__(self, key: str, registry: dict[str, int]) -> None:
        super().__init__()
        self.key = key
        self.registry = registry

    def wrap(self, _w: float, _h: float) -> tuple[float, float]:
        return 0, 0

    def draw(self) -> None:
        self.registry[self.key] = self.canv.getPageNumber()


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

    campos = (
        "id", "numero", "label", "tipo", "nome",
        "saudacao", "idade", "cidade", "foto", "epigrafe", "assinatura",
    )

    cartas: list[Carta] = []
    for obj_text in objs:
        valores: dict[str, str] = {}
        for campo in campos:
            m = re.search(rf'{campo}:\s*"((?:[^"\\]|\\.)*)"', obj_text)
            valores[campo] = m.group(1) if m else ""
        pag_m = re.search(r"paginas:\s*\[(.*?)\n\s*\]", obj_text, re.DOTALL)
        paginas = tuple(_extrair_paginas_array(pag_m.group(1))) if pag_m else ()
        cartas.append(Carta(**valores, paginas=paginas))
    return cartas


# ==========================================================================
# HTML → flowables (texto fluido, sem page breaks artificiais)
# ==========================================================================


def _limpar_inline(html: str) -> str:
    """Converte HTML inline para o subset suportado pelo Paragraph."""
    html = re.sub(r"<em\b[^>]*>", "<i>", html)
    html = re.sub(r"</em>", "</i>", html)
    html = re.sub(r"<strong\b[^>]*>", "<b>", html)
    html = re.sub(r"</strong>", "</b>", html)
    html = re.sub(r"<br\s*/?>", "<br/>", html)
    html = re.sub(r'<a[^>]*href="[^"]+"[^>]*>(.*?)</a>', r"\1", html)
    html = re.sub(r"<(?!/?(?:i|b|br|font|sup|sub)\b)[^>]+>", "", html)
    return (
        html.replace("&ldquo;", "“").replace("&rdquo;", "”")
        .replace("&lsquo;", "‘").replace("&rsquo;", "’")
        .replace("&hellip;", "…").replace("&mdash;", "—").replace("&ndash;", "–")
        .replace("&nbsp;", " ").strip()
    )


def _destacar_primeira_letra(html: str) -> str:
    """Coloca a primeira letra real em cor terra (destaque sutil, sem
    alterar tamanho — não causa sobreposição como o drop-cap)."""
    m = re.match(
        r"^(<[^>]+>)*([A-Za-zÁÉÍÓÚÀÂÊÔÃÕÇáéíóúàâêôãõç])", html.lstrip()
    )
    if not m:
        return html
    pos = m.start(2)
    letra = m.group(2)
    return (
        html[:pos]
        + f'<font color="#A84A2A"><b>{letra}</b></font>'
        + html[pos + 1 :]
    )


def texto_da_carta(
    carta: Carta,
    styles: dict[str, ParagraphStyle],
) -> list:
    """Concatena todas as paginas[] da carta como um único fluxo, sem
    forçar quebras de página entre elas. Reportlab pagina naturalmente."""
    flow: list = []
    primeiro_paragrafo = True

    for pHtml in carta.paginas:
        blocos = re.split(r"(?=<(?:p|blockquote|div)[\s>])", pHtml)
        for blk in blocos:
            blk = blk.strip()
            if not blk:
                continue

            # blockquote citacao
            if re.match(r'<blockquote[^>]*class="citacao"', blk):
                inner = re.sub(r"<blockquote[^>]*>", "", blk)
                inner = re.sub(r"</blockquote>\s*$", "", inner)
                atrib_m = re.search(
                    r'<span[^>]*class="citacao-atribuicao"[^>]*>(.*?)</span>',
                    inner,
                )
                atribuicao = atrib_m.group(1).strip() if atrib_m else ""
                if atrib_m:
                    inner = inner.replace(atrib_m.group(0), "").strip()
                flow.append(Paragraph(_limpar_inline(inner), styles["citacao"]))
                if atribuicao:
                    flow.append(Paragraph(_limpar_inline(atribuicao), styles["atribuicao"]))
                continue

            # dialogo
            if re.match(r'<div[^>]*class="dialogo"', blk):
                inner = re.sub(r"<div[^>]*>", "", blk, count=1)
                inner = re.sub(r"</div>\s*$", "", inner)
                flow.append(Paragraph(_limpar_inline(inner), styles["dialogo"]))
                continue

            # parágrafo
            m_p = re.match(r"<p([^>]*)>(.*)</p>\s*$", blk, re.DOTALL)
            if m_p:
                attrs, content = m_p.group(1), m_p.group(2)
                sem_indent = "sem-indent" in attrs
                conteudo = _limpar_inline(content)

                if primeiro_paragrafo:
                    conteudo = _destacar_primeira_letra(conteudo)
                    primeiro_paragrafo = False

                style = styles["p_sem_indent"] if sem_indent else styles["p"]
                flow.append(Paragraph(conteudo, style))

    return flow


# ==========================================================================
# ESTILOS
# ==========================================================================


def montar_estilos() -> dict[str, ParagraphStyle]:
    s: dict[str, ParagraphStyle] = {}

    # Capa
    s["capa_marca"] = ParagraphStyle(
        "capa_marca", fontName=FONTE_META_BOLD, fontSize=10,
        leading=14, textColor=MEL, alignment=TA_CENTER, spaceAfter=10,
    )
    s["capa_titulo"] = ParagraphStyle(
        "capa_titulo", fontName=FONTE_TITULO_ITAL, fontSize=80,
        leading=86, textColor=CREME, alignment=TA_CENTER, spaceAfter=18,
    )
    s["capa_autora"] = ParagraphStyle(
        "capa_autora", fontName=FONTE_META, fontSize=11,
        leading=15, textColor=CREME, alignment=TA_CENTER,
    )
    s["capa_ano"] = ParagraphStyle(
        "capa_ano", fontName=FONTE_META_BOLD, fontSize=9,
        leading=13, textColor=MEL, alignment=TA_CENTER,
    )

    # Folha de rosto
    s["rosto_titulo"] = ParagraphStyle(
        "rosto_titulo", fontName=FONTE_TITULO_ITAL, fontSize=56,
        leading=62, textColor=TINTA, alignment=TA_CENTER, spaceAfter=14,
    )
    s["rosto_subtitulo"] = ParagraphStyle(
        "rosto_subtitulo", fontName=FONTE_TITULO_ITAL, fontSize=18,
        leading=24, textColor=TERRA, alignment=TA_CENTER, spaceAfter=60,
    )
    s["rosto_autora"] = ParagraphStyle(
        "rosto_autora", fontName=FONTE_META, fontSize=12,
        leading=18, textColor=CARVAO, alignment=TA_CENTER,
    )

    # Ficha técnica
    s["ficha_secao"] = ParagraphStyle(
        "ficha_secao", fontName=FONTE_META_BOLD, fontSize=8,
        leading=12, textColor=MEL, alignment=TA_LEFT, spaceAfter=2,
    )
    s["ficha_valor"] = ParagraphStyle(
        "ficha_valor", fontName=FONTE_TEXTO, fontSize=10,
        leading=15, textColor=CARVAO, alignment=TA_LEFT, spaceAfter=12,
    )

    # Sumário (compacto, em uma página)
    s["sum_titulo"] = ParagraphStyle(
        "sum_titulo", fontName=FONTE_TITULO_ITAL, fontSize=38,
        leading=42, textColor=TINTA, alignment=TA_CENTER, spaceAfter=24,
    )
    s["sum_secao"] = ParagraphStyle(
        "sum_secao", fontName=FONTE_META_BOLD, fontSize=8.5,
        leading=12, textColor=MEL, alignment=TA_LEFT,
        spaceBefore=12, spaceAfter=4,
    )
    s["sum_numero"] = ParagraphStyle(
        "sum_numero", fontName=FONTE_META, fontSize=9,
        leading=18, textColor=CINZA, alignment=TA_LEFT,
    )
    s["sum_nome"] = ParagraphStyle(
        "sum_nome", fontName=FONTE_TITULO_ITAL, fontSize=13,
        leading=18, textColor=TINTA, alignment=TA_LEFT,
    )
    s["sum_pagina"] = ParagraphStyle(
        "sum_pagina", fontName=FONTE_META, fontSize=10,
        leading=18, textColor=MEL, alignment=TA_RIGHT,
    )

    # Separador (fundo creme — anuncia a carta com tipografia grande)
    s["sep_rotulo"] = ParagraphStyle(
        "sep_rotulo", fontName=FONTE_TITULO_ITAL, fontSize=32,
        leading=40, textColor=MEL, alignment=TA_CENTER, spaceAfter=8,
    )

    # Retrato (fundo tinta — foto + nome + epígrafe + meta)
    # (a saudação "Oi, Nome" foi removida do retrato)
    s["retr_nome"] = ParagraphStyle(
        "retr_nome", fontName=FONTE_TITULO_ITAL, fontSize=15,
        leading=20, textColor=MEL, alignment=TA_CENTER, spaceAfter=6,
    )
    s["retr_epigrafe"] = ParagraphStyle(
        "retr_epigrafe", fontName=FONTE_TEXTO_ITAL, fontSize=13,
        leading=20, textColor=CREME, alignment=TA_CENTER,
        leftIndent=30, rightIndent=30, spaceAfter=8,
    )
    s["retr_meta"] = ParagraphStyle(
        "retr_meta", fontName=FONTE_META, fontSize=10,
        leading=14, textColor=MEL, alignment=TA_CENTER, spaceBefore=8,
    )

    # Corpo da carta — 11.5pt / 17pt para A4
    s["p"] = ParagraphStyle(
        "p", fontName=FONTE_TEXTO, fontSize=11.5, leading=17,
        textColor=TINTA, alignment=TA_JUSTIFY,
        firstLineIndent=18, spaceAfter=3,
    )
    s["p_sem_indent"] = ParagraphStyle(
        "p_sem_indent", parent=s["p"],
        firstLineIndent=0, spaceBefore=6,
    )
    s["citacao"] = ParagraphStyle(
        "citacao", fontName=FONTE_TEXTO_ITAL, fontSize=12,
        leading=18, textColor=TINTA, alignment=TA_LEFT,
        leftIndent=28, rightIndent=28, spaceBefore=14, spaceAfter=8,
    )
    s["atribuicao"] = ParagraphStyle(
        "atribuicao", fontName=FONTE_META, fontSize=8.5,
        leading=12, textColor=CINZA, alignment=TA_RIGHT,
        leftIndent=28, rightIndent=28, spaceAfter=12,
    )
    s["dialogo"] = ParagraphStyle(
        "dialogo", fontName=FONTE_TEXTO, fontSize=11,
        leading=16, textColor=OLIVA, alignment=TA_LEFT,
        leftIndent=22, spaceBefore=8, spaceAfter=12,
    )

    # Fechamento
    s["ornamento"] = ParagraphStyle(
        "ornamento", fontName=FONTE_META, fontSize=11,
        leading=14, textColor=MEL, alignment=TA_CENTER,
        spaceBefore=20, spaceAfter=12,
    )
    s["assinatura"] = ParagraphStyle(
        "assinatura", fontName=FONTE_TITULO_ITAL, fontSize=26,
        leading=30, textColor=TINTA, alignment=TA_RIGHT, spaceBefore=8,
    )
    s["assinatura_meta"] = ParagraphStyle(
        "assinatura_meta", fontName=FONTE_META, fontSize=9,
        leading=14, textColor=CINZA, alignment=TA_RIGHT,
    )

    # Colofão
    s["colofao_citacao"] = ParagraphStyle(
        "colofao_citacao", fontName=FONTE_TITULO_ITAL, fontSize=17,
        leading=26, textColor=TINTA, alignment=TA_CENTER,
        leftIndent=26, rightIndent=26, spaceAfter=10,
    )
    s["colofao_credito"] = ParagraphStyle(
        "colofao_credito", fontName=FONTE_META_BOLD, fontSize=9,
        leading=14, textColor=MEL, alignment=TA_CENTER,
    )

    return s


# ==========================================================================
# FUNDOS DE PÁGINA
# ==========================================================================


_ctx: dict[str, object] = {
    "carta_atual": "",
    "mostrar_numero": True,
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
    _filete(c, MARGIN_OUTER, PG_W - MARGIN_OUTER, PG_H - 40 * mm)
    _filete(c, PG_W / 2 - 22 * mm, PG_W / 2 + 22 * mm, 26 * mm)


def fundo_separador(c, _doc) -> None:
    """Fundo tinta limpo — sem filetes fixos. Os elementos visuais
    decorativos agora ficam ATRELADOS ao conteúdo (HRFlowable abaixo
    do nome, com largura proporcional à frase)."""
    c.saveState()
    c.setFillColor(TINTA)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()


def fundo_creme_simples(c, _doc) -> None:
    """Folhas creme sem header (rosto, ficha, sumário, retrato)."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    c.restoreState()
    _filete(c, PG_W / 2 - 18 * mm, PG_W / 2 + 18 * mm, PG_H - 22 * mm, MEL, 0.3)
    if _ctx.get("mostrar_numero"):
        c.saveState()
        c.setFont(FONTE_META, 8)
        c.setFillColor(CINZA)
        c.drawCentredString(PG_W / 2, 14 * mm, str(c.getPageNumber()))
        c.restoreState()


def fundo_texto(c, _doc) -> None:
    """Páginas de corpo de carta: header com 'TRAVESSIAS' apenas + footer
    com número de página."""
    c.saveState()
    c.setFillColor(CREME)
    c.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)

    # Header: somente "TRAVESSIAS" (sem nome da carta — convenção de coletânea)
    c.setFont(FONTE_META_BOLD, 8)
    c.setFillColor(MEL)
    c.drawCentredString(PG_W / 2, PG_H - 18 * mm, "TRAVESSIAS")
    _filete(
        c,
        PG_W / 2 - 18 * mm, PG_W / 2 + 18 * mm,
        PG_H - 21 * mm, MEL, 0.3,
    )

    # Footer: número de página
    c.setFont(FONTE_META, 8)
    c.setFillColor(CINZA)
    c.drawCentredString(PG_W / 2, 14 * mm, str(c.getPageNumber()))

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
    t = Table(data, colWidths=[50 * mm, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _bloco_sumario(
    cartas: list[Carta],
    mapa_paginas: dict[str, int],
    styles: dict[str, ParagraphStyle],
) -> list:
    """Sumário compacto, projetado para caber em UMA página A4."""
    flow: list = []

    def render_secao(titulo: str, entradas: list[Carta]) -> None:
        if not entradas:
            return
        flow.append(Paragraph(titulo.upper(), styles["sum_secao"]))
        data = []
        for c in entradas:
            num = c.numero if c.numero else "—"
            pag = mapa_paginas.get(c.id, 0)
            data.append([
                Paragraph(num, styles["sum_numero"]),
                Paragraph(c.nome, styles["sum_nome"]),
                Paragraph(str(pag), styles["sum_pagina"]),
            ])
        t = Table(data, colWidths=[12 * mm, None, 16 * mm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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


PAGINAS_PRETEXTUAIS = 4  # capa(1) + rosto(2) + ficha(3) + sumário(4)


def _predicao_paginas(cartas: list[Carta]) -> dict[str, int]:
    """Predição inicial: cada entrada = 1 sep + 1 retrato + 1 texto.
    O two-pass corrige para o número real."""
    pg = PAGINAS_PRETEXTUAIS + 1
    mapa: dict[str, int] = {}
    for c in cartas:
        mapa[c.id] = pg
        pg += 3
    return mapa


def _build_uma_passada(
    cartas: list[Carta],
    mapa_paginas: dict[str, int],
    registry: dict[str, int],
    saida: str,
) -> None:
    """Constroi o PDF uma vez. Markers populam o registry com páginas reais."""
    styles = montar_estilos()

    doc = BaseDocTemplate(
        saida, pagesize=A4,
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
        topPadding=8 * mm, bottomPadding=4 * mm,
        id="texto",
    )

    doc.addPageTemplates([
        PageTemplate(id="capa",       frames=[frame_full],  onPage=fundo_capa),
        PageTemplate(id="pretextual", frames=[frame_full],  onPage=fundo_creme_simples),
        # Separador (anúncio da carta) em fundo CREME — dramatizado pela
        # tipografia grande "CARTA III" em mel.
        PageTemplate(id="separador",  frames=[frame_full],  onPage=fundo_creme_simples),
        # Retrato (foto + saudação + epígrafe) em fundo TINTA — o retrato
        # vira a "página de capa" da carta, cinematográfica.
        PageTemplate(id="retrato",    frames=[frame_full],  onPage=fundo_separador),
        PageTemplate(id="texto",      frames=[frame_texto], onPage=fundo_texto),
    ])

    story: list = []

    # -------- 1. CAPA --------
    story.append(NextPageTemplate("capa"))
    _ctx["mostrar_numero"] = False
    story.append(Spacer(1, 26 * mm))
    story.append(Paragraph("CARTAS DE MULHERES REAIS", styles["capa_marca"]))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Travessias", styles["capa_titulo"]))

    foto_renata = _foto_existe("fotos/renata_leao.jpg")
    if foto_renata:
        img = Image(foto_renata, width=90 * mm, height=120 * mm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 18 * mm))
    else:
        story.append(Spacer(1, 80 * mm))

    story.append(Paragraph("Por <b>RENATA LEÃO</b>", styles["capa_autora"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("VOLUME 01 · 2025", styles["capa_ano"]))
    story.append(PageBreak())

    # -------- 2. FOLHA DE ROSTO --------
    story.append(NextPageTemplate("pretextual"))
    _ctx["mostrar_numero"] = False
    story.append(Spacer(1, 70 * mm))
    story.append(Paragraph("Travessias", styles["rosto_titulo"]))
    story.append(Paragraph("cartas de mulheres reais", styles["rosto_subtitulo"]))
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("Por", styles["rosto_autora"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("<b>RENATA LEÃO</b>", styles["rosto_autora"]))
    story.append(PageBreak())

    # -------- 3. FICHA TÉCNICA --------
    _ctx["mostrar_numero"] = False
    story.append(Spacer(1, 50 * mm))
    story.append(_tabela_ficha([
        ("Obra", "<b>Travessias — cartas de mulheres reais</b><br/>Volume 01 · Edição 2025"),
        ("Idealização", "Renata Leão"),
        ("Fotografia e palavra", "Renata Leão"),
        ("Prefácio", "Nicole Pelosi"),
        ("Origem", "Entrevistas realizadas durante a 1ª edição do Festival MEL — Mulheres em Lutas, em 2025."),
        ("Contato", "@renataleaofotografia<br/>renataleaofotografia@gmail.com"),
    ], styles))
    story.append(PageBreak())

    # -------- 4. SUMÁRIO (uma página) --------
    _ctx["mostrar_numero"] = True
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph("Sumário", styles["sum_titulo"]))
    story.extend(_bloco_sumario(cartas, mapa_paginas, styles))
    # Sem PageBreak — a primeira carta tem seu próprio
    # NextPageTemplate + PageBreak que encerra o sumário corretamente.

    # -------- 5. CADA ENTRADA --------
    # Ordenação correta: NextPageTemplate define o template DO NEXT page;
    # o PageBreak imediato aplica e move pra essa página, então o conteúdo
    # flowi no template certo.
    for carta in cartas:
        # 5a · Separador (fundo creme — anúncio dramático)
        story.append(NextPageTemplate("separador"))
        story.append(PageBreak())
        story.append(PageMarker(carta.id, registry))
        story.append(Spacer(1, PG_H * 0.42))  # centro vertical do papel
        story.append(Paragraph(carta.rotulo.upper(), styles["sep_rotulo"]))

        # 5b · Retrato (fundo tinta — foto + nome + epígrafe + filete + meta)
        # Sem saudação acima da foto (era ruidoso e duplicava o nome).
        story.append(NextPageTemplate("retrato"))
        story.append(PageBreak())
        story.append(Spacer(1, 32 * mm))

        foto = _foto_existe(carta.foto)
        if foto:
            img = Image(foto, width=82 * mm, height=114 * mm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 12 * mm))

        # Nome em Times itálico mel logo abaixo da foto
        story.append(Paragraph(carta.nome, styles["retr_nome"]))

        if carta.epigrafe:
            # Quebra natural após o travessão " — " (vale para qualquer
            # carta cuja epígrafe contenha essa pontuação)
            epigrafe_quebrada = carta.epigrafe.replace(" — ", " —<br/>")
            story.append(Paragraph(
                f"“{epigrafe_quebrada}”", styles["retr_epigrafe"]
            ))
            # Filete proporcional à largura da epígrafe (~60% da página)
            story.append(HRFlowable(
                width="50%", thickness=0.5, color=MEL,
                hAlign="CENTER", spaceBefore=4, spaceAfter=8,
            ))

        meta = " · ".join(p for p in (carta.idade, carta.cidade) if p)
        if meta:
            story.append(Paragraph(meta, styles["retr_meta"]))

        # 5c · Texto fluido (paginação automática)
        story.append(NextPageTemplate("texto"))
        story.append(PageBreak())
        story.extend(texto_da_carta(carta, styles))

        # 5d · Fechamento (na mesma página onde o texto termina, se couber)
        story.append(Paragraph("· · ·", styles["ornamento"]))
        story.append(Paragraph(carta.assinatura, styles["assinatura"]))
        if carta.eh_carta:
            meta_ass = "Abril · 2025<br/>Por Renata Leão"
        elif carta.tipo == "prefacio":
            meta_ass = "2025<br/>Por Nicole Pelosi"
        else:
            meta_ass = "2025"
        story.append(Paragraph(meta_ass, styles["assinatura_meta"]))
        # Sem PageBreak aqui — a próxima carta começa com seu próprio
        # NextPageTemplate("separador") + PageBreak.

    # -------- 6. COLOFÃO FINAL --------
    story.append(NextPageTemplate("pretextual"))
    story.append(PageBreak())
    story.append(Spacer(1, 100 * mm))
    story.append(Paragraph("· · ·", styles["ornamento"]))
    story.append(Spacer(1, 16 * mm))
    story.append(Paragraph(
        "Travessias é sobre mulheres que seguem,<br/>"
        "que atravessam a própria vida.",
        styles["colofao_citacao"],
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "<i>Mulheres que sustentam outras mulheres.<br/>"
        "Mulheres que, juntas, criam abrigo<br/>"
        "enquanto buscam abrigo em outras travessias.</i>",
        styles["colofao_citacao"],
    ))
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("RENATA LEÃO · VOLUME 01 · 2025", styles["colofao_credito"]))

    doc.build(story)


def construir_pdf(cartas: list[Carta], saida: str = "travessias.pdf") -> str:
    """Two-pass build: predição + correção via PageMarker.

    Escreve sempre em um arquivo temp e renomeia ao final, evitando
    erros de Permission caso o PDF esteja aberto em outro leitor.
    """
    import tempfile, shutil
    tmp_saida = saida + ".tmp"

    mapa_predito = _predicao_paginas(cartas)
    registry: dict[str, int] = {}
    _build_uma_passada(cartas, mapa_predito, registry, tmp_saida)

    if registry != mapa_predito:
        registry2: dict[str, int] = {}
        _build_uma_passada(cartas, registry, registry2, tmp_saida)

    try:
        shutil.move(tmp_saida, saida)
    except PermissionError:
        # Arquivo final está aberto — entrega o temp pra revisão manual
        print(f"AVISO: {saida} está em uso. PDF gerado em {tmp_saida}.")
        return tmp_saida
    return saida


# ==========================================================================
# ENTRADA
# ==========================================================================


def main() -> int:
    cartas = extrair_cartas("src/cartas.js")
    saida = construir_pdf(cartas, "travessias.pdf")
    sz_kb = os.path.getsize(saida) // 1024

    print(f"{'rótulo':12}  {'nome':24}  páginas paginas[]")
    print("-" * 60)
    for c in cartas:
        print(f"  {c.rotulo:10}  {c.nome:24}  {len(c.paginas):>3}")
    print()
    print(f"PDF: {saida} · {sz_kb} KB")
    print(f"Formato: A4 retrato (210 × 297 mm)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

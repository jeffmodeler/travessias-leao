# coding: utf-8
"""
Travessias — Gerador de PDF (livro)
Lê src/cartas.js e gera travessias.pdf com fotos + texto, pronto para
upload em ferramentas como Claude Design / leitores de ebook.
"""

import re, os, io
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    KeepTogether, NextPageTemplate, PageTemplate, Frame, BaseDocTemplate
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Cores da paleta Travessias
CREME      = HexColor('#FAF7F2')
TINTA      = HexColor('#1E2A38')
TINTA_SUAVE= HexColor('#2C3849')
TERRA      = HexColor('#A84A2A')
MEL        = HexColor('#C89B4A')
OLIVA      = HexColor('#5C6B4E')
CARVAO     = HexColor('#3A3A3A')
CINZA      = HexColor('#8A8578')

# Tamanho de página A5 (148 × 210mm — proporção de livro)
PG_W, PG_H = A5
MARGIN_LR = 18*mm
MARGIN_TB = 22*mm

# Tentar registrar fontes do projeto (woff2 não funciona direto, usa fallbacks)
# ReportLab vem com Times, Helvetica, Courier embutidos. Usaremos esses para PDF
# pois woff2 das fontes do projeto requer conversão.
FONTE_TITULO = 'Times-Roman'
FONTE_TITULO_ITAL = 'Times-Italic'
FONTE_TEXTO  = 'Times-Roman'
FONTE_TEXTO_ITAL = 'Times-Italic'
FONTE_META   = 'Helvetica'
FONTE_META_BOLD = 'Helvetica-Bold'


# -------------------- Parser de cartas.js --------------------

def extrair_cartas(path='src/cartas.js'):
    """Lê o arquivo JS e extrai a lista de cartas como dicts Python."""
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    cartas = []
    # Cada entrada: { id, numero, label, nome, saudacao, idade, cidade, foto, epigrafe, assinatura, paginas }
    # Achar o array CARTAS = [ ... ]; e iterar objetos
    array_match = re.search(r'const CARTAS\s*=\s*\[(.*?)\n\];', src, re.DOTALL)
    if not array_match:
        raise RuntimeError("Não achei const CARTAS = [...]")
    body = array_match.group(1)

    # Cada objeto começa com { e termina com }, no nível raiz
    # Encontra blocos { ... } balanceados
    objs = []
    depth = 0; start = None
    for i, ch in enumerate(body):
        if ch == '{':
            if depth == 0: start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                objs.append(body[start:i+1])

    for obj_text in objs:
        c = {}
        # Campos simples
        for campo in ['id', 'numero', 'label', 'tipo', 'nome', 'saudacao',
                      'idade', 'cidade', 'foto', 'epigrafe', 'assinatura']:
            m = re.search(rf'{campo}:\s*"((?:[^"\\]|\\.)*)"', obj_text)
            c[campo] = m.group(1) if m else ''
        # paginas
        pag_m = re.search(r'paginas:\s*\[(.*?)\n\s*\]', obj_text, re.DOTALL)
        pags = []
        if pag_m:
            arr = pag_m.group(1)
            # Extrai cada `...`
            i = 0; n = len(arr)
            while i < n:
                while i < n and arr[i] != '`': i += 1
                if i >= n: break
                i += 1; s = i
                while i < n and arr[i] != '`': i += 1
                pags.append(arr[s:i]); i += 1
        c['paginas'] = pags
        cartas.append(c)
    return cartas


# -------------------- Conversor HTML → reportlab --------------------

def html_to_paragrafos(html, styles):
    """Converte o HTML inline da página em uma lista de flowables."""
    flow = []
    # Split por tags de bloco (p, blockquote, div)
    blocks = re.split(r'(?=<(?:p|blockquote|div)[\s>])', html)
    for blk in blocks:
        blk = blk.strip()
        if not blk: continue

        # Identifica tipo
        # blockquote class="citacao"
        if re.match(r'<blockquote[^>]*class="citacao"', blk):
            inner = re.sub(r'<blockquote[^>]*>', '', blk)
            inner = re.sub(r'</blockquote>\s*$', '', inner)
            # Pode ter <span class="citacao-atribuicao"> dentro
            attrib_m = re.search(r'<span[^>]*class="citacao-atribuicao"[^>]*>(.*?)</span>', inner)
            atribuicao = attrib_m.group(1).strip() if attrib_m else ''
            if attrib_m:
                inner = inner.replace(attrib_m.group(0), '').strip()
            inner = limpar_inline(inner)
            flow.append(Paragraph(inner, styles['citacao']))
            if atribuicao:
                flow.append(Paragraph(limpar_inline(atribuicao), styles['atribuicao']))
            flow.append(Spacer(1, 6))
            continue

        # div class="dialogo"
        if re.match(r'<div[^>]*class="dialogo"', blk):
            inner = re.sub(r'<div[^>]*>', '', blk)
            inner = re.sub(r'</div>\s*$', '', inner)
            inner = limpar_inline(inner)
            flow.append(Paragraph(inner, styles['dialogo']))
            continue

        # div class="aviso-provisorio" (do prefácio)
        if re.match(r'<div[^>]*class="aviso-provisorio"', blk):
            inner = re.sub(r'<div[^>]*>', '', blk, count=1)
            inner = re.sub(r'</div>\s*$', '', inner)
            inner = re.sub(r'<span[^>]*>|</span>', '', inner)
            inner = limpar_inline(inner)
            flow.append(Paragraph(f'<font color="#A84A2A"><b>{inner.strip()}</b></font>', styles['aviso']))
            flow.append(Spacer(1, 8))
            continue

        # <p> normal ou sem-indent
        m_p = re.match(r'<p([^>]*)>(.*)</p>\s*$', blk, re.DOTALL)
        if m_p:
            attrs, content = m_p.group(1), m_p.group(2)
            sem_indent = 'sem-indent' in attrs
            content = limpar_inline(content)
            style = styles['p_sem_indent'] if sem_indent else styles['p']
            flow.append(Paragraph(content, style))
            continue

        # Fallback: pula
    return flow


def limpar_inline(html):
    """Converte tags inline HTML para o subset que reportlab Paragraph aceita."""
    # <em>, <i> → <i>
    html = re.sub(r'<em\b[^>]*>', '<i>', html)
    html = re.sub(r'</em>', '</i>', html)
    # <strong>, <b> → <b>
    html = re.sub(r'<strong\b[^>]*>', '<b>', html)
    html = re.sub(r'</strong>', '</b>', html)
    # <br> → <br/>
    html = re.sub(r'<br\s*/?>', '<br/>', html)
    # <a href> → texto + url entre parênteses
    html = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'\2', html)
    # remove outras tags desconhecidas mas mantém texto
    html = re.sub(r'<(?!/?(?:i|b|br|font|sup|sub)\b)[^>]+>', '', html)
    # Entidades HTML
    html = html.replace('&ldquo;', '“').replace('&rdquo;', '”')
    html = html.replace('&lsquo;', '‘').replace('&rsquo;', '’')
    html = html.replace('&hellip;', '…').replace('&mdash;', '—').replace('&ndash;', '–')
    html = html.replace('&nbsp;', ' ')
    return html.strip()


# -------------------- Estilos --------------------

def montar_estilos():
    base = getSampleStyleSheet()
    s = {}
    s['titulo_capa'] = ParagraphStyle('titulo_capa',
        fontName=FONTE_TITULO_ITAL, fontSize=44, leading=48,
        textColor=CREME, alignment=TA_CENTER, spaceAfter=18)
    s['subtitulo_capa'] = ParagraphStyle('subtitulo_capa',
        fontName=FONTE_TITULO_ITAL, fontSize=18, leading=22,
        textColor=MEL, alignment=TA_CENTER, spaceAfter=40)
    s['autora_capa'] = ParagraphStyle('autora_capa',
        fontName=FONTE_META, fontSize=11, leading=14,
        textColor=CREME, alignment=TA_CENTER, spaceAfter=4)
    s['ano_capa'] = ParagraphStyle('ano_capa',
        fontName=FONTE_META, fontSize=10, leading=12,
        textColor=MEL, alignment=TA_CENTER)

    s['rotulo_carta'] = ParagraphStyle('rotulo_carta',
        fontName=FONTE_META_BOLD, fontSize=10, leading=12,
        textColor=MEL, alignment=TA_CENTER, spaceAfter=12)
    s['saudacao'] = ParagraphStyle('saudacao',
        fontName=FONTE_TITULO_ITAL, fontSize=28, leading=32,
        textColor=TINTA, alignment=TA_CENTER, spaceAfter=14)
    s['epigrafe'] = ParagraphStyle('epigrafe',
        fontName=FONTE_TEXTO_ITAL, fontSize=12, leading=18,
        textColor=CARVAO, alignment=TA_CENTER, spaceAfter=8,
        leftIndent=20, rightIndent=20)
    s['meta'] = ParagraphStyle('meta',
        fontName=FONTE_META, fontSize=8, leading=12,
        textColor=CINZA, alignment=TA_CENTER, spaceAfter=2)

    s['p'] = ParagraphStyle('p',
        fontName=FONTE_TEXTO, fontSize=11, leading=17,
        textColor=TINTA, alignment=TA_JUSTIFY,
        firstLineIndent=14, spaceAfter=2)
    s['p_sem_indent'] = ParagraphStyle('p_sem_indent', parent=s['p'],
        firstLineIndent=0, spaceBefore=4)
    s['citacao'] = ParagraphStyle('citacao',
        fontName=FONTE_TEXTO_ITAL, fontSize=12, leading=18,
        textColor=TINTA, alignment=TA_LEFT,
        leftIndent=20, rightIndent=20, spaceBefore=10, spaceAfter=4,
        borderColor=MEL, borderWidth=0, borderPadding=0)
    s['atribuicao'] = ParagraphStyle('atribuicao',
        fontName=FONTE_META, fontSize=8, leading=10,
        textColor=CINZA, alignment=TA_RIGHT,
        leftIndent=20, rightIndent=20, spaceAfter=10)
    s['dialogo'] = ParagraphStyle('dialogo',
        fontName=FONTE_TEXTO, fontSize=10.5, leading=16,
        textColor=OLIVA, alignment=TA_LEFT,
        leftIndent=14, spaceBefore=6, spaceAfter=10)
    s['aviso'] = ParagraphStyle('aviso',
        fontName=FONTE_META, fontSize=9, leading=12,
        textColor=CARVAO, alignment=TA_CENTER,
        leftIndent=10, rightIndent=10, spaceAfter=10,
        backColor=Color(1,0.95,0.92))

    s['assinatura'] = ParagraphStyle('assinatura',
        fontName=FONTE_TITULO_ITAL, fontSize=18, leading=22,
        textColor=TINTA, alignment=TA_RIGHT, spaceBefore=14)
    s['assinatura_meta'] = ParagraphStyle('assinatura_meta',
        fontName=FONTE_META, fontSize=7, leading=11,
        textColor=CINZA, alignment=TA_RIGHT)

    s['ornamento'] = ParagraphStyle('ornamento',
        fontName=FONTE_META, fontSize=10, leading=14,
        textColor=MEL, alignment=TA_CENTER, spaceBefore=8, spaceAfter=4)

    s['toc_titulo'] = ParagraphStyle('toc_titulo',
        fontName=FONTE_TITULO_ITAL, fontSize=22, leading=26,
        textColor=TINTA, alignment=TA_CENTER, spaceAfter=22)
    s['toc_item'] = ParagraphStyle('toc_item',
        fontName=FONTE_TEXTO, fontSize=11, leading=18,
        textColor=TINTA, alignment=TA_LEFT, spaceAfter=4)
    s['toc_rotulo'] = ParagraphStyle('toc_rotulo',
        fontName=FONTE_META, fontSize=8, leading=12,
        textColor=MEL, alignment=TA_LEFT, spaceAfter=0)

    return s


# -------------------- Layout das páginas --------------------

def fundo_tinta(canvas, doc):
    """Pintura de fundo azul para páginas de capa."""
    canvas.saveState()
    canvas.setFillColor(TINTA)
    canvas.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    canvas.restoreState()


def fundo_creme(canvas, doc):
    """Pintura de fundo creme para páginas de leitura."""
    canvas.saveState()
    canvas.setFillColor(CREME)
    canvas.rect(0, 0, PG_W, PG_H, fill=1, stroke=0)
    # Rodapé com número de página
    canvas.setFont(FONTE_META, 7)
    canvas.setFillColor(CINZA)
    canvas.drawCentredString(PG_W/2, 10*mm, f"{canvas.getPageNumber()}")
    canvas.restoreState()


def construir_pdf(cartas, saida='travessias.pdf'):
    styles = montar_estilos()

    # DocTemplate com múltiplos page templates (capa, capa-carta, texto)
    doc = BaseDocTemplate(saida, pagesize=A5,
                          leftMargin=MARGIN_LR, rightMargin=MARGIN_LR,
                          topMargin=MARGIN_TB, bottomMargin=MARGIN_TB,
                          title='Travessias — cartas de mulheres reais',
                          author='Renata Leão',
                          subject='Cartas de mulheres reais',
                          allowSplitting=1)

    frame_capa = Frame(0, 0, PG_W, PG_H, leftPadding=18*mm, rightPadding=18*mm,
                       topPadding=22*mm, bottomPadding=22*mm, id='capa')
    frame_texto = Frame(MARGIN_LR, MARGIN_TB,
                        PG_W - 2*MARGIN_LR, PG_H - 2*MARGIN_TB,
                        leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0, id='texto')

    doc.addPageTemplates([
        PageTemplate(id='capa-livro',  frames=[frame_capa],  onPage=fundo_tinta),
        PageTemplate(id='capa-carta',  frames=[frame_capa],  onPage=fundo_tinta),
        PageTemplate(id='texto',       frames=[frame_texto], onPage=fundo_creme),
    ])

    story = []

    # ---- CAPA DO LIVRO ----
    story.append(NextPageTemplate('capa-livro'))
    story.append(Spacer(1, 50*mm))
    story.append(Paragraph('TRAVESSIAS', styles['titulo_capa']))
    story.append(Paragraph('cartas de mulheres reais', styles['subtitulo_capa']))
    # Foto da autora pequena no centro
    foto_renata = 'fotos/renata_leao.jpg'
    if os.path.exists(foto_renata):
        img = Image(foto_renata, width=50*mm, height=64*mm)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 10*mm))
    story.append(Paragraph('Por <b>RENATA LEÃO</b>', styles['autora_capa']))
    story.append(Paragraph('2025', styles['ano_capa']))
    story.append(PageBreak())

    # ---- SUMÁRIO ----
    story.append(NextPageTemplate('texto'))
    story.append(Spacer(1, 18*mm))
    story.append(Paragraph('Sumário', styles['toc_titulo']))
    story.append(Spacer(1, 8*mm))
    for c in cartas:
        rotulo = c['label'] if c['label'] else (f"Carta {c['numero']}" if c['numero'] else '')
        story.append(Paragraph(f'<font color="#C89B4A">{rotulo.upper()}</font>', styles['toc_rotulo']))
        story.append(Paragraph(f"<b>{c['nome']}</b>", styles['toc_item']))
    story.append(PageBreak())

    # ---- CADA CARTA ----
    for c in cartas:
        # Capa da carta (foto + nome + epigrafe)
        story.append(NextPageTemplate('capa-carta'))
        story.append(Spacer(1, 12*mm))

        rotulo = c['label'] if c['label'] else (f"CARTA {c['numero']}" if c['numero'] else 'CARTA')
        story.append(Paragraph(rotulo.upper(), styles['rotulo_carta']))

        foto = c['foto']
        if foto and os.path.exists(foto):
            img = Image(foto, width=60*mm, height=84*mm)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 8*mm))

        story.append(Paragraph(f'<font color="#FAF7F2">{c["saudacao"]}</font>', styles['saudacao']))

        # epigrafe em branco-creme
        if c['epigrafe']:
            story.append(Paragraph(f'<font color="#FAF7F2">“{c["epigrafe"]}”</font>',
                                   styles['epigrafe']))

        # idade · cidade (se houver)
        meta_parts = [p for p in [c['idade'], c['cidade']] if p]
        if meta_parts:
            story.append(Spacer(1, 6*mm))
            story.append(Paragraph(f'<font color="#C89B4A">{" · ".join(meta_parts)}</font>',
                                   styles['meta']))

        story.append(PageBreak())

        # Páginas de texto
        story.append(NextPageTemplate('texto'))

        for i, pHtml in enumerate(c['paginas']):
            flow = html_to_paragrafos(pHtml, styles)
            story.extend(flow)

        # Fechamento ao fim da última página
        data = 'Abril · 2025' if c['numero'] else '2025'
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph('· · ·', styles['ornamento']))
        story.append(Paragraph(c['assinatura'], styles['assinatura']))
        story.append(Paragraph(f'{data}<br/>Por Renata Leão', styles['assinatura_meta']))

        story.append(PageBreak())

    doc.build(story)
    return saida


if __name__ == '__main__':
    cartas = extrair_cartas('src/cartas.js')
    print(f"Carregadas {len(cartas)} entradas")
    for c in cartas:
        print(f"  - {c['nome']:20} · {len(c['paginas'])} págs")

    saida = construir_pdf(cartas, 'travessias.pdf')
    sz = os.path.getsize(saida)
    print(f"\nOK PDF gerado: {saida} ({sz//1024} KB)")

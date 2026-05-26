# Travessias

> *cartas de mulheres reais*

eBook interativo de cartas autobiográficas escritas por **Renata Leão**, fotógrafa e comunicadora, na voz de dez mulheres entrevistadas durante a 1ª edição do Festival MEL — Mulheres em Lutas, em 2025. A décima carta é da Sheila, mãe da autora.

O nome do projeto vem da carta da Sheila: *"O Travessia nunca acabou, Sheilinha. Você também é… uma travessia, VIVA."*

---

## Acessar

- **Site interativo**: [renataleaofotografia.github.io/travessias-leao](https://renataleaofotografia.github.io/travessias-leao/)
- **Repositório**: [github.com/jeffmodeler/travessias-leao](https://github.com/jeffmodeler/travessias-leao)
- **Livro em PDF**: [`Travessias - Renata Leao.pdf`](Travessias%20-%20Renata%20Leao.pdf) — 668 KB · 58 páginas A4
- **Página única standalone (HTML+CSS+JS inline)**: [`travessias.html`](travessias.html) — 141 KB

---

## O livro

12 entradas:

| # | Numeral | Entrada |
|---|---------|---------|
| — | Autora | **Renata Leão** — Sobre a autora |
| — | Prefácio | **Nicole Pelosi** — Antes de começar |
| 1 | I | Marília Martins · *Atrás de uma grande mulher tem sempre outra grande mulher* |
| 2 | II | Hosana · *Desisti de desistir* |
| 3 | III | Márcia · *As tramas que embalariam nosso fim deram início ao recomeço* |
| 4 | IV | Ana Claudia · *Há muitas Anas Claudias que habitam dentro de mim — e uma delas, grita* |
| 5 | V | Ariane · *Acabou o gás… mas não acabou a comida* |
| 6 | VI | Thainá · *Esse corpo que abriga a nossa história* |
| 7 | VII | Luiza · *Nós somos grandes, Luiza. Sempre fomos* |
| 8 | VIII | Silvia · *A Silvinha, pequenina e cheia de culpa, e a Silvia, consciente e plena* |
| 9 | IX | Paula · *Aquela menina nunca precisou ser consertada. Ela só precisava ser compreendida* |
| 10 | X | Sheila · *Você também é… uma travessia, VIVA* |

---

## Estrutura do projeto

```
travessias-leao/
├── index.html                        Site interativo (entry point)
├── travessias.html                   Standalone (CSS + JS inline)
├── Travessias - Renata Leao.pdf      eBook em PDF
├── gerar_pdf.py                      Gerador do PDF (Python + ReportLab)
├── wrangler.jsonc                    Config Cloudflare Workers Assets
├── CLAUDE.md                         Guia de projeto para Claude Code
│
├── src/
│   ├── tokens.css                    Variáveis de design, fontes, blocos compartilhados
│   ├── mobile.css                    Layout < 960px (cards + tela carta com swipe)
│   ├── desktop.css                   Layout ≥ 960px (sidebar + hover + painel)
│   ├── cartas.js                     Array CARTAS com todos os textos
│   └── app.js                        Render, navegação, swipe, modal "Faça parte"
│
├── fotos/                            Retratos P&B 440px (~50 KB cada)
│   ├── renata_leao.jpg
│   ├── nicole_pelosi.jpg
│   └── 10 protagonistas (.jpg)
│
└── fonts/                            woff2 locais
    ├── Caveat (manuscrita — saudações)
    ├── Fraunces (Times-like — títulos)
    ├── Lora (corpo de texto)
    └── Inter (metadados)
```

---

## Como rodar localmente

```bash
# Qualquer servidor HTTP estático serve
python3 -m http.server 8080
# ou
npx serve .
```

Abra `http://localhost:8080` no navegador.

> **Não abra `index.html` direto como arquivo** (`file://`) — fontes e fotos são bloqueadas por CORS.

---

## Decisões de design

- **Paleta editorial**: creme (#FAF7F2), tinta (#1E2A38), terra (#A84A2A), mel (#C89B4A), oliva (#5C6B4E)
- **Fotografias** sempre em P&B, sem duotone, sem recorte circular
- **Saudações** em Caveat (manuscrita); títulos em Fraunces; corpo em Lora; metadados em Inter
- **Mobile** (< 960px): lista de cards + tela de carta fullscreen com swipe
- **Desktop** (≥ 960px): coluna lateral com nomes + preview ao hover + painel deslizante

---

## Gerar o PDF

```bash
pip install reportlab pillow python-docx
python gerar_pdf.py
```

Saída: `Travessias - Renata Leao.pdf` — 58 páginas A4, com capa, folha de rosto, ficha técnica, sumário, 10 cartas + abertura + prefácio (cada uma com separador, retrato, texto distribuído uniformemente e fechamento) e colofão.

---

## Histórico

- **Abril 2025** — Entrevistas durante o Festival MEL — Mulheres em Lutas (1ª edição)
- **2025** — Projeto nasce como *Enxame — cartas de travessia* com 7 cartas
- **Maio 2026** — Rebranding para *Travessias*, expansão para 10 cartas + abertura da autora + prefácio da Nicole Pelosi

---

## Créditos

- **Idealização, fotografia e palavra**: Renata Leão
- **Prefácio**: Nicole Pelosi
- **Diagramação**: Jefferson Borges de Lima
- **Contato**: [@renataleaofotografia](https://instagram.com/renataleaofotografia) · renataleaofotografia@gmail.com

Por *Renata Leão* · Volume 01 · 2025

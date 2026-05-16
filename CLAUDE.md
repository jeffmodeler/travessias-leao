# TRAVESSIAS — cartas de mulheres reais
## Guia de projeto para Claude Code

---

## O que é este projeto

**Travessias** é um eBook interativo de cartas autobiográficas escritas por **Renata Leão**, fotógrafa e comunicadora, na voz de dez mulheres entrevistadas durante a 1ª edição do Festival MEL — Mulheres em Lutas (2025). A décima carta é da Sheila, mãe da autora.

O nome "Travessias" vem da carta da Sheila — *"O Travessia nunca acabou, Sheilinha. Você também é… uma travessia, VIVA."*

O projeto é uma aplicação HTML/CSS/JS pura (sem framework, sem bundler), adaptativa para **mobile e desktop** a partir de um único arquivo `index.html`.

---

## Estrutura de arquivos

```
travessias/
├── index.html              # Ponto de entrada único (mobile + desktop)
├── CLAUDE.md               # Este arquivo
├── fonts/                  # Fontes woff2 locais
│   ├── caveat-latin-*.woff2
│   ├── fraunces-latin-*.woff2
│   ├── lora-latin-*.woff2
│   └── inter-latin-*.woff2
├── fotos/                  # Retratos P&B (jpg)
│   ├── renata_leao.jpg     # Autora (abertura)
│   ├── ana_claudia.jpg     # Carta I
│   ├── luiza.jpg           # Carta II
│   ├── silvia_teixeira.jpg # Carta III
│   ├── thaina_britto.jpg   # Carta IV
│   ├── marcia.jpg          # Carta V
│   ├── hosana.jpg          # Carta VI
│   ├── marilia_martins.jpg # Carta VII
│   ├── ariane.jpg          # Carta VIII
│   ├── paula.jpg           # Carta IX
│   └── sheila.jpg          # Carta X
├── src/
│   ├── tokens.css          # @font-face + variáveis + .contato + variante .abertura
│   ├── mobile.css          # Layout mobile (< 960px)
│   ├── desktop.css         # Layout desktop (≥ 960px)
│   ├── cartas.js           # Array CARTAS — Abertura + 10 cartas
│   └── app.js              # Lógica de interação
├── ENXAME/                 # Material-fonte original (fotos altas + PDFs das cartas)
└── backup_pre_travessias/  # Snapshot antes da migração de Enxame → Travessias
```

---

## Estrutura do conteúdo (Abertura + 10 cartas)

| # | id        | Nome              | Numeral | Fonte original em ENXAME/CARTAS |
|---|-----------|-------------------|---------|----------------------------------|
| — | renata    | Renata Leão       | Abertura| autobiografia (autora)           |
| 1 | ana       | Ana Claudia       | I       | Ana Claudia.pdf                  |
| 2 | luiza     | Luiza             | II      | Luiza.pdf                        |
| 3 | silvia    | Silvia            | III     | Silvia Teixeira.pdf              |
| 4 | thaina    | Thainá            | IV      | Thainá Britto.pdf                |
| 5 | marcia    | Márcia            | V       | Marcia.pdf                       |
| 6 | hosana    | Hosana            | VI      | Hosana.pdf                       |
| 7 | marilia   | Marília Martins   | VII     | Marília Martins.pdf              |
| 8 | ariane    | Ariane            | VIII    | Ariane.pdf                       |
| 9 | paula     | Paula             | IX      | Paula.pdf                        |
| 10| sheila    | Sheila            | X       | Sheilinha.pdf                    |

A entrada `renata` é tratada como **abertura** (não como carta). O campo `numero` está vazio e o campo `label: "Abertura"` é usado. Renderização condicional em [index.html](index.html) e [src/app.js](src/app.js) detecta isso via `c.numero ? ... : c.label`.

---

## Decisões de arquitetura

### Breakpoint
- `< 960px` → **layout mobile**: lista de cards + tela de carta em fullscreen com swipe
- `≥ 960px` → **layout desktop**: coluna lateral com nomes + hover com preview + painel deslizante da direita

### Detecção de layout
- Feita em [src/app.js](src/app.js) via `window.innerWidth`
- O `estado.layout` é atualizado ao redimensionar a janela
- **Ambos os layouts estão no DOM ao mesmo tempo** — CSS controla qual aparece via `@media`
- Event listeners são registrados uma vez para cada layout na inicialização

### Dados das cartas
- Todas as entradas estão em [src/cartas.js](src/cartas.js) como array `CARTAS` global
- Cada entrada: `id`, `numero` (romano ou ""), `label` (opcional, para abertura), `nome`, `saudacao`, `idade`, `cidade`, `foto`, `epigrafe`, `assinatura`, `paginas[]`
- `paginas` é array de strings HTML — cada item é uma "página" de leitura paginada

### Padrão BLOCO de organização
Todo arquivo grande usa comentários `BLOCO 01 — Nome`, `BLOCO 02 — Nome`, etc., para tornar a estrutura legível e o código fácil de editar por seções independentes. Ver [src/cartas.js](src/cartas.js), [index.html](index.html), [src/app.js](src/app.js), [src/tokens.css](src/tokens.css).

---

## Paleta de cores (variáveis CSS em [src/tokens.css](src/tokens.css))

| Variável        | Hex       | Uso principal                    |
|-----------------|-----------|----------------------------------|
| `--creme`       | #FAF7F2   | Fundo das páginas de leitura     |
| `--tinta`       | #1E2A38   | Fundo da coluna lateral/capa     |
| `--terra`       | #A84A2A   | Capitulares, números de carta    |
| `--mel`         | #C89B4A   | Subtítulos, destaques, abertura  |
| `--oliva`       | #5C6B4E   | Fios, diálogos, elementos sutis  |
| `--cinza`       | #8A8578   | Metadados, rodapés               |
| `--cinza-claro` | #C4BFB4   | Pontos de navegação inativos     |

---

## Tipografia

| Variável         | Fonte      | Uso                              |
|------------------|------------|----------------------------------|
| `--fonte-titulo` | Fraunces   | Títulos, hero, saudações (backup)|
| `--fonte-texto`  | Lora       | Corpo das cartas                 |
| `--fonte-mao`    | Caveat     | Saudações manuscritas            |
| `--fonte-meta`   | Inter      | Metadados, versaletes, contato   |

---

## Como adicionar uma nova carta

1. **Coloque a foto** em `fotos/<id>.jpg` (recomendado: P&B, ~400×600px)
2. **Abra [src/cartas.js](src/cartas.js)** e copie um BLOCO existente como template
3. Preencha os campos:
   ```js
   {
     id: "nome-da-carta",         // slug único
     numero: "XI",                // numeral romano (vazio = abertura)
     nome: "Nome Completo",
     saudacao: "Oi, Nome",
     idade: "XX anos",            // ou ""
     cidade: "Cidade · UF",       // ou ""
     foto: "fotos/nome.jpg",
     epigrafe: "Frase marcante.",
     assinatura: "Nome",
     paginas: [
       `<p class="sem-indent">Primeiro parágrafo...</p>
        <p>Segundo parágrafo...</p>`,
       // ...
     ]
   }
   ```
4. Adicione o objeto ao array `CARTAS` e crie um BLOCO próprio com comentário `/* BLOCO NN — CARTA XI · Nome */`
5. Atualize o subtítulo no [index.html](index.html) (Dez → Onze) se for protagonista

### Classes HTML disponíveis dentro das páginas

```html
<p>Parágrafo normal (indenta a partir do segundo)</p>
<p class="sem-indent">Parágrafo sem indentação</p>
<em>Itálico</em>

<!-- Citação destacada (fio mel) -->
<div class="citacao">
  Texto citado aqui.
  <span class="citacao-atribuicao">— Autora, título</span>
</div>

<!-- Diálogo em bloco (fio oliva) -->
<div class="dialogo">
  — Fala de alguém.<br>
  — Resposta.
</div>

<!-- Bloco de contato (usado na abertura da autora) -->
<div class="contato">
  <div class="contato-titulo">contato</div>
  <div class="contato-linha"><span class="contato-rotulo">Instagram</span><a href="...">@handle</a></div>
</div>

<!-- Fechamento padrão -->
<div class="fechamento">
  <div class="fechamento-ornamento">· · ·</div>
  <div class="assinatura">Nome</div>
  <div class="assinatura-meta">
    <span>Abril · 2025</span><br>Por Renata Leão
  </div>
</div>
```

---

## Como rodar localmente

```bash
# Qualquer servidor HTTP simples serve
python3 -m http.server 8080
# ou
npx serve .
# ou
php -S localhost:8080
```

Abra `http://localhost:8080` no browser.

**Não abra `index.html` direto como arquivo** (`file://`) — fontes e fotos via caminhos relativos podem ser bloqueadas por CORS.

---

## Observações de design (não alterar sem deliberação)

- **"Por Renata Leão"** — atribuição exata, não reformular
- Fotos: **sempre P&B** (`filter: grayscale(1)`), sem duotone, sem recorte circular
- Capitular: só na **primeira página** de leitura de cada carta, cor `--terra`
- Citações: fio vertical `--mel`, Fraunces itálica, tamanho 17–19px
- Saudação: **sempre em Caveat** (manuscrita) — não substituir por Fraunces
- A paleta **não tem rosa** — decisão editorial deliberada
- O hero desktop usa `font-size: clamp(82px, 9vw, 140px)` para "TRAVESSIAS" caber em telas 1280px sem truncar
- Variante `.abertura` (faixa lateral `--mel`, label "Abertura" sem numeral) sinaliza visualmente a entrada da autora — usada em card mobile, item lateral desktop, preview desktop e painel

---

## Histórico

- **2025** — Projeto nasce como "Enxame — cartas de travessia" para o Festival MEL (sete cartas: Ana Claudia, Luiza, Silvia, Thainá, Márcia, Hosana, Marília).
- **Maio 2026** — Rebranding para "Travessias", com três novas cartas (Ariane, Paula, Sheila) e a inclusão da autora Renata Leão como abertura. Selo "Mulheres em Lutas · MEL" removido. Numeração I–X completa, abertura sem numeral. Backup do estado anterior em `backup_pre_travessias/`.

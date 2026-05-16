/**
 * TRAVESSIAS — cartas de mulheres reais
 * app.js — Orquestra mobile e desktop a partir de um único ponto de entrada
 *
 * Lógica:
 * - Detecta o breakpoint (960px) via window.innerWidth
 * - Inicializa o layout correto (mobile ou desktop)
 * - Reage ao redimensionamento da janela e troca de layout se necessário
 *
 * BLOCO 01 — Constantes e estado
 * BLOCO 02 — Detecção de layout
 * BLOCO 03 — Utilitários compartilhados
 * BLOCO 04 — Versão mobile
 * BLOCO 05 — Versão desktop
 * BLOCO 06 — Inicialização
 */

/* ==========================================================================
   BLOCO 01 — Constantes e estado
   ========================================================================== */

const BP_DESKTOP = 960;

/* Rótulo do número da carta (suporta Abertura, Prefácio e outras sem numeral) */
function rotuloNumero(c) {
  return c.numero ? `Carta ${c.numero}` : (c.label || "");
}

// Estado global da aplicação
const estado = {
  cartaAtiva: null,
  paginaIdx: 0,
  layout: null, // "mobile" | "desktop"
};

/* ==========================================================================
   BLOCO 02 — Detecção de layout
   ========================================================================== */

function layoutAtual() {
  return window.innerWidth >= BP_DESKTOP ? "desktop" : "mobile";
}

function inicializar() {
  const layout = layoutAtual();
  estado.layout = layout;
  if (layout === "desktop") {
    inicializarDesktop();
  } else {
    inicializarMobile();
  }
}

// Trocar de layout se a janela for redimensionada cruzando o breakpoint
let layoutAnterior = null;
window.addEventListener("resize", () => {
  const novoLayout = layoutAtual();
  if (novoLayout !== layoutAnterior) {
    layoutAnterior = novoLayout;
    estado.layout = novoLayout;
    fecharTudo();
    // Não precisa re-inicializar os event listeners (já estão no DOM)
    // Só precisamos garantir que o estado visual está limpo
  }
});

/* ==========================================================================
   BLOCO 03 — Utilitários compartilhados
   ========================================================================== */

/* Fechamento padrão de uma carta — sempre carrega "Por Renata Leão", alinhado à direita */
function fechamentoHtml(carta) {
  const data = carta.numero ? "Abril · 2025" : "2025";
  return `
    <div class="fechamento">
      <div class="fechamento-ornamento">· · ·</div>
      <div class="assinatura">${carta.assinatura}</div>
      <div class="assinatura-meta"><span>${data}</span><br>Por Renata Leão</div>
    </div>`;
}

/* Normalização tipográfica: aspas curvas, em-dash, reticências */
function normalizarTipografia(html) {
  return html
    .replace(/"([^"]+)"/g, "&ldquo;$1&rdquo;")  // aspas retas → curvas
    .replace(/(\w)--(\w)/g, "$1—$2")             // hífen duplo entre letras → em-dash
    .replace(/\.{3}/g, "…");                     // três pontos → reticências
}

function fecharTudo() {
  // Mobile
  const telaCarta = document.getElementById("tela-carta");
  if (telaCarta) telaCarta.classList.remove("aberta");
  document.body.classList.remove("carta-aberta");

  // Desktop
  const painel = document.getElementById("painel");
  const overlay = document.getElementById("painel-overlay");
  const palco = document.getElementById("palco-desktop");
  if (painel) painel.classList.remove("aberto");
  if (overlay) overlay.classList.remove("aberto");
  if (palco) palco.classList.remove("has-open");

  document.querySelectorAll(".carta-item").forEach((el) =>
    el.classList.remove("ativa")
  );
  estado.cartaAtiva = null;
  estado.paginaIdx = 0;
}

function metaHtml(carta) {
  const partes = [];
  if (carta.idade) partes.push(`<span>${carta.idade}</span>`);
  if (carta.cidade) partes.push(`<span>${carta.cidade}</span>`);
  partes.push("Por <span>Renata Leão</span>");
  return partes.join("<br>");
}

/* ==========================================================================
   BLOCO 04 — Versão mobile
   ========================================================================== */

/* Define o variant da pagina de abertura mobile baseado em tipo */
function classeTipo(carta) {
  return carta.numero ? "" : " carta-" + (carta.tipo || "abertura");
}

function inicializarMobile() {
  // Cards da lista → abrir carta
  document.querySelectorAll(".card[data-id]").forEach((card) => {
    card.addEventListener("click", () => {
      if (estado.layout !== "mobile") return;
      abrirCartaMobile(card.dataset.id);
    });
  });

  // Botão voltar
  const btnVoltar = document.getElementById("btn-voltar");
  if (btnVoltar) btnVoltar.addEventListener("click", fecharCartaMobile);

  // Navegação
  document.getElementById("btn-ant")?.addEventListener("click", () =>
    irParaPaginaMobile(estado.paginaIdx - 1)
  );
  document.getElementById("btn-prox")?.addEventListener("click", () =>
    irParaPaginaMobile(estado.paginaIdx + 1)
  );

  // Pontos de navegação (delegação)
  document.getElementById("nav-pontos-mobile")?.addEventListener("click", (e) => {
    const ponto = e.target.closest(".nav-ponto");
    if (ponto) irParaPaginaMobile(parseInt(ponto.dataset.idx, 10));
  });

  // Swipe
  let touchStartX = 0, touchStartY = 0;
  const viewport = document.getElementById("paginas-viewport-mobile");
  if (viewport) {
    viewport.addEventListener("touchstart", (e) => {
      if (e.touches.length !== 1) return;
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    }, { passive: true });

    viewport.addEventListener("touchend", (e) => {
      if (estado.layout !== "mobile") return;
      const t = e.changedTouches[0];
      const dx = t.clientX - touchStartX;
      const dy = t.clientY - touchStartY;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        if (dx < 0) irParaPaginaMobile(estado.paginaIdx + 1);
        else irParaPaginaMobile(estado.paginaIdx - 1);
      }
    }, { passive: true });
  }

  // Teclado
  window.addEventListener("keydown", (e) => {
    if (estado.layout !== "mobile") return;
    const telaCarta = document.getElementById("tela-carta");
    if (!telaCarta?.classList.contains("aberta")) return;
    if (e.key === "Escape") fecharCartaMobile();
    if (e.key === "ArrowLeft") irParaPaginaMobile(estado.paginaIdx - 1);
    if (e.key === "ArrowRight") irParaPaginaMobile(estado.paginaIdx + 1);
  });
}

function abrirCartaMobile(id) {
  const carta = CARTAS.find((c) => c.id === id);
  if (!carta) return;
  estado.cartaAtiva = carta;
  estado.paginaIdx = 0;

  // Preencher cabeçalho
  document.getElementById("carta-topo-nome").textContent = carta.nome;

  // Montar páginas: primeira é a abertura
  const viewport = document.getElementById("paginas-viewport-mobile");
  let html = `
    <div class="pagina-mobile pagina-abertura${classeTipo(carta)}" data-idx="0">
      <img class="abertura-foto" src="${carta.foto}" alt="${carta.nome}">
      <div class="abertura-info">
        <div class="abertura-numero">${rotuloNumero(carta)}</div>
        <div class="abertura-saudacao">${carta.saudacao}</div>
        <div class="abertura-fio"></div>
        <div class="abertura-meta">${metaHtml(carta)}</div>
        <div class="abertura-epigrafe">&ldquo;${carta.epigrafe}&rdquo;</div>
        <div class="abertura-swipe-dica">arraste para ler</div>
      </div>
    </div>`;

  carta.paginas.forEach((pHtml, i) => {
    const cls = i === 0
      ? "pagina-mobile pagina-leitura primeira"
      : "pagina-mobile pagina-leitura";
    const ehUltima = i === carta.paginas.length - 1;
    const conteudo = normalizarTipografia(pHtml) + (ehUltima ? fechamentoHtml(carta) : "");
    html += `<div class="${cls}" data-idx="${i + 1}">${conteudo}</div>`;
  });

  viewport.innerHTML = html;

  // Pontos
  const total = carta.paginas.length + 1;
  const navPontos = document.getElementById("nav-pontos-mobile");
  navPontos.innerHTML = Array.from({ length: total }, (_, i) =>
    `<span class="nav-ponto" data-idx="${i}"></span>`
  ).join("");

  document.getElementById("pag-total-mobile").textContent = String(total).padStart(2, "0");

  atualizarPaginaMobile();

  // Abrir tela
  document.getElementById("tela-carta").classList.add("aberta");
  document.body.classList.add("carta-aberta");
  window.scrollTo(0, 0);
}

function fecharCartaMobile() {
  document.getElementById("tela-carta").classList.remove("aberta");
  document.body.classList.remove("carta-aberta");
  setTimeout(() => {
    if (!document.getElementById("tela-carta").classList.contains("aberta")) {
      document.getElementById("paginas-viewport-mobile").innerHTML = "";
      estado.cartaAtiva = null;
    }
  }, 450);
}

function irParaPaginaMobile(i) {
  if (!estado.cartaAtiva) return;
  const total = estado.cartaAtiva.paginas.length + 1;
  if (i < 0 || i >= total) return;
  estado.paginaIdx = i;
  atualizarPaginaMobile();
}

function atualizarPaginaMobile() {
  if (!estado.cartaAtiva) return;
  const paginas = document.querySelectorAll("#paginas-viewport-mobile .pagina-mobile");
  paginas.forEach((p, i) => {
    p.classList.remove("ativa", "fora-esquerda");
    if (i === estado.paginaIdx) { p.classList.add("ativa"); p.scrollTop = 0; }
    else if (i < estado.paginaIdx) p.classList.add("fora-esquerda");
  });

  const total = estado.cartaAtiva.paginas.length + 1;
  document.getElementById("pag-atual-mobile").textContent =
    String(estado.paginaIdx + 1).padStart(2, "0");
  document.getElementById("btn-ant").disabled = estado.paginaIdx === 0;
  document.getElementById("btn-prox").disabled = estado.paginaIdx === total - 1;

  document.querySelectorAll("#nav-pontos-mobile .nav-ponto").forEach((p, i) =>
    p.classList.toggle("ativo", i === estado.paginaIdx)
  );
}

/* ==========================================================================
   BLOCO 05 — Versão desktop
   ========================================================================== */

function inicializarDesktop() {
  const lista = document.getElementById("cartas-lista");
  const palco = document.getElementById("palco-desktop");

  // Hover → preview
  lista?.addEventListener("mouseover", (e) => {
    if (estado.layout !== "desktop") return;
    const item = e.target.closest(".carta-item");
    if (!item) return;
    palco.classList.add("has-hover");
    document.querySelectorAll(".preview").forEach((p) =>
      p.classList.toggle("visible", p.dataset.id === item.dataset.id)
    );
  });

  lista?.addEventListener("mouseleave", () => {
    if (estado.layout !== "desktop") return;
    palco.classList.remove("has-hover");
    document.querySelectorAll(".preview").forEach((p) =>
      p.classList.remove("visible")
    );
  });

  // Clique → abrir painel
  lista?.addEventListener("click", (e) => {
    if (estado.layout !== "desktop") return;
    const item = e.target.closest(".carta-item");
    if (item) abrirPainel(item.dataset.id);
  });

  // Fechar painel
  document.getElementById("btn-fechar")?.addEventListener("click", fecharPainel);
  document.getElementById("painel-overlay")?.addEventListener("click", fecharPainel);

  // Navegação do painel
  document.getElementById("btn-anterior")?.addEventListener("click", () =>
    irParaPaginaDesktop(estado.paginaIdx - 1)
  );
  document.getElementById("btn-proxima")?.addEventListener("click", () =>
    irParaPaginaDesktop(estado.paginaIdx + 1)
  );

  // Pontos (delegação)
  document.getElementById("nav-pontos-desktop")?.addEventListener("click", (e) => {
    const ponto = e.target.closest(".nav-ponto");
    if (ponto) irParaPaginaDesktop(parseInt(ponto.dataset.idx, 10));
  });

  // Teclado
  window.addEventListener("keydown", (e) => {
    if (estado.layout !== "desktop") return;
    if (!document.getElementById("painel")?.classList.contains("aberto")) return;
    if (e.key === "Escape") fecharPainel();
    if (e.key === "ArrowLeft") irParaPaginaDesktop(estado.paginaIdx - 1);
    if (e.key === "ArrowRight") irParaPaginaDesktop(estado.paginaIdx + 1);
  });
}

function abrirPainel(id) {
  const carta = CARTAS.find((c) => c.id === id);
  if (!carta) return;
  estado.cartaAtiva = carta;
  estado.paginaIdx = 0;

  // Foto e info
  document.getElementById("painel-img").src = carta.foto;
  document.getElementById("painel-img").alt = carta.nome;
  document.getElementById("painel-numero").textContent = rotuloNumero(carta);
  document.getElementById("painel-saudacao").textContent = carta.saudacao;
  document.getElementById("painel-meta").innerHTML = metaHtml(carta);
  document.getElementById("painel-topo-nome").textContent = carta.nome;
  const painelEl = document.getElementById("painel");
  painelEl.classList.remove("painel-abertura", "painel-prefacio");
  if (!carta.numero) painelEl.classList.add("painel-" + (carta.tipo || "abertura"));

  // Páginas: render direto do texto (sem cover azul intermediária)
  const track = document.getElementById("paginas-track-desktop");
  track.innerHTML = carta.paginas.map((pHtml, i) => {
    const cls = i === 0 ? "pagina-desktop primeira" : "pagina-desktop";
    const ehUltima = i === carta.paginas.length - 1;
    const conteudo = normalizarTipografia(pHtml) + (ehUltima ? fechamentoHtml(carta) : "");
    return `<div class="${cls}" data-idx="${i}">${conteudo}</div>`;
  }).join("");

  // Pontos
  const total = carta.paginas.length;
  document.getElementById("nav-pontos-desktop").innerHTML = Array.from(
    { length: total },
    (_, i) => `<span class="nav-ponto" data-idx="${i}"></span>`
  ).join("");
  document.getElementById("pag-total-desktop").textContent =
    String(total).padStart(2, "0");

  atualizarPaginaDesktop();

  // Destaque lateral
  document.querySelectorAll(".carta-item").forEach((el) =>
    el.classList.toggle("ativa", el.dataset.id === id)
  );

  // Abrir
  document.getElementById("painel").classList.add("aberto");
  document.getElementById("painel-overlay").classList.add("aberto");
  document.getElementById("palco-desktop").classList.add("has-open");
}

function fecharPainel() {
  document.getElementById("painel").classList.remove("aberto");
  document.getElementById("painel-overlay").classList.remove("aberto");
  document.getElementById("palco-desktop").classList.remove("has-open");
  document.querySelectorAll(".carta-item").forEach((el) =>
    el.classList.remove("ativa")
  );
  estado.cartaAtiva = null;
}

function irParaPaginaDesktop(i) {
  if (!estado.cartaAtiva) return;
  if (i < 0 || i >= estado.cartaAtiva.paginas.length) return;
  estado.paginaIdx = i;
  atualizarPaginaDesktop();
}

function atualizarPaginaDesktop() {
  if (!estado.cartaAtiva) return;
  const paginas = document.querySelectorAll("#paginas-track-desktop .pagina-desktop");
  paginas.forEach((p, i) => {
    p.classList.remove("ativa", "fora-esquerda");
    if (i === estado.paginaIdx) { p.classList.add("ativa"); p.scrollTop = 0; }
    else if (i < estado.paginaIdx) p.classList.add("fora-esquerda");
  });

  const total = estado.cartaAtiva.paginas.length;
  document.getElementById("pag-atual-desktop").textContent =
    String(estado.paginaIdx + 1).padStart(2, "0");
  document.getElementById("btn-anterior").disabled = estado.paginaIdx === 0;
  document.getElementById("btn-proxima").disabled = estado.paginaIdx === total - 1;

  document.querySelectorAll("#nav-pontos-desktop .nav-ponto").forEach((p, i) =>
    p.classList.toggle("ativo", i === estado.paginaIdx)
  );
}

/* ==========================================================================
   BLOCO 06 — Modal "Faça parte"
   ========================================================================== */

function inicializarModalParticipar() {
  const modal   = document.getElementById("modal-participar");
  const overlay = document.getElementById("modal-overlay");
  if (!modal || !overlay) return;

  function abrir() {
    modal.classList.add("aberto");
    overlay.classList.add("aberto");
    modal.setAttribute("aria-hidden", "false");
    const firstInput = modal.querySelector("input, textarea");
    if (firstInput) setTimeout(() => firstInput.focus(), 250);
  }
  function fechar() {
    modal.classList.remove("aberto");
    overlay.classList.remove("aberto");
    modal.setAttribute("aria-hidden", "true");
  }

  document.getElementById("abrir-participar")?.addEventListener("click", abrir);
  document.getElementById("abrir-participar-mobile")?.addEventListener("click", abrir);
  document.getElementById("fechar-participar")?.addEventListener("click", fechar);
  overlay.addEventListener("click", fechar);
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("aberto")) fechar();
  });
}

/* ==========================================================================
   BLOCO 07 — Inicialização
   ========================================================================== */
document.addEventListener("DOMContentLoaded", () => {
  layoutAnterior = layoutAtual();
  inicializar();
  inicializarModalParticipar();
});

// ── marked.js config ─────────────────────────────────────────────────────────
marked.setOptions({ breaks: true, gfm: true });

// ── Estado global ────────────────────────────────────────────────────────────
const state = {
  activeDocId: null,
  activeDocLabel: null,
  chatHistory: [],
  searchDebounce: null,
  allDocs: null,       // cache de /api/documents
};

// ── Elementos DOM ────────────────────────────────────────────────────────────
const els = {
  searchInput:     document.getElementById("search-input"),
  sidebarResults:  document.getElementById("sidebar-results"),
  docHeader:       document.getElementById("doc-header"),
  docTitle:        document.getElementById("doc-title"),
  docMetaText:     document.getElementById("doc-meta-text"),
  docPdfLink:      document.getElementById("doc-pdf-link"),
  docLanding:      document.getElementById("doc-landing"),
  docContent:      document.getElementById("doc-content"),
  chatContext:     document.getElementById("chat-context"),
  chatPlaceholder: document.getElementById("chat-placeholder"),
  chatMessages:    document.getElementById("chat-messages"),
  chatInputArea:   document.getElementById("chat-input-area"),
  chatInput:       document.getElementById("chat-input"),
  chatSend:        document.getElementById("chat-send"),
};

// ── Init: cargar lista de documentos ─────────────────────────────────────────
async function init() {
  try {
    const res = await fetch("/api/documents");
    const data = await res.json();
    state.allDocs = data.grupos;
    renderDocList(state.allDocs);
  } catch {
    renderSidebarError();
  }
}

function renderDocList(grupos) {
  const html = Object.entries(grupos).map(([esp, docs]) => `
    <div class="doc-group">
      <div class="doc-group-label">${escapeHtml(esp)}</div>
      ${docs.map(d => `
        <div
          class="doc-list-item${d.id === state.activeDocId ? " active" : ""}"
          data-doc-id="${escapeHtml(d.id)}"
          onclick="loadDoc('${escapeHtml(d.id)}')"
        >${escapeHtml(d.label)}</div>
      `).join("")}
    </div>
  `).join("");
  els.sidebarResults.innerHTML = html;
}

// ── Búsqueda BM25 ─────────────────────────────────────────────────────────────
els.searchInput.addEventListener("input", () => {
  clearTimeout(state.searchDebounce);
  const q = els.searchInput.value.trim();
  if (!q) {
    if (state.allDocs) renderDocList(state.allDocs);
    else renderSidebarEmpty();
    return;
  }
  state.searchDebounce = setTimeout(() => fetchSearch(q), 280);
});

async function fetchSearch(q) {
  renderSidebarLoading();
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    renderResults(data.results, q);
  } catch {
    renderSidebarError();
  }
}

function renderResults(results, query) {
  if (!results.length) {
    els.sidebarResults.innerHTML = `
      <div class="sidebar-empty">
        <span class="icon">🔎</span>
        Sin resultados para "${escapeHtml(query)}"
      </div>`;
    return;
  }
  const tokens = query.toLowerCase().split(/\s+/).filter(t => t.length >= 3);
  els.sidebarResults.innerHTML = results.map(r => `
    <div
      class="result-item${r.doc_id === state.activeDocId ? " active" : ""}"
      data-doc-id="${escapeHtml(r.doc_id)}"
      onclick="loadDoc('${escapeHtml(r.doc_id)}', ${r.page})"
    >
      <div class="result-doc">${escapeHtml(r.doc_label)}</div>
      <div class="result-page">Página ${r.page}</div>
      <div class="result-excerpt">${highlightTerms(escapeHtml(r.excerpt), tokens)}</div>
    </div>
  `).join("");
}

// ── Carga de documento ────────────────────────────────────────────────────────
async function loadDoc(docId, scrollToPage = null) {
  setActiveInSidebar(docId);

  if (state.activeDocId === docId) {
    if (scrollToPage) scrollToPageBlock(scrollToPage);
    return;
  }

  showDocLoading();

  try {
    const res = await fetch(`/api/doc/${encodeURIComponent(docId)}`);
    if (!res.ok) throw new Error();
    const doc = await res.json();

    state.activeDocId = docId;
    state.activeDocLabel = doc.label;
    state.chatHistory = [];

    renderDoc(doc);
    resetChat(doc.label);

    if (scrollToPage) setTimeout(() => scrollToPageBlock(scrollToPage), 80);
  } catch {
    showDocError();
  }
}

function setActiveInSidebar(docId) {
  document.querySelectorAll(".result-item, .doc-list-item").forEach(el => {
    el.classList.toggle("active", el.dataset.docId === docId);
  });
}

function renderDoc(doc) {
  els.docTitle.textContent = doc.label;
  els.docMetaText.textContent = doc.especialidad;
  els.docPdfLink.href = doc.url;
  els.docHeader.style.display = "";
  els.docLanding.style.display = "none";

  els.docContent.innerHTML = doc.pages.map(p => `
    <div class="page-block" id="page-${p.page}">
      <div class="page-label">Página ${p.page}</div>
      <div class="page-md">${marked.parse(p.content)}</div>
    </div>
  `).join("");

  els.docContent.style.display = "";
  els.docContent.scrollTop = 0;
}

function scrollToPageBlock(page) {
  const block = document.getElementById(`page-${page}`);
  if (!block) return;
  block.scrollIntoView({ behavior: "smooth", block: "start" });
  const label = block.querySelector(".page-label");
  if (label) {
    label.classList.add("highlight");
    setTimeout(() => label.classList.remove("highlight"), 2200);
  }
}

// ── Chat ──────────────────────────────────────────────────────────────────────
function resetChat(label) {
  state.chatHistory = [];
  els.chatContext.textContent = `Contexto: ${label}`;
  els.chatPlaceholder.style.display = "none";
  els.chatMessages.style.display = "";
  els.chatMessages.innerHTML = "";
  els.chatInputArea.style.display = "";
  els.chatInput.value = "";
  els.chatSend.disabled = false;
}

els.chatSend.addEventListener("click", sendMessage);
els.chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

async function sendMessage() {
  const text = els.chatInput.value.trim();
  if (!text || !state.activeDocId) return;

  appendMessage("user", text);
  els.chatInput.value = "";
  els.chatSend.disabled = true;

  const thinkingId = appendThinking();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        doc_id: state.activeDocId,
        message: text,
        history: state.chatHistory.slice(-6),
      }),
    });
    const data = await res.json();
    removeThinking(thinkingId);
    appendMessage("assistant", data.answer, data.citations);
    state.chatHistory.push({ role: "user", content: text });
    state.chatHistory.push({ role: "assistant", content: data.answer });
  } catch {
    removeThinking(thinkingId);
    appendMessage("assistant", "Error al conectar con el servidor. Intenta de nuevo.");
  } finally {
    els.chatSend.disabled = false;
    els.chatInput.focus();
  }
}

function appendMessage(role, content, citations = []) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;

  const roleLabel = role === "user" ? "Tú" : "Asistente";

  // Usuarios en plain text, asistente en markdown
  const bubbleContent = role === "assistant"
    ? marked.parse(content)
    : escapeHtml(content);

  const citationHtml = citations.length
    ? `<div class="msg-citation">📄 pág. ${citations.map(c => c.page).join(", ")}</div>`
    : "";

  div.innerHTML = `
    <div class="msg-role">${roleLabel}</div>
    <div class="msg-bubble">${bubbleContent}</div>
    ${citationHtml}
  `;

  els.chatMessages.appendChild(div);
  els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
}

function appendThinking() {
  const id = "thinking-" + Date.now();
  const div = document.createElement("div");
  div.className = "msg assistant";
  div.id = id;
  div.innerHTML = `
    <div class="msg-role">Asistente</div>
    <div class="msg-bubble"><span class="spinner"></span> Buscando...</div>
  `;
  els.chatMessages.appendChild(div);
  els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
  return id;
}

function removeThinking(id) {
  document.getElementById(id)?.remove();
}

// ── UI helpers ────────────────────────────────────────────────────────────────
function renderSidebarEmpty() {
  els.sidebarResults.innerHTML = `
    <div class="sidebar-empty">
      <span class="icon">🔍</span>
      Escribe una palabra clave para buscar en todos los protocolos.
    </div>`;
}

function renderSidebarLoading() {
  els.sidebarResults.innerHTML = `
    <div class="sidebar-empty"><span class="spinner"></span> Buscando...</div>`;
}

function renderSidebarError() {
  els.sidebarResults.innerHTML = `
    <div class="sidebar-empty">Error al cargar. Recarga la página.</div>`;
}

function showDocLoading() {
  els.docLanding.style.display = "none";
  els.docContent.innerHTML = `<div class="doc-landing"><span class="spinner"></span><p>Cargando...</p></div>`;
  els.docContent.style.display = "";
  els.docHeader.style.display = "none";
}

function showDocError() {
  els.docContent.innerHTML = `<div class="doc-landing"><p>Error al cargar el protocolo.</p></div>`;
}

function highlightTerms(text, tokens) {
  let result = text;
  tokens.forEach(token => {
    const re = new RegExp(`(${escapeRegex(token)})`, "gi");
    result = result.replace(re, "<mark>$1</mark>");
  });
  return result;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// ── Estilos para lista de docs en sidebar ─────────────────────────────────────
const sidebarStyles = document.createElement("style");
sidebarStyles.textContent = `
  .doc-group { padding: 6px 0; border-bottom: 1px solid var(--borde-sutil); }
  .doc-group:last-child { border-bottom: none; }
  .doc-group-label {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; color: var(--salvia);
    padding: 8px 14px 4px;
  }
  .doc-list-item {
    padding: 7px 14px 7px 20px;
    font-size: 13px; color: var(--texto);
    cursor: pointer;
    border-left: 3px solid transparent;
  }
  .doc-list-item:hover { background: rgba(90,97,72,0.08); }
  .doc-list-item.active {
    border-left-color: var(--terracota);
    background: rgba(202,101,60,0.07);
    font-weight: 500;
  }

  /* Markdown en el viewer */
  .page-md table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 12px; }
  .page-md th { background: var(--beige); padding: 6px 10px; border: 1px solid var(--borde); font-weight: 600; text-align: left; }
  .page-md td { padding: 5px 10px; border: 1px solid var(--borde); vertical-align: top; }
  .page-md h1 { font-size: 16px; margin: 16px 0 8px; }
  .page-md h2 { font-size: 14px; margin: 14px 0 6px; }
  .page-md h3 { font-size: 13px; font-weight: 600; margin: 12px 0 5px; }
  .page-md p  { font-size: 13px; line-height: 1.75; color: #333; margin-bottom: 8px; }
  .page-md ul, .page-md ol { padding-left: 20px; margin-bottom: 10px; }
  .page-md li { font-size: 13px; line-height: 1.7; color: #333; }
  .page-md hr { border: none; border-top: 1px solid var(--borde); margin: 16px 0; }
  .page-md strong { font-weight: 600; }
  .page-md code { background: var(--beige); padding: 1px 4px; border-radius: 2px; font-size: 12px; }
  .page-md img { max-width: 100%; display: none; } /* imágenes de referencia, no relevantes */

  /* Markdown en el chat */
  .msg-bubble table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 12px; }
  .msg-bubble th { background: var(--beige); padding: 5px 8px; border: 1px solid var(--borde); font-weight: 600; }
  .msg-bubble td { padding: 4px 8px; border: 1px solid var(--borde); vertical-align: top; }
  .msg-bubble p  { margin-bottom: 6px; }
  .msg-bubble ul, .msg-bubble ol { padding-left: 18px; margin-bottom: 6px; }
  .msg-bubble li { margin-bottom: 2px; }
  .msg-bubble h1, .msg-bubble h2, .msg-bubble h3 { margin: 8px 0 4px; font-size: 13px; }
  .msg-bubble hr { border: none; border-top: 1px solid var(--borde); margin: 10px 0; }
  .msg-bubble a { color: var(--terracota); }
  .msg.user .msg-bubble table th { background: rgba(255,255,255,0.15); }
  .msg.user .msg-bubble a { color: #fff; }
`;
document.head.appendChild(sidebarStyles);

// ── Arrancar ──────────────────────────────────────────────────────────────────
init();

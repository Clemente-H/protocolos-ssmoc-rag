import streamlit as st

from rag.documents import documentos_por_especialidad, get_by_id, Documento
from rag.generator import generate_answer
from rag.retriever import retrieve_chunks

st.set_page_config(
    page_title="Protocolos Médicos SSMOC",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS mínimo ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Reduce padding del sidebar */
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
/* Estilo del documento renderizado */
.doc-viewer { font-size: 0.92rem; line-height: 1.6; }
/* Mensajes del chat */
.stChatMessage { font-size: 0.93rem; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🩺 Protocolos SSMOC")
    st.caption("Selecciona un protocolo para consultarlo.")
    st.divider()

    busqueda = st.text_input("🔍 Buscar protocolo", placeholder="ej: diabetes, cardio...")

    grupos = documentos_por_especialidad()
    doc_seleccionado: Documento | None = None

    for especialidad, docs in grupos.items():
        # Filtrar si hay búsqueda activa
        docs_filtrados = docs
        if busqueda.strip():
            q = busqueda.strip().lower()
            docs_filtrados = [
                d for d in docs
                if q in d.label.lower() or q in d.especialidad.lower()
            ]
        if not docs_filtrados:
            continue

        with st.expander(especialidad, expanded=bool(busqueda.strip())):
            for doc in docs_filtrados:
                if st.button(doc.label, key=f"btn_{doc.id}", use_container_width=True):
                    st.session_state["doc_id"] = doc.id
                    st.session_state["chat_history"] = []

    st.divider()
    st.caption("Fuente: [ssmoc.redsalud.gob.cl](https://ssmoc.redsalud.gob.cl/medicos/)")


# ── Panel principal ───────────────────────────────────────────────────────────
doc_id = st.session_state.get("doc_id")

if not doc_id:
    # Landing
    st.markdown("## Bienvenido")
    st.markdown(
        "Selecciona un **protocolo** en el panel izquierdo para visualizarlo "
        "y hacer preguntas sobre él."
    )
    st.markdown(
        "Puedes usar el buscador del sidebar para filtrar por nombre de protocolo "
        "o especialidad."
    )
    st.stop()

doc = get_by_id(doc_id)
if not doc:
    st.error("Documento no encontrado.")
    st.stop()

st.header(doc.label)
st.caption(f"Especialidad: **{doc.especialidad}** · [Ver PDF original]({doc.display_url})")

tab_doc, tab_chat = st.tabs(["📄 Protocolo", "💬 Chat"])

# ── Tab: Documento ─────────────────────────────────────────────────────────
with tab_doc:
    md_parts = []
    for md_path in doc.md_paths:
        if md_path.exists():
            md_parts.append(md_path.read_text(encoding="utf-8"))

    if md_parts:
        st.info(
            "💡 Usa **Ctrl+F** (o **Cmd+F** en Mac) para buscar texto dentro del documento.",
            icon=None,
        )
        st.markdown('<div class="doc-viewer">', unsafe_allow_html=True)
        st.markdown("\n\n---\n\n".join(md_parts))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No se encontró el archivo Markdown para este protocolo.")

# ── Tab: Chat ──────────────────────────────────────────────────────────────
with tab_chat:
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    history: list[dict] = st.session_state["chat_history"]

    st.caption(
        f"Haciendo preguntas sobre: **{doc.label}**. "
        "Las respuestas citan la página del protocolo."
    )

    # Mostrar historial
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Escribe tu pregunta sobre este protocolo..."):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en el protocolo..."):
                chunks = retrieve_chunks(
                    prompt,
                    top_k=6,
                    source_files=doc.filenames,
                )

            if not chunks:
                answer = "No encontré información relevante en este protocolo para tu pregunta."
            else:
                with st.spinner("Generando respuesta..."):
                    answer = generate_answer(prompt, chunks)

            st.markdown(answer)

            if chunks:
                with st.expander("📎 Fragmentos fuente"):
                    for i, chunk in enumerate(chunks, 1):
                        st.markdown(
                            f"**Fuente {i}** — pág. {chunk['page']} "
                            f"· relevancia: {chunk['score']}"
                        )
                        st.caption(chunk["text"][:300].replace("\n", " "))
                        st.markdown("---")

        history.append({"role": "assistant", "content": answer})
        st.session_state["chat_history"] = history

import os
import streamlit as st

from rag.generator import generate_answer
from rag.retriever import retrieve_chunks

st.set_page_config(page_title="Protocolos Médicos", page_icon="🩺", layout="wide")

st.title("📋 Búsqueda de Protocolos Médicos")
st.caption("Consulta protocolos y guías de referencia y contrarreferencia del SESAM CENIA")

query = st.text_input("Escribe tu pregunta sobre un protocolo:", placeholder="Ej: ¿cómo se deriva un paciente con diabetes tipo 2 a endocrinología?")

if query:
    with st.spinner("Buscando en los protocolos..."):
        chunks = retrieve_chunks(query, top_k=6)

    if not chunks:
        st.warning("No se encontraron fragmentos relevantes.")
    else:
        with st.spinner("Generando respuesta con Mistral..."):
            answer = generate_answer(query, chunks)

        st.markdown("### Respuesta")
        st.markdown(answer)

        with st.expander("📎 Fuentes encontradas"):
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"**Fuente {i}** — {chunk['source_file']} (pág. {chunk['page']})")
                if chunk.get("original_url"):
                    st.markdown(f"[Abrir documento original]({chunk['original_url']})")
                st.caption(f"Puntuación de relevancia: {chunk['score']}")
                st.markdown("---")

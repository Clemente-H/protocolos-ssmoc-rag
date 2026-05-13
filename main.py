import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag.documents import get_by_id, documentos_por_especialidad
from rag.generator import generate_answer
from rag.retriever import retrieve_chunks
from rag.search import search

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Protocolos SSMOC", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Regex para limpiar referencias a imágenes locales del parser (no existen en prod)
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\.(jpg|jpeg|png|gif|webp|svg)[^)]*\)", re.IGNORECASE)


def _strip_images(text: str) -> str:
    return _IMAGE_RE.sub("", text)


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(STATIC_DIR / "index.html")


# ── API: lista de documentos (sidebar default) ───────────────────────────────

@app.get("/api/documents")
def api_documents():
    grupos = documentos_por_especialidad()
    return {
        "grupos": {
            esp: [{"id": d.id, "label": d.label} for d in docs]
            for esp, docs in grupos.items()
        }
    }


# ── API: búsqueda BM25 (sidebar) ──────────────────────────────────────────────

@app.get("/api/search")
def api_search(q: str = Query(default="", min_length=1)):
    if not q.strip():
        return {"results": []}
    results = search(q.strip(), top_k=8)
    return {"results": results}


# ── API: contenido del documento ──────────────────────────────────────────────

@app.get("/api/doc/{doc_id}")
def api_doc(doc_id: str):
    doc = get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    pages: list[dict] = []
    for md_path in doc.md_paths:
        if not md_path.exists():
            continue
        raw = md_path.read_text(encoding="utf-8")
        blocks = re.split(r"--- Página (\d+) ---\n", raw)
        i = 1
        while i + 1 < len(blocks):
            page_num = int(blocks[i])
            content = _strip_images(blocks[i + 1].strip())
            if content:
                pages.append({"page": page_num, "content": content})
            i += 2

    return {
        "id": doc.id,
        "label": doc.label,
        "especialidad": doc.especialidad,
        "url": doc.display_url,
        "pages": pages,
    }


# ── API: chat ─────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    doc_id: str
    message: str
    history: list[ChatMessage] = []

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    doc = get_by_id(req.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    try:
        chunks = retrieve_chunks(req.message, top_k=6, source_files=doc.filenames)
    except Exception as e:
        logger.error("retrieve_chunks falló: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en búsqueda vectorial: {e}")

    if not chunks:
        return {
            "answer": "No encontré información relevante en este protocolo para tu pregunta.",
            "citations": [],
        }

    try:
        answer = generate_answer(req.message, chunks)
    except Exception as e:
        logger.error("generate_answer falló: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {e}")

    citations = [
        {"page": c["page"], "source_file": c["source_file"], "score": c["score"]}
        for c in chunks[:3]
    ]

    return {"answer": answer, "citations": citations}


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

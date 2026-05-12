"""
BM25 sobre el corpus completo — usado para el sidebar de búsqueda.

Carga el índice en memoria al primer uso y lo reutiliza.
"""

import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from rag.documents import get_by_filename

DATA_DIR = Path(__file__).parent.parent / "data"
PARSED_FILE = DATA_DIR / "parsed" / "parsed_documents.json"

_bm25: BM25Okapi | None = None
_chunks: list[dict] = []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9]+", text.lower())


def _get_index() -> tuple[BM25Okapi, list[dict]]:
    global _bm25, _chunks
    if _bm25 is None:
        with open(PARSED_FILE, "r", encoding="utf-8") as f:
            all_chunks = json.load(f)
        _chunks = [c for c in all_chunks if c["text"].strip()]
        corpus = [_tokenize(c["text"]) for c in _chunks]
        _bm25 = BM25Okapi(corpus)
    return _bm25, _chunks


def search(query: str, top_k: int = 8) -> list[dict]:
    """Busca en todos los documentos usando BM25. Devuelve chunks con metadata enriquecida."""
    bm25, chunks = _get_index()
    tokens = _tokenize(query)
    if not tokens:
        return []

    scores = bm25.get_scores(tokens)
    top_indices = scores.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        if scores[idx] <= 0:
            continue
        chunk = chunks[idx]
        meta = chunk["metadata"]
        filename = meta.get("source_file", "")
        doc = get_by_filename(filename)

        results.append({
            "doc_id": doc.id if doc else filename,
            "doc_label": doc.label if doc else filename,
            "filename": filename,
            "page": meta.get("page", "?"),
            "score": round(float(scores[idx]), 4),
            "excerpt": _make_excerpt(chunk["text"], tokens),
        })

    return results


def _make_excerpt(text: str, tokens: list[str], length: int = 200) -> str:
    """Extrae un fragmento centrado en la primera aparición de algún token."""
    lower = text.lower()
    best_pos = len(text)
    for token in tokens:
        pos = lower.find(token)
        if 0 <= pos < best_pos:
            best_pos = pos

    start = max(0, best_pos - 60)
    end = min(len(text), start + length)
    excerpt = text[start:end].strip().replace("\n", " ")
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."
    return excerpt

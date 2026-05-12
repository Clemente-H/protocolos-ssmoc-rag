import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

import chromadb

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
PARSED_FILE = DATA_DIR / "parsed" / "parsed_documents.json"
CHROMA_DIR = DATA_DIR / "chroma_db"

EMBED_BATCH_SIZE = 10
EMBED_MODEL = "BAAI/bge-m3"

_hf_client = None


def _get_hf_client():
    global _hf_client
    if _hf_client is None:
        _hf_client = InferenceClient(api_key=os.getenv("HUGGING_FACE_API_KEY"))
    return _hf_client


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings from HuggingFace Inference API via feature_extraction."""
    client = _get_hf_client()
    result = client.feature_extraction(
        text=texts,
        model=EMBED_MODEL,
    )
    # feature_extraction returns list of vectors (one per input text)
    # Each vector is a list of floats
    return [[float(x) for x in v] for v in result]


def get_text_embedding(text: str) -> list[float]:
    """Get a single text embedding."""
    return get_embeddings([text])[0]


def get_text_embedding_batch(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a batch of texts."""
    return get_embeddings(texts)


def build_index():
    """Load parsed documents and create embeddings in ChromaDB via HuggingFace."""
    with open(PARSED_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    total = len(chunks)
    print(f"Cargados {total} documentos desde {PARSED_FILE}")
    print(f"Modelo: {EMBED_MODEL} | Lotes de {EMBED_BATCH_SIZE}")
    print("Generando embeddings y guardando en ChromaDB...")

    chroma_client = chromadb.PersistentClient(str(CHROMA_DIR))
    # Recrear siempre para garantizar cosine distance
    try:
        chroma_client.delete_collection("protocolos")
    except Exception:
        pass
    collection = chroma_client.create_collection(
        "protocolos",
        metadata={"hnsw:space": "cosine"},
    )

    inserted = 0
    for i in range(0, total, EMBED_BATCH_SIZE):
        batch = chunks[i:i + EMBED_BATCH_SIZE]
        texts = [c["text"] for c in batch]
        metas = [c["metadata"] for c in batch]
        ids = [f"doc-{i + j}" for j in range(len(batch))]

        for attempt in range(5):
            try:
                embeddings = get_text_embedding_batch(texts)

                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metas,
                )
                inserted += len(batch)
                print(f"  {inserted}/{total} chunks embebidos")
                break
            except Exception as e:
                if attempt < 4:
                    wait = 10 * (2 ** attempt)
                    print(f"  Error: {e}. Reintento en {wait}s...")
                    time.sleep(wait)
                else:
                    raise

    print(f"Indice listo. Total: {inserted} vectores en ChromaDB.")


def load_index():
    """Load existing ChromaDB collection."""
    chroma_client = chromadb.PersistentClient(str(CHROMA_DIR))
    collection = chroma_client.get_collection("protocolos")
    return collection


def retrieve(query: str, collection, top_k: int = 6, source_files: list[str] | None = None) -> list[dict]:
    """Retrieve chunks by embedding query and querying ChromaDB.

    source_files: si se pasa, filtra por esos archivos antes de buscar (modo documento).
    """
    query_embedding = get_text_embedding(query)

    where = None
    if source_files:
        if len(source_files) == 1:
            where = {"source_file": {"$eq": source_files[0]}}
        else:
            where = {"source_file": {"$in": source_files}}

    hits = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        hits["documents"][0],
        hits["metadatas"][0],
        hits["distances"][0],
    ):
        # Con cosine distance en ChromaDB: dist ∈ [0, 2], 0 = idéntico
        score = round(1.0 - dist, 4)
        chunks.append({
            "text": doc,
            "source_file": meta.get("source_file", "desconocido"),
            "original_url": meta.get("original_url", ""),
            "page": meta.get("page", "?"),
            "score": score,
        })

    return chunks
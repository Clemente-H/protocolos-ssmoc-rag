#!/usr/bin/env python3
"""Test BM25 retrieval standalone (sin ChromaDB, sin embeddings densos)."""

import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

DATA_DIR = Path(__file__).parent.parent / "data"
PARSED_FILE = DATA_DIR / "parsed" / "parsed_documents.json"

with open(PARSED_FILE, "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

chunks = [c for c in all_chunks if c["text"].strip()]
print(f"Cargados {len(chunks)} chunks")

texts = [c["text"] for c in chunks]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+", text.lower())


tokenized_corpus = [tokenize(t) for t in texts]
bm25 = BM25Okapi(tokenized_corpus)
print("Índice BM25 listo.\n")

queries = [
    "¿cómo se deriva un paciente con diabetes tipo 2 a endocrinología?",
    "criterios de contrarreferencia de neumonía",
    "protocolo de referencia prenatal alto riesgo",
]

for query in queries:
    print(f"QUERY: {query}")
    tokens = tokenize(query)
    scores = bm25.get_scores(tokens)
    top_indices = scores.argsort()[-5:][::-1]

    for idx in top_indices:
        chunk = chunks[idx]
        meta = chunk["metadata"]
        preview = chunk["text"][:160].replace("\n", " ")
        print(f"  score={scores[idx]:.4f} | {meta.get('source_file', '?')} pág. {meta.get('page', '?')}")
        print(f"    {preview}")
        print()

    print("=" * 80)
    print()

from rag.embed import load_index


def retrieve_chunks(query: str, top_k: int = 6) -> list[dict]:
    """Retrieve the most relevant chunks from the index for a given query.

    Returns raw context only — no LLM call.
    """
    index = load_index()
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)

    chunks = []
    for node in nodes:
        meta = node.node.metadata
        chunks.append({
            "text": node.node.text,
            "source_file": meta.get("source_file", "desconocido"),
            "original_url": meta.get("original_url", ""),
            "page": meta.get("page", "?"),
            "score": round(node.score, 4),
        })

    return chunks

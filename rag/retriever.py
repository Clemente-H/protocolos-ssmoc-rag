from rag.embed import load_index, retrieve

_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        _collection = load_index()
    return _collection


def retrieve_chunks(query: str, top_k: int = 6, source_files: list[str] | None = None) -> list[dict]:
    """Recupera los chunks más relevantes para una query.

    source_files: lista de filenames para restringir la búsqueda a un documento.
    Si es None, busca en todo el corpus.
    """
    collection = _get_collection()
    return retrieve(query, collection, top_k=top_k, source_files=source_files)

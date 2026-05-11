import json
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import Document
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
PARSED_FILE = DATA_DIR / "parsed" / "parsed_documents.json"
CHROMA_DIR = DATA_DIR / "chroma_db"


def build_index() -> VectorStoreIndex:
    """Load parsed documents and create embeddings in ChromaDB via Mistral."""
    chroma_client = chromadb.PersistentClient(str(CHROMA_DIR))
    collection = chroma_client.get_or_create_collection("protocolos")
    vector_store = ChromaVectorStore(chroma_collection=collection, persist_dir=str(CHROMA_DIR))
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    embed_model = MistralAIEmbedding(model_name="mistral-embed")

    with open(PARSED_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    documents = [
        Document(text=chunk["text"], metadata=chunk["metadata"])
        for chunk in chunks
    ]

    print(f"Cargados {len(documents)} documentos desde {PARSED_FILE}")
    print("Generando embeddings y guardando en ChromaDB...")

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    print("Index listo.")
    return index


def load_index() -> VectorStoreIndex:
    """Load existing index from ChromaDB without re-embedding."""
    chroma_client = chromadb.PersistentClient(str(CHROMA_DIR))
    collection = chroma_client.get_or_create_collection("protocolos")
    vector_store = ChromaVectorStore(chroma_collection=collection, persist_dir=str(CHROMA_DIR))
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    embed_model = MistralAIEmbedding(model_name="mistral-embed")

    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )

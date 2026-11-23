"""Retrieval sur la base de connaissance perso.

Domain: RAG (hybrid search semaine 11, reranking semaine 11,
RAG agentique semaine 13).

Semaine 5: retrieval dense simple (top-k cosine similarity), via le port
VectorStore — pas d'appel direct à Qdrant ici non plus.
"""
from app.core.storage_factory import get_vector_store
from app.rag.ingest import COLLECTION_NAME


def retrieve(query: str, top_k: int = 5) -> list[str]:
    """TODO semaine 5: embedder la query, puis get_vector_store().search(...)."""
    get_vector_store()
    raise NotImplementedError("Retrieval dense à écrire semaine 5, cf. COLLECTION_NAME=" + COLLECTION_NAME)


def retrieve_hybrid(query: str, top_k: int = 5) -> list[str]:
    """TODO semaine 11: fusion dense + BM25 (Reciprocal Rank Fusion) + reranking."""
    raise NotImplementedError("Hybrid search à écrire semaine 11")

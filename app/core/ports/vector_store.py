"""Port pour le stockage vectoriel (RAG, mémoire long terme).

Même principe que KVStore : app/rag/ ne parle jamais à Qdrant directement.
Changer Qdrant pour Pinecone/Weaviate/pgvector = un nouvel adapter dans
app/core/adapters/, zéro changement dans app/rag/ingest.py ou retriever.py.
"""
from abc import abstractmethod
from dataclasses import dataclass

from app.core.ports.capability import Capability


@dataclass
class VectorMatch:
    id: str
    score: float
    payload: dict


class VectorStore(Capability):
    @abstractmethod
    def upsert(self, collection: str, id: str, vector: list[float], payload: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, collection: str, query_vector: list[float], top_k: int = 5) -> list[VectorMatch]:
        raise NotImplementedError

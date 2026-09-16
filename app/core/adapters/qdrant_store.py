"""Adapter Qdrant pour le port VectorStore."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.ports.vector_store import VectorMatch, VectorStore


class QdrantVectorStore(VectorStore):
    name = "qdrant"

    def __init__(self, url: str, embedding_dim: int = 1024) -> None:
        self._client = QdrantClient(url=url)
        self._dim = embedding_dim

    def _ensure_collection(self, collection: str) -> None:
        if not self._client.collection_exists(collection):
            self._client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=self._dim, distance=Distance.COSINE),
            )

    def upsert(self, collection: str, id: str, vector: list[float], payload: dict) -> None:
        self._ensure_collection(collection)
        self._client.upsert(collection, points=[PointStruct(id=id, vector=vector, payload=payload)])

    def search(self, collection: str, query_vector: list[float], top_k: int = 5) -> list[VectorMatch]:
        self._ensure_collection(collection)
        hits = self._client.search(collection, query_vector=query_vector, limit=top_k)
        return [VectorMatch(id=str(h.id), score=h.score, payload=h.payload or {}) for h in hits]

    def is_available(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception:  # noqa: BLE001 — idem : health check, jamais d'exception qui remonte
            return False

"""Sélection des adapters de stockage actifs — même rôle que
app/core/llm/factory.py, appliqué à KVStore et VectorStore.

Changer de fournisseur de base de données = changer STORAGE_KV_PROVIDER ou
STORAGE_VECTOR_PROVIDER dans .env, écrire l'adapter s'il n'existe pas
encore, et c'est tout : app/core/memory.py et app/rag/ n'en savent rien.
"""
from functools import lru_cache

from app.config import settings
from app.core.adapters.qdrant_store import QdrantVectorStore
from app.core.adapters.redis_kv import RedisKVStore
from app.core.ports.kv_store import KVStore
from app.core.ports.vector_store import VectorStore


@lru_cache(maxsize=1)
def get_kv_store() -> KVStore:
    if settings.kv_store_provider == "redis":
        return RedisKVStore(url=settings.redis_url)
    raise ValueError(f"STORAGE_KV_PROVIDER='{settings.kv_store_provider}' inconnu (seul 'redis' est câblé pour l'instant).")


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    if settings.vector_store_provider == "qdrant":
        return QdrantVectorStore(url=settings.qdrant_url)
    raise ValueError(f"STORAGE_VECTOR_PROVIDER='{settings.vector_store_provider}' inconnu (seul 'qdrant' est câblé pour l'instant).")

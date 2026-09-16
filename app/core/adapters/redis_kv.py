"""Adapter Redis pour le port KVStore."""
import redis

from app.core.ports.kv_store import KVStore


class RedisKVStore(KVStore):
    name = "redis"

    def __init__(self, url: str) -> None:
        self._client = redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str) -> None:
        self._client.set(key, value)

    def is_available(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:  # noqa: BLE001 — un health check doit survivre à N'IMPORTE quelle erreur réseau/auth
            return False

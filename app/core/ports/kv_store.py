"""Port pour le stockage clé-valeur (mémoire court terme).

Même principe que app/core/llm/base.py::LLMProvider, appliqué au stockage :
app/core/memory.py ne parle jamais à Redis directement, seulement à cette
interface. Changer Redis pour autre chose (Valkey, DynamoDB, SQLite...) =
écrire un nouvel adapter dans app/core/adapters/, zéro changement ailleurs.
"""
from abc import abstractmethod

from app.core.ports.capability import Capability


class KVStore(Capability):
    @abstractmethod
    def get(self, key: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        raise NotImplementedError

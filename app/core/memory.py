"""Mémoire de Jarvis.

Bloc catalogue technique: Agents IA — mémoire d'agent
(court terme / long terme / épisodique).

Ne parle plus jamais à Redis directement : passe par le port KVStore
(app/core/ports/kv_store.py) via app/core/storage_factory.py — changer de
backend de mémoire court terme ne touche pas ce fichier.

Semaine 5 de la roadmap.
"""
import json

from app.core.storage_factory import get_kv_store

HISTORY_KEY = "jarvis:session:{session_id}:history"
MAX_TURNS = 20  # fenêtre de contexte court terme — au-delà, ça doit passer par le long terme (RAG)


def get_short_term_history(session_id: str) -> list[dict]:
    """Mémoire court terme = historique de la session courante."""
    raw = get_kv_store().get(HISTORY_KEY.format(session_id=session_id))
    return json.loads(raw) if raw else []


def save_turn(session_id: str, user_message: str, assistant_reply: str) -> None:
    history = get_short_term_history(session_id)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_reply})
    history = history[-MAX_TURNS:]
    get_kv_store().set(HISTORY_KEY.format(session_id=session_id), json.dumps(history))


def get_long_term_context(query: str, session_id: str) -> list[str]:
    """Mémoire long terme / épisodique — déléguée à app/rag/retriever.py
    (capacité "rag", optionnelle : si aucun VectorStore n'est disponible,
    retourne une liste vide plutôt que de faire planter l'agent).
    """
    from app.core.capabilities import registry

    if not registry.has("rag"):
        return []
    from app.rag.retriever import retrieve

    return retrieve(query)

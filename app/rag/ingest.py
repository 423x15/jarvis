"""Pipeline d'ingestion de la base de connaissance perso de Jarvis.

Bloc catalogue technique: RAG (chunking & indexation, embeddings, bases
vectorielles), Data & Pipelines (pipelines d'ingestion pour LLM).

Ne parle plus jamais à Qdrant directement : passe par le port VectorStore
(app/core/ports/vector_store.py) via app/core/storage_factory.py.

Semaine 5 de la roadmap: premier corpus = notes perso / docs génériques.

TODO semaine 5:
1. Charger les documents (dossier local, notes markdown, PDF...)
2. Chunker (stratégie récursive pour commencer)
3. Embedder avec Mistral Embed (ou le provider LLM actif s'il expose des
   embeddings — cf. app/core/llm/)
4. Indexer via get_vector_store().upsert(...)
"""
from app.core.storage_factory import get_vector_store

COLLECTION_NAME = "jarvis_knowledge"


def ingest_documents(paths: list[str]) -> int:
    """TODO semaine 5: parsing -> chunking -> embedding -> upsert.

    Retourne le nombre de chunks indexés.
    """
    get_vector_store()  # vérifie que le backend actif répond avant de commencer
    raise NotImplementedError("Pipeline d'ingestion à écrire semaine 5")

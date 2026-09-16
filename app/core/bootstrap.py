"""Point unique où chaque bloc optionnel tente de s'enregistrer dans le
registre de capacités, au démarrage (appelé depuis app/main.py).

Ajouter un nouveau bloc modulaire à Jarvis = ajouter une fonction
`_try_register_xxx()` ici, sur ce même modèle. Rien d'autre ne doit
changer ailleurs dans le code pour qu'il devienne découvrable.
"""
import structlog

from app.core.capabilities import registry

log = structlog.get_logger()


def bootstrap() -> None:
    _try_register_vision()
    _try_register_vector_store()
    _try_register_kv_store()
    log.info("bootstrap.done", capabilities=registry.available())


def _try_register_vision() -> None:
    try:
        from app.core.vision.camera import CameraCapability

        cam = CameraCapability()
        if cam.is_available():
            registry.register("vision", cam)
    except Exception as exc:  # noqa: BLE001 — un bloc absent/down ne doit jamais faire planter Jarvis
        log.warning("capability.unavailable", name="vision", reason=str(exc))


def _try_register_vector_store() -> None:
    try:
        from app.core.storage_factory import get_vector_store

        store = get_vector_store()
        if store.is_available():
            registry.register("rag", store)
    except Exception as exc:  # noqa: BLE001
        log.warning("capability.unavailable", name="rag", reason=str(exc))


def _try_register_kv_store() -> None:
    try:
        from app.core.storage_factory import get_kv_store

        store = get_kv_store()
        if store.is_available():
            registry.register("short_term_memory", store)
    except Exception as exc:  # noqa: BLE001
        log.warning("capability.unavailable", name="short_term_memory", reason=str(exc))

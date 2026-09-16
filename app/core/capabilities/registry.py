"""Registre central des capacités disponibles — le mécanisme qui rend
Jarvis vraiment modulaire (cf. app/core/ports/capability.py pour le
pourquoi). Rempli une fois au démarrage par app/core/bootstrap.py.

N'importe quel bloc peut demander `has("vision")` ou `get("vision")` sans
jamais importer app.core.vision — c'est ce découplage qui permet de
retirer un bloc sans casser les autres, et d'en ajouter un que les blocs
existants découvrent automatiquement.
"""
_capabilities: dict[str, object] = {}


def register(name: str, instance: object) -> None:
    _capabilities[name] = instance


def get(name: str) -> object | None:
    return _capabilities.get(name)


def has(name: str) -> bool:
    return name in _capabilities


def available() -> list[str]:
    return sorted(_capabilities)


def reset() -> None:
    """Utilisé par les tests — vide le registre entre deux cas."""
    _capabilities.clear()

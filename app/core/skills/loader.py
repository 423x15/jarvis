"""Charge le corps complet d'un skill à la demande.

Exposé comme outil (`load_skill`) dans app/core/tools/registry.py — c'est
l'agent lui-même qui décide, en voyant l'index de app/core/skills/registry.py,
qu'un skill est pertinent et qu'il faut en charger le mode d'emploi complet.
"""
from app.core.skills.registry import list_skills, split_frontmatter


def load_skill(name: str) -> str:
    for meta in list_skills():
        if meta.name == name:
            _, body = split_frontmatter(meta.path.read_text(encoding="utf-8"))
            return body
    raise ValueError(f"Skill inconnu: {name}. Utilise l'index du prompt système pour voir les skills disponibles.")


load_skill_schema = {
    "type": "function",
    "function": {
        "name": "load_skill",
        "description": "Charge les instructions complètes d'un skill précédemment appris, identifié par son nom.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Nom exact du skill (cf. index du prompt système)"}},
            "required": ["name"],
        },
    },
}

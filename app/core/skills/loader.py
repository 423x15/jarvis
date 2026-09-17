"""Charge / décharge le corps complet d'un skill à la demande.

Exposés comme outils (`load_skill`, `unload_skill`) dans
app/core/tools/registry.py — c'est l'agent lui-même qui décide, en voyant
l'index de app/core/skills/registry.py, qu'un skill est pertinent, puis
qu'il ne l'est plus. Le corps chargé vit dans AgentState.loaded_skills
(app/core/agent_state.py) — jamais renvoyé tel quel comme tool_result —
c'est ce qui permet à app.core.agent.build_system_prompt() de l'injecter
dans le prompt système tant qu'il est chargé, et de l'oublier dès que
`unload_skill` le retire de l'état.
"""
from app.core.agent_state import AgentState
from app.core.skills.registry import list_skills, split_frontmatter


def load_skill(name: str, state: AgentState) -> str:
    for meta in list_skills():
        if meta.name == name:
            _, body = split_frontmatter(meta.path.read_text(encoding="utf-8"))
            state.loaded_skills[name] = body
            return f"{name} chargé — son contenu complet est maintenant dans ton prompt système."
    raise ValueError(f"Skill inconnu: {name}. Utilise l'index du prompt système pour voir les skills disponibles.")


def unload_skill(name: str, state: AgentState) -> str:
    if state.loaded_skills.pop(name, None) is None:
        return f"{name} n'était pas chargé."
    return f"{name} déchargé — ne réapparaîtra plus dans ton prompt système tant que tu ne le recharges pas."


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

unload_skill_schema = {
    "type": "function",
    "function": {
        "name": "unload_skill",
        "description": (
            "Décharge un skill précédemment chargé, quand il n'est plus utile "
            "à la suite de la tâche en cours — libère du contexte."
        ),
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Nom exact du skill à décharger"}},
            "required": ["name"],
        },
    },
}

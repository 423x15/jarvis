"""Registre central des outils que Jarvis peut appeler.

Bloc catalogue technique: Agents IA — function calling / tool use,
Sécurité IA — guardrails (scopes de permission par outil).

Chaque outil déclare:
- un schéma JSON strict (validé par Pydantic dans son propre module)
- un scope de permission ("read", "write" ou "irreversible")
- une fonction d'exécution

La liste des outils n'est plus statique : `build_tools()` n'ajoute un outil
optionnel que si sa capacité est enregistrée (cf.
app/core/capabilities/registry.py) — c'est ce qui fait qu'ajouter ou
retirer un bloc (ex: la caméra) ne casse jamais l'agent, et que les outils
disponibles reflètent toujours l'environnement réel (conteneur sans
webcam, Qdrant down...).

Semaine 4: outils "métier" (draft_linkedin_post, read_personal_notes...).
Semaine 12: tout outil marqué "irreversible" doit passer par un
human-in-the-loop avant exécution (cf. app/core/agent.py).
Semaine 17: outils skills (load_skill, learn_skill).
Semaine 19: outil vision (look_at_workspace), conditionné à la capacité.
"""
from typing import Any

from app.core.capabilities import registry as capabilities
from app.core.skills.generator import learn_skill_schema, learn_skill_tool
from app.core.skills.loader import load_skill, load_skill_schema
from app.core.tools.web_search import web_search, web_search_schema
from app.core.vision.tool import look_at_workspace, look_at_workspace_schema

# Outils toujours présents, quel que soit l'environnement.
_CORE_EXECUTORS = {
    "web_search": web_search,
    "load_skill": load_skill,
    "learn_skill": learn_skill_tool,
}
_CORE_SCHEMAS = [web_search_schema, load_skill_schema, learn_skill_schema]

# Outils conditionnés à une capacité enregistrée: (nom_capacité, schéma, executor)
_OPTIONAL_TOOLS = [
    ("vision", look_at_workspace_schema, look_at_workspace),
]

# Scope de permission par outil — cf. Sécurité IA du catalogue technique.
# learn_skill n'est PAS irreversible : il n'écrit qu'un brouillon "-draft"
# qu'Alexis doit relire et renommer pour l'activer (cf. skills/generator.py).
_SCOPES = {
    "web_search": "read",
    "load_skill": "read",
    "learn_skill": "write",
    "look_at_workspace": "read",
}


def build_tools() -> tuple[list[dict], dict[str, Any]]:
    """Construit la liste de schémas + le dict d'executors pour l'environnement
    ACTUEL — appelé à chaque tour plutôt que figé au chargement du module,
    pour refléter une capacité qui apparaît/disparaît en cours de session.
    """
    schemas = list(_CORE_SCHEMAS)
    executors = dict(_CORE_EXECUTORS)
    for capability_name, schema, executor in _OPTIONAL_TOOLS:
        if capabilities.has(capability_name):
            schemas.append(schema)
            executors[schema["function"]["name"]] = executor
    return schemas, executors


def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    _, executors = build_tools()
    if name not in executors:
        raise ValueError(f"Outil inconnu ou capacité indisponible: {name}")
    if _SCOPES.get(name) == "irreversible":
        # TODO semaine 12: brancher ici la validation humaine (human-in-the-loop)
        raise PermissionError(f"L'outil {name} nécessite une validation humaine (non implémentée)")
    return executors[name](**arguments)

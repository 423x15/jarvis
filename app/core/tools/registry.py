"""Registre central des outils que Jarvis peut appeler.

Bloc catalogue technique: Agents IA — function calling / tool use,
Sécurité IA — guardrails (scopes de permission par outil).

Chaque outil déclare:
- un schéma JSON strict (validé par Pydantic dans son propre module)
- un scope de permission ("read", "write" ou "irreversible")
- une fonction d'exécution

La liste des outils n'est pas statique : `build_tools(state)` n'ajoute un
outil optionnel que si sa capacité est enregistrée (cf.
app/core/capabilities/registry.py) — c'est ce qui fait qu'ajouter ou
retirer un bloc (ex: la caméra) ne casse jamais l'agent.

Le garde-fou "irreversible" (_authorize ci-dessous) est la pièce la plus
sensible du fichier : un outil marqué ainsi n'est JAMAIS exécuté au
premier essai. Il ne peut être débloqué qu'entre deux messages HTTP
distincts (AgentState.human_replied_since_block, remis à True une seule
fois par tour de app.core.agent.run_agent, juste après réception d'un
VRAI message d'Alexis) — jamais par un tool_call du modèle lui-même, pour
qu'aucune suite de raisonnement ne puisse s'auto-approuver une action
irréversible sans qu'Alexis n'ait réellement répondu entre-temps.
"""
from typing import Any

from app.core.agent_state import AgentState, PendingConfirmation, fingerprint
from app.core.capabilities import registry as capabilities
from app.core.skills.generator import learn_skill_schema, learn_skill_tool
from app.core.skills.loader import load_skill, load_skill_schema, unload_skill, unload_skill_schema
from app.core.tools.ask_user import ask_user, ask_user_schema
from app.core.tools.think import think, think_schema
from app.core.tools.todo import (
    update_todo_schema,
    update_todo_tool,
    write_todo_schema,
    write_todo_tool,
)
from app.core.tools.web_search import web_search, web_search_schema
from app.core.vision.tool import look_at_workspace, look_at_workspace_schema

# Outils toujours présents, quel que soit l'environnement.
_CORE_SCHEMAS = [
    web_search_schema,
    think_schema,
    ask_user_schema,
    load_skill_schema,
    unload_skill_schema,
    learn_skill_schema,
    write_todo_schema,
    update_todo_schema,
]

# Outils conditionnés à une capacité enregistrée: (nom_capacité, schéma, executor)
_OPTIONAL_TOOLS = [
    ("vision", look_at_workspace_schema, look_at_workspace),
]

# Scope de permission par outil — cf. Sécurité IA du catalogue technique.
# learn_skill n'est PAS irreversible : il n'écrit qu'un brouillon "-draft"
# qu'Alexis doit relire et renommer pour l'activer (cf. skills/generator.py).
#
# Aucun outil "irreversible" n'est encore câblé dans ce starter (ce sera
# le premier vrai outil métier, ex: publish_linkedin_post, semaine 4+) —
# la ligne ci-dessous montre juste comment le déclarer le jour venu :
#   "publish_linkedin_post": "irreversible",
_SCOPES = {
    "web_search": "read",
    "think": "read",
    "ask_user": "read",
    "load_skill": "read",
    "unload_skill": "read",
    "learn_skill": "write",
    "write_todo": "write",
    "update_todo": "write",
    "look_at_workspace": "read",
}


def build_tools(state: AgentState) -> tuple[list[dict], dict[str, Any]]:
    """Construit la liste de schémas + le dict d'executors pour l'environnement
    ET l'état ACTUELS — appelé à chaque tour plutôt que figé au chargement du
    module, pour refléter une capacité qui apparaît/disparaît en cours de
    session ET l'état courant de l'agent (to-do, skills chargés).
    """
    schemas = list(_CORE_SCHEMAS)
    executors: dict[str, Any] = {
        "web_search": web_search,
        "think": think,
        "ask_user": ask_user,
        "load_skill": lambda name: load_skill(name, state),
        "unload_skill": lambda name: unload_skill(name, state),
        "learn_skill": learn_skill_tool,
        "write_todo": lambda items: write_todo_tool(state, items),
        "update_todo": lambda **kwargs: update_todo_tool(state, **kwargs),
    }
    for capability_name, schema, executor in _OPTIONAL_TOOLS:
        if capabilities.has(capability_name):
            schemas.append(schema)
            executors[schema["function"]["name"]] = executor
    return schemas, executors


def _authorize(name: str, arguments: dict[str, Any], state: AgentState) -> None:
    """Lève PermissionError si `name` est un outil irreversible non encore
    confirmé. Isolée de execute_tool() pour rester testable sans exécuter
    un vrai outil (cf. tests/test_tools_registry.py).
    """
    if _SCOPES.get(name) != "irreversible":
        return

    fp = fingerprint(name, arguments)
    pc = state.pending_confirmation
    already_approved = (
        pc is not None
        and pc.tool_name == name
        and pc.args_fingerprint == fp
        and state.human_replied_since_block
    )
    if already_approved:
        state.pending_confirmation = None
        return

    # Bloque, et mémorise PRÉCISÉMENT cette action pour ne débloquer que
    # celle-ci — jamais un blanc-seing sur tous les outils irreversibles.
    state.pending_confirmation = PendingConfirmation(tool_name=name, args_fingerprint=fp)
    state.human_replied_since_block = False
    raise PermissionError(
        f"L'outil {name} nécessite une validation humaine explicite avant de s'exécuter. "
        "Explique à Alexis ce que tu t'apprêtes à faire et pourquoi, puis arrête-toi — "
        "n'insiste pas dans ce même tour, même si tu es sûr de toi."
    )


def execute_tool(name: str, arguments: dict[str, Any], state: AgentState) -> Any:
    _, executors = build_tools(state)
    if name not in executors:
        raise ValueError(f"Outil inconnu ou capacité indisponible: {name}")
    _authorize(name, arguments, state)
    return executors[name](**arguments)

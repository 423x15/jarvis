"""État de l'agent — tout ce qui doit survivre d'un tour de boucle à
l'autre, ET d'un message HTTP au suivant.

Différence essentielle avec l'historique de conversation
(app/core/memory.py) : l'historique est un journal append-only des
événements (qui a dit/fait quoi). AgentState est un instantané de ce qui
est VRAI EN CE MOMENT (quels skills sont chargés, où en est la to-do, une
question ou une confirmation est-elle en attente) — c'est à partir de cet
état, pas de l'historique, que app.core.agent.build_system_prompt()
reconstruit le prompt système à chaque tour. C'est aussi ce qui permet de
DÉCHARGER un skill ou une info sans avoir à toucher à l'historique.

Persisté via le port KVStore (jamais gardé seulement en mémoire du
process) : un redémarrage de Jarvis ne doit pas perdre une to-do en cours
ou une question posée à Alexis.

Bloc catalogue technique: Agents IA — mémoire d'agent, human-in-the-loop.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field


@dataclass
class TodoItem:
    text: str
    done: bool = False


@dataclass
class TaskPlan:
    items: list[TodoItem] = field(default_factory=list)


@dataclass
class PendingConfirmation:
    """Une action irréversible a été bloquée en attendant qu'Alexis
    confirme. Ne peut être levée qu'entre deux messages HTTP distincts
    (cf. AgentState.human_replied_since_block) — jamais par le modèle
    lui-même dans le même tour. Voir app/core/tools/registry.py::_authorize.
    """
    tool_name: str
    args_fingerprint: str


@dataclass
class AgentState:
    loaded_skills: dict[str, str] = field(default_factory=dict)  # nom -> corps complet, évictable
    todo: TaskPlan | None = None
    pending_question: str | None = None  # ask_user en attente d'une réponse d'Alexis
    pending_confirmation: PendingConfirmation | None = None  # garde-fou "irreversible"
    human_replied_since_block: bool = False  # mis à True uniquement par run_agent(), jamais par un outil

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw: str | None) -> AgentState:
        if not raw:
            return cls()
        data = json.loads(raw)
        todo = None
        if data.get("todo"):
            todo = TaskPlan(items=[TodoItem(**item) for item in data["todo"]["items"]])
        pending_confirmation = None
        if data.get("pending_confirmation"):
            pending_confirmation = PendingConfirmation(**data["pending_confirmation"])
        return cls(
            loaded_skills=data.get("loaded_skills", {}),
            todo=todo,
            pending_question=data.get("pending_question"),
            pending_confirmation=pending_confirmation,
            human_replied_since_block=data.get("human_replied_since_block", False),
        )


def fingerprint(tool_name: str, arguments: dict) -> str:
    """Identifie une action précise (outil + arguments) pour vérifier que
    la confirmation humaine porte bien sur CETTE action-là, pas une autre.
    """
    payload = json.dumps({"tool": tool_name, "args": arguments}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

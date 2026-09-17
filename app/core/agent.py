"""Orchestrateur de l'agent Jarvis.

Bloc catalogue technique: Agents IA (function calling, orchestration, patterns
de raisonnement, mémoire, human-in-the-loop).

Ce fichier ne connaît AUCUN SDK de LLM ni de base de données : il parle à
app.core.llm.base.LLMProvider (via la factory) et à
app.core.tools.registry.build_tools(), qui lui-même ne construit la liste
d'outils qu'à partir de ce qui est réellement disponible (cf.
app/core/capabilities/registry.py). Retirer un bloc, changer de moteur, ou
tourner sans caméra ne touche jamais ce fichier.

## Le prompt système : statique + dynamique, reconstruit à CHAQUE tour

`build_system_prompt(state)` n'est jamais accumulée d'un tour sur l'autre —
elle est régénérée intégralement à chaque appel, à partir de deux choses :
une identité/des règles fixes, et `AgentState` (app/core/agent_state.py) qui
capture ce qui est vrai maintenant (skills chargés, to-do en cours). Ce qui
grossit réellement au fil d'une tâche longue, c'est `messages[]` — la liste
append-only des tool_calls/tool_results — jamais le prompt système lui-même.

## Trois façons de sortir de la boucle, pas une seule

1. Plus aucun tool_call dans la réponse -> le modèle a fini, on retourne
   sa réponse texte (condition normale).
2. MAX_HOPS atteint -> garde-fou anti-boucle-infinie, indépendant de ce
   que veut le modèle.
3. Le modèle appelle `ask_user` -> ni une fin, ni une boucle qui continue :
   une SUSPENSION. L'état (AgentState.pending_question) est persisté via
   le KVStore et la boucle rend la main. La reprise n'a rien de spécial :
   le prochain message HTTP pour cette session redéclenche run_agent()
   normalement, et la réponse d'Alexis rejoint l'historique comme
   n'importe quel autre tour de conversation.
"""
from app.core.agent_state import AgentState
from app.core.llm.base import Message
from app.core.llm.factory import get_provider
from app.core.memory import get_agent_state, get_short_term_history, save_agent_state, save_turn
from app.core.skills.registry import skills_index_prompt
from app.core.tools.ask_user import AskUserInterrupt
from app.core.tools.registry import build_tools, execute_tool

MAX_HOPS = 8  # garde-fou anti-boucle infinie — cf. condition d'arrêt n°2 ci-dessus

BASE_IDENTITY = """Tu es Jarvis, l'assistant IA personnel d'Alexis.
Tu agis de manière autonome : tu choisis toi-même quels outils utiliser, quels
skills charger ou décharger, et quand une tâche nécessite une to-do list
explicite (outil write_todo) plutôt qu'une réponse directe."""

RULES_BLOCK = """# RÈGLES
- Un outil marqué "irreversible" ne s'exécute jamais directement : une erreur
  te demandera d'expliquer ton intention à Alexis et de t'arrêter, plutôt que
  d'insister dans le même tour.
- N'invente jamais un chiffre ou une donnée : utilise un outil pour l'obtenir,
  ou dis explicitement que tu ne l'as pas.
- Utilise `think` pour réfléchir sans mettre fin à ton tour de parole ;
  utilise `ask_user` uniquement quand la question doit vraiment attendre une
  réponse d'Alexis avant de continuer.
- Décharge (`unload_skill`) un skill chargé dès qu'il ne sert plus à la suite
  de la tâche en cours.
- Réponds en français, direct, sans détour inutile."""


def build_system_prompt(state: AgentState) -> str:
    """Pure (aucun effet de bord) — reconstruite intégralement à chaque
    tour à partir de `state`. Rien ici n'est jamais concaténé à la version
    du tour précédent.
    """
    parts = [BASE_IDENTITY, "# SKILLS DISPONIBLES\n" + skills_index_prompt()]

    for skill_name, body in state.loaded_skills.items():
        parts.append(f"# SKILL CHARGÉ: {skill_name}\n{body}")

    if state.todo:
        todo_lines = "\n".join(f"[{'x' if it.done else ' '}] {it.text}" for it in state.todo.items)
        parts.append("# TA TO-DO ACTUELLE\n" + (todo_lines or "(vide)"))

    parts.append(RULES_BLOCK)
    return "\n\n".join(parts)


async def run_agent(message: str, session_id: str) -> str:
    """Point d'entrée unique de l'agent.

    TODO semaine 5: brancher get_long_term_context() (RAG) dans le prompt.
    TODO semaine 6+: migrer cette boucle manuelle vers LangGraph — les trois
    conditions d'arrêt documentées en tête de fichier deviendront des noeuds
    explicites plutôt que des branches dans une boucle Python.
    TODO: fidélité du tool-calling — on ne renvoie ici que le texte de
    chaque tool_result au provider, pas la structure native de son appel
    (ToolCall id/name/arguments). Suffisant pour les providers actuels du
    starter, mais à muscler si un provider exige strictement l'écho de
    l'appel d'origine dans l'historique.
    """
    state = get_agent_state(session_id)
    state.pending_question = None  # ce message, s'il répond à un ask_user, referme la question posée
    state.human_replied_since_block = True  # un VRAI message HTTP vient d'arriver — cf. tools/registry.py::_authorize

    provider = get_provider()
    history = get_short_term_history(session_id)
    messages = [
        *[Message(role=h["role"], content=h["content"]) for h in history],
        Message(role="user", content=message),
    ]

    hops = 0
    result = None
    while True:
        tools, _ = build_tools(state)
        system_prompt = build_system_prompt(state)
        result = provider.chat(
            [Message(role="system", content=system_prompt), *messages],
            tools=tools if provider.supports_tools else None,
        )

        if not result.tool_calls:
            break  # condition d'arrêt n°1 : réponse finale

        if hops >= MAX_HOPS:
            if not result.content:
                result.content = (
                    "J'ai atteint ma limite de tours sur cette tâche — voici où j'en suis, "
                    "dis-moi comment tu veux que je continue."
                )
            break  # condition d'arrêt n°2 : garde-fou anti-boucle infinie

        try:
            for call in result.tool_calls:
                tool_result = execute_tool(call.name, call.arguments, state)
                messages.append(
                    Message(role="tool", content=str(tool_result), tool_call_id=call.id, name=call.name)
                )
        except AskUserInterrupt as interrupt:
            # condition d'arrêt n°3 : SUSPENSION, pas une fin — cf. docstring de module.
            state.pending_question = interrupt.question
            save_agent_state(session_id, state)
            save_turn(session_id, message, interrupt.question)
            return interrupt.question
        except PermissionError as guardrail:
            # Le garde-fou a bloqué un outil : ce n'est pas fatal — le modèle
            # voit l'erreur comme un tool_result normal et réagit au tour
            # suivant (typiquement : explique et demande confirmation en texte,
            # ce qui redevient la condition d'arrêt n°1 naturellement).
            messages.append(
                Message(role="tool", content=str(guardrail), tool_call_id=call.id, name=call.name)
            )

        hops += 1

    reply = result.content
    save_agent_state(session_id, state)
    save_turn(session_id, message, reply)
    return reply

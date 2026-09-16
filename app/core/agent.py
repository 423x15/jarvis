"""Orchestrateur de l'agent Jarvis.

Bloc catalogue technique: Agents IA (function calling, orchestration, patterns
de raisonnement, mémoire, human-in-the-loop).

Semaine 3: ReAct minimal À LA MAIN (boucle ci-dessous). Semaine 4: migrer
vers un vrai graphe LangGraph dont les nœuds seront ceux déjà esquissés
dans app/core/kernel/pipeline.py (analyze_intent -> route -> plan_todo ->
act -> respond) — c'est pour ça qu'ils sont appelés dès maintenant, même
sous forme de stubs : le rewrite semaine 4 change l'implémentation de
chaque étape, pas la structure.

Ce fichier ne connaît AUCUN SDK de LLM ni de base de données : il parle à
app.core.llm.base.LLMProvider (via la factory) et à
app.core.tools.registry.build_tools(), qui lui-même ne construit la liste
d'outils qu'à partir de ce qui est réellement disponible (cf.
app/core/capabilities/registry.py). Retirer un bloc, changer de moteur, ou
tourner sans caméra ne touche jamais ce fichier.
"""
from app.core.kernel.pipeline import analyze_intent, route
from app.core.llm.base import Message
from app.core.llm.factory import get_provider
from app.core.memory import get_short_term_history, save_turn
from app.core.skills.registry import skills_index_prompt
from app.core.tools.registry import build_tools, execute_tool

BASE_SYSTEM_PROMPT = """Tu es Jarvis, l'assistant IA personnel d'Alexis.
Tu as accès à des outils. Utilise-les quand c'est utile plutôt que d'inventer une réponse.

Tu as aussi accès à des "skills" : des procédures qu'Alexis t'a apprises. Leur
liste (nom + description) est donnée ci-dessous. Si une tâche correspond à
l'une d'elles, appelle l'outil `load_skill` pour en charger le mode d'emploi
complet avant d'agir, plutôt que d'improviser.

{skills_index}
"""


async def run_agent(message: str, session_id: str) -> str:
    """Point d'entrée unique de l'agent.

    TODO semaine 5: brancher get_long_term_context() (RAG) dans le prompt.
    TODO semaine 6+: quand plan_todo() est implémenté, exécuter la checklist
    étape par étape plutôt que la boucle ReAct plate ci-dessous.
    TODO semaine 12: ajouter un human-in-the-loop avant tout outil marqué "irréversible".
    """
    # Étapes du noyau — stubs aujourd'hui, vrais nœuds LangGraph semaine 4.
    intent = analyze_intent(message)
    route(intent)  # ignoré pour l'instant: un seul chemin (ReAct générique)

    provider = get_provider()  # <- seul endroit où le moteur actif est choisi
    tools, _ = build_tools()  # <- reflète les capacités réellement dispo
    history = get_short_term_history(session_id)

    system_prompt = BASE_SYSTEM_PROMPT.format(skills_index=skills_index_prompt())
    messages = [
        Message(role="system", content=system_prompt),
        *[Message(role=h["role"], content=h["content"]) for h in history],
        Message(role="user", content=message),
    ]

    result = provider.chat(messages, tools=tools if provider.supports_tools else None)

    # Squelette de boucle d'appel d'outil — à muscler semaine 3/4.
    max_hops = 4  # évite une boucle infinie si le modèle s'entête à appeler des outils
    hops = 0
    while result.tool_calls and hops < max_hops:
        for call in result.tool_calls:
            tool_result = execute_tool(call.name, call.arguments)
            messages.append(
                Message(role="tool", content=str(tool_result), tool_call_id=call.id, name=call.name)
            )
        result = provider.chat(messages, tools=tools if provider.supports_tools else None)
        hops += 1

    reply = result.content
    save_turn(session_id, message, reply)
    return reply

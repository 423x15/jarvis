"""Le noyau de Jarvis — les étapes explicites par lesquelles passe chaque
requête. Chaque fonction est un nœud indépendant, pensé pour devenir un
nœud LangGraph semaine 4 (StateGraph : analyze_intent -> route ->
load_skills -> plan_todo -> act -> respond) sans changer sa signature.

Aujourd'hui (semaine 1-3) ce sont des stubs volontairement simples — la
boucle ReAct manuelle de app/core/agent.py les appelle déjà dans le bon
ordre, ce qui évite un rewrite quand LangGraph arrive semaine 4.

Bloc catalogue technique: Agents IA — patterns de raisonnement,
orchestration.
"""
from dataclasses import dataclass, field


@dataclass
class Intent:
    """Résultat de l'analyse du besoin — semaine 4: à produire via un appel
    LLM structuré (function calling avec un schéma "classify_intent") plutôt
    qu'à deviner.
    """
    raw_message: str
    category: str = "unclassified"  # ex: "question", "tache_multi_etapes", "action_physique"
    requires_todo: bool = False


@dataclass
class TodoItem:
    description: str
    done: bool = False


@dataclass
class TaskPlan:
    items: list[TodoItem] = field(default_factory=list)


def analyze_intent(message: str) -> Intent:
    """TODO semaine 4: classifier le message (question simple / tâche
    multi-étapes / action nécessitant la caméra...) pour orienter le routing.
    Stub actuel: tout passe par le même chemin (ReAct générique).
    """
    return Intent(raw_message=message)


def route(intent: Intent) -> str:
    """TODO semaine 4: décider quel(s) skill(s)/outil(s) privilégier selon
    l'intent. Stub actuel: route toujours vers la boucle ReAct générale.
    """
    return "react_loop"


def plan_todo(intent: Intent) -> TaskPlan | None:
    """Pour une tâche identifiée comme multi-étapes, produit une checklist
    explicite AVANT d'agir — pour rester pilotable et reprenable en cas
    d'interruption, plutôt qu'un enchaînement d'outils opaque.

    TODO semaine 6+ (une fois le premier vrai cas multi-étapes rencontré,
    ex: "prépare ma candidature Mistral" -> plusieurs sous-tâches).
    """
    if not intent.requires_todo:
        return None
    raise NotImplementedError("Planification de tâche à écrire — cf. TODO ci-dessus")

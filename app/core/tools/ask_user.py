"""Outil `ask_user` — le seul qui INTERROMPT la boucle plutôt que de la
nourrir.

Tout autre outil renvoie un résultat qu'on peut obtenir de façon
synchrone (même `learn_skill`, qui écrit juste un fichier). `ask_user`
est différent : sa "valeur de retour" n'existe pas tant qu'Alexis n'a pas
répondu, et cette réponse peut arriver dans 30 secondes comme dans 3
heures. Le faire attendre dans ce process (un `await` bloquant) tiendrait
une ressource pour une durée arbitraire et ne survivrait pas à un
redémarrage de Jarvis.

Le choix retenu : `ask_user` ne renvoie jamais de résultat. Il lève
AskUserInterrupt, qu'app/core/agent.py::run_agent attrape spécifiquement
pour suspendre la boucle et PERSISTER l'état (AgentState.pending_question,
via le KVStore) — la reprise n'a lieu ni dans ce process ni dans ce tour,
mais au prochain message HTTP reçu pour cette session, comme une
conversation tout à fait normale.
"""


class AskUserInterrupt(Exception):
    def __init__(self, question: str):
        self.question = question
        super().__init__(question)


def ask_user(question: str) -> str:
    raise AskUserInterrupt(question)


ask_user_schema = {
    "type": "function",
    "function": {
        "name": "ask_user",
        "description": (
            "Pose une question à Alexis quand une information te manque ou "
            "qu'un choix lui revient, et suspend ton exécution jusqu'à sa "
            "réponse. N'appelle JAMAIS cet outil pour demander la confirmation "
            "d'une action irréversible : ce garde-fou est automatique, inutile "
            "de le déclencher toi-même."
        ),
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
        },
    },
}

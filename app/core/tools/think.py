"""Outil `think` — un espace de raisonnement structuré, sans aucun effet
sur le monde extérieur.

Pourquoi c'est un outil et pas juste du texte libre : la boucle de
app/core/agent.py s'arrête dès qu'un tour ne contient plus aucun
tool_call (c'est la condition d'arrêt normale — "le modèle a fini"). Un
tour 100% texte est donc interprété comme la réponse finale, même si le
modèle voulait seulement dire "attends, laisse-moi réfléchir" avant de
continuer. `think` compte comme un tool_call ordinaire aux yeux de la
boucle : elle continue, sans qu'aucun code spécial n'ait été nécessaire.
"""

think_schema = {
    "type": "function",
    "function": {
        "name": "think",
        "description": (
            "Réfléchis avant d'agir : reformule ce que tu sais, ce qui manque, "
            "ta prochaine étape. N'a aucun effet sur le monde extérieur — sert "
            "uniquement à structurer ton raisonnement sans mettre fin à ton tour "
            "de parole (contrairement à une réponse texte sans outil)."
        ),
        "parameters": {
            "type": "object",
            "properties": {"thought": {"type": "string"}},
            "required": ["thought"],
        },
    },
}


def think(thought: str) -> str:
    return "Noté."

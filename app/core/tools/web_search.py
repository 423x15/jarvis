"""Premier outil de Jarvis: recherche web.

Volontairement le plus simple possible — sert de référence pour écrire
les outils suivants (semaine 4 de la roadmap).
"""

web_search_schema = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Recherche des informations récentes sur le web.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "La requête de recherche"},
            },
            "required": ["query"],
        },
    },
}


def web_search(query: str) -> str:
    """TODO: brancher une vraie API de recherche (ex: Tavily, Brave Search, SerpAPI)."""
    raise NotImplementedError("Brancher une API de recherche web réelle — semaine 4")

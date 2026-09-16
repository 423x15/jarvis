"""Outil `look_at_workspace` — permet à l'agent de "voir" ce qu'Alexis a
sous les yeux sur un projet physique.

Ne fait AUCUNE hypothèse sur la présence d'une caméra : passe par le
registre de capacités (app/core/capabilities/registry.py). Cet outil n'est
même pas ajouté à TOOLS si "vision" n'est pas enregistrée — cf.
app/core/tools/registry.py::build_tools().

Nécessite aussi un provider LLM avec `supports_vision=True`.
"""
from app.core.capabilities import registry
from app.core.llm.base import ImageBlock, Message, TextBlock
from app.core.llm.factory import get_provider

look_at_workspace_schema = {
    "type": "function",
    "function": {
        "name": "look_at_workspace",
        "description": "Prend une photo via la webcam et décrit ce qu'elle montre — utile pour un projet physique en cours.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Ce qu'il faut chercher à observer précisément (optionnel)",
                }
            },
        },
    },
}


def look_at_workspace(question: str = "") -> str:
    camera = registry.get("vision")
    if camera is None:
        return "Aucune caméra disponible pour l'instant (capacité 'vision' non enregistrée)."

    provider = get_provider()
    if not provider.supports_vision:
        return (
            f"Le moteur actif ({provider.name}) ne supporte pas la vision. "
            "Passe JARVIS_LLM_PROVIDER sur mistral, anthropic, openai, "
            "ou un modèle Ollama vision (llava, qwen2.5vl)."
        )

    frame_b64 = camera.capture_frame_base64()
    prompt = question or "Décris précisément ce que montre cette image, dans le contexte d'un projet en cours."
    result = provider.chat([
        Message(role="user", content=[TextBlock(text=prompt), ImageBlock(data_base64=frame_b64)])
    ])
    return result.content

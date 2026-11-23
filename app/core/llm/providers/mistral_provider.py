"""Adapter Mistral — moteur par défaut de Jarvis.

Traduit l'interface commune (app/core/llm/base.py) vers le SDK `mistralai`.
"""
from mistralai.client import (
    Mistral,  # cf. mistralai>=2.10 : le client a été déplacé sous mistralai.client
)

from app.core.llm.base import ChatResult, LLMProvider, Message, TextBlock, ToolCall


class MistralProvider(LLMProvider):
    name = "mistral"
    supports_tools = True
    supports_vision = True  # pixtral-large-latest

    def __init__(self, api_key: str, model: str = "mistral-large-latest") -> None:
        self._client = Mistral(api_key=api_key)
        self._model = model

    def chat(self, messages: list[Message], tools: list[dict] | None = None) -> ChatResult:
        payload = [_to_mistral_message(m) for m in messages]
        response = self._client.chat.complete(model=self._model, messages=payload, tools=tools)
        choice = response.choices[0].message
        tool_calls = [
            ToolCall(id=c.id, name=c.function.name, arguments=c.function.arguments)
            for c in (choice.tool_calls or [])
        ]
        return ChatResult(content=choice.content or "", tool_calls=tool_calls, raw=response)


def _to_mistral_message(m: Message) -> dict:
    if isinstance(m.content, str):
        content = m.content
    else:
        # TODO: brancher le format multimodal Pixtral (image_url) quand le
        # module vision (semaine 19) a besoin d'envoyer une image à Mistral.
        content = "".join(b.text for b in m.content if isinstance(b, TextBlock))
    msg: dict = {"role": m.role, "content": content}
    if m.role == "tool":
        msg["tool_call_id"] = m.tool_call_id
        msg["name"] = m.name
    return msg

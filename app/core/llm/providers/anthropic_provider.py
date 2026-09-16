"""Adapter Claude (Anthropic) — pour comparer les moteurs, ou l'utiliser en
secours si l'API Mistral est indisponible.
"""
from anthropic import Anthropic

from app.core.llm.base import ChatResult, ImageBlock, LLMProvider, Message, TextBlock, ToolCall


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    supports_tools = True
    supports_vision = True

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5") -> None:
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def chat(self, messages: list[Message], tools: list[dict] | None = None) -> ChatResult:
        system = "\n".join(m.content for m in messages if m.role == "system" and isinstance(m.content, str))
        payload = [_to_anthropic_message(m) for m in messages if m.role != "system"]
        response = self._client.messages.create(
            model=self._model,
            system=system,
            messages=payload,
            tools=_to_anthropic_tools(tools) if tools else [],
            max_tokens=2048,
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        tool_calls = [
            ToolCall(id=b.id, name=b.name, arguments=b.input)
            for b in response.content if b.type == "tool_use"
        ]
        return ChatResult(content=text, tool_calls=tool_calls, raw=response)


def _to_anthropic_message(m: Message) -> dict:
    if isinstance(m.content, str):
        return {"role": m.role, "content": m.content}
    blocks = []
    for b in m.content:
        if isinstance(b, TextBlock):
            blocks.append({"type": "text", "text": b.text})
        elif isinstance(b, ImageBlock):
            blocks.append({
                "type": "image",
                "source": {"type": "base64", "media_type": b.media_type, "data": b.data_base64},
            })
    return {"role": m.role, "content": blocks}


def _to_anthropic_tools(tools: list[dict]) -> list[dict]:
    """Les deux formats suivent JSON Schema mais avec des clés différentes —
    on traduit ici plutôt que de dupliquer la définition des outils.
    """
    out = []
    for t in tools:
        fn = t["function"]
        out.append({"name": fn["name"], "description": fn["description"], "input_schema": fn["parameters"]})
    return out

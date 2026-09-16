"""Adapter OpenAI — et, par construction, tout serveur qui expose une API
compatible OpenAI (`/v1/chat/completions`). C'est ce qui permet à Jarvis de
tourner en local sans rien changer au code : Ollama, LM Studio, vLLM en mode
serveur exposent tous ce même contrat.

Bloc catalogue technique: Infra & Déploiement (inférence LLM optimisée) —
c'est cet adapter qui rend Jarvis déployable dans un environnement restreint
avec un modèle local (cf. OllamaProvider ci-dessous, qui n'est qu'une
configuration différente de cette même classe).
"""
from openai import OpenAI

from app.core.llm.base import ChatResult, ImageBlock, LLMProvider, Message, TextBlock, ToolCall


class OpenAICompatibleProvider(LLMProvider):
    """Fonctionne avec l'API OpenAI (base_url par défaut) ou tout serveur
    OpenAI-compatible en passant un `base_url` custom (Ollama, LM Studio, vLLM…).
    """

    supports_tools = True

    def __init__(
        self,
        api_key: str = "not-needed-for-local-servers",
        model: str = "gpt-4o",
        base_url: str | None = None,
        name: str = "openai",
        supports_vision: bool = True,
    ) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self.name = name
        self.supports_vision = supports_vision

    def chat(self, messages: list[Message], tools: list[dict] | None = None) -> ChatResult:
        payload = [_to_openai_message(m) for m in messages]
        response = self._client.chat.completions.create(
            model=self._model, messages=payload, tools=tools or None
        )
        choice = response.choices[0].message
        tool_calls = [
            ToolCall(id=c.id, name=c.function.name, arguments=c.function.arguments)
            for c in (choice.tool_calls or [])
        ]
        return ChatResult(content=choice.content or "", tool_calls=tool_calls, raw=response)


def _to_openai_message(m: Message) -> dict:
    if isinstance(m.content, str):
        content: str | list[dict] = m.content
    else:
        parts = []
        for b in m.content:
            if isinstance(b, TextBlock):
                parts.append({"type": "text", "text": b.text})
            elif isinstance(b, ImageBlock):
                parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{b.media_type};base64,{b.data_base64}"},
                })
        content = parts
    msg: dict = {"role": m.role, "content": content}
    if m.role == "tool":
        msg["tool_call_id"] = m.tool_call_id
    return msg

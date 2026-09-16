"""Interface commune à tous les fournisseurs de LLM.

C'est LE fichier qui fait la force de Jarvis : le reste du code (agent,
outils, mémoire) ne parle jamais à Mistral, Claude, OpenAI ou Ollama
directement — il parle à cette interface. Changer de moteur = changer
une ligne de config, jamais une ligne d'app/core/agent.py.

Bloc catalogue technique: Architecture logicielle & système (patterns
d'architecture — ici, un port/adapter classique).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ImageBlock:
    """Image encodée en base64 (jpeg/png) — utilisée par le module vision."""
    data_base64: str
    media_type: str = "image/jpeg"


@dataclass
class TextBlock:
    text: str


ContentBlock = TextBlock | ImageBlock


@dataclass
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[ContentBlock]
    tool_call_id: str | None = None  # rempli pour role="tool"
    name: str | None = None  # nom de l'outil pour role="tool"


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ChatResult:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None  # réponse brute du SDK, utile pour debug/observabilité


class LLMProvider(ABC):
    """Port que chaque fournisseur (Mistral, Claude, OpenAI, Ollama...) implémente."""

    name: str = "base"
    supports_tools: bool = True
    supports_vision: bool = False

    @abstractmethod
    def chat(self, messages: list[Message], tools: list[dict] | None = None) -> ChatResult:
        """Envoie une conversation au modèle et retourne sa réponse normalisée.

        `tools` suit le format JSON Schema "function calling" popularisé par
        OpenAI et repris par Mistral/Anthropic — chaque adapter le traduit
        dans le format natif de son SDK.
        """
        raise NotImplementedError

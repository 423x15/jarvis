"""Point d'entrée unique pour obtenir un provider LLM.

Change de moteur = changer JARVIS_LLM_PROVIDER dans .env, rien d'autre.
C'est ce qui permet à Jarvis de tourner avec Claude, OpenAI, Mistral, ou
un modèle local via Ollama — au prix de cette (petite) couche d'adaptation.
"""
from functools import lru_cache

from app.config import settings
from app.core.llm.base import LLMProvider
from app.core.llm.providers.anthropic_provider import AnthropicProvider
from app.core.llm.providers.mistral_provider import MistralProvider
from app.core.llm.providers.openai_compatible_provider import OpenAICompatibleProvider


@lru_cache(maxsize=1)
def get_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()

    if provider == "mistral":
        return MistralProvider(api_key=settings.mistral_api_key)

    if provider == "anthropic":
        return AnthropicProvider(api_key=settings.anthropic_api_key)

    if provider == "openai":
        return OpenAICompatibleProvider(api_key=settings.openai_api_key, model=settings.openai_model)

    if provider == "ollama":
        # Ollama expose une API compatible OpenAI sur /v1 depuis 2024 —
        # même classe adapter, juste une base_url et une clé factices.
        return OpenAICompatibleProvider(
            api_key="ollama",
            model=settings.ollama_model,
            base_url=f"{settings.ollama_host}/v1",
            name="ollama",
            supports_vision=settings.ollama_model in {"llava", "qwen2.5vl", "llama3.2-vision"},
        )

    raise ValueError(
        f"JARVIS_LLM_PROVIDER='{provider}' inconnu. "
        "Valeurs supportées: mistral, anthropic, openai, ollama."
    )

"""Configuration centrale — chargée depuis les variables d'environnement (.env).

Bloc catalogue technique: Architecture logicielle & système.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Moteur LLM actif — voir app/core/llm/factory.py. C'est LE réglage qui
    # fait de Jarvis un projet "orchestration pure", indépendant du modèle.
    llm_provider: str = "mistral"  # mistral | anthropic | openai | ollama

    mistral_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Fournisseurs de stockage — voir app/core/storage_factory.py. Même
    # principe que llm_provider: changer de base de données = un nouvel
    # adapter dans app/core/adapters/, jamais un changement dans memory.py
    # ou app/rag/.
    kv_store_provider: str = "redis"
    vector_store_provider: str = "qdrant"

    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://localhost:6379/0"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    skills_dir: str = "skills"

    jarvis_env: str = "dev"
    log_level: str = "INFO"


settings = Settings()

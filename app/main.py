"""Point d'entrée FastAPI de Jarvis.

Semaine 2 de la roadmap: /health + CI.
Bloc catalogue technique: Architecture logicielle & système (design d'API),
Monitoring & Observabilité (logging structuré, à activer ici en premier).
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.core.bootstrap import bootstrap
from app.core.capabilities import registry as capabilities

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap()  # enregistre les blocs optionnels (vision, rag, mémoire...) réellement disponibles
    log.info("jarvis.startup", env=settings.jarvis_env, capabilities=capabilities.available())
    yield


app = FastAPI(
    title="Jarvis",
    description="Assistant IA personnel — projet phare de stage Mistral AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "env": settings.jarvis_env, "capabilities": capabilities.available()}

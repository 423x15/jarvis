"""Endpoints HTTP exposés par Jarvis.

Domain: Architecture logicielle & système (design d'API).
TODO semaine 9: ajouter le streaming SSE pour /chat (Performance & Scalabilité — latence).
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.agent import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Point d'entrée conversationnel unique. Toute la logique vit dans core/agent.py."""
    reply = await run_agent(message=payload.message, session_id=payload.session_id)
    return ChatResponse(reply=reply)

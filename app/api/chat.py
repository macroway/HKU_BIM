from fastapi import APIRouter, HTTPException

from app.agent.loop import run_agent_loop
from app.api.schemas import ChatRequest, ChatResponse
from app.models.store import get_model

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    try:
        get_model(body.model_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = run_agent_loop(body.model_id, body.message)
    return ChatResponse(**result)

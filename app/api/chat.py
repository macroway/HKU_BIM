from fastapi import APIRouter, HTTPException

from app.agent.loop import run_agent_loop
from app.api.schemas import ChatRequest, ChatResponse
from app.config import ARK_MODEL, CHECKBIM_OFFLINE, OPENAI_MODEL, llm_available, resolve_llm_provider
from app.models.store import get_model

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/llm/status")
def llm_status():
    provider = resolve_llm_provider()
    model = ARK_MODEL if provider == "ark" else (OPENAI_MODEL if provider == "openai" else None)
    return {
        "offline_mode": CHECKBIM_OFFLINE,
        "available": llm_available(),
        "provider": provider,
        "model": model,
        "planner_label": "doubao" if provider == "ark" else ("llm" if provider == "openai" else "rules"),
    }


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    try:
        get_model(body.model_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = run_agent_loop(body.model_id, body.message)
    return ChatResponse(**result)

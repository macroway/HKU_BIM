from typing import Any

import httpx

from app.agent.ark_client import ark_responses_create
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, resolve_llm_provider


def chat_with_tools(messages: list[dict[str, Any]], tools: list[dict] | None = None) -> dict:
    provider = resolve_llm_provider()
    if provider == "ark":
        return ark_responses_create(messages, tools=tools)
    if provider == "openai":
        return _openai_chat_with_tools(messages, tools=tools)
    raise RuntimeError("No LLM provider configured (set ARK_API_KEY or OPENAI_API_KEY, or disable CHECKBIM_OFFLINE)")


def _openai_chat_with_tools(messages: list[dict[str, Any]], tools: list[dict] | None = None) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")

    base = (OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    payload: dict[str, Any] = {
        "model": OPENAI_MODEL,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json=payload,
        )
        response.raise_for_status()
        return response.json()

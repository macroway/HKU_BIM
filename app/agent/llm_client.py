import json
from typing import Any

import httpx

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from app.tools.registry import get_openai_tools_schema


def chat_with_tools(messages: list[dict[str, Any]], tools: list[dict] | None = None) -> dict:
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

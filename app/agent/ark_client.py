"""Volcengine Ark Responses API client (Doubao)."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import ARK_API_KEY, ARK_BASE_URL, ARK_MODEL

# Volcengine tool schema rejects some JSON Schema keywords
_STRIP_TOOL_KEYS = frozenset(
    {"minLength", "maxLength", "minItems", "maxItems", "minContains", "maxContains", "additionalProperties"}
)


def _clean_schema(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _clean_schema(v) for k, v in obj.items() if k not in _STRIP_TOOL_KEYS}
    if isinstance(obj, list):
        return [_clean_schema(x) for x in obj]
    return obj


def convert_tools_for_ark_responses(tools: list[dict] | None) -> list[dict] | None:
    """OpenAI chat tools → Ark Responses flat FunctionTool (no nested `function` key)."""
    if not tools:
        return tools

    converted: list[dict] = []
    for tool in tools:
        if tool.get("type") != "function":
            continue
        if "function" in tool:
            fn = tool["function"]
            converted.append(
                {
                    "type": "function",
                    "name": fn.get("name", ""),
                    "description": fn.get("description", ""),
                    "parameters": _clean_schema(fn.get("parameters") or {"type": "object", "properties": {}}),
                }
            )
        elif "name" in tool:
            converted.append(_clean_schema(tool))
    return converted


def sanitize_tools_for_ark(tools: list[dict] | None) -> list[dict] | None:
    """Alias kept for tests — Responses API uses flat tool schema."""
    return convert_tools_for_ark_responses(tools)


def messages_to_ark_payload(messages: list[dict[str, Any]]) -> tuple[str | None, list[dict[str, Any]]]:
    """Map OpenAI-style messages → Ark Responses `instructions` + `input`."""
    instructions: str | None = None
    input_items: list[dict[str, Any]] = []

    for msg in messages:
        role = msg.get("role")
        if role == "system":
            instructions = msg.get("content") or instructions
            continue

        if role == "user":
            input_items.append(
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": msg.get("content") or ""}],
                }
            )
            continue

        if role == "assistant":
            if msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    fn = call.get("function") or {}
                    input_items.append(
                        {
                            "type": "function_call",
                            "call_id": call.get("id") or call.get("call_id") or "call_unknown",
                            "name": fn.get("name", ""),
                            "arguments": fn.get("arguments") or "{}",
                        }
                    )
            content = msg.get("content")
            if content:
                input_items.append(
                    {
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": content}],
                    }
                )
            continue

        if role == "tool":
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": msg.get("tool_call_id") or msg.get("call_id") or "",
                    "output": msg.get("content") or "",
                }
            )

    return instructions, input_items


def normalize_ark_response(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize Ark /responses body to OpenAI chat.completion-like shape for agent loop."""
    if data.get("choices"):
        return data

    message: dict[str, Any] = {"role": "assistant", "content": None}
    tool_calls: list[dict[str, Any]] = []
    text_parts: list[str] = []

    outputs = data.get("output") or []
    if isinstance(outputs, dict):
        outputs = [outputs]

    for item in outputs:
        itype = item.get("type") or ""
        if itype == "function_call":
            tool_calls.append(
                {
                    "id": item.get("call_id") or item.get("id") or f"call_{len(tool_calls)}",
                    "type": "function",
                    "function": {
                        "name": item.get("name", ""),
                        "arguments": item.get("arguments") or "{}",
                    },
                }
            )
        elif itype == "message":
            content = item.get("content") or []
            if isinstance(content, str):
                text_parts.append(content)
            else:
                for block in content:
                    if block.get("type") in ("output_text", "text"):
                        text_parts.append(block.get("text") or "")
        elif itype in ("output_text", "text"):
            text_parts.append(item.get("text") or item.get("content") or "")

    if tool_calls:
        message["tool_calls"] = tool_calls
    if text_parts:
        message["content"] = "\n".join(text_parts).strip()

    return {"choices": [{"message": message}]}


def ark_responses_create(
    messages: list[dict[str, Any]],
    tools: list[dict] | None = None,
) -> dict[str, Any]:
    if not ARK_API_KEY:
        raise RuntimeError("ARK_API_KEY not configured")

    instructions, input_items = messages_to_ark_payload(messages)
    payload: dict[str, Any] = {
        "model": ARK_MODEL,
        "input": input_items,
    }
    if instructions:
        payload["instructions"] = instructions
    if tools:
        payload["tools"] = convert_tools_for_ark_responses(tools)
        payload["tool_choice"] = "auto"

    with httpx.Client(timeout=90.0) as client:
        response = client.post(
            f"{ARK_BASE_URL}/responses",
            headers={
                "Authorization": f"Bearer {ARK_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if response.status_code >= 400:
            detail = response.text[:500]
            raise RuntimeError(f"Ark Responses API error {response.status_code}: {detail}")
        return normalize_ark_response(response.json())

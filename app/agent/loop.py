import json
import logging
from typing import Any

from app.agent.llm_client import chat_with_tools
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.router_fallback import is_gibberish, plan_tools_from_message
from app.config import CHECKBIM_OFFLINE, llm_available, planner_label, resolve_llm_provider
from app.tools.registry import execute_tool, get_openai_tools_schema

MAX_STEPS = 5
logger = logging.getLogger(__name__)

UNCLEAR_INTENT_REPLY = (
    "我还不确定你的检查意图。请说明例如：「帮我查碰撞」「查属性完整性」或「两个都查」。"
)


def _summarize_offline(message: str, tool_traces: list[dict], results: dict) -> str:
    if not tool_traces:
        return UNCLEAR_INTENT_REPLY
    parts: list[str] = []
    if "collision" in results:
        count = len(results["collision"].get("pairs", []))
        parts.append(f"碰撞检测完成：发现 {count} 对冲突。")
    if "attributes" in results:
        count = len(results["attributes"].get("missing", []))
        parts.append(f"属性检查完成：缺失项 {count} 条。")
    if "model_info" in results:
        info = results["model_info"]
        parts.append(f"模型共 {info['element_count']} 个构件。")
    if not parts:
        return "尚未执行检查工具，无法给出检查结论。请说明要查碰撞还是属性。"
    return " ".join(parts)


def _unclear_intent_response(planner: str) -> dict:
    return {
        "reply": UNCLEAR_INTENT_REPLY,
        "tool_traces": [],
        "results": {},
        "did_run_tools": False,
        "planner": planner,
    }


def _guard_reply(reply: str, did_run_tools: bool) -> str:
    if did_run_tools:
        return reply
    unsafe = ("通过", "无碰撞", "没有冲突", "检查完成", "一切正常")
    if any(word in reply for word in unsafe):
        return UNCLEAR_INTENT_REPLY
    lower = reply.lower()
    fake_report_markers = (
        "ifcwall",
        "ifcbeam",
        "ifcpipe",
        "碰撞对",
        "检查结果",
        "aabb_v1",
        "碰撞检测",
        "属性检查",
        "汇总",
    )
    if any(m in reply or m in lower for m in fake_report_markers):
        return UNCLEAR_INTENT_REPLY
    if len(reply.strip()) > 100 and ("###" in reply or "**" in reply):
        return UNCLEAR_INTENT_REPLY
    return reply or UNCLEAR_INTENT_REPLY


def run_agent_loop(model_id: str, message: str, *, force_offline: bool | None = None) -> dict:
    offline = CHECKBIM_OFFLINE or not llm_available() if force_offline is None else force_offline
    provider = resolve_llm_provider()
    planner = planner_label(None if offline else provider)

    if offline:
        return _run_offline_loop(model_id, message, planner=planner)

    if is_gibberish(message):
        return _unclear_intent_response(planner)

    try:
        return _run_online_loop(model_id, message, planner)
    except Exception as exc:
        logger.warning("LLM planner failed, falling back to rules: %s", exc)
        return _run_offline_loop(
            model_id,
            message,
            planner="rules",
            prefix="（LLM 暂不可用，已降级规则路由）",
        )


def _run_offline_loop(
    model_id: str,
    message: str,
    *,
    planner: str = "rules",
    prefix: str = "",
) -> dict:
    tool_traces: list[dict] = []
    results: dict[str, Any] = {}
    planned = plan_tools_from_message(message)[:MAX_STEPS]
    for name in planned:
        output = execute_tool(name, model_id)
        tool_traces.append({"tool": name, "output": output, "planner": planner})
        if output.get("ok") and "result" in output:
            if name == "run_collision_check":
                results["collision"] = output["result"]
            elif name == "run_attribute_check":
                results["attributes"] = output["result"]
            elif name == "get_model_info":
                results["model_info"] = output["result"]
    reply = _summarize_offline(message, tool_traces, results)
    if prefix and reply != UNCLEAR_INTENT_REPLY:
        reply = f"{prefix} {reply}"
    did_run = bool(tool_traces)
    return {
        "reply": _guard_reply(reply, did_run),
        "tool_traces": tool_traces,
        "results": results,
        "did_run_tools": did_run,
        "planner": planner,
    }


def _run_online_loop(model_id: str, message: str, planner: str) -> dict:
    tool_traces: list[dict] = []
    results: dict[str, Any] = {}
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"当前模型 ID: {model_id}\n用户消息: {message}"},
    ]
    tools = get_openai_tools_schema()

    for _ in range(MAX_STEPS):
        data = chat_with_tools(messages, tools=tools)
        choice = data["choices"][0]["message"]
        tool_calls = choice.get("tool_calls") or []

        if not tool_calls:
            reply = choice.get("content") or ""
            did_run = bool(tool_traces)
            return {
                "reply": _guard_reply(reply, did_run),
                "tool_traces": tool_traces,
                "results": results,
                "did_run_tools": did_run,
                "planner": planner,
            }

        messages.append(choice)
        for call in tool_calls:
            fn = call["function"]
            name = fn["name"]
            output = execute_tool(name, model_id)
            tool_traces.append({"tool": name, "output": output, "planner": planner})
            if output.get("ok") and "result" in output:
                if name == "run_collision_check":
                    results["collision"] = output["result"]
                elif name == "run_attribute_check":
                    results["attributes"] = output["result"]
                elif name == "get_model_info":
                    results["model_info"] = output["result"]
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(output, ensure_ascii=False),
                }
            )

    return {
        "reply": "已达到最大规划步数，请缩小问题范围后重试。",
        "tool_traces": tool_traces,
        "results": results,
        "did_run_tools": bool(tool_traces),
        "planner": planner,
    }

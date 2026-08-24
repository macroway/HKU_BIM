import json
from typing import Any

from app.agent.llm_client import chat_with_tools
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.router_fallback import plan_tools_from_message
from app.config import CHECKBIM_OFFLINE, OPENAI_API_KEY
from app.tools.registry import execute_tool, get_openai_tools_schema

MAX_STEPS = 5

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


def _guard_reply(reply: str, did_run_tools: bool) -> str:
    if did_run_tools:
        return reply
    unsafe = ("通过", "无碰撞", "没有冲突", "检查完成", "一切正常")
    if any(word in reply for word in unsafe):
        return "尚未执行检查工具，无法给出检查结论。请先让我调用碰撞或属性检查。"
    return reply


def run_agent_loop(model_id: str, message: str, *, force_offline: bool | None = None) -> dict:
    offline = CHECKBIM_OFFLINE or not OPENAI_API_KEY if force_offline is None else force_offline

    tool_traces: list[dict] = []
    results: dict[str, Any] = {}
    planner = "rules"

    if offline:
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
        did_run = bool(tool_traces)
        return {
            "reply": _guard_reply(reply, did_run),
            "tool_traces": tool_traces,
            "results": results,
            "did_run_tools": did_run,
            "planner": planner,
        }

    # Online:受控 ReAct with LLM tool calling
    planner = "llm"
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

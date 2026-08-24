from app.models.schema import InternalModel
from app.models.store import get_model
from app.tools.attributes import run_attribute_check
from app.tools.collision import run_collision_check

TOOL_NAMES = (
    "run_collision_check",
    "run_attribute_check",
    "get_model_info",
)


def get_openai_tools_schema() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "run_collision_check",
                "description": "对当前模型执行几何碰撞检测（墙/梁/管道）",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_attribute_check",
                "description": "检查 Name / FireRating 等关键属性是否缺失",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_model_info",
                "description": "获取当前模型的构件数量与类型统计",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
    ]


def execute_tool(name: str, model_id: str) -> dict:
    if name not in TOOL_NAMES:
        return {"ok": False, "error": f"Unknown tool: {name}"}

    model = get_model(model_id)

    if name == "get_model_info":
        types: dict[str, int] = {}
        for element in model.elements:
            types[element.type] = types.get(element.type, 0) + 1
        return {
            "ok": True,
            "tool": name,
            "result": {
                "model_id": model_id,
                "element_count": len(model.elements),
                "types": types,
            },
        }

    if name == "run_collision_check":
        return {"ok": True, "tool": name, "result": run_collision_check(model)}

    if name == "run_attribute_check":
        return {"ok": True, "tool": name, "result": run_attribute_check(model)}

    return {"ok": False, "error": f"Unhandled tool: {name}"}

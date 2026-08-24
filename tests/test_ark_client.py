from app.agent.ark_client import (
    messages_to_ark_payload,
    normalize_ark_response,
    sanitize_tools_for_ark,
)


def test_messages_to_ark_payload_system_and_user():
    instructions, items = messages_to_ark_payload(
        [
            {"role": "system", "content": "你是助手"},
            {"role": "user", "content": "查碰撞"},
        ]
    )
    assert instructions == "你是助手"
    assert len(items) == 1
    assert items[0]["role"] == "user"
    assert items[0]["content"][0]["type"] == "input_text"
    assert items[0]["content"][0]["text"] == "查碰撞"


def test_messages_to_ark_tool_roundtrip():
    instructions, items = messages_to_ark_payload(
        [
            {"role": "assistant", "tool_calls": [{"id": "call_1", "function": {"name": "run_collision_check", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "call_1", "content": '{"ok": true}'},
        ]
    )
    assert instructions is None
    assert items[0]["type"] == "function_call"
    assert items[0]["name"] == "run_collision_check"
    assert items[1]["type"] == "function_call_output"
    assert items[1]["call_id"] == "call_1"


def test_normalize_ark_function_call_response():
    data = {
        "output": [
            {
                "type": "function_call",
                "call_id": "call_abc",
                "name": "run_collision_check",
                "arguments": "{}",
            }
        ]
    }
    normalized = normalize_ark_response(data)
    msg = normalized["choices"][0]["message"]
    assert msg["tool_calls"][0]["function"]["name"] == "run_collision_check"
    assert msg["tool_calls"][0]["id"] == "call_abc"


def test_normalize_ark_text_response():
    data = {
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": "检查完成，发现 2 对冲突。"}],
            }
        ]
    }
    normalized = normalize_ark_response(data)
    assert normalized["choices"][0]["message"]["content"] == "检查完成，发现 2 对冲突。"


def test_convert_tools_flat_ark_schema():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_collision_check",
                "description": "碰撞检测",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        }
    ]
    converted = sanitize_tools_for_ark(tools)
    assert "function" not in converted[0]
    assert converted[0]["name"] == "run_collision_check"
    assert converted[0]["type"] == "function"
    assert "additionalProperties" not in converted[0]["parameters"]

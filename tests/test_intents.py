"""Intent routing tests for enriched utterances (Loop4)."""

import pytest

from app.agent.router_fallback import has_actionable_intent, plan_tools_from_message


@pytest.mark.parametrize(
    "message,expected",
    [
        ("帮我查碰撞", ["run_collision_check"]),
        ("有没有硬碰", ["run_collision_check"]),
        ("看看空间冲突", ["run_collision_check"]),
        ("风管有没有撞墙", ["run_collision_check"]),
        ("查属性完整性", ["run_attribute_check"]),
        ("防火等级齐全吗", ["run_attribute_check"]),
        ("FireRating 缺不缺", ["run_attribute_check"]),
        ("两个都查", ["run_collision_check", "run_attribute_check"]),
        ("交付前帮我过一遍", ["run_collision_check", "run_attribute_check"]),
        ("全面自查", ["run_collision_check", "run_attribute_check"]),
        ("模型有多少构件", ["get_model_info"]),
        ("统计一下模型情况", ["get_model_info"]),
    ],
)
def test_actionable_intents(message: str, expected: list[str]):
    assert plan_tools_from_message(message) == expected
    assert has_actionable_intent(message)


@pytest.mark.parametrize(
    "message",
    ["111", "你好", "???", "", "   "],
)
def test_non_actionable_intents(message: str):
    assert plan_tools_from_message(message) == []
    assert not has_actionable_intent(message)

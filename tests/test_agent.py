from pathlib import Path

import pytest

from app.agent.loop import _guard_reply, run_agent_loop
from app.models.store import clear_models, register_model

SAMPLES = Path(__file__).resolve().parent.parent / "test_samples"


@pytest.fixture(autouse=True)
def reset_store():
    clear_models()
    yield
    clear_models()


def _register(name: str) -> str:
    return register_model(SAMPLES / f"{name}.json")


def test_offline_collision_intent():
    model_id = _register("collision_positive")
    out = run_agent_loop(model_id, "帮我查碰撞", force_offline=True)
    assert out["did_run_tools"]
    assert "collision" in out["results"]
    assert len(out["results"]["collision"]["pairs"]) >= 1
    assert out["planner"] == "rules"


def test_offline_both_checks():
    model_id = _register("collision_positive")
    out = run_agent_loop(model_id, "两个都查", force_offline=True)
    assert "collision" in out["results"]
    assert "attributes" in out["results"]
    assert len(out["tool_traces"]) == 2


def test_guard_blocks_false_pass_without_tools():
    reply = _guard_reply("检查通过，无碰撞，一切正常。", did_run_tools=False)
    assert "尚未执行检查工具" in reply


def test_offline_attrs_on_missing_sample():
    model_id = _register("attrs_missing")
    out = run_agent_loop(model_id, "查属性完整性", force_offline=True)
    assert out["did_run_tools"]
    assert len(out["results"]["attributes"]["missing"]) >= 1


def test_offline_unclear_intent_does_not_run_tools():
    model_id = _register("attrs_missing")
    for msg in ("1", "33", "你好", "???"):
        out = run_agent_loop(model_id, msg, force_offline=True)
        assert out["did_run_tools"] is False, msg
        assert out["results"] == {}
        assert out["tool_traces"] == []
        assert "不确定" in out["reply"] or "请说明" in out["reply"]


def test_offline_generic_check_runs_both():
    model_id = _register("collision_positive")
    out = run_agent_loop(model_id, "帮我检查一下", force_offline=True)
    assert out["did_run_tools"]
    assert "collision" in out["results"]
    assert "attributes" in out["results"]

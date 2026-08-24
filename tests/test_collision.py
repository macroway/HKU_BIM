import json
from pathlib import Path

import pytest

from app.models.loader import load_json_model
from app.tools.collision import run_collision_check

SAMPLES = Path(__file__).resolve().parent.parent / "test_samples"


@pytest.mark.parametrize(
    "sample_name",
    ["collision_positive", "collision_negative", "building_l1"],
)
def test_collision_golden(sample_name: str):
    model = load_json_model(SAMPLES / f"{sample_name}.json")
    result = run_collision_check(model)
    expected_path = SAMPLES / (
        f"{sample_name}.expected.json"
        if sample_name != "building_l1"
        else "building_l1.collision.expected.json"
    )
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert result == expected


def test_collision_positive_no_false_negative():
    """漏报防护：金标中的每一对碰撞都必须出现在结果里。"""
    model = load_json_model(SAMPLES / "collision_positive.json")
    result = run_collision_check(model)
    expected_pairs = {
        (p["a"], p["b"])
        for p in json.loads((SAMPLES / "collision_positive.expected.json").read_text())["pairs"]
    }
    actual_pairs = {(p["a"], p["b"]) for p in result["pairs"]}
    assert expected_pairs.issubset(actual_pairs), f"漏报: {expected_pairs - actual_pairs}"

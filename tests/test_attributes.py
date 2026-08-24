import json
from pathlib import Path

import pytest

from app.models.loader import load_json_model
from app.tools.attributes import run_attribute_check

SAMPLES = Path(__file__).resolve().parent.parent / "test_samples"


@pytest.mark.parametrize("sample_name", ["attrs_missing", "attrs_ok"])
def test_attribute_golden(sample_name: str):
    model = load_json_model(SAMPLES / f"{sample_name}.json")
    result = run_attribute_check(model)
    expected = json.loads((SAMPLES / f"{sample_name}.expected.json").read_text(encoding="utf-8"))
    assert result == expected

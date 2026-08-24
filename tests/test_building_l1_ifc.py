"""IFC integration tests for building-l1 demo model."""

from pathlib import Path

from app.models.loader import load_ifc_model, load_model
from app.tools.attributes import run_attribute_check
from app.tools.collision import run_collision_check

BUILDING_L1_IFC = Path(__file__).resolve().parent.parent / "test_samples/demo/building-l1.ifc"


def test_building_l1_ifc_exists():
    assert BUILDING_L1_IFC.exists(), "Run scripts/create_building_l1.py first"


def test_building_l1_ifc_element_count():
    model = load_ifc_model(BUILDING_L1_IFC)
    assert len(model.elements) == 10
    assert all(e.aabb is not None for e in model.elements)


def test_building_l1_ifc_known_collisions():
    model = load_ifc_model(BUILDING_L1_IFC)
    result = run_collision_check(model)
    assert len(result["pairs"]) == 4


def test_building_l1_ifc_known_missing_attrs():
    model = load_ifc_model(BUILDING_L1_IFC)
    result = run_attribute_check(model)
    assert len(result["missing"]) == 3


def test_building_l1_ifc_via_dispatcher():
    model = load_model(BUILDING_L1_IFC, model_id="demo/building-l1")
    assert model.model_id == "demo/building-l1"

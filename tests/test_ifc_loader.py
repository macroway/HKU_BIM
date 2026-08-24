from pathlib import Path

from app.models.loader import load_ifc_model, load_model
from app.tools.attributes import run_attribute_check
from app.tools.collision import run_collision_check

DEMO_IFC = Path(__file__).resolve().parent.parent / "test_samples/demo/demo-collision.ifc"


def test_load_ifc_model_has_walls():
    assert DEMO_IFC.exists(), "Run scripts/create_demo_ifc.py first"
    model = load_ifc_model(DEMO_IFC)
    walls = [e for e in model.elements if e.type == "IfcWall"]
    assert len(walls) >= 2
    assert all(e.aabb is not None for e in walls)


def test_ifc_demo_has_known_collision():
    model = load_ifc_model(DEMO_IFC)
    result = run_collision_check(model)
    assert len(result["pairs"]) >= 1, "演示 IFC 应至少检测到 1 对墙碰撞"


def test_load_model_dispatcher_ifc():
    model = load_model(DEMO_IFC)
    assert model.model_id == "demo-collision"


def test_ifc_demo_attributes_ok():
    model = load_ifc_model(DEMO_IFC)
    result = run_attribute_check(model)
    assert result["missing"] == []

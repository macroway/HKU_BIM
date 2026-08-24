"""Generate test_samples/building_l1.json and golden expected files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "test_samples"

ELEMENTS = [
    {
        "id": "wall-ext-w",
        "type": "IfcWall",
        "name": "一层-西外墙",
        "props": {"Name": "一层-西外墙", "FireRating": "2h"},
        "aabb": {"min": [0, 0, 0], "max": [0.3, 15, 3]},
    },
    {
        "id": "wall-ext-e",
        "type": "IfcWall",
        "name": "一层-东外墙",
        "props": {"Name": "一层-东外墙", "FireRating": "2h"},
        "aabb": {"min": [19.7, 0, 0], "max": [20, 15, 3]},
    },
    {
        "id": "wall-part-1",
        "type": "IfcWall",
        "name": "一层-1号隔墙",
        "props": {"Name": "一层-1号隔墙", "FireRating": "1h"},
        "aabb": {"min": [9.7, 3, 0], "max": [10.3, 12, 3]},
    },
    {
        "id": "wall-part-2",
        "type": "IfcWall",
        "name": "一层-2号隔墙",
        "props": {"Name": "一层-2号隔墙", "FireRating": "1h"},
        "aabb": {"min": [5, 9.7, 0], "max": [12, 10.3, 3]},
    },
    {
        "id": "beam-main",
        "type": "IfcBeam",
        "name": "一层-主梁B1",
        "props": {"Name": "一层-主梁B1"},
        "aabb": {"min": [5, 7.5, 2.8], "max": [15, 8, 3.2]},
    },
    {
        "id": "pipe-supply",
        "type": "IfcPipeSegment",
        "name": "风管-送风-01",
        "props": {"Name": "风管-送风-01", "FireRating": "1h"},
        "aabb": {"min": [9.5, 6, 1], "max": [10.5, 6.4, 2]},
    },
    {
        "id": "pipe-return",
        "type": "IfcPipeSegment",
        "name": "风管-回风-02",
        "props": {"Name": "风管-回风-02", "FireRating": "1h"},
        "aabb": {"min": [14, 4, 2.5], "max": [14.4, 8, 2.9]},
    },
    {
        "id": "door-d1",
        "type": "IfcDoor",
        "name": "防火门-D1",
        "props": {"Name": "防火门-D1"},
        "aabb": {"min": [10, 5, 0], "max": [10.2, 6, 2.1]},
    },
    {
        "id": "door-d2",
        "type": "IfcDoor",
        "name": "防火门-D2",
        "props": {"Name": "防火门-D2", "FireRating": "1h"},
        "aabb": {"min": [10, 8, 0], "max": [10.2, 9, 2.1]},
    },
    {
        "id": "door-d3",
        "type": "IfcDoor",
        "name": "门-D3",
        "props": {},
        "aabb": {"min": [5, 5, 0], "max": [5.2, 6, 2.1]},
    },
]


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT))
    from app.models.loader import load_json_model
    from app.tools.attributes import run_attribute_check
    from app.tools.collision import run_collision_check

    sample_path = OUT / "building_l1.json"
    sample_path.write_text(
        json.dumps({"elements": ELEMENTS}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    model = load_json_model(sample_path, model_id="building_l1")
    collision = run_collision_check(model)
    attrs = run_attribute_check(model)

    (OUT / "building_l1.collision.expected.json").write_text(
        json.dumps(collision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "building_l1.attrs.expected.json").write_text(
        json.dumps(attrs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {sample_path} ({len(ELEMENTS)} elements)")
    print(f"  collisions: {len(collision['pairs'])} pairs")
    print(f"  missing attrs: {len(attrs['missing'])} items")

    import subprocess

    subprocess.run([sys.executable, str(ROOT / "scripts/create_building_l1_ifc.py")], check=True)


if __name__ == "__main__":
    main()

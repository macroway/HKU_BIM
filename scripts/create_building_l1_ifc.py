"""Generate test_samples/demo/building-l1.ifc from building_l1.json geometry."""

from __future__ import annotations

import json
from pathlib import Path

import ifcopenshell.api

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "test_samples/building_l1.json"
OUT_PATH = ROOT / "test_samples/demo/building-l1.ifc"

IFC_CLASS = {
    "IfcWall": "IfcWall",
    "IfcBeam": "IfcBeam",
    "IfcPipeSegment": "IfcPipeSegment",
    "IfcDoor": "IfcDoor",
}


def _box_mesh(aabb: dict) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    x0, y0, z0 = aabb["min"]
    x1, y1, z1 = aabb["max"]
    verts = [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    return verts, faces


def main() -> None:
    if not JSON_PATH.exists():
        raise SystemExit(f"Missing {JSON_PATH}; run scripts/create_building_l1.py first")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    elements = data["elements"]

    f = ifcopenshell.api.run("project.create_file", version="IFC4")
    ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcProject", name="CheckBIM Building L1")
    ifcopenshell.api.run("unit.assign_unit", f)
    ifcopenshell.api.run("context.add_context", f, context_type="Model")
    storey = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="一层")
    ctx = f.by_type("IfcGeometricRepresentationContext")[0]

    for raw in elements:
        ifc_class = IFC_CLASS[raw["type"]]
        product = ifcopenshell.api.run(
            "root.create_entity",
            f,
            ifc_class=ifc_class,
            name=raw.get("name") or raw["id"],
        )
        ifcopenshell.api.run("spatial.assign_container", f, relating_structure=storey, products=[product])
        verts, faces = _box_mesh(raw["aabb"])
        rep = ifcopenshell.api.run(
            "geometry.add_mesh_representation",
            f,
            context=ctx,
            vertices=[verts],
            faces=[faces],
        )
        ifcopenshell.api.run("geometry.assign_representation", f, product=product, representation=rep)
        ifcopenshell.api.run(
            "attribute.edit_attributes",
            f,
            product=product,
            attributes={"Name": raw.get("name") or raw["id"]},
        )
        props = raw.get("props") or {}
        if "FireRating" in props:
            pset_name = {
                "IfcWall": "Pset_WallCommon",
                "IfcBeam": "Pset_BeamCommon",
                "IfcPipeSegment": "Pset_PipeSegmentTypeCommon",
                "IfcDoor": "Pset_DoorCommon",
            }.get(raw["type"], "Pset_CheckBIM")
            pset = ifcopenshell.api.run("pset.add_pset", f, product=product, name=pset_name)
            ifcopenshell.api.run(
                "pset.edit_pset",
                f,
                pset=pset,
                properties={"FireRating": props["FireRating"]},
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(OUT_PATH))
    print(f"Wrote {OUT_PATH} ({len(elements)} elements)")


if __name__ == "__main__":
    main()

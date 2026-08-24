"""Regenerate test_samples/demo/demo-collision.ifc"""

from pathlib import Path

import ifcopenshell.api


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "test_samples/demo/demo-collision.ifc"
    out.parent.mkdir(parents=True, exist_ok=True)

    f = ifcopenshell.api.run("project.create_file", version="IFC4")
    ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcProject", name="CheckBIM Demo")
    ifcopenshell.api.run("unit.assign_unit", f)
    ifcopenshell.api.run("context.add_context", f, context_type="Model")

    storey = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="L1")
    ctx = f.by_type("IfcGeometricRepresentationContext")[0]

    def add_wall(name: str, x: float, y: float, z: float, length: float = 10.0):
        wall = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcWall", name=name)
        ifcopenshell.api.run("spatial.assign_container", f, relating_structure=storey, products=[wall])
        rep = ifcopenshell.api.run(
            "geometry.add_wall_representation", f, context=ctx, length=length, height=3.0, thickness=0.3
        )
        ifcopenshell.api.run("geometry.assign_representation", f, product=wall, representation=rep)
        matrix = [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]
        ifcopenshell.api.run("geometry.edit_object_placement", f, product=wall, matrix=matrix)
        ifcopenshell.api.run("attribute.edit_attributes", f, product=wall, attributes={"Name": name})
        pset = ifcopenshell.api.run("pset.add_pset", f, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.run("pset.edit_pset", f, pset=pset, properties={"FireRating": "2h"})
        return wall

    add_wall("外墙 A", 0, 0, 0)
    add_wall("内隔墙 B", 5, 0, 0, length=6.0)

    f.write(str(out))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

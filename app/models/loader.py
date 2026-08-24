import json
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom as ifc_geom
import ifcopenshell.util.element as ifc_element

from app.models.schema import AABB, InternalElement, InternalModel

COLLISION_TYPES = {"IfcWall", "IfcBeam", "IfcPipeSegment"}
IFC_TYPE_MAP = {
    "IfcWall": "IfcWall",
    "IfcWallStandardCase": "IfcWall",
    "IfcBeam": "IfcBeam",
    "IfcPipeSegment": "IfcPipeSegment",
    "IfcDoor": "IfcDoor",
}
CHECK_IFC_CLASSES = list(IFC_TYPE_MAP.keys())


def load_json_model(path: Path, model_id: str | None = None) -> InternalModel:
    data = json.loads(path.read_text(encoding="utf-8"))
    mid = model_id or path.stem
    elements: list[InternalElement] = []

    for raw in data.get("elements", []):
        aabb = None
        if raw.get("aabb"):
            box = raw["aabb"]
            aabb = AABB(min=box["min"], max=box["max"])
        elements.append(
            InternalElement(
                id=raw["id"],
                type=raw["type"],
                name=raw.get("name"),
                props=raw.get("props", {}),
                aabb=aabb,
            )
        )

    return InternalModel(model_id=mid, elements=elements)


def _aabb_from_shape(shape) -> AABB | None:
    geometry = shape.geometry
    verts = geometry.verts
    if not verts:
        return None
    xs = verts[0::3]
    ys = verts[1::3]
    zs = verts[2::3]
    return AABB(min=[min(xs), min(ys), min(zs)], max=[max(xs), max(ys), max(zs)])


def _props_from_element(element) -> dict:
    props: dict[str, str] = {}
    name = getattr(element, "Name", None)
    if name:
        props["Name"] = name
    for definition in ifc_element.get_psets(element).values():
        if isinstance(definition, dict):
            for key, value in definition.items():
                if key in ("id", "type") or value is None:
                    continue
                props[key] = value
    return props


def load_ifc_model(path: Path, model_id: str | None = None) -> InternalModel:
    ifc_file = ifcopenshell.open(str(path))
    mid = model_id or path.stem
    settings = ifc_geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    elements: list[InternalElement] = []
    for ifc_class in CHECK_IFC_CLASSES:
        for element in ifc_file.by_type(ifc_class):
            mapped_type = IFC_TYPE_MAP.get(element.is_a(), element.is_a())
            aabb = None
            try:
                shape = ifc_geom.create_shape(settings, element)
                aabb = _aabb_from_shape(shape)
            except Exception:
                aabb = None

            props = _props_from_element(element)
            elements.append(
                InternalElement(
                    id=element.GlobalId,
                    type=mapped_type,
                    name=getattr(element, "Name", None),
                    props=props,
                    aabb=aabb,
                )
            )

    return InternalModel(model_id=mid, elements=elements)


def load_model(path: Path, model_id: str | None = None) -> InternalModel:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json_model(path, model_id)
    if suffix in {".ifc", ".ifczip"}:
        return load_ifc_model(path, model_id)
    raise ValueError(f"Unsupported model format: {suffix}")

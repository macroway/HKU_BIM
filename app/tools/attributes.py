from app.models.loader import COLLISION_TYPES
from app.models.schema import InternalModel

ATTRIBUTE_TYPES = COLLISION_TYPES | {"IfcDoor"}
FIELDS_CHECKED = ["Name", "FireRating"]


def _is_missing(props: dict, field: str) -> bool:
    if field not in props:
        return True
    value = props[field]
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def run_attribute_check(model: InternalModel) -> dict:
    missing: list[dict] = []

    for element in model.elements:
        if element.type not in ATTRIBUTE_TYPES:
            continue
        props = dict(element.props)
        if element.name and "Name" not in props:
            props["Name"] = element.name
        for field in FIELDS_CHECKED:
            if _is_missing(props, field):
                missing.append({"id": element.id, "type": element.type, "field": field})

    missing.sort(key=lambda m: (m["id"], m["field"]))

    return {
        "missing": missing,
        "fields_checked": list(FIELDS_CHECKED),
        "types_checked": sorted(ATTRIBUTE_TYPES),
    }

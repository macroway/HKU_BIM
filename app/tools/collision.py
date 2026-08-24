from app.models.loader import COLLISION_TYPES
from app.models.schema import InternalModel


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def run_collision_check(model: InternalModel) -> dict:
    candidates = [
        e for e in model.elements if e.type in COLLISION_TYPES and e.aabb is not None
    ]
    by_id = {e.id: e for e in candidates}
    pairs: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for i, a in enumerate(candidates):
        for b in candidates[i + 1 :]:
            if not a.aabb.intersects(b.aabb):
                continue
            key = _pair_key(a.id, b.id)
            if key in seen:
                continue
            seen.add(key)
            ea = by_id[key[0]]
            eb = by_id[key[1]]
            pairs.append(
                {
                    "a": key[0],
                    "b": key[1],
                    "a_type": ea.type,
                    "b_type": eb.type,
                    "a_name": ea.name or "",
                    "b_name": eb.name or "",
                }
            )

    pairs.sort(key=lambda p: (p["a"], p["b"]))

    return {
        "pairs": pairs,
        "engine": "aabb_v1",
        "element_types_checked": sorted(COLLISION_TYPES),
    }

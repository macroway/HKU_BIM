from dataclasses import dataclass, field
from typing import Any


@dataclass
class AABB:
    min: list[float]
    max: list[float]

    def intersects(self, other: "AABB") -> bool:
        for i in range(3):
            if self.max[i] < other.min[i] or self.min[i] > other.max[i]:
                return False
        return True


@dataclass
class InternalElement:
    id: str
    type: str
    name: str | None = None
    props: dict[str, Any] = field(default_factory=dict)
    aabb: AABB | None = None


@dataclass
class InternalModel:
    model_id: str
    elements: list[InternalElement]

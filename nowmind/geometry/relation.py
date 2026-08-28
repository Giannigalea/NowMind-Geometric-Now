from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RelationType(str, Enum):
    AT = "at"
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    ABOVE = "above"
    BELOW = "below"
    INSIDE = "inside"
    CONTAINS = "contains"
    TOUCHING = "touching"
    ON = "on"
    UNDER = "under"
    NEAR = "near"
    DISTANCE = "distance"
    COLLIDES_WITH = "collides_with"
    REACHABLE = "reachable"
    OCCUPANCY = "occupancy"


class Provenance(str, Enum):
    OBSERVED_NOW = "observed_now"
    INFERRED_NOW = "inferred_now"


@dataclass(frozen=True, slots=True)
class Relation:
    """A typed relation in the current Present Geometry."""

    relation_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float
    provenance: Provenance
    rule_id: str | None = None
    premise_ids: tuple[str, ...] = field(default_factory=tuple)
    value: Any | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if not self.relation_id:
            raise ValueError("relation_id must be non-empty")
        if not self.source_id or not self.target_id:
            raise ValueError("relation endpoints must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
        object.__setattr__(self, "premise_ids", tuple(self.premise_ids))

    @property
    def key(self) -> tuple[str, RelationType, str]:
        return (self.source_id, self.relation_type, self.target_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "confidence": self.confidence,
            "provenance": self.provenance.value,
            "rule_id": self.rule_id,
            "premise_ids": list(self.premise_ids),
            "value": self.value,
            "unit": self.unit,
        }

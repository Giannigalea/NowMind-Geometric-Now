from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nowmind.geometry.relation import Relation, RelationType
from nowmind.world.model import WorldRelation


@dataclass(frozen=True, slots=True)
class Proposition:
    """Compact symbolic content carried by temporal-source records."""

    source_id: str
    relation_type: RelationType
    target_id: str
    value: Any | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("proposition endpoints must be non-empty")

    @property
    def key(self) -> tuple[str, RelationType, str]:
        return (self.source_id, self.relation_type, self.target_id)

    def matches(
        self,
        source_id: str | None = None,
        relation_type: RelationType | None = None,
        target_id: str | None = None,
    ) -> bool:
        if source_id is not None and self.source_id != source_id:
            return False
        if relation_type is not None and self.relation_type is not relation_type:
            return False
        if target_id is not None and self.target_id != target_id:
            return False
        return True

    def display(self) -> str:
        return f"{self.source_id} {self.relation_type.name} {self.target_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "relation_type": self.relation_type.value,
            "target_id": self.target_id,
            "value": self.value,
            "unit": self.unit,
            "display": self.display(),
        }

    @classmethod
    def from_relation(cls, relation: Relation | WorldRelation) -> Proposition:
        return cls(
            source_id=relation.source_id,
            relation_type=relation.relation_type,
            target_id=relation.target_id,
            value=relation.value,
            unit=relation.unit,
        )

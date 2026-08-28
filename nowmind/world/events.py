from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from nowmind.geometry.relation import RelationType
from nowmind.world.model import WorldRelation, WorldState


@dataclass(frozen=True, slots=True)
class AddEntity:
    entity_id: str
    kind: str
    label: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def apply(self, world: WorldState) -> None:
        world._add_entity(self.entity_id, self.kind, self.label, self.attributes)


@dataclass(frozen=True, slots=True)
class RemoveEntity:
    entity_id: str

    def apply(self, world: WorldState) -> None:
        world._remove_entity(self.entity_id)


@dataclass(frozen=True, slots=True)
class SetRelation:
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    value: Any | None = None
    unit: str | None = None

    def apply(self, world: WorldState) -> None:
        world._set_relation(
            WorldRelation(
                source_id=self.source_id,
                target_id=self.target_id,
                relation_type=self.relation_type,
                confidence=self.confidence,
                value=self.value,
                unit=self.unit,
            )
        )


@dataclass(frozen=True, slots=True)
class MoveRelation(SetRelation):
    """Replace the current relation family between two entities.

    This is useful for state-change demos: moving A from left of B to right of B
    removes the old left/right facts in the world before adding the new fact.
    """

    def apply(self, world: WorldState) -> None:
        world._remove_family_between(self.source_id, self.target_id, self.relation_type)
        SetRelation.apply(self, world)


@dataclass(frozen=True, slots=True)
class RemoveRelation:
    source_id: str
    target_id: str
    relation_type: RelationType

    def apply(self, world: WorldState) -> None:
        world._remove_relation(self.source_id, self.target_id, self.relation_type)

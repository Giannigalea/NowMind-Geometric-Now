from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nowmind.geometry.entity import Entity
from nowmind.geometry.relation import RelationType


@dataclass(frozen=True, slots=True)
class ObservedRelation:
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    source: str = "perfect_world_perception"
    value: Any | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")


@dataclass(frozen=True, slots=True)
class Observation:
    cycle_id: int
    world_version: int
    observed_entities: tuple[Entity, ...]
    observed_relations: tuple[ObservedRelation, ...] = field(default_factory=tuple)
    source: str = "perfect_world_perception"

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed_entities", tuple(self.observed_entities))
        object.__setattr__(self, "observed_relations", tuple(self.observed_relations))


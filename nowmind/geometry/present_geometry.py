from __future__ import annotations

from dataclasses import dataclass, field

from nowmind.geometry.entity import Entity
from nowmind.geometry.relation import Relation, RelationType
from nowmind.geometry.validation import ValidationResult


@dataclass(frozen=True, slots=True)
class PresentGeometry:
    """Read-only relational graph for one current cognitive cycle."""

    cycle_id: int
    world_version: int
    entities: tuple[Entity, ...]
    relations: tuple[Relation, ...]
    validation: ValidationResult = field(default_factory=ValidationResult)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entities", tuple(self.entities))
        object.__setattr__(self, "relations", tuple(self.relations))

    @property
    def entity_ids(self) -> frozenset[str]:
        return frozenset(entity.entity_id for entity in self.entities)

    @property
    def relation_by_id(self) -> dict[str, Relation]:
        return {relation.relation_id: relation for relation in self.relations}

    def find_relations(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        relation_type: RelationType | None = None,
    ) -> tuple[Relation, ...]:
        matches = []
        for relation in self.relations:
            if source_id is not None and relation.source_id != source_id:
                continue
            if target_id is not None and relation.target_id != target_id:
                continue
            if relation_type is not None and relation.relation_type is not relation_type:
                continue
            matches.append(relation)
        return tuple(matches)

    def find_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
    ) -> Relation | None:
        for relation in self.relations:
            if (
                relation.source_id == source_id
                and relation.target_id == target_id
                and relation.relation_type is relation_type
            ):
                return relation
        return None


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from nowmind.geometry.entity import Entity
from nowmind.geometry.relation import RelationType


class WorldEvent(Protocol):
    def apply(self, world: WorldState) -> None:
        ...


@dataclass(frozen=True, slots=True)
class WorldRelation:
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    value: Any | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")

    @property
    def key(self) -> tuple[str, RelationType, str]:
        return (self.source_id, self.relation_type, self.target_id)


class WorldState:
    """Persistent environment ground truth.

    The world persists across cycles, but it is external to cognition. Runtime
    reasoning receives a fresh NowState, not this object.
    """

    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}
        self._relations: dict[tuple[str, RelationType, str], WorldRelation] = {}
        self.world_version = 0

    @property
    def entities(self) -> tuple[Entity, ...]:
        return tuple(sorted(self._entities.values(), key=lambda entity: entity.entity_id))

    @property
    def relations(self) -> tuple[WorldRelation, ...]:
        return tuple(
            sorted(
                self._relations.values(),
                key=lambda relation: (
                    relation.source_id,
                    relation.relation_type.value,
                    relation.target_id,
                ),
            )
        )

    def apply(self, event: WorldEvent) -> WorldState:
        event.apply(self)
        self.world_version += 1
        return self

    def _add_entity(
        self,
        entity_id: str,
        kind: str,
        label: str | None = None,
        attributes: Mapping[str, Any] | None = None,
    ) -> None:
        self._entities[entity_id] = Entity(
            entity_id=entity_id,
            kind=kind,
            label=label,
            attributes=attributes or {},
        )

    def _remove_entity(self, entity_id: str) -> None:
        self._entities.pop(entity_id, None)
        self._relations = {
            key: relation
            for key, relation in self._relations.items()
            if relation.source_id != entity_id and relation.target_id != entity_id
        }

    def _set_relation(self, relation: WorldRelation) -> None:
        self._relations[relation.key] = relation

    def _remove_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
    ) -> None:
        self._relations.pop((source_id, relation_type, target_id), None)

    def _remove_family_between(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
    ) -> None:
        family = _family_for(relation_type)
        unordered_pair = frozenset((source_id, target_id))
        self._relations = {
            key: relation
            for key, relation in self._relations.items()
            if not (
                relation.relation_type in family
                and frozenset((relation.source_id, relation.target_id)) == unordered_pair
            )
        }


def _family_for(relation_type: RelationType) -> frozenset[RelationType]:
    if relation_type in {RelationType.LEFT_OF, RelationType.RIGHT_OF}:
        return frozenset((RelationType.LEFT_OF, RelationType.RIGHT_OF))
    if relation_type in {RelationType.ABOVE, RelationType.BELOW}:
        return frozenset((RelationType.ABOVE, RelationType.BELOW))
    if relation_type in {RelationType.INSIDE, RelationType.CONTAINS}:
        return frozenset((RelationType.INSIDE, RelationType.CONTAINS))
    if relation_type in {RelationType.ON, RelationType.UNDER}:
        return frozenset((RelationType.ON, RelationType.UNDER))
    return frozenset((relation_type,))


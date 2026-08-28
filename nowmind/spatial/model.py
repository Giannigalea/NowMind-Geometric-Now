from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from nowmind.geometry.entity import Entity
from nowmind.geometry.present_geometry import PresentGeometry
from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.geometry.validation import ValidationResult


class OccupancyState(str, Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True, order=True)
class Pose2D:
    x: int
    y: int

    def moved(self, dx: int, dy: int) -> Pose2D:
        return Pose2D(self.x + dx, self.y + dy)

    def manhattan_distance(self, other: Pose2D) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def cell_id(self) -> str:
        return f"cell:{self.x},{self.y}"

    def to_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y}


@dataclass(frozen=True, slots=True)
class SpatialEntity:
    entity_id: str
    kind: str
    pose: Pose2D
    label: str | None = None
    blocks_movement: bool = False
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id must be non-empty")
        if not self.kind:
            raise ValueError("kind must be non-empty")
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))

    def with_pose(self, pose: Pose2D) -> SpatialEntity:
        return replace(self, pose=pose)

    def to_entity(self) -> Entity:
        attributes = dict(self.attributes)
        attributes.update(
            {
                "x": self.pose.x,
                "y": self.pose.y,
                "blocks_movement": self.blocks_movement,
            }
        )
        return Entity(
            entity_id=self.entity_id,
            kind=self.kind,
            label=self.label,
            attributes=attributes,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "kind": self.kind,
            "label": self.label,
            "pose": self.pose.to_dict(),
            "blocks_movement": self.blocks_movement,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True, slots=True)
class CellOccupancy:
    pose: Pose2D
    state: OccupancyState

    def to_dict(self) -> dict[str, Any]:
        return {"pose": self.pose.to_dict(), "state": self.state.value}


@dataclass(frozen=True, slots=True)
class SpatialGeometry:
    width: int
    height: int
    entities: tuple[SpatialEntity, ...]
    occupancy: tuple[CellOccupancy, ...]
    derived_relations: tuple[Relation, ...]
    cycle_id: int
    world_version: int = 0
    _occupancy_index: Mapping[Pose2D, OccupancyState] = field(
        init=False,
        repr=False,
        compare=False,
    )
    _entity_index: Mapping[str, SpatialEntity] = field(
        init=False,
        repr=False,
        compare=False,
    )
    _trusted_occupancy: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("spatial geometry dimensions must be positive")
        object.__setattr__(
            self,
            "entities",
            tuple(self.entities),
        )
        object.__setattr__(
            self,
            "occupancy",
            tuple(self.occupancy),
        )
        object.__setattr__(
            self,
            "derived_relations",
            tuple(
                sorted(
                    self.derived_relations,
                    key=lambda relation: (
                        relation.source_id,
                        relation.relation_type.value,
                        relation.target_id,
                        relation.relation_id,
                    ),
                )
            ),
        )
        seen: set[str] = set()
        for entity in self.entities:
            if entity.entity_id in seen:
                raise ValueError(f"duplicate spatial entity id: {entity.entity_id}")
            seen.add(entity.entity_id)
            if not self.in_bounds(entity.pose):
                raise ValueError(f"entity {entity.entity_id} is out of bounds")
        if len(self.occupancy) != self.width * self.height:
            raise ValueError("occupancy must contain exactly one entry for every cell")
        if not self._trusted_occupancy:
            occupancy_poses = set()
            for cell in self.occupancy:
                if not self.in_bounds(cell.pose):
                    raise ValueError("occupancy contains an out-of-bounds cell")
                if cell.pose in occupancy_poses:
                    raise ValueError("occupancy contains duplicate cells")
                occupancy_poses.add(cell.pose)
        object.__setattr__(
            self,
            "_occupancy_index",
            MappingProxyType({cell.pose: cell.state for cell in self.occupancy}),
        )
        object.__setattr__(
            self,
            "_entity_index",
            MappingProxyType({entity.entity_id: entity for entity in self.entities}),
        )

    def in_bounds(self, pose: Pose2D) -> bool:
        return 0 <= pose.x < self.width and 0 <= pose.y < self.height

    @property
    def occupancy_map(self) -> dict[Pose2D, OccupancyState]:
        return dict(self._occupancy_index)

    @property
    def entity_map(self) -> dict[str, SpatialEntity]:
        return dict(self._entity_index)

    def entity(self, entity_id: str) -> SpatialEntity:
        try:
            return self._entity_index[entity_id]
        except KeyError as exc:
            raise KeyError(f"unknown spatial entity: {entity_id}") from exc

    def agent(self, actor_id: str = "agent") -> SpatialEntity:
        return self.entity(actor_id)

    def target(self, target_id: str = "target") -> SpatialEntity:
        return self.entity(target_id)

    def occupancy_at(self, pose: Pose2D) -> OccupancyState:
        if not self.in_bounds(pose):
            return OccupancyState.OCCUPIED
        return self._occupancy_index[pose]

    def blocking_entity_at(self, pose: Pose2D) -> SpatialEntity | None:
        for entity in self.entities:
            if entity.pose == pose and entity.blocks_movement:
                return entity
        return None

    def is_traversable(self, pose: Pose2D, allow_unknown: bool = False) -> bool:
        if not self.in_bounds(pose):
            return False
        state = self.occupancy_at(pose)
        if state is OccupancyState.OCCUPIED:
            return False
        if state is OccupancyState.UNKNOWN:
            return allow_unknown
        return True

    def with_entity_pose(
        self,
        entity_id: str,
        pose: Pose2D,
        derive_relations: bool = False,
    ) -> SpatialGeometry:
        entities = tuple(
            entity.with_pose(pose) if entity.entity_id == entity_id else entity
            for entity in self.entities
        )
        moved_entity = self.entity(entity_id)
        if not derive_relations and not moved_entity.blocks_movement:
            return SpatialGeometry(
                width=self.width,
                height=self.height,
                entities=entities,
                occupancy=self.occupancy,
                derived_relations=(),
                cycle_id=self.cycle_id,
                world_version=self.world_version,
                _trusted_occupancy=True,
            )
        unknown_cells = {
            cell.pose for cell in self.occupancy if cell.state is OccupancyState.UNKNOWN
        }
        return build_spatial_geometry(
            width=self.width,
            height=self.height,
            entities=entities,
            cycle_id=self.cycle_id,
            world_version=self.world_version,
            unknown_cells=unknown_cells,
            derive_relations=derive_relations,
        )

    def to_present_geometry(self) -> PresentGeometry:
        entity_ids = {entity.entity_id for entity in self.entities}
        relations = tuple(
            relation
            for relation in self.derived_relations
            if relation.source_id in entity_ids and relation.target_id in entity_ids
        )
        return PresentGeometry(
            cycle_id=self.cycle_id,
            world_version=self.world_version,
            entities=tuple(entity.to_entity() for entity in self.entities),
            relations=relations,
            validation=ValidationResult(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "cycle_id": self.cycle_id,
            "world_version": self.world_version,
            "entities": [entity.to_dict() for entity in self.entities],
            "occupancy": [cell.to_dict() for cell in self.occupancy],
            "derived_relations": [
                relation.to_dict() for relation in self.derived_relations
            ],
        }


class SpatialWorldState:
    """Persistent external 2D world used by G2.1 planning experiments."""

    def __init__(
        self,
        width: int,
        height: int,
        entities: Iterable[SpatialEntity] | None = None,
        hidden_cells: Iterable[Pose2D] | None = None,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("world dimensions must be positive")
        self.width = width
        self.height = height
        self.world_version = 0
        self._entities: dict[str, SpatialEntity] = {}
        self._hidden_cells: set[Pose2D] = set(hidden_cells or ())
        for entity in entities or ():
            self.set_entity(entity)

    @property
    def entities(self) -> tuple[SpatialEntity, ...]:
        return tuple(sorted(self._entities.values(), key=lambda entity: entity.entity_id))

    @property
    def hidden_cells(self) -> frozenset[Pose2D]:
        return frozenset(self._hidden_cells)

    def copy(self) -> SpatialWorldState:
        copied = SpatialWorldState(
            self.width,
            self.height,
            entities=self.entities,
            hidden_cells=self.hidden_cells,
        )
        copied.world_version = self.world_version
        return copied

    def in_bounds(self, pose: Pose2D) -> bool:
        return 0 <= pose.x < self.width and 0 <= pose.y < self.height

    def set_entity(self, entity: SpatialEntity) -> None:
        if not self.in_bounds(entity.pose):
            raise ValueError(f"entity {entity.entity_id} is out of bounds")
        self._entities[entity.entity_id] = entity
        self.world_version += 1

    def remove_entity(self, entity_id: str) -> None:
        if entity_id in self._entities:
            del self._entities[entity_id]
            self.world_version += 1

    def entity(self, entity_id: str) -> SpatialEntity:
        try:
            return self._entities[entity_id]
        except KeyError as exc:
            raise KeyError(f"unknown spatial world entity: {entity_id}") from exc

    def move_entity(self, entity_id: str, pose: Pose2D) -> None:
        if not self.in_bounds(pose):
            raise ValueError("cannot move entity out of bounds")
        self._entities[entity_id] = self.entity(entity_id).with_pose(pose)
        self.world_version += 1

    def set_obstacle(self, pose: Pose2D, obstacle_id: str | None = None) -> str:
        if not self.in_bounds(pose):
            raise ValueError("obstacle pose is out of bounds")
        entity_id = obstacle_id or f"obstacle_{pose.x}_{pose.y}"
        self.set_entity(
            SpatialEntity(
                entity_id=entity_id,
                kind="obstacle",
                label="Obstacle",
                pose=pose,
                blocks_movement=True,
            )
        )
        return entity_id

    def remove_obstacle_at(self, pose: Pose2D) -> None:
        for entity in list(self._entities.values()):
            if entity.pose == pose and entity.blocks_movement:
                self.remove_entity(entity.entity_id)

    def hide_cell(self, pose: Pose2D) -> None:
        if not self.in_bounds(pose):
            raise ValueError("hidden cell is out of bounds")
        self._hidden_cells.add(pose)
        self.world_version += 1

    def reveal_cell(self, pose: Pose2D) -> None:
        if pose in self._hidden_cells:
            self._hidden_cells.remove(pose)
            self.world_version += 1

    def is_blocked_truth(self, pose: Pose2D) -> bool:
        if not self.in_bounds(pose):
            return True
        return any(
            entity.pose == pose and entity.blocks_movement
            for entity in self._entities.values()
        )

    def observe(self, cycle_id: int, derive_relations: bool = True) -> SpatialGeometry:
        visible_entities = []
        for entity in self.entities:
            if entity.pose in self._hidden_cells and entity.kind not in {"agent", "target"}:
                continue
            visible_entities.append(entity)
        return build_spatial_geometry(
            width=self.width,
            height=self.height,
            entities=visible_entities,
            cycle_id=cycle_id,
            world_version=self.world_version,
            unknown_cells=self._hidden_cells,
            derive_relations=derive_relations,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "world_version": self.world_version,
            "entities": [entity.to_dict() for entity in self.entities],
            "hidden_cells": [pose.to_dict() for pose in sorted(self.hidden_cells)],
        }


def build_spatial_geometry(
    width: int,
    height: int,
    entities: Iterable[SpatialEntity],
    cycle_id: int,
    world_version: int = 0,
    unknown_cells: Iterable[Pose2D] = (),
    derive_relations: bool = True,
) -> SpatialGeometry:
    entity_tuple = tuple(entities)
    unknown = frozenset(unknown_cells)
    blocking_poses = {entity.pose for entity in entity_tuple if entity.blocks_movement}
    occupancy = []
    for y in range(height):
        for x in range(width):
            pose = Pose2D(x, y)
            if pose in unknown:
                state = OccupancyState.UNKNOWN
            elif pose in blocking_poses:
                state = OccupancyState.OCCUPIED
            else:
                state = OccupancyState.FREE
            occupancy.append(CellOccupancy(pose, state))
    geometry_without_relations = SpatialGeometry(
        width=width,
        height=height,
        entities=entity_tuple,
        occupancy=tuple(occupancy),
        derived_relations=(),
        cycle_id=cycle_id,
        world_version=world_version,
        _trusted_occupancy=True,
    )
    if not derive_relations:
        return geometry_without_relations
    return SpatialGeometry(
        width=width,
        height=height,
        entities=entity_tuple,
        occupancy=tuple(occupancy),
        derived_relations=_derive_spatial_relations(geometry_without_relations),
        cycle_id=cycle_id,
        world_version=world_version,
        _trusted_occupancy=True,
    )


def _derive_spatial_relations(geometry: SpatialGeometry) -> tuple[Relation, ...]:
    relations: list[Relation] = []
    entities = geometry.entities
    relation_index = 0
    for source in entities:
        for target in entities:
            if source.entity_id == target.entity_id:
                continue
            distance = source.pose.manhattan_distance(target.pose)
            for relation_type in _directional_relations(source.pose, target.pose):
                relations.append(
                    _spatial_relation(
                        relation_index,
                        source.entity_id,
                        target.entity_id,
                        relation_type,
                    )
                )
                relation_index += 1
            relations.append(
                _spatial_relation(
                    relation_index,
                    source.entity_id,
                    target.entity_id,
                    RelationType.DISTANCE,
                    value=distance,
                    unit="grid_steps",
                )
            )
            relation_index += 1
            if distance <= 1:
                relations.append(
                    _spatial_relation(
                        relation_index,
                        source.entity_id,
                        target.entity_id,
                        RelationType.NEAR,
                    )
                )
                relation_index += 1
            if distance == 0:
                relations.append(
                    _spatial_relation(
                        relation_index,
                        source.entity_id,
                        target.entity_id,
                        RelationType.COLLIDES_WITH,
                    )
                )
                relation_index += 1
    try:
        agent = geometry.agent()
        target = geometry.target()
    except KeyError:
        return tuple(relations)
    if _reachable(geometry, agent.pose, target.pose):
        relations.append(
            _spatial_relation(
                relation_index,
                agent.entity_id,
                target.entity_id,
                RelationType.REACHABLE,
            )
        )
    return tuple(relations)


def _directional_relations(source: Pose2D, target: Pose2D) -> tuple[RelationType, ...]:
    relations = []
    if source.x < target.x:
        relations.append(RelationType.LEFT_OF)
    elif source.x > target.x:
        relations.append(RelationType.RIGHT_OF)
    if source.y < target.y:
        relations.append(RelationType.ABOVE)
    elif source.y > target.y:
        relations.append(RelationType.BELOW)
    return tuple(relations)


def _spatial_relation(
    index: int,
    source_id: str,
    target_id: str,
    relation_type: RelationType,
    value: Any | None = None,
    unit: str | None = None,
) -> Relation:
    return Relation(
        relation_id=f"s{index:04d}",
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        confidence=1.0,
        provenance=Provenance.INFERRED_NOW,
        rule_id="SPATIAL_GEOMETRY_DERIVED",
        value=value,
        unit=unit,
    )


def _reachable(geometry: SpatialGeometry, start: Pose2D, goal: Pose2D) -> bool:
    if not geometry.is_traversable(start) or not geometry.is_traversable(goal):
        return False
    frontier = [start]
    seen = {start}
    while frontier:
        current = frontier.pop(0)
        if current == goal:
            return True
        for neighbor in _neighbors(current):
            if neighbor in seen or not geometry.is_traversable(neighbor):
                continue
            seen.add(neighbor)
            frontier.append(neighbor)
    return False


def _neighbors(pose: Pose2D) -> tuple[Pose2D, ...]:
    return (
        pose.moved(0, -1),
        pose.moved(1, 0),
        pose.moved(0, 1),
        pose.moved(-1, 0),
    )

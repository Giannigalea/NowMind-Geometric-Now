from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from nowmind.spatial.model import OccupancyState, Pose2D, SpatialGeometry
from nowmind.temporal.source import TemporalSource


class TransformationType(str, Enum):
    MOVE_NORTH = "move_north"
    MOVE_SOUTH = "move_south"
    MOVE_EAST = "move_east"
    MOVE_WEST = "move_west"
    WAIT = "wait"

    @property
    def delta(self) -> tuple[int, int]:
        if self is TransformationType.MOVE_NORTH:
            return (0, -1)
        if self is TransformationType.MOVE_SOUTH:
            return (0, 1)
        if self is TransformationType.MOVE_EAST:
            return (1, 0)
        if self is TransformationType.MOVE_WEST:
            return (-1, 0)
        return (0, 0)

    @property
    def movement_cost(self) -> float:
        return 0.0 if self is TransformationType.WAIT else 1.0


class ConstraintCode(str, Enum):
    OUT_OF_BOUNDS = "out_of_bounds"
    COLLISION = "collision"
    BLOCKED = "blocked"
    UNKNOWN_CELL = "unknown_cell"
    INVALID_TRANSFORMATION = "invalid_transformation"


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    code: ConstraintCode
    message: str
    pose: Pose2D | None = None
    entity_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "pose": self.pose.to_dict() if self.pose else None,
            "entity_id": self.entity_id,
        }


@dataclass(frozen=True, slots=True)
class Transformation:
    transformation_id: UUID
    transformation_type: TransformationType
    actor_id: str
    cost: float
    source_cycle_id: int
    generation_reason: str

    @classmethod
    def create(
        cls,
        transformation_type: TransformationType,
        actor_id: str = "agent",
        source_cycle_id: int = 0,
        generation_reason: str = "candidate_move",
        cost: float | None = None,
    ) -> Transformation:
        return cls(
            transformation_id=uuid4(),
            transformation_type=transformation_type,
            actor_id=actor_id,
            cost=transformation_type.movement_cost if cost is None else cost,
            source_cycle_id=source_cycle_id,
            generation_reason=generation_reason,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "transformation_id": str(self.transformation_id),
            "transformation_type": self.transformation_type.value,
            "actor_id": self.actor_id,
            "cost": self.cost,
            "source_cycle_id": self.source_cycle_id,
            "generation_reason": self.generation_reason,
        }


@dataclass(frozen=True, slots=True)
class HypotheticalGeometry:
    hypothesis_id: UUID
    parent_id: UUID | None
    created_at_cycle_id: int
    root_cycle_id: int
    depth: int
    geometry: SpatialGeometry
    transformation: Transformation
    valid: bool
    violations: tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    assumption_ids: tuple[UUID, ...] = field(default_factory=tuple)
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE

    def __post_init__(self) -> None:
        if self.provenance is not TemporalSource.HYPOTHETICAL_FUTURE:
            raise ValueError("hypothetical geometries must be HYPOTHETICAL_FUTURE")
        object.__setattr__(self, "violations", tuple(self.violations))
        object.__setattr__(self, "assumption_ids", tuple(self.assumption_ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": str(self.hypothesis_id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "created_at_cycle_id": self.created_at_cycle_id,
            "root_cycle_id": self.root_cycle_id,
            "depth": self.depth,
            "valid": self.valid,
            "violations": [violation.to_dict() for violation in self.violations],
            "assumption_ids": [str(assumption_id) for assumption_id in self.assumption_ids],
            "provenance": self.provenance.value,
            "transformation": self.transformation.to_dict(),
            "geometry": self.geometry.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class TransformationOutcome:
    transformation: Transformation
    from_pose: Pose2D
    to_pose: Pose2D
    hypothetical_geometry: HypotheticalGeometry

    @property
    def valid(self) -> bool:
        return self.hypothetical_geometry.valid

    @property
    def violations(self) -> tuple[ConstraintViolation, ...]:
        return self.hypothetical_geometry.violations

    def to_dict(self) -> dict[str, Any]:
        return {
            "transformation": self.transformation.to_dict(),
            "from_pose": self.from_pose.to_dict(),
            "to_pose": self.to_pose.to_dict(),
            "valid": self.valid,
            "violations": [violation.to_dict() for violation in self.violations],
            "hypothetical_geometry_id": str(self.hypothetical_geometry.hypothesis_id),
        }


def apply_transformation(
    geometry: SpatialGeometry,
    transformation: Transformation,
    parent: HypotheticalGeometry | None = None,
    allow_unknown: bool = False,
    assumption_ids: tuple[UUID, ...] = (),
) -> TransformationOutcome:
    actor = geometry.entity(transformation.actor_id)
    dx, dy = transformation.transformation_type.delta
    from_pose = actor.pose
    to_pose = from_pose.moved(dx, dy)
    violations = _validate_move(geometry, transformation, from_pose, to_pose, allow_unknown)
    valid = not violations
    next_geometry = (
        geometry.with_entity_pose(transformation.actor_id, to_pose) if valid else geometry
    )
    parent_id = parent.hypothesis_id if parent else None
    depth = parent.depth + 1 if parent else 1
    hypothetical = HypotheticalGeometry(
        hypothesis_id=uuid4(),
        parent_id=parent_id,
        created_at_cycle_id=geometry.cycle_id,
        root_cycle_id=parent.root_cycle_id if parent else geometry.cycle_id,
        depth=depth,
        geometry=next_geometry,
        transformation=transformation,
        valid=valid,
        violations=violations,
        assumption_ids=assumption_ids,
    )
    return TransformationOutcome(
        transformation=transformation,
        from_pose=from_pose,
        to_pose=to_pose,
        hypothetical_geometry=hypothetical,
    )


def _validate_move(
    geometry: SpatialGeometry,
    transformation: Transformation,
    from_pose: Pose2D,
    to_pose: Pose2D,
    allow_unknown: bool,
) -> tuple[ConstraintViolation, ...]:
    violations: list[ConstraintViolation] = []
    distance = from_pose.manhattan_distance(to_pose)
    expected_distance = 0 if transformation.transformation_type is TransformationType.WAIT else 1
    if distance != expected_distance:
        violations.append(
            ConstraintViolation(
                ConstraintCode.INVALID_TRANSFORMATION,
                "cardinal transformations must move exactly one cell; wait moves zero cells",
                to_pose,
                transformation.actor_id,
            )
        )
    if not geometry.in_bounds(to_pose):
        violations.append(
            ConstraintViolation(
                ConstraintCode.OUT_OF_BOUNDS,
                "candidate pose is outside the observed grid bounds",
                to_pose,
                transformation.actor_id,
            )
        )
        return tuple(violations)
    occupancy = geometry.occupancy_at(to_pose)
    if occupancy is OccupancyState.OCCUPIED:
        blocker = geometry.blocking_entity_at(to_pose)
        violations.append(
            ConstraintViolation(
                ConstraintCode.COLLISION,
                "candidate pose collides with an observed blocking entity",
                to_pose,
                blocker.entity_id if blocker else transformation.actor_id,
            )
        )
        violations.append(
            ConstraintViolation(
                ConstraintCode.BLOCKED,
                "observed occupied cells are not traversable",
                to_pose,
                transformation.actor_id,
            )
        )
    if occupancy is OccupancyState.UNKNOWN and not allow_unknown:
        violations.append(
            ConstraintViolation(
                ConstraintCode.UNKNOWN_CELL,
                "unknown cells require an explicit planning assumption",
                to_pose,
                transformation.actor_id,
            )
        )
    return tuple(violations)


def transformation_for_step(
    from_pose: Pose2D,
    to_pose: Pose2D,
    actor_id: str,
    source_cycle_id: int,
    generation_reason: str = "astar_path_step",
) -> Transformation:
    dx = to_pose.x - from_pose.x
    dy = to_pose.y - from_pose.y
    mapping = {
        (0, -1): TransformationType.MOVE_NORTH,
        (0, 1): TransformationType.MOVE_SOUTH,
        (1, 0): TransformationType.MOVE_EAST,
        (-1, 0): TransformationType.MOVE_WEST,
        (0, 0): TransformationType.WAIT,
    }
    transformation_type = mapping.get((dx, dy))
    if transformation_type is None:
        transformation_type = TransformationType.WAIT
    return Transformation.create(
        transformation_type=transformation_type,
        actor_id=actor_id,
        source_cycle_id=source_cycle_id,
        generation_reason=generation_reason,
    )

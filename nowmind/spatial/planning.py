from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import isfinite
from time import perf_counter
from typing import Any, Iterable
from uuid import UUID, uuid4

from nowmind.geometry.relation import RelationType
from nowmind.spatial.model import OccupancyState, Pose2D, SpatialGeometry
from nowmind.spatial.transformations import (
    ConstraintViolation,
    Transformation,
    TransformationOutcome,
    TransformationType,
    apply_transformation,
    transformation_for_step,
)
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource


@dataclass(frozen=True, slots=True)
class PlanningAssumption:
    assumption_id: UUID
    proposition: Proposition
    source: TemporalSource
    confidence: float
    description: str

    def __post_init__(self) -> None:
        if self.source is TemporalSource.OBSERVED_NOW:
            raise ValueError("planning assumptions must not be relabeled as observation")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("assumption confidence must be within [0, 1]")

    @classmethod
    def memory_free_cell(
        cls,
        pose: Pose2D,
        confidence: float,
        description: str = "memory reconstructed this unknown cell as free",
    ) -> PlanningAssumption:
        return cls(
            assumption_id=uuid4(),
            proposition=Proposition(
                source_id=pose.cell_id(),
                relation_type=RelationType.OCCUPANCY,
                target_id=OccupancyState.FREE.value,
            ),
            source=TemporalSource.RECONSTRUCTED_MEMORY,
            confidence=confidence,
            description=description,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "assumption_id": str(self.assumption_id),
            "proposition": self.proposition.to_dict(),
            "source": self.source.value,
            "confidence": self.confidence,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class PlanStep:
    step_index: int
    transformation: Transformation
    from_pose: Pose2D
    to_pose: Pose2D
    cost: float
    outcome: TransformationOutcome
    assumption_ids: tuple[UUID, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "assumption_ids", tuple(self.assumption_ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "transformation": self.transformation.to_dict(),
            "from_pose": self.from_pose.to_dict(),
            "to_pose": self.to_pose.to_dict(),
            "cost": self.cost,
            "valid": self.outcome.valid,
            "violations": [violation.to_dict() for violation in self.outcome.violations],
            "assumption_ids": [str(assumption_id) for assumption_id in self.assumption_ids],
            "hypothetical_geometry_id": str(
                self.outcome.hypothetical_geometry.hypothesis_id
            ),
        }


@dataclass(frozen=True, slots=True)
class RejectedAlternative:
    transformation: Transformation
    from_pose: Pose2D
    to_pose: Pose2D
    reason: str
    violations: tuple[ConstraintViolation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "violations", tuple(self.violations))

    def to_dict(self) -> dict[str, Any]:
        return {
            "transformation": self.transformation.to_dict(),
            "from_pose": self.from_pose.to_dict(),
            "to_pose": self.to_pose.to_dict(),
            "reason": self.reason,
            "violations": [violation.to_dict() for violation in self.violations],
        }


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: UUID
    created_at_cycle_id: int
    start: Pose2D
    goal: Pose2D
    steps: tuple[PlanStep, ...]
    total_cost: float
    valid: bool
    assumptions: tuple[PlanningAssumption, ...]
    conditional: bool
    rejected_alternatives: tuple[RejectedAlternative, ...]
    explanation: tuple[str, ...]
    planning_time_ms: float
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE

    def __post_init__(self) -> None:
        if self.provenance is not TemporalSource.HYPOTHETICAL_FUTURE:
            raise ValueError("plans are present hypotheses, not observations")
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "assumptions", tuple(self.assumptions))
        object.__setattr__(self, "rejected_alternatives", tuple(self.rejected_alternatives))
        object.__setattr__(self, "explanation", tuple(self.explanation))

    @property
    def planned_step_count(self) -> int:
        return len(self.steps)

    def first_step(self) -> PlanStep | None:
        return self.steps[0] if self.steps else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": str(self.plan_id),
            "created_at_cycle_id": self.created_at_cycle_id,
            "start": self.start.to_dict(),
            "goal": self.goal.to_dict(),
            "steps": [step.to_dict() for step in self.steps],
            "total_cost": self.total_cost,
            "valid": self.valid,
            "assumptions": [assumption.to_dict() for assumption in self.assumptions],
            "conditional": self.conditional,
            "rejected_alternatives": [
                alternative.to_dict() for alternative in self.rejected_alternatives
            ],
            "explanation": list(self.explanation),
            "planning_time_ms": self.planning_time_ms,
            "provenance": self.provenance.value,
        }


@dataclass(frozen=True, slots=True)
class ActionProposal:
    proposal_id: UUID
    plan_id: UUID
    step: PlanStep
    created_at_cycle_id: int
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE

    def __post_init__(self) -> None:
        if self.provenance is not TemporalSource.HYPOTHETICAL_FUTURE:
            raise ValueError("action proposals must remain hypothetical")

    @classmethod
    def from_plan(cls, plan: Plan) -> ActionProposal | None:
        first = plan.first_step()
        if first is None:
            return None
        return cls(
            proposal_id=uuid4(),
            plan_id=plan.plan_id,
            step=first,
            created_at_cycle_id=plan.created_at_cycle_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": str(self.proposal_id),
            "plan_id": str(self.plan_id),
            "created_at_cycle_id": self.created_at_cycle_id,
            "provenance": self.provenance.value,
            "step": self.step.to_dict(),
        }


class AStarPlanner:
    """Transparent A* planner for four-directional deterministic grid movement."""

    movement_order = (
        TransformationType.MOVE_EAST,
        TransformationType.MOVE_SOUTH,
        TransformationType.MOVE_WEST,
        TransformationType.MOVE_NORTH,
    )

    def __init__(
        self,
        actor_id: str = "agent",
        prefer_observed_route: bool = True,
        unknown_memory_surcharge: float = 2.0,
    ) -> None:
        self.actor_id = actor_id
        self.prefer_observed_route = prefer_observed_route
        self.unknown_memory_surcharge = unknown_memory_surcharge

    def plan(
        self,
        geometry: SpatialGeometry,
        goal: Pose2D | None = None,
        memory_reconstructions: Iterable[MemoryReconstruction] = (),
    ) -> Plan:
        started = perf_counter()
        start = geometry.entity(self.actor_id).pose
        goal = goal or geometry.target().pose
        if not geometry.in_bounds(start) or not geometry.in_bounds(goal):
            return self._invalid_plan(
                geometry,
                start,
                goal,
                ("Start or goal lies outside grid bounds.",),
                started,
            )

        assumptions_by_pose = _memory_assumptions_for_unknown_free_cells(
            geometry,
            memory_reconstructions,
        )
        attempts: list[tuple[str, dict[Pose2D, PlanningAssumption]]] = []
        if self.prefer_observed_route:
            attempts.append(("observed_only", {}))
            attempts.append(("memory_supported_unknown", assumptions_by_pose))
        else:
            attempts.append(("chronological_record_resolution", assumptions_by_pose))
            attempts.append(("observed_only", {}))

        no_route_notes: list[str] = []
        rejected = _first_step_rejections(geometry, start, source_cycle_id=geometry.cycle_id)
        for attempt_name, allowed_assumptions in attempts:
            path, cost = self._search(geometry, start, goal, allowed_assumptions)
            if path is None:
                no_route_notes.append(f"{attempt_name}: no route found")
                continue
            return self._plan_from_path(
                geometry,
                path,
                cost,
                allowed_assumptions,
                rejected,
                attempt_name,
                started,
            )
        return self._invalid_plan(
            geometry,
            start,
            goal,
            tuple(no_route_notes) or ("No traversable route found.",),
            started,
            rejected,
        )

    def _search(
        self,
        geometry: SpatialGeometry,
        start: Pose2D,
        goal: Pose2D,
        allowed_assumptions: dict[Pose2D, PlanningAssumption],
    ) -> tuple[list[Pose2D] | None, float]:
        if start == goal:
            return [start], 0.0
        if not geometry.is_traversable(start):
            return None, 0.0
        if not _traversable_for_plan(geometry, goal, allowed_assumptions):
            return None, 0.0

        frontier: list[tuple[float, float, int, int, int, Pose2D]] = []
        heappush(frontier, (start.manhattan_distance(goal), 0.0, start.y, start.x, 0, start))
        came_from: dict[Pose2D, Pose2D | None] = {start: None}
        cost_so_far: dict[Pose2D, float] = {start: 0.0}
        push_index = 1

        while frontier:
            _, current_cost, _, _, _, current = heappop(frontier)
            if current == goal:
                return _reconstruct_path(came_from, current), current_cost
            for transformation_type in self.movement_order:
                dx, dy = transformation_type.delta
                neighbor = current.moved(dx, dy)
                if not _traversable_for_plan(geometry, neighbor, allowed_assumptions):
                    continue
                step_cost = transformation_type.movement_cost
                if geometry.occupancy_at(neighbor) is OccupancyState.UNKNOWN:
                    step_cost += self.unknown_memory_surcharge
                new_cost = current_cost + step_cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    priority = new_cost + neighbor.manhattan_distance(goal)
                    heappush(
                        frontier,
                        (priority, new_cost, neighbor.y, neighbor.x, push_index, neighbor),
                    )
                    push_index += 1
        return None, 0.0

    def _plan_from_path(
        self,
        geometry: SpatialGeometry,
        path: list[Pose2D],
        total_cost: float,
        allowed_assumptions: dict[Pose2D, PlanningAssumption],
        rejected: tuple[RejectedAlternative, ...],
        attempt_name: str,
        started: float,
    ) -> Plan:
        steps: list[PlanStep] = []
        used_assumption_ids: set[UUID] = set()
        current_geometry = geometry
        parent = None
        for index, (from_pose, to_pose) in enumerate(zip(path, path[1:]), start=1):
            assumption = allowed_assumptions.get(to_pose)
            assumption_ids = (assumption.assumption_id,) if assumption else ()
            used_assumption_ids.update(assumption_ids)
            transformation = transformation_for_step(
                from_pose,
                to_pose,
                self.actor_id,
                source_cycle_id=geometry.cycle_id,
            )
            outcome = apply_transformation(
                current_geometry,
                transformation,
                parent=parent,
                allow_unknown=assumption is not None,
                assumption_ids=assumption_ids,
            )
            step_cost = transformation.cost
            if assumption is not None:
                step_cost += self.unknown_memory_surcharge
            steps.append(
                PlanStep(
                    step_index=index,
                    transformation=transformation,
                    from_pose=from_pose,
                    to_pose=to_pose,
                    cost=step_cost,
                    outcome=outcome,
                    assumption_ids=assumption_ids,
                )
            )
            parent = outcome.hypothetical_geometry
            current_geometry = outcome.hypothetical_geometry.geometry
        assumptions = tuple(
            assumption
            for assumption in allowed_assumptions.values()
            if assumption.assumption_id in used_assumption_ids
        )
        explanation = [
            "A* search with Manhattan heuristic and deterministic E,S,W,N tie-breaking.",
            "Cardinal move cost is 1; wait cost is 0.",
        ]
        if attempt_name == "observed_only":
            explanation.append("Selected a fully observed route; memory was not needed.")
        elif attempt_name == "memory_supported_unknown":
            explanation.append(
                "No fully observed route was found; route depends on reconstructed-memory assumptions."
            )
        else:
            explanation.append(
                "Chronological control used the same pathfinding quality with record-based resolution."
            )
        return Plan(
            plan_id=uuid4(),
            created_at_cycle_id=geometry.cycle_id,
            start=path[0],
            goal=path[-1],
            steps=tuple(steps),
            total_cost=total_cost,
            valid=all(step.outcome.valid for step in steps),
            assumptions=assumptions,
            conditional=bool(assumptions),
            rejected_alternatives=rejected,
            explanation=tuple(explanation),
            planning_time_ms=(perf_counter() - started) * 1000.0,
        )

    def _invalid_plan(
        self,
        geometry: SpatialGeometry,
        start: Pose2D,
        goal: Pose2D,
        explanation: tuple[str, ...],
        started: float,
        rejected: tuple[RejectedAlternative, ...] = (),
    ) -> Plan:
        return Plan(
            plan_id=uuid4(),
            created_at_cycle_id=geometry.cycle_id,
            start=start,
            goal=goal,
            steps=(),
            total_cost=0.0,
            valid=False,
            assumptions=(),
            conditional=False,
            rejected_alternatives=rejected,
            explanation=(
                "A* search with Manhattan heuristic and deterministic E,S,W,N tie-breaking.",
                *explanation,
            ),
            planning_time_ms=(perf_counter() - started) * 1000.0,
        )


class ChronologicalGeometricPlanner(AStarPlanner):
    """Fair symbolic control using chronological record-style resolution."""

    def __init__(self, actor_id: str = "agent") -> None:
        super().__init__(actor_id=actor_id, prefer_observed_route=False)


class ReactiveCurrentOnlyPlanner(AStarPlanner):
    """Restricted baseline that uses current observation only."""

    def __init__(self, actor_id: str = "agent") -> None:
        super().__init__(actor_id=actor_id, prefer_observed_route=True)

    def plan(
        self,
        geometry: SpatialGeometry,
        goal: Pose2D | None = None,
        memory_reconstructions: Iterable[MemoryReconstruction] = (),
    ) -> Plan:
        return super().plan(geometry, goal=goal, memory_reconstructions=())


def _memory_assumptions_for_unknown_free_cells(
    geometry: SpatialGeometry,
    reconstructions: Iterable[MemoryReconstruction],
) -> dict[Pose2D, PlanningAssumption]:
    assumptions: dict[Pose2D, PlanningAssumption] = {}
    for reconstruction in reconstructions:
        proposition = reconstruction.proposition
        pose = pose_from_cell_id(proposition.source_id)
        if pose is None:
            continue
        if proposition.relation_type is not RelationType.OCCUPANCY:
            continue
        if proposition.target_id != OccupancyState.FREE.value:
            continue
        if not geometry.in_bounds(pose):
            continue
        if geometry.occupancy_at(pose) is not OccupancyState.UNKNOWN:
            continue
        tags = ",".join(reconstruction.distortion_tags)
        description = "memory reconstructed this unknown cell as free"
        if tags:
            description = f"{description}; tags={tags}"
        assumptions[pose] = PlanningAssumption.memory_free_cell(
            pose,
            confidence=reconstruction.confidence,
            description=description,
        )
    return assumptions


def pose_from_cell_id(cell_id: str) -> Pose2D | None:
    if not cell_id.startswith("cell:"):
        return None
    try:
        coords = cell_id.removeprefix("cell:")
        x_raw, y_raw = coords.split(",", 1)
        return Pose2D(int(x_raw), int(y_raw))
    except ValueError:
        return None


def _traversable_for_plan(
    geometry: SpatialGeometry,
    pose: Pose2D,
    allowed_assumptions: dict[Pose2D, PlanningAssumption],
) -> bool:
    if not geometry.in_bounds(pose):
        return False
    occupancy = geometry.occupancy_at(pose)
    if occupancy is OccupancyState.OCCUPIED:
        return False
    if occupancy is OccupancyState.UNKNOWN:
        return pose in allowed_assumptions
    return True


def _reconstruct_path(came_from: dict[Pose2D, Pose2D | None], current: Pose2D) -> list[Pose2D]:
    path = [current]
    while came_from[current] is not None:
        current = came_from[current]  # type: ignore[assignment]
        path.append(current)
    path.reverse()
    return path


def _first_step_rejections(
    geometry: SpatialGeometry,
    start: Pose2D,
    source_cycle_id: int,
) -> tuple[RejectedAlternative, ...]:
    rejected = []
    for transformation_type in AStarPlanner.movement_order:
        transformation = Transformation.create(
            transformation_type,
            source_cycle_id=source_cycle_id,
            generation_reason="first_step_candidate",
        )
        outcome = apply_transformation(geometry, transformation)
        if not outcome.valid:
            reason = ", ".join(violation.code.value for violation in outcome.violations)
        else:
            reason = "not selected by lowest-cost path"
        rejected.append(
            RejectedAlternative(
                transformation=transformation,
                from_pose=start,
                to_pose=outcome.to_pose,
                reason=reason,
                violations=outcome.violations,
            )
        )
    return tuple(rejected)


def plan_cost_or_none(plan: Plan) -> float | None:
    if not plan.valid:
        return None
    if not isfinite(plan.total_cost):
        return None
    return plan.total_cost

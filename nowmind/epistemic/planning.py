from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from heapq import heappop, heappush
from statistics import mean
from time import perf_counter
from typing import Any, Iterable
from uuid import UUID, uuid4

from nowmind.geometry.relation import RelationType
from nowmind.spatial.model import OccupancyState, Pose2D
from nowmind.spatial.planning import PlanningAssumption
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource

from nowmind.epistemic.model import EpistemicCell, EpistemicGeometry, pose_from_cell_id


class EpistemicActionType(str, Enum):
    MOVE_NORTH = "move_north"
    MOVE_EAST = "move_east"
    MOVE_SOUTH = "move_south"
    MOVE_WEST = "move_west"
    SCAN = "scan"
    WAIT = "wait"

    @property
    def delta(self) -> tuple[int, int]:
        return {
            EpistemicActionType.MOVE_NORTH: (0, -1),
            EpistemicActionType.MOVE_EAST: (1, 0),
            EpistemicActionType.MOVE_SOUTH: (0, 1),
            EpistemicActionType.MOVE_WEST: (-1, 0),
            EpistemicActionType.SCAN: (0, 0),
            EpistemicActionType.WAIT: (0, 0),
        }[self]

    @property
    def is_movement(self) -> bool:
        return self in {
            EpistemicActionType.MOVE_NORTH,
            EpistemicActionType.MOVE_EAST,
            EpistemicActionType.MOVE_SOUTH,
            EpistemicActionType.MOVE_WEST,
        }


class EpistemicDecisionType(str, Enum):
    KNOWN_SAFE = "known_safe"
    CONDITIONAL_SHORTCUT = "conditional_shortcut"
    VERIFY_FIRST = "verify_first"
    EXPLORE = "explore"
    NO_ROUTE = "no_route"
    ORACLE = "oracle"


@dataclass(frozen=True, slots=True)
class EpistemicPolicyConfig:
    scan_cost: float = 2.0
    unknown_cell_penalty: float = 3.0
    memory_risk_weight: float = 8.0
    failure_penalty: float = 10.0
    verify_risk_threshold: float = 0.16
    shortcut_confidence_threshold: float = 0.82
    safe_route_margin: float = 1.0


@dataclass(frozen=True, slots=True)
class EpistemicPlanStep:
    step_index: int
    action_type: EpistemicActionType
    from_pose: Pose2D
    to_pose: Pose2D
    cost: float
    assumption_ids: tuple[UUID, ...] = field(default_factory=tuple)
    reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "assumption_ids", tuple(self.assumption_ids))

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "action_type": self.action_type.value,
            "from_pose": self.from_pose.to_dict(),
            "to_pose": self.to_pose.to_dict(),
            "cost": self.cost,
            "assumption_ids": [str(assumption_id) for assumption_id in self.assumption_ids],
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class EpistemicPlan:
    plan_id: UUID
    created_at_cycle_id: int
    decision_type: EpistemicDecisionType
    start: Pose2D
    goal: Pose2D | None
    steps: tuple[EpistemicPlanStep, ...]
    total_cost: float
    valid: bool
    assumptions: tuple[PlanningAssumption, ...]
    conditional: bool
    verification_required: bool
    explanation: tuple[str, ...]
    evidence_items_inspected: int
    memory_traces_retrieved: int
    planning_time_ms: float
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE

    def __post_init__(self) -> None:
        if self.provenance is not TemporalSource.HYPOTHETICAL_FUTURE:
            raise ValueError("epistemic plans are current hypotheses, not observation")
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "assumptions", tuple(self.assumptions))
        object.__setattr__(self, "explanation", tuple(self.explanation))

    def first_step(self) -> EpistemicPlanStep | None:
        return self.steps[0] if self.steps else None

    @property
    def uses_memory(self) -> bool:
        return any(assumption.source is TemporalSource.RECONSTRUCTED_MEMORY for assumption in self.assumptions)

    @property
    def uses_future(self) -> bool:
        return any(assumption.source is TemporalSource.HYPOTHETICAL_FUTURE for assumption in self.assumptions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": str(self.plan_id),
            "created_at_cycle_id": self.created_at_cycle_id,
            "decision_type": self.decision_type.value,
            "start": self.start.to_dict(),
            "goal": self.goal.to_dict() if self.goal else None,
            "steps": [step.to_dict() for step in self.steps],
            "total_cost": self.total_cost,
            "valid": self.valid,
            "assumptions": [assumption.to_dict() for assumption in self.assumptions],
            "conditional": self.conditional,
            "verification_required": self.verification_required,
            "explanation": list(self.explanation),
            "evidence_items_inspected": self.evidence_items_inspected,
            "memory_traces_retrieved": self.memory_traces_retrieved,
            "planning_time_ms": self.planning_time_ms,
            "provenance": self.provenance.value,
        }


class EpistemicPlanner:
    movement_order = (
        EpistemicActionType.MOVE_EAST,
        EpistemicActionType.MOVE_SOUTH,
        EpistemicActionType.MOVE_WEST,
        EpistemicActionType.MOVE_NORTH,
    )

    def __init__(
        self,
        policy: EpistemicPolicyConfig | None = None,
        use_memory: bool = True,
        use_future: bool = True,
        can_scan: bool = True,
        indexed_history: bool = False,
    ) -> None:
        self.policy = policy or EpistemicPolicyConfig()
        self.use_memory = use_memory
        self.use_future = use_future
        self.can_scan = can_scan
        self.indexed_history = indexed_history

    def plan(
        self,
        geometry: EpistemicGeometry,
        memory_reconstructions: Iterable[MemoryReconstruction] = (),
        future_hypotheses: Iterable[FutureHypothesis] = (),
        history_record_count: int = 0,
        disconfirmed_target_poses: Iterable[Pose2D] = (),
        invalidated_poses: Iterable[Pose2D] = (),
    ) -> EpistemicPlan:
        started = perf_counter()
        memories = tuple(memory_reconstructions) if self.use_memory else ()
        futures = tuple(future_hypotheses) if self.use_future else ()
        disconfirmed_targets = frozenset(disconfirmed_target_poses)
        invalidated = frozenset(invalidated_poses)
        evidence_inspected = self._evidence_items_inspected(memories, futures, history_record_count)
        if disconfirmed_targets and geometry.target_pose is None:
            return self._exploration_plan(
                geometry,
                started,
                evidence_inspected,
                len(memories),
                "Target-location assumption was disconfirmed; using deterministic frontier recovery.",
            )
        goal, goal_assumption = self._select_goal(
            geometry,
            memories,
            futures,
            disconfirmed_targets,
        )
        if goal is None:
            return self._exploration_plan(
                geometry,
                started,
                evidence_inspected,
                len(memories),
                "No current, memory, or hypothesis target location is available.",
            )

        memory_assumptions = _memory_free_assumptions(geometry, memories, invalidated)
        future_assumptions = _future_assumptions(geometry, futures, invalidated)
        all_assumptions = {**memory_assumptions, **future_assumptions}
        if goal_assumption is not None:
            all_assumptions[goal] = goal_assumption

        safe_path, safe_cost = _search(geometry, geometry.agent_pose, goal, {})
        conditional_path, conditional_cost = _search(
            geometry,
            geometry.agent_pose,
            goal,
            all_assumptions,
        )
        if safe_path is not None:
            safe_plan_score = safe_cost
        else:
            safe_plan_score = float("inf")
        conditional_score = float("inf")
        conditional_assumptions: tuple[PlanningAssumption, ...] = ()
        if conditional_path is not None:
            conditional_assumptions = _assumptions_used(conditional_path, all_assumptions)
            conditional_score = conditional_cost + _assumption_penalty(
                conditional_assumptions,
                self.policy,
            )

        should_verify = self._should_verify(
            geometry,
            safe_path,
            safe_plan_score,
            conditional_path,
            conditional_cost,
            conditional_assumptions,
        )
        if should_verify:
            return self._scan_plan(
                geometry,
                goal,
                conditional_assumptions,
                safe_plan_score,
                conditional_score,
                started,
                evidence_inspected,
                len(memories),
            )
        if goal_assumption is None and safe_path is not None and (
            conditional_path is None
            or safe_plan_score <= conditional_score + self.policy.safe_route_margin
        ):
            return self._path_plan(
                geometry,
                goal,
                safe_path,
                safe_cost,
                (),
                EpistemicDecisionType.KNOWN_SAFE,
                (
                    "Selected known-safe route through currently observed free cells.",
                    f"safe_cost={safe_plan_score:.2f}; conditional_score={conditional_score:.2f}",
                ),
                started,
                evidence_inspected,
                len(memories),
            )
        if conditional_path is not None:
            return self._path_plan(
                geometry,
                goal,
                conditional_path,
                conditional_cost,
                conditional_assumptions,
                EpistemicDecisionType.CONDITIONAL_SHORTCUT,
                (
                    "Selected conditional route; assumptions remain typed and fallible.",
                    f"safe_cost={safe_plan_score:.2f}; conditional_score={conditional_score:.2f}",
                ),
                started,
                evidence_inspected,
                len(memories),
            )
        return self._invalid_plan(
            geometry,
            goal,
            started,
            evidence_inspected,
            len(memories),
            "No known-safe or assumption-supported route was found.",
        )

    def _select_goal(
        self,
        geometry: EpistemicGeometry,
        memories: tuple[MemoryReconstruction, ...],
        futures: tuple[FutureHypothesis, ...],
        disconfirmed_target_poses: frozenset[Pose2D],
    ) -> tuple[Pose2D | None, PlanningAssumption | None]:
        if geometry.target_pose is not None:
            return geometry.target_pose, None
        if self.use_memory:
            for memory in sorted(memories, key=lambda item: (-item.confidence, item.proposition.target_id)):
                if memory.proposition.source_id != "target":
                    continue
                if memory.proposition.relation_type is not RelationType.AT:
                    continue
                pose = pose_from_cell_id(memory.proposition.target_id)
                if pose is None or not geometry.in_bounds(pose):
                    continue
                if pose in disconfirmed_target_poses:
                    continue
                if pose in geometry.visible_cells and geometry.target_pose != pose:
                    continue
                return pose, PlanningAssumption(
                    assumption_id=uuid4(),
                    proposition=memory.proposition,
                    source=TemporalSource.RECONSTRUCTED_MEMORY,
                    confidence=memory.confidence,
                    description="memory reconstructed the hidden target location",
                )
        if self.use_future:
            for hypothesis in sorted(futures, key=lambda item: (-item.confidence, item.proposition.target_id)):
                if hypothesis.proposition.source_id != "target":
                    continue
                if hypothesis.proposition.relation_type is not RelationType.AT:
                    continue
                pose = _pose_from_future(hypothesis)
                if pose is None or not geometry.in_bounds(pose):
                    continue
                return pose, PlanningAssumption(
                    assumption_id=uuid4(),
                    proposition=hypothesis.proposition,
                    source=TemporalSource.HYPOTHETICAL_FUTURE,
                    confidence=hypothesis.confidence,
                    description="future hypothesis supplied a possible target location",
                )
        return None, None

    def _should_verify(
        self,
        geometry: EpistemicGeometry,
        safe_path: list[Pose2D] | None,
        safe_score: float,
        conditional_path: list[Pose2D] | None,
        conditional_cost: float,
        assumptions: tuple[PlanningAssumption, ...],
    ) -> bool:
        if not self.can_scan or not assumptions or conditional_path is None:
            return False
        if any(geometry.cell_at(pose).quality.value == "contradictory" for pose in conditional_path):
            return True
        if geometry.scan_used:
            return False
        confidences = [assumption.confidence for assumption in assumptions]
        risk = 1.0 - mean(confidences) if confidences else 0.0
        if safe_path is not None and safe_score <= conditional_cost:
            return False
        detour = safe_score - conditional_cost if safe_path is not None else self.policy.failure_penalty
        scan_reaches_assumption = any(
            geometry.agent_pose.manhattan_distance(_pose_for_assumption(assumption) or geometry.agent_pose)
            <= geometry.sensor_config.visibility_radius + geometry.sensor_config.scan_radius_bonus
            for assumption in assumptions
        )
        if not scan_reaches_assumption:
            return False
        expected_failure_cost = risk * self.policy.failure_penalty
        verification_value = min(detour, expected_failure_cost) - self.policy.scan_cost
        return risk >= self.policy.verify_risk_threshold and verification_value > 0.0

    def _scan_plan(
        self,
        geometry: EpistemicGeometry,
        goal: Pose2D,
        assumptions: tuple[PlanningAssumption, ...],
        safe_score: float,
        conditional_score: float,
        started: float,
        evidence_items_inspected: int,
        memory_traces_retrieved: int,
    ) -> EpistemicPlan:
        step = EpistemicPlanStep(
            1,
            EpistemicActionType.SCAN,
            geometry.agent_pose,
            geometry.agent_pose,
            geometry.sensor_config.scan_cost,
            tuple(assumption.assumption_id for assumption in assumptions),
            "verify uncertain remembered/hypothesized geometry before moving",
        )
        return EpistemicPlan(
            plan_id=uuid4(),
            created_at_cycle_id=geometry.cycle_id,
            decision_type=EpistemicDecisionType.VERIFY_FIRST,
            start=geometry.agent_pose,
            goal=goal,
            steps=(step,),
            total_cost=step.cost,
            valid=True,
            assumptions=assumptions,
            conditional=True,
            verification_required=True,
            explanation=(
                "Deterministic epistemic policy selected SCAN before movement.",
                f"safe_score={safe_score:.2f}; conditional_score={conditional_score:.2f}; scan_cost={geometry.sensor_config.scan_cost:.2f}",
                "Information action changes current observation only; it does not mutate world truth.",
            ),
            evidence_items_inspected=evidence_items_inspected,
            memory_traces_retrieved=memory_traces_retrieved,
            planning_time_ms=(perf_counter() - started) * 1000.0,
        )

    def _path_plan(
        self,
        geometry: EpistemicGeometry,
        goal: Pose2D,
        path: list[Pose2D],
        cost: float,
        assumptions: tuple[PlanningAssumption, ...],
        decision_type: EpistemicDecisionType,
        explanation: tuple[str, ...],
        started: float,
        evidence_items_inspected: int,
        memory_traces_retrieved: int,
    ) -> EpistemicPlan:
        steps = []
        assumption_by_pose = {_pose_for_assumption(assumption): assumption for assumption in assumptions}
        for index, (from_pose, to_pose) in enumerate(zip(path, path[1:]), start=1):
            action_type = _action_for_step(from_pose, to_pose)
            assumption = assumption_by_pose.get(to_pose)
            assumption_ids = (assumption.assumption_id,) if assumption else ()
            steps.append(
                EpistemicPlanStep(
                    index,
                    action_type,
                    from_pose,
                    to_pose,
                    geometry.sensor_config.move_cost,
                    assumption_ids,
                    "movement through observed free cell" if assumption is None else "movement depends on typed assumption",
                )
            )
        return EpistemicPlan(
            plan_id=uuid4(),
            created_at_cycle_id=geometry.cycle_id,
            decision_type=decision_type,
            start=geometry.agent_pose,
            goal=goal,
            steps=tuple(steps),
            total_cost=cost,
            valid=True,
            assumptions=assumptions,
            conditional=bool(assumptions),
            verification_required=False,
            explanation=(
                "A* search over epistemic geometry with deterministic E,S,W,N tie-breaking.",
                *explanation,
            ),
            evidence_items_inspected=evidence_items_inspected,
            memory_traces_retrieved=memory_traces_retrieved,
            planning_time_ms=(perf_counter() - started) * 1000.0,
        )

    def _exploration_plan(
        self,
        geometry: EpistemicGeometry,
        started: float,
        evidence_items_inspected: int,
        memory_traces_retrieved: int,
        reason: str,
    ) -> EpistemicPlan:
        if self.can_scan and not geometry.scan_used and _scan_could_reveal_unknown(geometry):
            step = EpistemicPlanStep(
                1,
                EpistemicActionType.SCAN,
                geometry.agent_pose,
                geometry.agent_pose,
                geometry.sensor_config.scan_cost,
                reason="explore because target/path is unknown",
            )
            return EpistemicPlan(
                plan_id=uuid4(),
                created_at_cycle_id=geometry.cycle_id,
                decision_type=EpistemicDecisionType.EXPLORE,
                start=geometry.agent_pose,
                goal=None,
                steps=(step,),
                total_cost=step.cost,
                valid=True,
                assumptions=(),
                conditional=False,
                verification_required=True,
                explanation=(reason, "Selected SCAN as an information-gathering action."),
                evidence_items_inspected=evidence_items_inspected,
                memory_traces_retrieved=memory_traces_retrieved,
                planning_time_ms=(perf_counter() - started) * 1000.0,
            )
        frontier_path = _frontier_path(geometry)
        if frontier_path is not None and len(frontier_path) > 1:
            return self._path_plan(
                geometry,
                frontier_path[-1],
                frontier_path,
                float(len(frontier_path) - 1) * geometry.sensor_config.move_cost,
                (),
                EpistemicDecisionType.EXPLORE,
                (
                    reason,
                    "Selected deterministic nearest frontier movement for target reacquisition.",
                ),
                started,
                evidence_items_inspected,
                memory_traces_retrieved,
            )
        if self.can_scan and not geometry.scan_used:
            step = EpistemicPlanStep(
                1,
                EpistemicActionType.SCAN,
                geometry.agent_pose,
                geometry.agent_pose,
                geometry.sensor_config.scan_cost,
                reason="frontier unavailable; scan current location once",
            )
            return EpistemicPlan(
                plan_id=uuid4(),
                created_at_cycle_id=geometry.cycle_id,
                decision_type=EpistemicDecisionType.EXPLORE,
                start=geometry.agent_pose,
                goal=None,
                steps=(step,),
                total_cost=step.cost,
                valid=True,
                assumptions=(),
                conditional=False,
                verification_required=True,
                explanation=(reason, "Selected SCAN as a fallback information action."),
                evidence_items_inspected=evidence_items_inspected,
                memory_traces_retrieved=memory_traces_retrieved,
                planning_time_ms=(perf_counter() - started) * 1000.0,
            )
        return self._invalid_plan(geometry, None, started, evidence_items_inspected, memory_traces_retrieved, reason)

    def _invalid_plan(
        self,
        geometry: EpistemicGeometry,
        goal: Pose2D | None,
        started: float,
        evidence_items_inspected: int,
        memory_traces_retrieved: int,
        reason: str,
    ) -> EpistemicPlan:
        return EpistemicPlan(
            plan_id=uuid4(),
            created_at_cycle_id=geometry.cycle_id,
            decision_type=EpistemicDecisionType.NO_ROUTE,
            start=geometry.agent_pose,
            goal=goal,
            steps=(),
            total_cost=0.0,
            valid=False,
            assumptions=(),
            conditional=False,
            verification_required=False,
            explanation=(reason,),
            evidence_items_inspected=evidence_items_inspected,
            memory_traces_retrieved=memory_traces_retrieved,
            planning_time_ms=(perf_counter() - started) * 1000.0,
        )

    def _evidence_items_inspected(
        self,
        memories: tuple[MemoryReconstruction, ...],
        futures: tuple[FutureHypothesis, ...],
        history_record_count: int,
    ) -> int:
        if self.indexed_history:
            return min(len(memories), 8) + min(len(futures), 4)
        return history_record_count + len(futures)


class NowMindEpistemicPlanner(EpistemicPlanner):
    def __init__(self, policy: EpistemicPolicyConfig | None = None) -> None:
        super().__init__(
            policy=policy,
            use_memory=True,
            use_future=True,
            can_scan=True,
            indexed_history=True,
        )


class ChronologicalEpistemicPlanner(EpistemicPlanner):
    def __init__(self, policy: EpistemicPolicyConfig | None = None) -> None:
        super().__init__(
            policy=policy,
            use_memory=True,
            use_future=True,
            can_scan=True,
            indexed_history=True,
        )


class ReactiveEpistemicPlanner(EpistemicPlanner):
    def __init__(self, policy: EpistemicPolicyConfig | None = None) -> None:
        super().__init__(policy=policy, use_memory=False, use_future=False, can_scan=True)


def _memory_free_assumptions(
    geometry: EpistemicGeometry,
    memories: tuple[MemoryReconstruction, ...],
    invalidated_poses: frozenset[Pose2D] = frozenset(),
) -> dict[Pose2D, PlanningAssumption]:
    assumptions: dict[Pose2D, PlanningAssumption] = {}
    for memory in sorted(memories, key=lambda item: (-item.confidence, item.proposition.source_id)):
        if memory.proposition.relation_type is not RelationType.OCCUPANCY:
            continue
        if memory.proposition.target_id != OccupancyState.FREE.value:
            continue
        pose = pose_from_cell_id(memory.proposition.source_id)
        if pose is None or not geometry.in_bounds(pose):
            continue
        if pose in invalidated_poses:
            continue
        if geometry.occupancy_at(pose) is not OccupancyState.UNKNOWN:
            continue
        assumptions.setdefault(
            pose,
            PlanningAssumption.memory_free_cell(
                pose,
                memory.confidence,
                _memory_description(memory),
            ),
        )
    return assumptions


def _future_assumptions(
    geometry: EpistemicGeometry,
    futures: tuple[FutureHypothesis, ...],
    invalidated_poses: frozenset[Pose2D] = frozenset(),
) -> dict[Pose2D, PlanningAssumption]:
    assumptions: dict[Pose2D, PlanningAssumption] = {}
    for future in futures:
        pose = _pose_from_future(future)
        if pose is None or not geometry.in_bounds(pose):
            continue
        if pose in invalidated_poses:
            continue
        if geometry.occupancy_at(pose) is not OccupancyState.UNKNOWN:
            continue
        assumptions.setdefault(
            pose,
            PlanningAssumption(
                assumption_id=uuid4(),
                proposition=Proposition(
                    source_id=pose.cell_id(),
                    relation_type=RelationType.OCCUPANCY,
                    target_id=OccupancyState.FREE.value,
                ),
                source=TemporalSource.HYPOTHETICAL_FUTURE,
                confidence=future.confidence,
                description="future hypothesis supports this unknown cell as usable",
            ),
        )
    return assumptions


def _scan_could_reveal_unknown(geometry: EpistemicGeometry) -> bool:
    scan_radius = geometry.sensor_config.visibility_radius + geometry.sensor_config.scan_radius_bonus
    return any(
        cell.is_unknown
        and geometry.agent_pose.manhattan_distance(cell.pose) <= scan_radius
        for cell in geometry.cells
    )


def _frontier_path(geometry: EpistemicGeometry) -> list[Pose2D] | None:
    unknowns = geometry.unknown_cells
    candidates = []
    for cell in geometry.cells:
        if not cell.is_known_free:
            continue
        if cell.pose == geometry.agent_pose:
            continue
        if any(neighbor in unknowns for neighbor in _neighbor_poses(cell.pose)):
            candidates.append(cell.pose)
    candidates.sort(
        key=lambda pose: (
            geometry.agent_pose.manhattan_distance(pose),
            pose.y,
            pose.x,
        )
    )
    best_path: list[Pose2D] | None = None
    for candidate in candidates:
        path, _ = _search(geometry, geometry.agent_pose, candidate, {})
        if path is None:
            continue
        if best_path is None or len(path) < len(best_path):
            best_path = path
    return best_path


def _neighbor_poses(pose: Pose2D) -> tuple[Pose2D, ...]:
    return (
        pose.moved(1, 0),
        pose.moved(0, 1),
        pose.moved(-1, 0),
        pose.moved(0, -1),
    )


def _search(
    geometry: EpistemicGeometry,
    start: Pose2D,
    goal: Pose2D,
    assumptions: dict[Pose2D, PlanningAssumption],
) -> tuple[list[Pose2D] | None, float]:
    if start == goal:
        return [start], 0.0
    if not _traversable(geometry, start, assumptions):
        return None, 0.0
    if not _traversable(geometry, goal, assumptions):
        return None, 0.0
    frontier: list[tuple[float, float, int, int, int, Pose2D]] = []
    heappush(frontier, (start.manhattan_distance(goal), 0.0, start.y, start.x, 0, start))
    came_from: dict[Pose2D, Pose2D | None] = {start: None}
    cost_so_far: dict[Pose2D, float] = {start: 0.0}
    push_index = 1
    while frontier:
        _, current_cost, _, _, _, current = heappop(frontier)
        if current == goal:
            return _reconstruct(came_from, current), current_cost
        for action_type in EpistemicPlanner.movement_order:
            dx, dy = action_type.delta
            neighbor = current.moved(dx, dy)
            if not _traversable(geometry, neighbor, assumptions):
                continue
            step_cost = geometry.sensor_config.move_cost
            new_cost = current_cost + step_cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                came_from[neighbor] = current
                cost_so_far[neighbor] = new_cost
                priority = new_cost + neighbor.manhattan_distance(goal)
                heappush(frontier, (priority, new_cost, neighbor.y, neighbor.x, push_index, neighbor))
                push_index += 1
    return None, 0.0


def _traversable(
    geometry: EpistemicGeometry,
    pose: Pose2D,
    assumptions: dict[Pose2D, PlanningAssumption],
) -> bool:
    if not geometry.in_bounds(pose):
        return False
    occupancy = geometry.occupancy_at(pose)
    if occupancy is OccupancyState.OCCUPIED:
        return False
    if occupancy is OccupancyState.UNKNOWN:
        return pose in assumptions
    return True


def _reconstruct(came_from: dict[Pose2D, Pose2D | None], current: Pose2D) -> list[Pose2D]:
    path = [current]
    while came_from[current] is not None:
        current = came_from[current]  # type: ignore[assignment]
        path.append(current)
    path.reverse()
    return path


def _assumptions_used(
    path: list[Pose2D],
    assumptions: dict[Pose2D, PlanningAssumption],
) -> tuple[PlanningAssumption, ...]:
    seen: set[UUID] = set()
    used = []
    for pose in path:
        assumption = assumptions.get(pose)
        if assumption is not None and assumption.assumption_id not in seen:
            used.append(assumption)
            seen.add(assumption.assumption_id)
    return tuple(used)


def _assumption_penalty(
    assumptions: tuple[PlanningAssumption, ...],
    policy: EpistemicPolicyConfig,
) -> float:
    penalty = 0.0
    for assumption in assumptions:
        if assumption.source is TemporalSource.RECONSTRUCTED_MEMORY:
            penalty += (1.0 - assumption.confidence) * policy.memory_risk_weight
        elif assumption.source is TemporalSource.HYPOTHETICAL_FUTURE:
            penalty += (1.0 - assumption.confidence) * policy.unknown_cell_penalty
    return penalty


def _action_for_step(from_pose: Pose2D, to_pose: Pose2D) -> EpistemicActionType:
    dx = to_pose.x - from_pose.x
    dy = to_pose.y - from_pose.y
    for action_type in EpistemicPlanner.movement_order:
        if action_type.delta == (dx, dy):
            return action_type
    if dx == 0 and dy == 0:
        return EpistemicActionType.WAIT
    raise ValueError("epistemic path contains non-cardinal movement")


def _pose_for_assumption(assumption: PlanningAssumption) -> Pose2D | None:
    if assumption.proposition.source_id == "target":
        return pose_from_cell_id(assumption.proposition.target_id)
    return pose_from_cell_id(assumption.proposition.source_id)


def _pose_from_future(hypothesis: FutureHypothesis) -> Pose2D | None:
    raw_pose = hypothesis.metadata.get("pose")
    if isinstance(raw_pose, dict):
        return Pose2D(int(raw_pose["x"]), int(raw_pose["y"]))
    return pose_from_cell_id(hypothesis.proposition.target_id)


def _memory_description(memory: MemoryReconstruction) -> str:
    tags = ",".join(memory.distortion_tags)
    suffix = f"; tags={tags}" if tags else ""
    return f"memory reconstructed this unknown cell as free{suffix}"

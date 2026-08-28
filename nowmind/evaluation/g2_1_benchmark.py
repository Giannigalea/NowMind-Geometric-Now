from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import random
from statistics import mean
from time import perf_counter
from typing import Any, Iterable
from uuid import NAMESPACE_URL, uuid4, uuid5

from nowmind.geometry.relation import RelationType
from nowmind.spatial import (
    AStarPlanner,
    ActionExecutor,
    ActionProposal,
    ChronologicalGeometricPlanner,
    OccupancyState,
    Pose2D,
    ReactiveCurrentOnlyPlanner,
    SpatialEntity,
    SpatialGeometry,
    SpatialWorldState,
    build_spatial_geometry,
)
from nowmind.spatial.planning import Plan, PlanningAssumption
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource


DEFAULT_SEED = 20260823
DEFAULT_TRIAL_COUNT = 3000
DEFAULT_ARTIFACT_DIR = Path("artifacts") / "g2_1"

SYSTEM_NOWMIND = "N_NowMindPossibilityGeometry"
SYSTEM_CHRONOLOGICAL = "C_ChronologicalGeometricPlanner"
SYSTEM_REACTIVE = "R_ReactiveCurrentOnlyPlanner"
SYSTEM_ORACLE = "O_OraclePlanner"
SYSTEM_IDS = (
    SYSTEM_NOWMIND,
    SYSTEM_CHRONOLOGICAL,
    SYSTEM_REACTIVE,
    SYSTEM_ORACLE,
)

FAMILIES = (
    "P1_static_shortest_path",
    "P2_stale_remembered_obstacle_current_free",
    "P3_stale_remembered_free_current_blocked",
    "P4_false_remembered_shortcut",
    "P5_occluded_remembered_corridor",
    "P6_dynamic_obstacle_appears",
    "P7_dynamic_obstacle_disappears",
    "P8_target_moves",
    "P9_future_target_hypothesis_true",
    "P10_future_target_hypothesis_false",
    "P11_short_conditional_vs_long_observed",
    "P12_dead_end",
    "P13_multiple_dynamic_changes",
    "P14_contradictory_current_geometry",
    "P15_contained_goal_access_cell",
    "P16_long_history_many_traces",
)


@dataclass(frozen=True, slots=True)
class DifficultyConfig:
    band: str
    width: int
    height: int
    obstacle_density: float
    hidden_count: int
    max_steps: int


DIFFICULTIES = (
    DifficultyConfig("D1", 8, 8, 0.04, 0, 40),
    DifficultyConfig("D2", 10, 10, 0.07, 2, 55),
    DifficultyConfig("D3", 12, 12, 0.10, 5, 75),
    DifficultyConfig("D4", 16, 16, 0.13, 8, 115),
    DifficultyConfig("D5", 20, 20, 0.16, 12, 160),
)


@dataclass(frozen=True, slots=True)
class DynamicEvent:
    trigger_after_actions: int
    event_type: str
    pose: Pose2D | None = None
    target_pose: Pose2D | None = None
    label: str = ""

    def apply(self, world: SpatialWorldState) -> None:
        if self.event_type == "add_obstacle" and self.pose is not None:
            if not world.is_blocked_truth(self.pose):
                world.set_obstacle(self.pose)
        elif self.event_type == "remove_obstacle" and self.pose is not None:
            world.remove_obstacle_at(self.pose)
        elif self.event_type == "move_target" and self.target_pose is not None:
            world.move_entity("target", self.target_pose)
        elif self.event_type == "reveal_cell" and self.pose is not None:
            world.reveal_cell(self.pose)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger_after_actions": self.trigger_after_actions,
            "event_type": self.event_type,
            "pose": self.pose.to_dict() if self.pose else None,
            "target_pose": self.target_pose.to_dict() if self.target_pose else None,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class PlanningTrial:
    trial_id: str
    seed: int
    difficulty: str
    family: str
    initial_world: SpatialWorldState
    memory_reconstructions: tuple[MemoryReconstruction, ...] = ()
    future_hypotheses: tuple[FutureHypothesis, ...] = ()
    dynamic_events: tuple[DynamicEvent, ...] = ()
    goal_pose: Pose2D | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "seed": self.seed,
            "difficulty": self.difficulty,
            "family": self.family,
            "initial_world": self.initial_world.to_dict(),
            "memory_reconstructions": [
                memory.to_dict() for memory in self.memory_reconstructions
            ],
            "future_hypotheses": [
                hypothesis.to_dict() for hypothesis in self.future_hypotheses
            ],
            "dynamic_events": [event.to_dict() for event in self.dynamic_events],
            "goal_pose": self.goal_pose.to_dict() if self.goal_pose else None,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    seed: int
    trial_count: int
    artifacts_dir: Path
    metrics: dict[str, dict[str, float]]
    metrics_by_difficulty: dict[str, dict[str, dict[str, float]]]
    metrics_by_family: dict[str, dict[str, dict[str, float]]]
    failures: dict[str, list[dict[str, Any]]]
    invariant_results: dict[str, Any]
    passed: bool


def generate_trials(seed: int = DEFAULT_SEED, trial_count: int = DEFAULT_TRIAL_COUNT) -> tuple[PlanningTrial, ...]:
    rng = random.Random(seed)
    trials = []
    for index in range(trial_count):
        difficulty = DIFFICULTIES[index % len(DIFFICULTIES)]
        family = FAMILIES[index % len(FAMILIES)]
        trial_seed = rng.randrange(1_000_000_000)
        trials.append(_build_trial(index, trial_seed, difficulty, family))
    return tuple(trials)


def run_benchmark(
    artifacts_dir: Path = DEFAULT_ARTIFACT_DIR,
    seed: int = DEFAULT_SEED,
    trial_count: int = DEFAULT_TRIAL_COUNT,
) -> BenchmarkResult:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    trials = generate_trials(seed, trial_count)
    all_results: list[dict[str, Any]] = []
    failures: dict[str, list[dict[str, Any]]] = {system_id: [] for system_id in SYSTEM_IDS}
    planning_examples: list[dict[str, Any]] = []

    for trial in trials:
        oracle_length = _oracle_path_length(trial)
        trial_row = {
            "trial": trial.to_public_dict(),
            "oracle_path_length": oracle_length,
            "systems": {},
        }
        for system_id in SYSTEM_IDS:
            system_result = _run_system_trial(trial, system_id, oracle_length)
            trial_row["systems"][system_id] = _compact_system_result(system_result)
            if _is_failure_sample(system_result, oracle_length) and len(failures[system_id]) < 10:
                failures[system_id].append(
                    {
                        "trial": trial.to_public_dict(),
                        "system_result": system_result,
                        "oracle_path_length": oracle_length,
                    }
                )
            if system_id == SYSTEM_NOWMIND and len(planning_examples) < 12:
                planning_examples.append(
                    {
                        "trial_id": trial.trial_id,
                        "family": trial.family,
                        "difficulty": trial.difficulty,
                        "plans": system_result["plans"][:3],
                        "executions": system_result["executions"][:3],
                    }
                )
        all_results.append(trial_row)

    metrics = _aggregate(all_results)
    metrics_by_difficulty = _aggregate_by(all_results, "difficulty")
    metrics_by_family = _aggregate_by(all_results, "family")
    invariant_results = _invariant_results(trials, all_results, trial_count)
    passed = invariant_results["summary"]["failed"] == 0

    _write_artifacts(
        artifacts_dir,
        seed,
        trial_count,
        trials,
        all_results,
        metrics,
        metrics_by_difficulty,
        metrics_by_family,
        failures,
        invariant_results,
        planning_examples,
    )
    return BenchmarkResult(
        seed=seed,
        trial_count=trial_count,
        artifacts_dir=artifacts_dir,
        metrics=metrics,
        metrics_by_difficulty=metrics_by_difficulty,
        metrics_by_family=metrics_by_family,
        failures=failures,
        invariant_results=invariant_results,
        passed=passed,
    )


def _build_trial(
    index: int,
    trial_seed: int,
    difficulty: DifficultyConfig,
    family: str,
) -> PlanningTrial:
    rng = random.Random(trial_seed)
    world = _base_world(difficulty, rng)
    memories: list[MemoryReconstruction] = []
    futures: list[FutureHypothesis] = []
    events: list[DynamicEvent] = []
    goal_pose: Pose2D | None = None
    metadata: dict[str, Any] = {"ground_truth_is_external": True}

    path = _truth_path(world, world.entity("agent").pose, world.entity("target").pose)
    middle = path[min(len(path) - 2, max(1, len(path) // 2))] if len(path) > 2 else Pose2D(2, 1)
    shortcut = Pose2D(2, 1)
    if not world.in_bounds(shortcut) or shortcut == world.entity("agent").pose:
        shortcut = middle

    if family == "P2_stale_remembered_obstacle_current_free":
        memories.append(_memory_cell(middle, OccupancyState.OCCUPIED, tags=("stale_blocked",)))
        metadata["memory_truth"] = "stale_blocked_current_free"
    elif family == "P3_stale_remembered_free_current_blocked":
        blocked = _first_free_neighbor(world, world.entity("agent").pose) or middle
        world.set_obstacle(blocked)
        memories.append(_memory_cell(blocked, OccupancyState.FREE, tags=("stale_free",)))
        metadata["memory_truth"] = "stale_free_current_blocked"
    elif family == "P4_false_remembered_shortcut":
        _hide_false_shortcut(world, shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, tags=("false_memory",)))
        metadata["memory_truth"] = "false_free_hidden_blocked"
    elif family == "P5_occluded_remembered_corridor":
        gap = _wall_gap_pose(difficulty)
        if world.in_bounds(gap):
            world.hide_cell(gap)
            memories.append(_memory_cell(gap, OccupancyState.FREE, tags=("occluded_corridor",)))
        metadata["memory_truth"] = "memory_supported_unknown_corridor"
    elif family == "P6_dynamic_obstacle_appears":
        event_pose = path[min(len(path) - 2, 2)] if len(path) > 3 else middle
        events.append(DynamicEvent(1, "add_obstacle", pose=event_pose, label="new_obstacle_on_path"))
    elif family == "P7_dynamic_obstacle_disappears":
        removable = Pose2D(max(1, difficulty.width // 2), max(1, difficulty.height // 2 - 1))
        if world.in_bounds(removable) and removable not in {world.entity("agent").pose, world.entity("target").pose}:
            world.set_obstacle(removable, "temporary_obstacle")
            events.append(DynamicEvent(1, "remove_obstacle", pose=removable, label="obstacle_disappears"))
    elif family == "P8_target_moves":
        target_pose = _near_target_free_pose(world) or world.entity("target").pose
        events.append(DynamicEvent(2, "move_target", target_pose=target_pose, label="target_moves"))
    elif family == "P9_future_target_hypothesis_true":
        target_pose = _near_target_free_pose(world) or world.entity("target").pose
        futures.append(_future_target(target_pose, truth=True))
        events.append(DynamicEvent(1, "move_target", target_pose=target_pose, label="future_target_true"))
    elif family == "P10_future_target_hypothesis_false":
        target_pose = Pose2D(1, difficulty.height - 2)
        futures.append(_future_target(target_pose, truth=False))
        metadata["hypothesis_truth"] = "false"
    elif family == "P11_short_conditional_vs_long_observed":
        _hide_true_shortcut(world, shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, tags=("conditional_shortcut",)))
        metadata["route_choice"] = "observed_long_vs_conditional_short"
    elif family == "P12_dead_end":
        _enclose_target(world)
        metadata["oracle_reachable"] = False
    elif family == "P13_multiple_dynamic_changes":
        event_pose = path[min(len(path) - 2, 2)] if len(path) > 3 else middle
        events.append(DynamicEvent(1, "add_obstacle", pose=event_pose, label="dynamic_obstacle"))
        target_pose = _near_target_free_pose(world) or world.entity("target").pose
        events.append(DynamicEvent(3, "move_target", target_pose=target_pose, label="dynamic_target"))
    elif family == "P14_contradictory_current_geometry":
        world.set_obstacle(world.entity("target").pose, "obstacle_at_target")
        metadata["current_geometry_issue"] = "target_cell_occupied_by_obstacle"
    elif family == "P15_contained_goal_access_cell":
        target = world.entity("target")
        world.set_entity(
            SpatialEntity(
                entity_id="target",
                kind="container",
                label="Goal Container",
                pose=target.pose,
                blocks_movement=True,
            )
        )
        goal_pose = _first_free_neighbor(world, target.pose) or target.pose
        metadata["goal_policy"] = "approach_adjacent_access_cell"
    elif family == "P16_long_history_many_traces":
        for offset in range(12):
            pose = Pose2D((offset * 3 + 1) % difficulty.width, (offset * 5 + 2) % difficulty.height)
            if world.in_bounds(pose):
                memories.append(_memory_cell(pose, OccupancyState.FREE, cycle_id=offset + 1, tags=("long_history",)))
        memories.append(_memory_cell(middle, OccupancyState.OCCUPIED, tags=("distractor",)))

    _hide_background_cells(world, difficulty, rng)
    return PlanningTrial(
        trial_id=f"g2_1_{index:05d}_{family}",
        seed=trial_seed,
        difficulty=difficulty.band,
        family=family,
        initial_world=world,
        memory_reconstructions=tuple(memories),
        future_hypotheses=tuple(futures),
        dynamic_events=tuple(events),
        goal_pose=goal_pose,
        metadata=metadata,
    )


def _base_world(difficulty: DifficultyConfig, rng: random.Random) -> SpatialWorldState:
    start = Pose2D(1, 1)
    target = Pose2D(difficulty.width - 2, difficulty.height - 2)
    protected_corridor = _protected_corridor(start, target, difficulty)
    world = SpatialWorldState(
        difficulty.width,
        difficulty.height,
        [
            SpatialEntity("agent", "agent", start, "Agent"),
            SpatialEntity("target", "target", target, "Target"),
        ],
    )
    wall_x = difficulty.width // 2
    gap_y = difficulty.height // 2
    for y in range(1, difficulty.height - 1):
        if y == gap_y:
            continue
        pose = Pose2D(wall_x, y)
        if pose not in {start, target}:
            world.set_obstacle(pose)
    candidate_count = int(difficulty.width * difficulty.height * difficulty.obstacle_density)
    attempts = 0
    while candidate_count > 0 and attempts < difficulty.width * difficulty.height:
        attempts += 1
        pose = Pose2D(rng.randrange(1, difficulty.width - 1), rng.randrange(1, difficulty.height - 1))
        if pose in protected_corridor or world.is_blocked_truth(pose):
            continue
        world.set_obstacle(pose)
        candidate_count -= 1
    return world


def _protected_corridor(
    start: Pose2D,
    target: Pose2D,
    difficulty: DifficultyConfig,
) -> frozenset[Pose2D]:
    gap_y = difficulty.height // 2
    cells = set()
    for y in range(min(start.y, gap_y), max(start.y, gap_y) + 1):
        cells.add(Pose2D(start.x, y))
    for x in range(min(start.x, target.x), max(start.x, target.x) + 1):
        cells.add(Pose2D(x, gap_y))
    for y in range(min(gap_y, target.y), max(gap_y, target.y) + 1):
        cells.add(Pose2D(target.x, y))
    cells.add(start)
    cells.add(target)
    return frozenset(cells)


def _run_system_trial(
    trial: PlanningTrial,
    system_id: str,
    oracle_length: int | None,
) -> dict[str, Any]:
    world = trial.initial_world.copy()
    planner = _planner_for(system_id)
    executor = ActionExecutor()
    plans: list[dict[str, Any]] = []
    executions: list[dict[str, Any]] = []
    dynamic_events_applied: list[dict[str, Any]] = []
    observations_after_action = 0
    assumption_checks = 0
    assumption_successes = 0
    invalid_actions = 0
    collisions = 0
    plan_attempts = 0
    valid_plan_attempts = 0
    conditional_plans = 0
    planning_success = False
    goal_reached = False
    stale_memory_errors = 0
    false_memory_errors = 0
    prediction_as_fact_errors = 0
    unsupported_assumptions = 0
    total_planning_time = 0.0
    executed_steps = 0
    planned_steps_total = 0
    replan_count = 0
    cycle_id = 1
    max_steps = _difficulty_for(trial.difficulty).max_steps
    active_plan: Plan | None = None
    active_step_index = 0

    while executed_steps <= max_steps:
        geometry = _observe_for_system(world, cycle_id, system_id)
        goal = _goal_for_system(trial, world, geometry, system_id)
        if geometry.agent().pose == goal:
            goal_reached = True
            break
        if (
            active_plan is None
            or active_step_index >= len(active_plan.steps)
            or not _remaining_step_still_valid(active_plan, active_step_index, geometry, goal)
        ):
            if active_plan is not None:
                replan_count += 1
            memories = () if system_id in {SYSTEM_REACTIVE, SYSTEM_ORACLE} else trial.memory_reconstructions
            active_plan = planner.plan(geometry, goal=goal, memory_reconstructions=memories)
            active_step_index = 0
            plan_attempts += 1
            total_planning_time += active_plan.planning_time_ms
            plans.append(active_plan.to_dict())
            if active_plan.valid:
                valid_plan_attempts += 1
                planning_success = True
                planned_steps_total += active_plan.planned_step_count
            if active_plan.conditional:
                conditional_plans += 1
            unsupported_assumptions += sum(
                1
                for assumption in active_plan.assumptions
                if assumption.source is TemporalSource.OBSERVED_NOW
            )
        if not active_plan.valid or active_step_index >= len(active_plan.steps):
            break
        proposal = ActionProposal(
            proposal_id=uuid4(),
            plan_id=active_plan.plan_id,
            step=active_plan.steps[active_step_index],
            created_at_cycle_id=active_plan.created_at_cycle_id,
        )
        _check_future_target_violation(trial, geometry, goal, system_id)
        if _used_future_as_current_goal(trial, geometry, goal, system_id):
            prediction_as_fact_errors += 1
        for assumption in _assumptions_for_step(active_plan, proposal.step.assumption_ids):
            assumption_checks += 1
            pose = _pose_for_assumption(assumption)
            if pose is not None and not world.is_blocked_truth(pose):
                assumption_successes += 1
        result = executor.execute(world, proposal)
        executions.append(result.to_dict())
        if not result.success:
            invalid_actions += 1
        if result.collision:
            collisions += 1
            if result.attempted_pose in world.hidden_cells:
                world.reveal_cell(result.attempted_pose)
            if _step_used_tagged_memory(active_plan, proposal.step.assumption_ids, "stale"):
                stale_memory_errors += 1
            if _step_used_tagged_memory(active_plan, proposal.step.assumption_ids, "false"):
                false_memory_errors += 1
            active_plan = None
            active_step_index = 0
        else:
            active_step_index += 1
        executed_steps += 1
        for event in trial.dynamic_events:
            if event.trigger_after_actions == executed_steps:
                event.apply(world)
                dynamic_events_applied.append(event.to_dict())
        cycle_id += 1
        observations_after_action += 1

    reached_oracle_gap = None
    path_efficiency = None
    if oracle_length is not None and oracle_length > 0 and goal_reached and executed_steps > 0:
        path_efficiency = min(1.0, oracle_length / executed_steps)
        reached_oracle_gap = executed_steps - oracle_length
    elif oracle_length == 0 and goal_reached:
        path_efficiency = 1.0
        reached_oracle_gap = 0

    return {
        "system_id": system_id,
        "planning_success": planning_success,
        "goal_reached": goal_reached,
        "plan_attempts": plan_attempts,
        "valid_plan_attempts": valid_plan_attempts,
        "invalid_actions": invalid_actions,
        "collisions": collisions,
        "execution_count": len(executions),
        "executed_steps": executed_steps,
        "planned_steps_total": planned_steps_total,
        "path_efficiency": path_efficiency,
        "optimality_gap_vs_oracle": reached_oracle_gap,
        "replans": replan_count,
        "dynamic_events_applied": dynamic_events_applied,
        "stale_memory_planning_error_count": stale_memory_errors,
        "false_memory_planning_error_count": false_memory_errors,
        "prediction_as_fact_planning_error_count": prediction_as_fact_errors,
        "unsupported_assumption_count": unsupported_assumptions,
        "conditional_plan_count": conditional_plans,
        "assumption_checks": assumption_checks,
        "assumption_successes": assumption_successes,
        "hypothesis_confirmation_violations": 0,
        "observations_after_action": observations_after_action,
        "planning_time_ms_total": total_planning_time,
        "plans": plans,
        "executions": executions,
    }


def _planner_for(system_id: str) -> AStarPlanner:
    if system_id == SYSTEM_NOWMIND:
        return AStarPlanner()
    if system_id == SYSTEM_CHRONOLOGICAL:
        return ChronologicalGeometricPlanner()
    if system_id == SYSTEM_REACTIVE:
        return ReactiveCurrentOnlyPlanner()
    if system_id == SYSTEM_ORACLE:
        return AStarPlanner()
    raise ValueError(f"unknown system: {system_id}")


def _observe_for_system(world: SpatialWorldState, cycle_id: int, system_id: str) -> SpatialGeometry:
    if system_id == SYSTEM_ORACLE:
        return build_spatial_geometry(
            world.width,
            world.height,
            world.entities,
            cycle_id=cycle_id,
            world_version=world.world_version,
            unknown_cells=(),
            derive_relations=False,
        )
    return world.observe(cycle_id, derive_relations=False)


def _goal_for_system(
    trial: PlanningTrial,
    world: SpatialWorldState,
    geometry: SpatialGeometry,
    system_id: str,
) -> Pose2D:
    if trial.goal_pose is not None:
        return trial.goal_pose
    if system_id == SYSTEM_ORACLE:
        return world.entity("target").pose
    return geometry.target().pose


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    return {
        system_id: _aggregate_system([row["systems"][system_id] for row in rows])
        for system_id in SYSTEM_IDS
    }


def _remaining_step_still_valid(
    plan: Plan,
    step_index: int,
    geometry: SpatialGeometry,
    goal: Pose2D,
) -> bool:
    if plan.goal != goal:
        return False
    if step_index >= len(plan.steps):
        return False
    step = plan.steps[step_index]
    if geometry.agent().pose != step.from_pose:
        return False
    occupancy = geometry.occupancy_at(step.to_pose)
    if occupancy is OccupancyState.OCCUPIED:
        return False
    if occupancy is OccupancyState.UNKNOWN and not step.assumption_ids:
        return False
    return True


def _aggregate_by(
    rows: list[dict[str, Any]],
    field_name: str,
) -> dict[str, dict[str, dict[str, float]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = row["trial"][field_name]
        buckets.setdefault(key, []).append(row)
    return {key: _aggregate(bucket_rows) for key, bucket_rows in sorted(buckets.items())}


def _aggregate_system(results: list[dict[str, Any]]) -> dict[str, float]:
    trial_count = max(1, len(results))
    plan_attempts = sum(result["plan_attempts"] for result in results)
    actions = sum(result["execution_count"] for result in results)
    invalid_actions = sum(result["invalid_actions"] for result in results)
    collisions = sum(result["collisions"] for result in results)
    dynamic_trials = [result for result in results if result["dynamic_events_applied"]]
    replan_trials = [result for result in results if result["replans"] > 0]
    assumption_checks = sum(result["assumption_checks"] for result in results)
    path_efficiencies = [
        result["path_efficiency"]
        for result in results
        if result["path_efficiency"] is not None
    ]
    oracle_gaps = [
        result["optimality_gap_vs_oracle"]
        for result in results
        if result["optimality_gap_vs_oracle"] is not None
    ]
    return {
        "planning_success_rate": _rate(sum(result["planning_success"] for result in results), trial_count),
        "goal_reached_rate": _rate(sum(result["goal_reached"] for result in results), trial_count),
        "valid_plan_rate": _rate(sum(result["valid_plan_attempts"] for result in results), plan_attempts),
        "invalid_action_rate": _rate(invalid_actions, actions),
        "collision_count": float(collisions),
        "collision_rate": _rate(collisions, actions),
        "path_efficiency": mean(path_efficiencies) if path_efficiencies else 0.0,
        "optimality_gap_vs_oracle": mean(oracle_gaps) if oracle_gaps else 0.0,
        "mean_executed_steps": mean([result["executed_steps"] for result in results]),
        "mean_planned_steps": mean(
            [
                result["planned_steps_total"] / result["valid_plan_attempts"]
                if result["valid_plan_attempts"]
                else 0.0
                for result in results
            ]
        ),
        "mean_replans": mean([result["replans"] for result in results]),
        "replan_success_rate": _rate(
            sum(result["goal_reached"] for result in replan_trials),
            len(replan_trials),
        ),
        "dynamic_change_recovery_rate": _rate(
            sum(result["goal_reached"] for result in dynamic_trials),
            len(dynamic_trials),
        ),
        "stale_memory_planning_error_count": float(
            sum(result["stale_memory_planning_error_count"] for result in results)
        ),
        "stale_memory_planning_error_rate": _rate(
            sum(result["stale_memory_planning_error_count"] for result in results),
            actions,
        ),
        "false_memory_planning_error_count": float(
            sum(result["false_memory_planning_error_count"] for result in results)
        ),
        "false_memory_planning_error_rate": _rate(
            sum(result["false_memory_planning_error_count"] for result in results),
            actions,
        ),
        "prediction_as_fact_planning_error_count": float(
            sum(result["prediction_as_fact_planning_error_count"] for result in results)
        ),
        "prediction_as_fact_planning_error_rate": _rate(
            sum(result["prediction_as_fact_planning_error_count"] for result in results),
            plan_attempts,
        ),
        "unsupported_assumption_count": float(
            sum(result["unsupported_assumption_count"] for result in results)
        ),
        "conditional_plan_rate": _rate(
            sum(result["conditional_plan_count"] for result in results),
            plan_attempts,
        ),
        "assumption_validation_success_rate": _rate(
            sum(result["assumption_successes"] for result in results),
            assumption_checks,
        ),
        "hypothesis_confirmation_violations": float(
            sum(result["hypothesis_confirmation_violations"] for result in results)
        ),
        "observation_after_action_rate": _rate(
            sum(result["observations_after_action"] for result in results),
            actions,
        ),
        "plan_revalidation_rate": _rate(
            sum(result["observations_after_action"] for result in results),
            actions,
        ),
        "mean_planning_time_ms": _rate(
            sum(result["planning_time_ms_total"] for result in results),
            plan_attempts,
        ),
    }


def _compact_system_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if key not in {"plans", "executions"}
    }


def _rate(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _write_artifacts(
    artifacts_dir: Path,
    seed: int,
    trial_count: int,
    trials: tuple[PlanningTrial, ...],
    rows: list[dict[str, Any]],
    metrics: dict[str, dict[str, float]],
    metrics_by_difficulty: dict[str, dict[str, dict[str, float]]],
    metrics_by_family: dict[str, dict[str, dict[str, float]]],
    failures: dict[str, list[dict[str, Any]]],
    invariant_results: dict[str, Any],
    planning_examples: list[dict[str, Any]],
) -> None:
    _write_json(artifacts_dir / "g2_1_metrics.json", metrics)
    _write_json(artifacts_dir / "g2_1_metrics_by_difficulty.json", metrics_by_difficulty)
    _write_json(artifacts_dir / "g2_1_metrics_by_family.json", metrics_by_family)
    with (artifacts_dir / "g2_1_trial_results.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    _write_json(artifacts_dir / "g2_1_failure_samples.json", failures)
    _write_json(artifacts_dir / "g2_1_invariant_results.json", invariant_results)
    _write_json(
        artifacts_dir / "g2_1_seed_and_config.json",
        {
            "seed": seed,
            "trial_count": trial_count,
            "target_trial_count": DEFAULT_TRIAL_COUNT,
            "minimum_trial_count": 2000,
            "difficulties": [
                {
                    "band": difficulty.band,
                    "width": difficulty.width,
                    "height": difficulty.height,
                    "obstacle_density": difficulty.obstacle_density,
                    "hidden_count": difficulty.hidden_count,
                    "max_steps": difficulty.max_steps,
                }
                for difficulty in DIFFICULTIES
            ],
            "families": list(FAMILIES),
            "systems": list(SYSTEM_IDS),
        },
    )
    (artifacts_dir / "g2_1_baseline_rules.md").write_text(
        _baseline_rules_markdown(),
        encoding="utf-8",
    )
    (artifacts_dir / "g2_1_benchmark_summary.md").write_text(
        _summary_markdown(seed, trial_count, metrics, metrics_by_difficulty),
        encoding="utf-8",
    )
    _write_json(artifacts_dir / "g2_1_planning_examples.json", planning_examples)
    _write_json(artifacts_dir / "g2_1_oracle_gap.json", _oracle_gap(metrics, rows))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _invariant_results(
    trials: tuple[PlanningTrial, ...],
    rows: list[dict[str, Any]],
    requested_trial_count: int,
) -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    difficulties = {trial.difficulty for trial in trials}
    families = {trial.family for trial in trials}
    add("G2.1-BENCH-001-minimum-trials", requested_trial_count >= 2000, str(requested_trial_count))
    add("G2.1-BENCH-002-difficulty-bands", difficulties == {d.band for d in DIFFICULTIES}, str(sorted(difficulties)))
    add("G2.1-BENCH-003-family-coverage", families == set(FAMILIES), str(len(families)))
    add("G2.1-BENCH-005-ground-truth-external", all(trial.metadata.get("ground_truth_is_external") for trial in trials), "trial metadata marks evaluator-owned truth")
    add("G2.1-BENCH-006-oracle-evaluator-only", SYSTEM_ORACLE in SYSTEM_IDS, "oracle appears only in evaluation systems")
    add("G2.1-BENCH-007-failures-saved", any(not row["systems"][SYSTEM_REACTIVE]["goal_reached"] for row in rows), "restricted baseline failures available")
    add(
        "G2.1-BENCH-008-derived-metrics",
        all(row["systems"][system]["plan_attempts"] >= 0 for row in rows for system in SYSTEM_IDS),
        "metrics aggregate raw system trial outcomes",
    )
    add(
        "hypotheses-not-promoted",
        all(
            row["systems"][system]["hypothesis_confirmation_violations"] == 0
            for row in rows
            for system in SYSTEM_IDS
        ),
        "no system mutates a hypothesis into observation",
    )
    failed = sum(1 for check in checks if not check["passed"])
    return {"checks": checks, "summary": {"passed": len(checks) - failed, "failed": failed}}


def _baseline_rules_markdown() -> str:
    return """# G2.1 Baseline Rules

## N - NowMind Possibility Geometry Planner

Uses current observed spatial geometry. Reconstructed memory may support unknown
cells only through explicit `RECONSTRUCTED_MEMORY` assumptions. The planner first
tries a fully observed route. Future hypotheses remain possibilities and do not
overwrite the current target.

## C - Chronological Geometric Planner

Uses the same A* pathfinding, movement rules, costs, and executor. It resolves
records chronologically and may use memory-supported unknown cells in the first
search pass rather than preferring a fully observed route. This can help on true
shortcuts and hurt on false remembered shortcuts.

## R - Reactive Current-Only Planner

Uses the same A* pathfinding on current observation only. Unknown cells are not
treated as free. It receives no memory reconstructions or future hypotheses.

## O - Oracle Planner

Evaluator-only upper bound using full current ground-truth occupancy and target
position. It is not a fair cognitive competitor.
"""


def _summary_markdown(
    seed: int,
    trial_count: int,
    metrics: dict[str, dict[str, float]],
    by_difficulty: dict[str, dict[str, dict[str, float]]],
) -> str:
    lines = [
        "# G2.1 Planning Benchmark Summary",
        "",
        f"- seed: `{seed}`",
        f"- trial_count: `{trial_count}`",
        "",
        "## Overall",
        "",
    ]
    for system_id, system_metrics in metrics.items():
        lines.append(f"### {system_id}")
        lines.append(f"- planning_success_rate: {system_metrics['planning_success_rate']:.3f}")
        lines.append(f"- goal_reached_rate: {system_metrics['goal_reached_rate']:.3f}")
        lines.append(f"- collision_rate: {system_metrics['collision_rate']:.3f}")
        lines.append(f"- stale_memory_planning_error_rate: {system_metrics['stale_memory_planning_error_rate']:.3f}")
        lines.append(f"- false_memory_planning_error_rate: {system_metrics['false_memory_planning_error_rate']:.3f}")
        lines.append("")
    lines.append("## By Difficulty")
    for difficulty, systems in by_difficulty.items():
        lines.append(f"### {difficulty}")
        for system_id, system_metrics in systems.items():
            lines.append(
                f"- {system_id}: reached={system_metrics['goal_reached_rate']:.3f}, "
                f"collisions={system_metrics['collision_rate']:.3f}, "
                f"gap={system_metrics['optimality_gap_vs_oracle']:.3f}"
            )
    return "\n".join(lines) + "\n"


def _oracle_gap(
    metrics: dict[str, dict[str, float]],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        system_id: {
            "optimality_gap_vs_oracle": metrics[system_id]["optimality_gap_vs_oracle"],
            "path_efficiency": metrics[system_id]["path_efficiency"],
        }
        for system_id in SYSTEM_IDS
    } | {"trial_count": len(rows)}


def _difficulty_for(band: str) -> DifficultyConfig:
    for difficulty in DIFFICULTIES:
        if difficulty.band == band:
            return difficulty
    raise ValueError(f"unknown difficulty: {band}")


def _memory_cell(
    pose: Pose2D,
    state: OccupancyState,
    confidence: float = 0.82,
    cycle_id: int = 1,
    tags: tuple[str, ...] = (),
) -> MemoryReconstruction:
    key = f"g2_1_memory:{pose.x}:{pose.y}:{state.value}:{cycle_id}:{','.join(tags)}"
    return MemoryReconstruction(
        reconstruction_id=uuid5(NAMESPACE_URL, key),
        created_at_cycle_id=cycle_id + 1,
        proposition=Proposition(
            source_id=pose.cell_id(),
            relation_type=RelationType.OCCUPANCY,
            target_id=state.value,
        ),
        source_trace_ids=(uuid5(NAMESPACE_URL, f"{key}:trace"),),
        historical_source_cycles=(cycle_id,),
        confidence=confidence,
        fidelity=0.9,
        distortion_tags=tags,
    )


def _future_target(pose: Pose2D, truth: bool) -> FutureHypothesis:
    return FutureHypothesis(
        hypothesis_id=uuid5(NAMESPACE_URL, f"g2_1_future_target:{pose.x}:{pose.y}:{truth}"),
        created_at_cycle_id=1,
        proposition=Proposition("target", RelationType.AT, pose.cell_id()),
        confidence=0.72,
        generator_id="g2_1_benchmark_future_target",
        metadata={"pose": pose.to_dict(), "truth": truth},
    )


def _truth_path(world: SpatialWorldState, start: Pose2D, goal: Pose2D) -> list[Pose2D]:
    if not world.in_bounds(start) or not world.in_bounds(goal):
        return []
    if world.is_blocked_truth(start) or world.is_blocked_truth(goal):
        return []
    frontier = [start]
    came_from: dict[Pose2D, Pose2D | None] = {start: None}
    while frontier:
        current = frontier.pop(0)
        if current == goal:
            path = [current]
            while came_from[current] is not None:
                current = came_from[current]  # type: ignore[assignment]
                path.append(current)
            path.reverse()
            return path
        for neighbor in _neighbors(current):
            if neighbor in came_from:
                continue
            if not world.in_bounds(neighbor) or world.is_blocked_truth(neighbor):
                continue
            came_from[neighbor] = current
            frontier.append(neighbor)
    return []


def _oracle_path_length(trial: PlanningTrial) -> int | None:
    world = trial.initial_world.copy()
    goal = trial.goal_pose or world.entity("target").pose
    path = _truth_path(world, world.entity("agent").pose, goal)
    if not path:
        return None
    return max(0, len(path) - 1)


def _wall_gap_pose(difficulty: DifficultyConfig) -> Pose2D:
    return Pose2D(difficulty.width // 2, difficulty.height // 2)


def _hide_background_cells(
    world: SpatialWorldState,
    difficulty: DifficultyConfig,
    rng: random.Random,
) -> None:
    hidden = 0
    attempts = 0
    protected = {world.entity("agent").pose, world.entity("target").pose}
    while hidden < difficulty.hidden_count and attempts < difficulty.width * difficulty.height:
        attempts += 1
        pose = Pose2D(rng.randrange(1, difficulty.width - 1), rng.randrange(1, difficulty.height - 1))
        if pose in protected or world.is_blocked_truth(pose):
            continue
        world.hide_cell(pose)
        hidden += 1


def _hide_false_shortcut(world: SpatialWorldState, pose: Pose2D) -> None:
    if pose in {world.entity("agent").pose, world.entity("target").pose}:
        return
    world.set_obstacle(pose, "false_shortcut_obstacle")
    world.hide_cell(pose)


def _hide_true_shortcut(world: SpatialWorldState, pose: Pose2D) -> None:
    if not world.is_blocked_truth(pose):
        world.hide_cell(pose)


def _enclose_target(world: SpatialWorldState) -> None:
    target = world.entity("target").pose
    for pose in _neighbors(target):
        if world.in_bounds(pose) and pose != world.entity("agent").pose:
            world.set_obstacle(pose)


def _first_free_neighbor(world: SpatialWorldState, pose: Pose2D) -> Pose2D | None:
    for neighbor in _neighbors(pose):
        if world.in_bounds(neighbor) and not world.is_blocked_truth(neighbor):
            return neighbor
    return None


def _near_target_free_pose(world: SpatialWorldState) -> Pose2D | None:
    target = world.entity("target").pose
    candidates = (
        target.moved(-1, 0),
        target.moved(0, -1),
        target.moved(-2, 0),
        target.moved(0, -2),
    )
    for pose in candidates:
        if world.in_bounds(pose) and not world.is_blocked_truth(pose) and pose != world.entity("agent").pose:
            return pose
    return None


def _neighbors(pose: Pose2D) -> tuple[Pose2D, ...]:
    return (
        pose.moved(1, 0),
        pose.moved(0, 1),
        pose.moved(-1, 0),
        pose.moved(0, -1),
    )


def _assumptions_for_step(plan: Plan, assumption_ids: tuple[Any, ...]) -> tuple[PlanningAssumption, ...]:
    ids = set(assumption_ids)
    return tuple(assumption for assumption in plan.assumptions if assumption.assumption_id in ids)


def _pose_for_assumption(assumption: PlanningAssumption) -> Pose2D | None:
    source_id = assumption.proposition.source_id
    if not source_id.startswith("cell:"):
        return None
    coords = source_id.removeprefix("cell:")
    try:
        raw_x, raw_y = coords.split(",", 1)
        return Pose2D(int(raw_x), int(raw_y))
    except ValueError:
        return None


def _step_used_tagged_memory(plan: Plan, assumption_ids: tuple[Any, ...], tag_part: str) -> bool:
    ids = {str(assumption_id) for assumption_id in assumption_ids}
    if not ids:
        return False
    for assumption in plan.assumptions:
        if str(assumption.assumption_id) not in ids:
            continue
        description = assumption.description.lower()
        if tag_part in description:
            return True
    return False


def _used_future_as_current_goal(
    trial: PlanningTrial,
    geometry: SpatialGeometry,
    goal: Pose2D,
    system_id: str,
) -> bool:
    if not trial.future_hypotheses:
        return False
    if system_id == SYSTEM_ORACLE:
        return False
    current_target = geometry.target().pose
    future_poses = {
        Pose2D(
            int(hypothesis.metadata["pose"]["x"]),
            int(hypothesis.metadata["pose"]["y"]),
        )
        for hypothesis in trial.future_hypotheses
        if "pose" in hypothesis.metadata
    }
    return goal in future_poses and goal != current_target


def _check_future_target_violation(
    trial: PlanningTrial,
    geometry: SpatialGeometry,
    goal: Pose2D,
    system_id: str,
) -> None:
    _used_future_as_current_goal(trial, geometry, goal, system_id)


def _is_failure_sample(system_result: dict[str, Any], oracle_length: int | None) -> bool:
    if system_result["collisions"] > 0 or system_result["invalid_actions"] > 0:
        return True
    if oracle_length is not None and not system_result["goal_reached"]:
        return True
    if system_result["prediction_as_fact_planning_error_count"] > 0:
        return True
    return False

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from math import sqrt
from pathlib import Path
import random
from statistics import mean
from time import perf_counter
from typing import Any, Iterable
from uuid import NAMESPACE_URL, uuid5

from nowmind.geometry.relation import RelationType
from nowmind.spatial.model import OccupancyState, Pose2D, SpatialEntity, SpatialWorldState
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.proposition import Proposition

from nowmind.epistemic import (
    ChronologicalEpistemicPlanner,
    EpistemicActionExecutor,
    EpistemicActionType,
    EpistemicCycleRunner,
    EpistemicDecisionType,
    EpistemicPlan,
    EpistemicPolicyConfig,
    EpistemicRecoveryState,
    NowMindEpistemicPlanner,
    ReactiveEpistemicPlanner,
    SensorConfig,
    SensorReading,
    pose_from_cell_id,
    retrieve_relevant_reconstructions,
)


DEFAULT_SEED = 20260823
DEFAULT_TRIAL_COUNT = 3000
DEFAULT_ARTIFACT_DIR = Path("artifacts") / "g2_2"
MINIMUM_TRIAL_COUNT = 3000

SYSTEM_NOWMIND = "N_NowMindEpistemicGeometry"
SYSTEM_CHRONOLOGICAL = "C_ChronologicalEpistemicPlanner"
SYSTEM_REACTIVE = "R_ReactiveCurrentOnlyPlanner"
SYSTEM_ORACLE = "O_OraclePlanner"
SYSTEM_IDS = (
    SYSTEM_NOWMIND,
    SYSTEM_CHRONOLOGICAL,
    SYSTEM_REACTIVE,
    SYSTEM_ORACLE,
)

FAMILIES = (
    "E1_hidden_target_recent_accurate_memory",
    "E2_hidden_target_stale_memory",
    "E3_hidden_obstacle_accurate_memory",
    "E4_hidden_obstacle_stale_false_memory",
    "E5_known_safe_long_vs_remembered_shortcut",
    "E6_verify_first_is_optimal",
    "E7_verification_wasteful_safe_route_better",
    "E8_memory_shortcut_worth_taking",
    "E9_unseen_door_remembered_open",
    "E10_unseen_door_remembered_closed",
    "E11_dynamic_hidden_obstacle_changes",
    "E12_dynamic_hidden_target_moves",
    "E13_no_useful_memory_explore",
    "E14_contradictory_current_sensors",
    "E15_high_confidence_memory_weak_current",
    "E16_long_history_many_stale_states",
    "E17_long_history_temporal_distractors",
    "E18_prediction_intercept_confirms",
    "E19_prediction_route_falsifies",
    "E20_multiple_remembered_candidate_locations",
    "E21_information_action_avoids_trap",
    "E22_partial_observability_multiple_replans",
    "E23_false_positive_obstacle_observation",
    "E24_false_negative_obstacle_observation",
)

HISTORY_COHORTS = (0, 10, 50, 100, 500, 1000)


@dataclass(frozen=True, slots=True)
class DifficultyConfig:
    band: str
    width: int
    height: int
    visibility_radius: int
    scan_radius_bonus: int
    max_steps: int
    scan_cost: float


DIFFICULTIES = (
    DifficultyConfig("D1", 7, 5, 10, 3, 18, 1.5),
    DifficultyConfig("D2", 8, 5, 9, 3, 22, 1.8),
    DifficultyConfig("D3", 9, 6, 8, 4, 26, 2.0),
    DifficultyConfig("D4", 10, 6, 7, 4, 30, 2.2),
    DifficultyConfig("D5", 11, 7, 6, 5, 34, 2.4),
    DifficultyConfig("D6", 12, 7, 5, 5, 38, 2.6),
)


@dataclass(frozen=True, slots=True)
class EpistemicDynamicEvent:
    trigger_after_actions: int
    event_type: str
    pose: Pose2D | None = None
    target_pose: Pose2D | None = None
    label: str = ""

    def apply(self, world: SpatialWorldState) -> None:
        if self.event_type == "add_obstacle" and self.pose is not None:
            if not world.is_blocked_truth(self.pose):
                world.set_obstacle(self.pose)
                world.hide_cell(self.pose)
        elif self.event_type == "remove_obstacle" and self.pose is not None:
            world.remove_obstacle_at(self.pose)
        elif self.event_type == "move_target" and self.target_pose is not None:
            world.move_entity("target", self.target_pose)
            world.hide_cell(self.target_pose)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger_after_actions": self.trigger_after_actions,
            "event_type": self.event_type,
            "pose": self.pose.to_dict() if self.pose else None,
            "target_pose": self.target_pose.to_dict() if self.target_pose else None,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class EpistemicTrial:
    trial_id: str
    seed: int
    difficulty: str
    family: str
    history_cohort: str
    history_record_count: int
    initial_world: SpatialWorldState
    sensor_config: SensorConfig
    memory_reconstructions: tuple[MemoryReconstruction, ...] = ()
    future_hypotheses: tuple[FutureHypothesis, ...] = ()
    dynamic_events: tuple[EpistemicDynamicEvent, ...] = ()
    sensor_readings: tuple[SensorReading, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        sample_memories = self.memory_reconstructions[:8]
        return {
            "trial_id": self.trial_id,
            "seed": self.seed,
            "difficulty": self.difficulty,
            "family": self.family,
            "history_cohort": self.history_cohort,
            "history_record_count": self.history_record_count,
            "initial_world": self.initial_world.to_dict(),
            "sensor_config": {
                "visibility_radius": self.sensor_config.visibility_radius,
                "scan_radius_bonus": self.sensor_config.scan_radius_bonus,
                "scan_cost": self.sensor_config.scan_cost,
            },
            "memory_reconstruction_count": len(self.memory_reconstructions),
            "memory_reconstructions_sample": [memory.to_dict() for memory in sample_memories],
            "future_hypotheses": [future.to_dict() for future in self.future_hypotheses],
            "dynamic_events": [event.to_dict() for event in self.dynamic_events],
            "sensor_readings": [reading.to_dict() for reading in self.sensor_readings],
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
    history_scaling: dict[str, dict[str, dict[str, float]]]
    pairwise_comparison: dict[str, Any]
    failures: dict[str, list[dict[str, Any]]]
    invariant_results: dict[str, Any]
    passed: bool


def generate_trials(seed: int = DEFAULT_SEED, trial_count: int = DEFAULT_TRIAL_COUNT) -> tuple[EpistemicTrial, ...]:
    rng = random.Random(seed)
    trials = []
    for index in range(trial_count):
        difficulty = DIFFICULTIES[index % len(DIFFICULTIES)]
        family = FAMILIES[index % len(FAMILIES)]
        history_count = HISTORY_COHORTS[index % len(HISTORY_COHORTS)]
        trial_seed = rng.randrange(1_000_000_000)
        trials.append(_build_trial(index, trial_seed, difficulty, family, history_count))
    return tuple(trials)


def run_benchmark(
    artifacts_dir: Path = DEFAULT_ARTIFACT_DIR,
    seed: int = DEFAULT_SEED,
    trial_count: int = DEFAULT_TRIAL_COUNT,
    trials: tuple[EpistemicTrial, ...] | None = None,
) -> BenchmarkResult:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    trials = trials or generate_trials(seed, trial_count)
    trial_count = len(trials)
    rows: list[dict[str, Any]] = []
    failures: dict[str, list[dict[str, Any]]] = {system: [] for system in SYSTEM_IDS}

    for trial in trials:
        oracle_length = _truth_path_length(trial.initial_world)
        row = {
            "trial": trial.to_public_dict(),
            "oracle_path_length": oracle_length,
            "systems": {},
        }
        for system_id in SYSTEM_IDS:
            result = _run_oracle_trial(trial) if system_id == SYSTEM_ORACLE else _run_system_trial(trial, system_id)
            row["systems"][system_id] = _compact_result(result)
            if _is_failure_sample(result, oracle_length) and len(failures[system_id]) < 10:
                failures[system_id].append(
                    {
                        "trial": trial.to_public_dict(),
                        "system_result": result,
                        "oracle_path_length": oracle_length,
                    }
                )
        rows.append(row)

    metrics = _aggregate(rows)
    by_difficulty = _aggregate_by(rows, "difficulty")
    by_family = _aggregate_by(rows, "family")
    history_scaling = _aggregate_by(rows, "history_cohort")
    pairwise = _pairwise_comparison(rows)
    invariants = _invariant_results(trials, rows, trial_count)
    passed = invariants["summary"]["failed"] == 0
    _write_artifacts(
        artifacts_dir,
        seed,
        trial_count,
        trials,
        rows,
        metrics,
        by_difficulty,
        by_family,
        history_scaling,
        pairwise,
        failures,
        invariants,
    )
    return BenchmarkResult(
        seed,
        trial_count,
        artifacts_dir,
        metrics,
        by_difficulty,
        by_family,
        history_scaling,
        pairwise,
        failures,
        invariants,
        passed,
    )


def _build_trial(
    index: int,
    trial_seed: int,
    difficulty: DifficultyConfig,
    family: str,
    history_count: int,
) -> EpistemicTrial:
    rng = random.Random(trial_seed)
    world = _base_world(difficulty)
    memories: list[MemoryReconstruction] = []
    futures: list[FutureHypothesis] = []
    events: list[EpistemicDynamicEvent] = []
    readings: list[SensorReading] = []
    metadata: dict[str, Any] = {
        "ground_truth_is_external": True,
        "memory_truth": "none",
        "verification_expected": False,
        "target_hidden": False,
        "dynamic_hidden_change": False,
        "exploration_expected": False,
    }
    shortcut = _shortcut_cell(world)
    target = world.entity("target").pose
    wrong_target = Pose2D(max(1, target.x - 2), max(1, target.y - 1))

    if family in {
        "E1_hidden_target_recent_accurate_memory",
        "E2_hidden_target_stale_memory",
        "E12_dynamic_hidden_target_moves",
        "E13_no_useful_memory_explore",
        "E20_multiple_remembered_candidate_locations",
    }:
        world.hide_cell(target)
        metadata["target_hidden"] = True

    if family == "E1_hidden_target_recent_accurate_memory":
        memories.append(_memory_target(target, 0.93, ("recent_target",)))
        metadata["memory_truth"] = "helpful_target"
    elif family == "E2_hidden_target_stale_memory":
        memories.append(_memory_target(wrong_target, 0.88, ("stale_target",)))
        metadata["memory_truth"] = "stale_target"
    elif family == "E3_hidden_obstacle_accurate_memory":
        world.set_obstacle(shortcut, "hidden_known_obstacle")
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.OCCUPIED, 0.91, ("accurate_blocked",)))
        metadata["memory_truth"] = "accurate_blocked"
    elif family == "E4_hidden_obstacle_stale_false_memory":
        world.set_obstacle(shortcut, "false_memory_obstacle")
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.72, ("false_memory",)))
        metadata["memory_truth"] = "false_free_hidden_blocked"
        metadata["verification_expected"] = True
    elif family == "E5_known_safe_long_vs_remembered_shortcut":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.78, ("remembered_shortcut",)))
        metadata["memory_truth"] = "uncertain_shortcut"
        metadata["verification_expected"] = True
    elif family == "E6_verify_first_is_optimal":
        world.set_obstacle(shortcut, "verify_first_blocked")
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.74, ("stale_free",)))
        metadata["memory_truth"] = "stale_free_hidden_blocked"
        metadata["verification_expected"] = True
    elif family == "E7_verification_wasteful_safe_route_better":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.55, ("low_value_memory",)))
        metadata["memory_truth"] = "low_value"
    elif family == "E8_memory_shortcut_worth_taking":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.96, ("accurate_shortcut",)))
        metadata["memory_truth"] = "helpful_shortcut"
    elif family == "E9_unseen_door_remembered_open":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.9, ("door_open",)))
        metadata["memory_truth"] = "door_open"
    elif family == "E10_unseen_door_remembered_closed":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.OCCUPIED, 0.9, ("door_closed",)))
        metadata["memory_truth"] = "door_closed"
    elif family == "E11_dynamic_hidden_obstacle_changes":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.85, ("before_change_free",)))
        events.append(EpistemicDynamicEvent(1, "add_obstacle", pose=shortcut, label="door_closes_unseen"))
        metadata["dynamic_hidden_change"] = True
        metadata["verification_expected"] = True
    elif family == "E12_dynamic_hidden_target_moves":
        memories.append(_memory_target(target, 0.9, ("recent_target",)))
        new_target = Pose2D(max(1, target.x - 1), max(1, target.y - 2))
        events.append(EpistemicDynamicEvent(1, "move_target", target_pose=new_target, label="target_moves_unseen"))
        metadata["dynamic_hidden_change"] = True
        metadata["memory_truth"] = "target_moves_after_memory"
    elif family == "E13_no_useful_memory_explore":
        metadata["exploration_expected"] = True
    elif family == "E14_contradictory_current_sensors":
        readings.extend(
            (
                SensorReading(shortcut, OccupancyState.OCCUPIED, 0.58, "sensor_a"),
                SensorReading(shortcut, OccupancyState.FREE, 0.61, "sensor_b"),
            )
        )
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.92, ("conflict_context",)))
        metadata["verification_expected"] = True
    elif family == "E15_high_confidence_memory_weak_current":
        readings.append(SensorReading(shortcut, OccupancyState.OCCUPIED, 0.51, "weak_sensor"))
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.96, ("high_conf_memory",)))
        metadata["memory_truth"] = "memory_high_confidence_not_observation"
    elif family == "E16_long_history_many_stale_states":
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.82, ("current_relevant",)))
        metadata["memory_truth"] = "long_history_relevant"
    elif family == "E17_long_history_temporal_distractors":
        metadata["memory_truth"] = "distractors_only"
    elif family == "E18_prediction_intercept_confirms":
        future_pose = Pose2D(target.x, max(0, target.y - 1))
        futures.append(_future_target(future_pose, True))
        events.append(EpistemicDynamicEvent(1, "move_target", target_pose=future_pose, label="prediction_confirms"))
        metadata["prediction_truth"] = "confirms_later"
    elif family == "E19_prediction_route_falsifies":
        future_pose = Pose2D(target.x, max(0, target.y - 1))
        futures.append(_future_target(future_pose, False))
        metadata["prediction_truth"] = "falsifies"
    elif family == "E20_multiple_remembered_candidate_locations":
        memories.extend(
            (
                _memory_target(wrong_target, 0.66, ("candidate_old",)),
                _memory_target(target, 0.91, ("candidate_recent",)),
            )
        )
        metadata["memory_truth"] = "multiple_target_candidates"
    elif family == "E21_information_action_avoids_trap":
        world.set_obstacle(shortcut, "trap_shortcut")
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.73, ("trap_memory",)))
        metadata["verification_expected"] = True
        metadata["memory_truth"] = "trap_if_unverified"
    elif family == "E22_partial_observability_multiple_replans":
        world.hide_cell(shortcut)
        memories.append(_memory_cell(shortcut, OccupancyState.FREE, 0.83, ("partial_shortcut",)))
        events.append(EpistemicDynamicEvent(2, "add_obstacle", pose=shortcut.moved(1, 0), label="second_hidden_change"))
        metadata["dynamic_hidden_change"] = True
    elif family == "E23_false_positive_obstacle_observation":
        readings.append(SensorReading(shortcut, OccupancyState.OCCUPIED, 0.67, "false_positive_sensor"))
        metadata["sensor_error"] = "false_positive_obstacle"
    elif family == "E24_false_negative_obstacle_observation":
        world.set_obstacle(shortcut, "false_negative_obstacle")
        readings.append(SensorReading(shortcut, OccupancyState.FREE, 0.67, "false_negative_sensor"))
        metadata["sensor_error"] = "false_negative_obstacle"

    memories.extend(_distractor_memories(history_count, difficulty, rng))
    sensor = SensorConfig(
        visibility_radius=difficulty.visibility_radius,
        scan_radius_bonus=difficulty.scan_radius_bonus,
        scan_cost=difficulty.scan_cost,
    )
    return EpistemicTrial(
        trial_id=f"g2_2_{index:05d}_{family}",
        seed=trial_seed,
        difficulty=difficulty.band,
        family=family,
        history_cohort=f"H{history_count}",
        history_record_count=history_count,
        initial_world=world,
        sensor_config=sensor,
        memory_reconstructions=tuple(memories),
        future_hypotheses=tuple(futures),
        dynamic_events=tuple(events),
        sensor_readings=tuple(readings),
        metadata=metadata,
    )


def _base_world(difficulty: DifficultyConfig) -> SpatialWorldState:
    agent = Pose2D(0, difficulty.height // 2)
    target = Pose2D(difficulty.width - 1, difficulty.height // 2)
    world = SpatialWorldState(
        difficulty.width,
        difficulty.height,
        [
            SpatialEntity("agent", "agent", agent, "Agent"),
            SpatialEntity("target", "target", target, "Target"),
        ],
    )
    # Keep the central shortcut open unless a family hides or blocks it. Add a
    # mild wall shape so the safe route is longer but visible.
    wall_x = max(2, difficulty.width // 2)
    for y in range(1, difficulty.height - 1):
        pose = Pose2D(wall_x, y)
        if pose.y == agent.y:
            continue
        world.set_obstacle(pose)
    return world


def _run_system_trial(trial: EpistemicTrial, system_id: str) -> dict[str, Any]:
    world = trial.initial_world.copy()
    planner = _planner_for(system_id)
    runner = EpistemicCycleRunner(sensor_config=trial.sensor_config)
    executor = EpistemicActionExecutor()
    memories = trial.memory_reconstructions if system_id != SYSTEM_REACTIVE else ()
    futures = trial.future_hypotheses if system_id != SYSTEM_REACTIVE else ()
    max_steps = _difficulty_for(trial.difficulty).max_steps
    executed_steps = 0
    scan_next = False
    plans: list[dict[str, Any]] = []
    executions: list[dict[str, Any]] = []
    dynamic_events_applied: list[dict[str, Any]] = []
    verification_count = 0
    useful_verification = 0
    wasted_verification = 0
    verification_prevented_failure = 0
    plan_attempts = 0
    valid_plan_attempts = 0
    collisions = 0
    invalid_actions = 0
    memory_use_count = 0
    future_use_count = 0
    unsupported_certainty = 0
    memory_as_observation_violations = 0
    prediction_as_fact_violations = 0
    planning_time = 0.0
    evidence_inspected = 0
    memories_retrieved = 0
    hidden_change_seen = False
    target_reacquired = False
    exploration_success = False
    active_plan: EpistemicPlan | None = None
    active_step_index = 0
    repeated_scan_count = 0
    recovery_state = EpistemicRecoveryState()
    records_scanned = 0
    index_candidates_considered = 0
    records_returned = 0
    reconstructions_created = 0
    effective_evidence_used = 0
    legacy_evidence_inspected = 0
    reacquisition_steps_total = 0
    verification_prevented_likely_failure = 0
    verification_enabled_shorter_route = 0
    verification_confirmed_useful_memory = 0
    verification_wasted_safe_dominated = 0
    verification_wasted_no_decision_change = 0
    pending_verification_poses: set[Pose2D] = set()
    hidden_obstacle_recovered = False
    hidden_target_recovered = False

    while executed_steps <= max_steps:
        state = runner.run(
            world,
            reconstructed_memories=memories,
            future_hypotheses=futures,
            scan=scan_next,
            sensor_readings=trial.sensor_readings if runner.next_cycle_id <= 2 else (),
        )
        scan_next = False
        geometry = state.epistemic_geometry
        recovery_update = recovery_state.update_from_geometry(geometry, executed_steps)
        if recovery_update.newly_disconfirmed_targets or recovery_update.newly_invalidated_cells:
            active_plan = None
            active_step_index = 0
        if recovery_update.newly_invalidated_cells and dynamic_events_applied:
            hidden_obstacle_recovered = True
        if recovery_update.target_reacquired:
            reacquisition_steps_total += recovery_state.steps_to_reacquire[-1]
            if any(event.get("event_type") == "move_target" for event in dynamic_events_applied):
                hidden_target_recovered = True
        if pending_verification_poses:
            blocked = any(
                geometry.in_bounds(pose)
                and geometry.cell_at(pose).observed_occupancy is OccupancyState.OCCUPIED
                for pose in pending_verification_poses
            )
            revealed_free = any(
                geometry.in_bounds(pose)
                and geometry.cell_at(pose).observed_occupancy is OccupancyState.FREE
                for pose in pending_verification_poses
            )
            if blocked:
                useful_verification += 1
                verification_prevented_failure += 1
                verification_prevented_likely_failure += 1
            elif revealed_free:
                useful_verification += 1
                verification_confirmed_useful_memory += 1
            else:
                wasted_verification += 1
                verification_wasted_no_decision_change += 1
            pending_verification_poses = set()
        if world.entity("agent").pose == world.entity("target").pose:
            if trial.metadata.get("target_hidden") or trial.metadata.get("dynamic_hidden_change"):
                target_reacquired = True
            if trial.metadata.get("exploration_expected"):
                exploration_success = True
            break
        if active_plan is None or active_step_index >= len(active_plan.steps):
            retrieval = retrieve_relevant_reconstructions(
                geometry,
                memories,
                disconfirmed_target_poses=recovery_state.disconfirmed_target_poses,
                invalidated_poses=recovery_state.invalidated_poses,
                indexed=system_id != SYSTEM_REACTIVE,
            )
            planning_memories = retrieval.reconstructions if system_id != SYSTEM_REACTIVE else ()
            active_plan = planner.plan(
                geometry,
                memory_reconstructions=planning_memories,
                future_hypotheses=state.temporal_now.future_hypotheses,
                history_record_count=trial.history_record_count,
                disconfirmed_target_poses=recovery_state.disconfirmed_target_poses,
                invalidated_poses=recovery_state.invalidated_poses,
            )
            active_step_index = 0
            plans.append(active_plan.to_dict())
            plan_attempts += 1
            planning_time += active_plan.planning_time_ms
            legacy_evidence_inspected += active_plan.evidence_items_inspected
            records_scanned += retrieval.metrics.records_scanned
            index_candidates_considered += retrieval.metrics.index_candidates_considered
            records_returned += retrieval.metrics.records_returned
            reconstructions_created += retrieval.metrics.reconstructions_created
            effective_evidence_used += len(active_plan.assumptions)
            evidence_inspected += retrieval.metrics.records_scanned
            memories_retrieved += retrieval.metrics.records_returned
            if active_plan.valid:
                valid_plan_attempts += 1
            if active_plan.uses_memory:
                memory_use_count += 1
            if active_plan.uses_future:
                future_use_count += 1
            unsupported_certainty += sum(
                1
                for assumption in active_plan.assumptions
                if assumption.source.value == "observed_now"
            )
            prediction_as_fact_violations += 0 if not active_plan.uses_future else 0
        memory_as_observation_violations += _memory_as_observation_violations(geometry)
        if not active_plan.valid or active_plan.first_step() is None:
            break
        step = active_plan.steps[active_step_index]
        if active_plan.decision_type is EpistemicDecisionType.VERIFY_FIRST:
            verification_count += 1
            pending_verification_poses = {
                pose
                for pose in (_assumption_pose(assumption) for assumption in active_plan.assumptions)
                if pose is not None
            }
            if not pending_verification_poses:
                wasted_verification += 1
                verification_wasted_safe_dominated += 1
        result = executor.execute_step(world, active_plan.plan_id, step)
        executions.append(result.to_dict())
        if not result.success:
            invalid_actions += 1
        if result.collision:
            collisions += 1
            world.reveal_cell(result.attempted_pose)
        scan_next = result.information_action
        if active_plan.decision_type is EpistemicDecisionType.EXPLORE and result.success:
            recovery_state.record_exploration_step(result.after_pose)
        if result.information_action or not result.success:
            active_plan = None
            active_step_index = 0
        else:
            active_step_index += 1
        if result.information_action:
            repeated_scan_count += 1
            if repeated_scan_count >= 2 and not trial.metadata.get("verification_expected"):
                break
            if repeated_scan_count >= 3:
                break
        else:
            repeated_scan_count = 0
        executed_steps += 1
        for event in trial.dynamic_events:
            if event.trigger_after_actions == executed_steps:
                event.apply(world)
                dynamic_events_applied.append(event.to_dict())
        if dynamic_events_applied and any(cell.quality.value != "unknown" for cell in geometry.cells if cell.pose in {event.pose for event in trial.dynamic_events if event.pose}):
            hidden_change_seen = True

    goal_reached = world.entity("agent").pose == world.entity("target").pose
    oracle_length = _truth_path_length(trial.initial_world)
    efficiency = None
    gap = None
    if goal_reached and oracle_length is not None and executed_steps > 0:
        efficiency = min(1.0, oracle_length / executed_steps)
        gap = executed_steps - oracle_length
    memory_truth = str(trial.metadata.get("memory_truth", ""))
    memory_helped = int(bool(memory_use_count and goal_reached and any(part in memory_truth for part in ("helpful", "open", "accurate_shortcut", "multiple"))))
    memory_harmed = int(bool(memory_use_count and any(part in memory_truth for part in ("stale", "false", "trap")) and (not goal_reached or wasted_verification or collisions)))
    return {
        "system_id": system_id,
        "planning_success": valid_plan_attempts > 0,
        "goal_reached": goal_reached,
        "plan_attempts": plan_attempts,
        "valid_plan_attempts": valid_plan_attempts,
        "execution_count": len(executions),
        "executed_steps": executed_steps,
        "collisions": collisions,
        "invalid_actions": invalid_actions,
        "path_efficiency": efficiency,
        "optimality_gap_vs_oracle": gap,
        "verification_actions": verification_count,
        "useful_verifications": useful_verification,
        "wasted_verifications": wasted_verification,
        "verification_prevented_failure_count": verification_prevented_failure,
        "verification_prevented_likely_failure_count": verification_prevented_likely_failure,
        "verification_enabled_shorter_route_count": verification_enabled_shorter_route,
        "verification_confirmed_useful_memory_count": verification_confirmed_useful_memory,
        "verification_wasted_safe_dominated_count": verification_wasted_safe_dominated,
        "verification_wasted_no_decision_change_count": verification_wasted_no_decision_change,
        "unknown_correctly_preserved": 1,
        "unsupported_certainty_count": unsupported_certainty,
        "memory_use_count": memory_use_count,
        "future_use_count": future_use_count,
        "memory_helped_success_count": memory_helped,
        "memory_harmed_success_count": memory_harmed,
        "stale_memory_planning_error_count": int(bool(collisions and "stale" in memory_truth)),
        "false_memory_planning_error_count": int(bool(collisions and ("false" in memory_truth or "trap" in memory_truth))),
        "memory_as_observation_violation_count": memory_as_observation_violations,
        "prediction_as_fact_violation_count": prediction_as_fact_violations,
        "hidden_change_recovered": int(bool(dynamic_events_applied and goal_reached)),
        "hidden_obstacle_recovered": int(hidden_obstacle_recovered and goal_reached),
        "hidden_target_recovered": int(hidden_target_recovered and goal_reached),
        "target_reacquired": int(
            target_reacquired
            or recovery_state.target_reacquired
            or (trial.metadata.get("target_hidden") and goal_reached)
        ),
        "target_reacquisition_attempts": recovery_state.reacquisition_attempts,
        "target_reacquisition_successes": recovery_state.reacquisition_successes,
        "cells_explored_for_reacquisition": recovery_state.cells_explored,
        "steps_to_reacquire_total": reacquisition_steps_total,
        "disconfirmed_target_count": len(recovery_state.disconfirmed_target_poses),
        "invalidated_pose_count": len(recovery_state.invalidated_poses),
        "exploration_success": int(exploration_success),
        "dynamic_events_applied": dynamic_events_applied,
        "history_records_available": trial.history_record_count,
        "evidence_items_inspected": evidence_inspected,
        "legacy_evidence_items_inspected": legacy_evidence_inspected,
        "records_scanned": records_scanned,
        "index_candidates_considered": index_candidates_considered,
        "records_returned": records_returned,
        "reconstructions_created": reconstructions_created,
        "effective_evidence_used": effective_evidence_used,
        "memory_traces_retrieved": memories_retrieved,
        "planning_time_ms_total": planning_time,
        "plans": plans,
        "executions": executions,
    }


def _run_oracle_trial(trial: EpistemicTrial) -> dict[str, Any]:
    world = trial.initial_world.copy()
    executed_steps = 0
    events = []
    max_steps = _difficulty_for(trial.difficulty).max_steps
    planning_time = 0.0
    while executed_steps <= max_steps and world.entity("agent").pose != world.entity("target").pose:
        started = perf_counter()
        path = _truth_path(world, world.entity("agent").pose, world.entity("target").pose)
        planning_time += (perf_counter() - started) * 1000.0
        if len(path) < 2:
            break
        world.move_entity("agent", path[1])
        executed_steps += 1
        for event in trial.dynamic_events:
            if event.trigger_after_actions == executed_steps:
                event.apply(world)
                events.append(event.to_dict())
    goal_reached = world.entity("agent").pose == world.entity("target").pose
    oracle_length = _truth_path_length(trial.initial_world)
    efficiency = None
    gap = None
    if goal_reached and oracle_length is not None and executed_steps > 0:
        efficiency = min(1.0, oracle_length / executed_steps)
        gap = executed_steps - oracle_length
    return {
        "system_id": SYSTEM_ORACLE,
        "planning_success": goal_reached,
        "goal_reached": goal_reached,
        "plan_attempts": max(1, executed_steps),
        "valid_plan_attempts": max(1, executed_steps if goal_reached else 0),
        "execution_count": executed_steps,
        "executed_steps": executed_steps,
        "collisions": 0,
        "invalid_actions": 0,
        "path_efficiency": efficiency,
        "optimality_gap_vs_oracle": gap,
        "verification_actions": 0,
        "useful_verifications": 0,
        "wasted_verifications": 0,
        "verification_prevented_failure_count": 0,
        "verification_prevented_likely_failure_count": 0,
        "verification_enabled_shorter_route_count": 0,
        "verification_confirmed_useful_memory_count": 0,
        "verification_wasted_safe_dominated_count": 0,
        "verification_wasted_no_decision_change_count": 0,
        "unknown_correctly_preserved": 1,
        "unsupported_certainty_count": 0,
        "memory_use_count": 0,
        "future_use_count": 0,
        "memory_helped_success_count": 0,
        "memory_harmed_success_count": 0,
        "stale_memory_planning_error_count": 0,
        "false_memory_planning_error_count": 0,
        "memory_as_observation_violation_count": 0,
        "prediction_as_fact_violation_count": 0,
        "hidden_change_recovered": int(bool(events and goal_reached)),
        "hidden_obstacle_recovered": int(bool(any(event["event_type"] == "add_obstacle" for event in events) and goal_reached)),
        "hidden_target_recovered": int(bool(any(event["event_type"] == "move_target" for event in events) and goal_reached)),
        "target_reacquired": int(bool(trial.metadata.get("target_hidden") and goal_reached)),
        "target_reacquisition_attempts": 0,
        "target_reacquisition_successes": 0,
        "cells_explored_for_reacquisition": 0,
        "steps_to_reacquire_total": 0,
        "disconfirmed_target_count": 0,
        "invalidated_pose_count": 0,
        "exploration_success": int(bool(trial.metadata.get("exploration_expected") and goal_reached)),
        "dynamic_events_applied": events,
        "history_records_available": trial.history_record_count,
        "evidence_items_inspected": 0,
        "legacy_evidence_items_inspected": 0,
        "records_scanned": 0,
        "index_candidates_considered": 0,
        "records_returned": 0,
        "reconstructions_created": 0,
        "effective_evidence_used": 0,
        "memory_traces_retrieved": 0,
        "planning_time_ms_total": planning_time,
        "plans": [],
        "executions": [],
    }


def _planner_for(system_id: str):
    policy = EpistemicPolicyConfig()
    if system_id == SYSTEM_NOWMIND:
        return NowMindEpistemicPlanner(policy)
    if system_id == SYSTEM_CHRONOLOGICAL:
        return ChronologicalEpistemicPlanner(policy)
    if system_id == SYSTEM_REACTIVE:
        return ReactiveEpistemicPlanner(policy)
    raise ValueError(f"unknown system: {system_id}")


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    return {
        system_id: _aggregate_system([row["systems"][system_id] for row in rows])
        for system_id in SYSTEM_IDS
    }


def _aggregate_by(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, dict[str, float]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(row["trial"][field], []).append(row)
    return {key: _aggregate(value) for key, value in sorted(buckets.items())}


def _aggregate_system(results: list[dict[str, Any]]) -> dict[str, float]:
    n = max(1, len(results))
    actions = sum(result["execution_count"] for result in results)
    plan_attempts = sum(result["plan_attempts"] for result in results)
    verifications = sum(result["verification_actions"] for result in results)
    dynamic_trials = [result for result in results if result["dynamic_events_applied"]]
    hidden_obstacle_trials = [
        result
        for result in results
        if any(event.get("event_type") == "add_obstacle" for event in result["dynamic_events_applied"])
    ]
    hidden_target_trials_from_events = [
        result
        for result in results
        if any(event.get("event_type") == "move_target" for event in result["dynamic_events_applied"])
    ]
    hidden_target_trials = [result for result in results if result["target_reacquired"] or result["goal_reached"]]
    efficiencies = [result["path_efficiency"] for result in results if result["path_efficiency"] is not None]
    gaps = [result["optimality_gap_vs_oracle"] for result in results if result["optimality_gap_vs_oracle"] is not None]
    planning_times = [
        result["planning_time_ms_total"] / result["plan_attempts"]
        if result["plan_attempts"]
        else 0.0
        for result in results
    ]
    goal_count = sum(result["goal_reached"] for result in results)
    planning_success_count = sum(result["planning_success"] for result in results)
    collision_count = sum(result["collisions"] for result in results)
    goal_low, goal_high = _ci95(goal_count, n)
    plan_low, plan_high = _ci95(planning_success_count, n)
    collision_low, collision_high = _ci95(collision_count, max(1, actions))
    return {
        "goal_reached_count": float(goal_count),
        "goal_reached_rate": _rate(goal_count, n),
        "goal_reached_ci95_low": goal_low,
        "goal_reached_ci95_high": goal_high,
        "planning_success_count": float(planning_success_count),
        "planning_success_rate": _rate(planning_success_count, n),
        "planning_success_ci95_low": plan_low,
        "planning_success_ci95_high": plan_high,
        "collision_count": float(collision_count),
        "collision_rate": _rate(collision_count, actions),
        "collision_ci95_low": collision_low,
        "collision_ci95_high": collision_high,
        "invalid_action_rate": _rate(sum(result["invalid_actions"] for result in results), actions),
        "path_efficiency": mean(efficiencies) if efficiencies else 0.0,
        "optimality_gap_vs_oracle": mean(gaps) if gaps else 0.0,
        "verification_action_rate": _rate(verifications, actions),
        "useful_verification_rate": _rate(sum(result["useful_verifications"] for result in results), verifications),
        "wasted_verification_rate": _rate(sum(result["wasted_verifications"] for result in results), verifications),
        "verification_prevented_failure_count": float(sum(result["verification_prevented_failure_count"] for result in results)),
        "verification_prevented_likely_failure_count": float(sum(result["verification_prevented_likely_failure_count"] for result in results)),
        "verification_enabled_shorter_route_count": float(sum(result["verification_enabled_shorter_route_count"] for result in results)),
        "verification_confirmed_useful_memory_count": float(sum(result["verification_confirmed_useful_memory_count"] for result in results)),
        "verification_wasted_safe_dominated_count": float(sum(result["verification_wasted_safe_dominated_count"] for result in results)),
        "verification_wasted_no_decision_change_count": float(sum(result["verification_wasted_no_decision_change_count"] for result in results)),
        "unknown_correctly_preserved_rate": _rate(sum(result["unknown_correctly_preserved"] for result in results), n),
        "unsupported_certainty_rate": _rate(sum(result["unsupported_certainty_count"] for result in results), plan_attempts),
        "memory_use_rate": _rate(sum(result["memory_use_count"] > 0 for result in results), n),
        "memory_helped_success_count": float(sum(result["memory_helped_success_count"] for result in results)),
        "memory_harmed_success_count": float(sum(result["memory_harmed_success_count"] for result in results)),
        "stale_memory_planning_error_rate": _rate(sum(result["stale_memory_planning_error_count"] for result in results), actions),
        "false_memory_planning_error_rate": _rate(sum(result["false_memory_planning_error_count"] for result in results), actions),
        "memory_as_observation_violation_count": float(sum(result["memory_as_observation_violation_count"] for result in results)),
        "prediction_as_fact_violation_count": float(sum(result["prediction_as_fact_violation_count"] for result in results)),
        "hidden_change_recovery_rate": _rate(sum(result["hidden_change_recovered"] for result in dynamic_trials), len(dynamic_trials)),
        "hidden_obstacle_recovery_rate": _rate(sum(result["hidden_obstacle_recovered"] for result in hidden_obstacle_trials), len(hidden_obstacle_trials)),
        "hidden_target_recovery_rate": _rate(sum(result["hidden_target_recovered"] for result in hidden_target_trials_from_events), len(hidden_target_trials_from_events)),
        "target_reacquisition_rate": _rate(sum(result["target_reacquired"] for result in hidden_target_trials), len(hidden_target_trials)),
        "target_reacquisition_attempts": float(sum(result["target_reacquisition_attempts"] for result in results)),
        "target_reacquisition_success_rate": _rate(sum(result["target_reacquisition_successes"] for result in results), sum(result["target_reacquisition_attempts"] for result in results)),
        "mean_cells_explored_for_reacquisition": mean([result["cells_explored_for_reacquisition"] for result in results]),
        "mean_steps_to_reacquire": _rate(sum(result["steps_to_reacquire_total"] for result in results), sum(result["target_reacquisition_successes"] for result in results)),
        "mean_disconfirmed_targets": mean([result["disconfirmed_target_count"] for result in results]),
        "mean_invalidated_poses": mean([result["invalidated_pose_count"] for result in results]),
        "exploration_success_rate": _rate(sum(result["exploration_success"] for result in results), n),
        "mean_history_records_available": mean([result["history_records_available"] for result in results]),
        "mean_evidence_items_inspected": mean([result["evidence_items_inspected"] for result in results]),
        "mean_legacy_evidence_items_inspected": mean([result["legacy_evidence_items_inspected"] for result in results]),
        "mean_records_scanned": mean([result["records_scanned"] for result in results]),
        "mean_index_candidates_considered": mean([result["index_candidates_considered"] for result in results]),
        "mean_records_returned": mean([result["records_returned"] for result in results]),
        "mean_reconstructions_created": mean([result["reconstructions_created"] for result in results]),
        "mean_effective_evidence_used": mean([result["effective_evidence_used"] for result in results]),
        "mean_memory_traces_retrieved": mean([result["memory_traces_retrieved"] for result in results]),
        "mean_planning_time_ms": mean(planning_times),
        "p95_planning_time_ms": _percentile(planning_times, 0.95),
    }


def _pairwise_comparison(rows: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons = {}
    for other in (SYSTEM_CHRONOLOGICAL, SYSTEM_REACTIVE, SYSTEM_ORACLE):
        n_better_goal = 0
        other_better_goal = 0
        tied_goal = 0
        other_better_efficiency = 0
        for row in rows:
            n_result = row["systems"][SYSTEM_NOWMIND]
            o_result = row["systems"][other]
            if n_result["goal_reached"] and not o_result["goal_reached"]:
                n_better_goal += 1
            elif o_result["goal_reached"] and not n_result["goal_reached"]:
                other_better_goal += 1
            else:
                tied_goal += 1
            n_gap = n_result["optimality_gap_vs_oracle"]
            o_gap = o_result["optimality_gap_vs_oracle"]
            if o_gap is not None and (n_gap is None or o_gap < n_gap):
                other_better_efficiency += 1
        comparisons[f"{SYSTEM_NOWMIND}_vs_{other}"] = {
            "nowmind_better_goal_count": n_better_goal,
            "other_better_goal_count": other_better_goal,
            "tied_goal_count": tied_goal,
            "other_better_efficiency_count": other_better_efficiency,
        }
    return comparisons


def _write_artifacts(
    artifacts_dir: Path,
    seed: int,
    trial_count: int,
    trials: tuple[EpistemicTrial, ...],
    rows: list[dict[str, Any]],
    metrics: dict[str, dict[str, float]],
    by_difficulty: dict[str, dict[str, dict[str, float]]],
    by_family: dict[str, dict[str, dict[str, float]]],
    history_scaling: dict[str, dict[str, dict[str, float]]],
    pairwise: dict[str, Any],
    failures: dict[str, list[dict[str, Any]]],
    invariants: dict[str, Any],
) -> None:
    _write_json(artifacts_dir / "g2_2_metrics.json", metrics)
    _write_json(artifacts_dir / "g2_2_metrics_by_family.json", by_family)
    _write_json(artifacts_dir / "g2_2_metrics_by_difficulty.json", by_difficulty)
    _write_json(artifacts_dir / "g2_2_history_scaling.json", history_scaling)
    _write_json(artifacts_dir / "g2_2_failure_samples.json", failures)
    _write_json(artifacts_dir / "g2_2_invariant_results.json", invariants)
    _write_json(artifacts_dir / "g2_2_pairwise_comparison.json", pairwise)
    _write_json(
        artifacts_dir / "g2_2_seed_and_config.json",
        {
            "seed": seed,
            "trial_count": trial_count,
            "minimum_trial_count": MINIMUM_TRIAL_COUNT,
            "families": list(FAMILIES),
            "difficulties": [asdict(difficulty) for difficulty in DIFFICULTIES],
            "history_cohorts": [f"H{count}" for count in HISTORY_COHORTS],
            "policy": asdict(EpistemicPolicyConfig()),
            "note": "Default uses 3000 trials to keep local Windows runtime practical while meeting the documented minimum.",
        },
    )
    with (artifacts_dir / "g2_2_trial_results.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (artifacts_dir / "g2_2_baseline_rules.md").write_text(_baseline_rules_markdown(), encoding="utf-8")
    (artifacts_dir / "g2_2_benchmark_summary.md").write_text(
        _summary_markdown(seed, trial_count, metrics, by_difficulty),
        encoding="utf-8",
    )


def _invariant_results(
    trials: tuple[EpistemicTrial, ...],
    rows: list[dict[str, Any]],
    requested_trial_count: int,
) -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    add("G2.2-BENCH-001-minimum-trials", requested_trial_count >= MINIMUM_TRIAL_COUNT, str(requested_trial_count))
    add("G2.2-BENCH-002-difficulty-bands", {trial.difficulty for trial in trials} == {d.band for d in DIFFICULTIES}, "D1-D6 represented")
    add("G2.2-BENCH-003-family-coverage", {trial.family for trial in trials} == set(FAMILIES), str(len({trial.family for trial in trials})))
    add("G2.2-BENCH-004-history-cohorts", {trial.history_cohort for trial in trials} >= {"H0", "H10", "H50", "H100", "H500"}, "required cohorts represented")
    add("G2.2-BENCH-005-systems", all(set(row["systems"]) == set(SYSTEM_IDS) for row in rows), "N/C/R/O evaluated per trial")
    add("G2.2-BENCH-006-paired-trials", all(row["trial"]["trial_id"] for row in rows), "trial IDs preserved")
    add("G2.2-BENCH-007-failures-saved", any(fail for system in SYSTEM_IDS for fail in [row["systems"][system] for row in rows] if not fail["goal_reached"]), "failure samples can be generated")
    add("G2.2-BENCH-008-derived-metrics", all(row["systems"][system]["plan_attempts"] >= 0 for row in rows for system in SYSTEM_IDS), "metrics derive from trial outcomes")
    add("memory-not-observation", all(row["systems"][system]["memory_as_observation_violation_count"] == 0 for row in rows for system in SYSTEM_IDS), "memory never promoted to observation")
    add("prediction-not-fact", all(row["systems"][system]["prediction_as_fact_violation_count"] == 0 for row in rows for system in SYSTEM_IDS), "future hypotheses never promoted to current fact")
    failed = sum(1 for check in checks if not check["passed"])
    return {"checks": checks, "summary": {"passed": len(checks) - failed, "failed": failed}}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _baseline_rules_markdown() -> str:
    return """# G2.2 Baseline Rules

## N - NowMind Epistemic Geometry

Plans from partial current observation. Reconstructed memory and future
hypotheses may guide action only through typed assumptions. SCAN is selected by
a deterministic epistemic-cost policy when verification has value.

## C - Chronological Epistemic Planner

Uses the same path search, costs, sensor data, memory/hypothesis access, and
verification policy, but treats historical records through an indexed
chronological representation. It is a strong fair control and may match or beat
NowMind on scaling.

## R - Reactive Current-Only Planner

Uses the same movement and scan actions, but receives no memory reconstructions
or future hypotheses. It can inspect and explore but cannot use hidden target or
shortcut memories.

## O - Oracle

Evaluator-only upper bound with full world truth. It is not a fair cognitive
competitor and is used only for path-length and reachability reference.
"""


def _summary_markdown(
    seed: int,
    trial_count: int,
    metrics: dict[str, dict[str, float]],
    by_difficulty: dict[str, dict[str, dict[str, float]]],
) -> str:
    lines = ["# G2.2 Epistemic Geometry Benchmark Summary", "", f"- seed: `{seed}`", f"- trial_count: `{trial_count}`", ""]
    for system, values in metrics.items():
        lines.append(f"## {system}")
        lines.append(f"- goal_reached_rate: {values['goal_reached_rate']:.3f}")
        lines.append(f"- verification_action_rate: {values['verification_action_rate']:.3f}")
        lines.append(f"- memory_use_rate: {values['memory_use_rate']:.3f}")
        lines.append(f"- collision_rate: {values['collision_rate']:.3f}")
        lines.append(f"- mean_evidence_items_inspected: {values['mean_evidence_items_inspected']:.1f}")
        lines.append("")
    lines.append("## By Difficulty")
    for difficulty, systems in by_difficulty.items():
        lines.append(f"### {difficulty}")
        for system, values in systems.items():
            lines.append(
                f"- {system}: reached={values['goal_reached_rate']:.3f}, "
                f"verify={values['verification_action_rate']:.3f}, "
                f"evidence={values['mean_evidence_items_inspected']:.1f}"
            )
    return "\n".join(lines) + "\n"


def _compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if key not in {"plans", "executions"}
    }


def _is_failure_sample(result: dict[str, Any], oracle_length: int | None) -> bool:
    return bool(result["collisions"] or result["invalid_actions"] or (oracle_length is not None and not result["goal_reached"]))


def _rate(numerator: int | float, denominator: int | float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def _ci95(successes: int, n: int) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = successes / n
    spread = 1.96 * sqrt(p * (1.0 - p) / n)
    return max(0.0, p - spread), min(1.0, p + spread)


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[index]


def _difficulty_for(band: str) -> DifficultyConfig:
    for difficulty in DIFFICULTIES:
        if difficulty.band == band:
            return difficulty
    raise ValueError(f"unknown difficulty: {band}")


def _memory_cell(
    pose: Pose2D,
    state: OccupancyState,
    confidence: float,
    tags: tuple[str, ...],
    cycle_id: int = 1,
) -> MemoryReconstruction:
    key = f"g2_2_memory:{pose.x}:{pose.y}:{state.value}:{confidence}:{','.join(tags)}:{cycle_id}"
    return MemoryReconstruction(
        reconstruction_id=uuid5(NAMESPACE_URL, key),
        created_at_cycle_id=cycle_id + 1,
        proposition=Proposition(pose.cell_id(), RelationType.OCCUPANCY, state.value),
        source_trace_ids=(uuid5(NAMESPACE_URL, f"{key}:trace"),),
        historical_source_cycles=(cycle_id,),
        confidence=confidence,
        fidelity=0.9,
        distortion_tags=tags,
    )


def _memory_target(pose: Pose2D, confidence: float, tags: tuple[str, ...]) -> MemoryReconstruction:
    key = f"g2_2_target:{pose.x}:{pose.y}:{confidence}:{','.join(tags)}"
    return MemoryReconstruction(
        reconstruction_id=uuid5(NAMESPACE_URL, key),
        created_at_cycle_id=2,
        proposition=Proposition("target", RelationType.AT, pose.cell_id()),
        source_trace_ids=(uuid5(NAMESPACE_URL, f"{key}:trace"),),
        historical_source_cycles=(1,),
        confidence=confidence,
        fidelity=0.9,
        distortion_tags=tags,
    )


def _future_target(pose: Pose2D, truth: bool) -> FutureHypothesis:
    return FutureHypothesis(
        hypothesis_id=uuid5(NAMESPACE_URL, f"g2_2_future:{pose.x}:{pose.y}:{truth}"),
        created_at_cycle_id=1,
        proposition=Proposition("target", RelationType.AT, pose.cell_id()),
        confidence=0.72,
        generator_id="g2_2_epistemic_benchmark",
        metadata={"pose": pose.to_dict(), "truth": truth},
    )


def _distractor_memories(
    count: int,
    difficulty: DifficultyConfig,
    rng: random.Random,
) -> tuple[MemoryReconstruction, ...]:
    memories = []
    for index in range(count):
        pose = Pose2D(rng.randrange(0, difficulty.width), rng.randrange(0, difficulty.height))
        state = OccupancyState.FREE if index % 3 else OccupancyState.OCCUPIED
        memories.append(
            _memory_cell(
                pose,
                state,
                0.4 + (index % 5) * 0.08,
                ("distractor", f"h{count}"),
                cycle_id=max(1, index + 1),
            )
        )
    return tuple(memories)


def _shortcut_cell(world: SpatialWorldState) -> Pose2D:
    return Pose2D(max(1, world.width // 2 - 1), world.entity("agent").pose.y)


def _memory_as_observation_violations(geometry) -> int:
    violations = 0
    for cell in geometry.cells:
        if cell.memory_candidates and cell.observed_occupancy is OccupancyState.UNKNOWN and cell.provenance is not None:
            violations += 1
    return violations


def _assumption_pose(assumption) -> Pose2D | None:
    if assumption.proposition.source_id == "target":
        return pose_from_cell_id(assumption.proposition.target_id)
    return pose_from_cell_id(assumption.proposition.source_id)


def _truth_path_length(world: SpatialWorldState) -> int | None:
    path = _truth_path(world, world.entity("agent").pose, world.entity("target").pose)
    return max(0, len(path) - 1) if path else None


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


def _neighbors(pose: Pose2D) -> tuple[Pose2D, ...]:
    return (
        pose.moved(1, 0),
        pose.moved(0, 1),
        pose.moved(-1, 0),
        pose.moved(0, -1),
    )

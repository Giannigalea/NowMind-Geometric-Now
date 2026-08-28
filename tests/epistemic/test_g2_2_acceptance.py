from __future__ import annotations

from uuid import uuid4

from nowmind.epistemic import (
    EpistemicActionExecutor,
    EpistemicActionType,
    EpistemicCycleRunner,
    EpistemicDecisionType,
    EpistemicPolicyConfig,
    NowMindEpistemicPlanner,
    ObservationQuality,
    ReactiveEpistemicPlanner,
    SensorConfig,
    SensorReading,
    observe_epistemic_geometry,
)
from nowmind.evaluation.g2_2_benchmark import DEFAULT_SEED, generate_trials
from nowmind.geometry.relation import RelationType
from nowmind.spatial import OccupancyState, Pose2D, SpatialEntity, SpatialWorldState
from nowmind.temporal import FutureHypothesis, Proposition, TemporalSource
from nowmind.temporal.memory import MemoryReconstruction


def _world(
    width: int = 7,
    height: int = 5,
    agent: Pose2D = Pose2D(0, 2),
    target: Pose2D = Pose2D(6, 2),
) -> SpatialWorldState:
    return SpatialWorldState(
        width,
        height,
        [
            SpatialEntity("agent", "agent", agent, "Agent"),
            SpatialEntity("target", "target", target, "Target"),
        ],
    )


def _memory_cell(
    pose: Pose2D,
    state: OccupancyState = OccupancyState.FREE,
    confidence: float = 0.74,
    tag: str = "test_memory",
) -> MemoryReconstruction:
    return MemoryReconstruction(
        reconstruction_id=uuid4(),
        created_at_cycle_id=2,
        proposition=Proposition(pose.cell_id(), RelationType.OCCUPANCY, state.value),
        source_trace_ids=(uuid4(),),
        historical_source_cycles=(1,),
        confidence=confidence,
        fidelity=0.9,
        distortion_tags=(tag,),
    )


def _memory_target(
    pose: Pose2D,
    confidence: float = 0.9,
    tag: str = "target_memory",
) -> MemoryReconstruction:
    return MemoryReconstruction(
        reconstruction_id=uuid4(),
        created_at_cycle_id=2,
        proposition=Proposition("target", RelationType.AT, pose.cell_id()),
        source_trace_ids=(uuid4(),),
        historical_source_cycles=(1,),
        confidence=confidence,
        fidelity=0.9,
        distortion_tags=(tag,),
    )


def _hidden_shortcut_world(blocked: bool = False) -> SpatialWorldState:
    world = _world()
    for pose in (
        Pose2D(2, 2),
        Pose2D(3, 2),
        Pose2D(4, 2),
        Pose2D(5, 2),
        Pose2D(6, 2),
    ):
        world.hide_cell(pose)
    if blocked:
        world.set_obstacle(Pose2D(3, 2), "hidden_blocker")
        world.hide_cell(Pose2D(3, 2))
    return world


def _shortcut_memories(confidence: float = 0.74) -> tuple[MemoryReconstruction, ...]:
    return (
        _memory_cell(Pose2D(2, 2), confidence=confidence),
        _memory_cell(Pose2D(3, 2), confidence=confidence),
        _memory_cell(Pose2D(4, 2), confidence=confidence),
        _memory_cell(Pose2D(5, 2), confidence=confidence),
        _memory_target(Pose2D(6, 2), confidence=0.9),
    )


def _wide_sensor(scan_cost: float = 1.0) -> SensorConfig:
    return SensorConfig(
        visibility_radius=10,
        scan_radius_bonus=3,
        scan_cost=scan_cost,
        line_of_sight_blocks=False,
    )


def _cell_state(world: SpatialWorldState, pose: Pose2D, scan: bool = False) -> OccupancyState:
    return observe_epistemic_geometry(world, 1, _wide_sensor(), scan=scan).occupancy_at(pose)


def test_g2_2_perception_keeps_unseen_and_occluded_truth_unknown() -> None:
    outside_world = _world(6, 3, Pose2D(0, 1), Pose2D(5, 1))
    outside_world.set_obstacle(Pose2D(4, 1), "distant_blocker")
    local = observe_epistemic_geometry(
        outside_world,
        1,
        SensorConfig(visibility_radius=1, line_of_sight_blocks=False),
    )
    outside_cell = local.cell_at(Pose2D(4, 1))
    assert outside_cell.observed_occupancy is OccupancyState.UNKNOWN
    assert outside_cell.provenance is None

    occluded_world = _world(5, 1, Pose2D(0, 0), Pose2D(4, 0))
    occluded_world.set_obstacle(Pose2D(1, 0), "wall")
    occluded = observe_epistemic_geometry(
        occluded_world,
        1,
        SensorConfig(visibility_radius=5, line_of_sight_blocks=True),
    )
    assert occluded.cell_at(Pose2D(2, 0)).observed_occupancy is OccupancyState.UNKNOWN
    assert occluded.target_pose is None

    reading = SensorReading(Pose2D(3, 2), OccupancyState.FREE, 0.61, "sensor_a")
    sensed = observe_epistemic_geometry(
        _world(),
        1,
        SensorConfig(visibility_radius=0),
        sensor_readings=(reading,),
    )
    sensed_cell = sensed.cell_at(Pose2D(3, 2))
    assert sensed_cell.provenance is TemporalSource.OBSERVED_NOW
    assert sensed_cell.observation_confidence == 0.61
    assert sensed_cell.sensor_readings == (reading,)


def test_g2_2_contradictory_sensor_evidence_stays_structured_uncertainty() -> None:
    readings = (
        SensorReading(Pose2D(2, 2), OccupancyState.OCCUPIED, 0.58, "sensor_a"),
        SensorReading(Pose2D(2, 2), OccupancyState.FREE, 0.61, "sensor_b"),
    )
    memory = _memory_cell(Pose2D(2, 2), confidence=0.92)
    geometry = observe_epistemic_geometry(
        _world(),
        1,
        _wide_sensor(),
        reconstructed_memories=(memory,),
        sensor_readings=readings,
    )
    cell = geometry.cell_at(Pose2D(2, 2))

    assert cell.quality is ObservationQuality.CONTRADICTORY
    assert cell.observed_occupancy is OccupancyState.UNKNOWN
    assert cell.provenance is None
    assert cell.memory_candidates[0].provenance is TemporalSource.RECONSTRUCTED_MEMORY


def test_g2_2_scan_changes_observation_not_world_truth_and_creates_fresh_now() -> None:
    world = _hidden_shortcut_world(blocked=False)
    memories = _shortcut_memories()
    runner = EpistemicCycleRunner(sensor_config=_wide_sensor())
    planner = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0))
    executor = EpistemicActionExecutor()

    first = runner.run(world, reconstructed_memories=memories)
    plan = planner.plan(
        first.epistemic_geometry,
        memory_reconstructions=first.temporal_now.reconstructed_memories,
        history_record_count=50,
    )
    world_version_before = world.world_version
    result = executor.execute(world, plan)
    second = runner.run(world, reconstructed_memories=memories, scan=result.information_action)
    replanned = planner.plan(
        second.epistemic_geometry,
        memory_reconstructions=second.temporal_now.reconstructed_memories,
        history_record_count=50,
    )

    assert plan.decision_type is EpistemicDecisionType.VERIFY_FIRST
    assert result.action_type is EpistemicActionType.SCAN
    assert result.information_action
    assert result.cost == 1.0
    assert world.world_version == world_version_before
    assert second.temporal_now.now_id != first.temporal_now.now_id
    assert second.epistemic_geometry.scan_used
    assert replanned.decision_type is EpistemicDecisionType.KNOWN_SAFE


def test_g2_2_memory_supported_unknown_remains_unknown_until_contradicted_by_scan() -> None:
    world = _hidden_shortcut_world(blocked=True)
    memories = _shortcut_memories(confidence=0.74)
    geometry = observe_epistemic_geometry(
        world,
        1,
        _wide_sensor(),
        reconstructed_memories=memories,
    )
    hidden = geometry.cell_at(Pose2D(3, 2))
    plan = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0)).plan(
        geometry,
        memory_reconstructions=geometry.reconstructed_memories,
        history_record_count=50,
    )

    assert hidden.observed_occupancy is OccupancyState.UNKNOWN
    assert hidden.memory_candidates
    assert hidden.memory_candidates[0].provenance is TemporalSource.RECONSTRUCTED_MEMORY
    assert plan.decision_type is EpistemicDecisionType.VERIFY_FIRST
    assert all(assumption.source is TemporalSource.RECONSTRUCTED_MEMORY for assumption in plan.assumptions)

    scanned = observe_epistemic_geometry(
        world,
        2,
        _wide_sensor(),
        reconstructed_memories=memories,
        scan=True,
    )
    blocked = scanned.cell_at(Pose2D(3, 2))
    replanned = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0)).plan(
        scanned,
        memory_reconstructions=scanned.reconstructed_memories,
        history_record_count=50,
    )

    assert blocked.observed_occupancy is OccupancyState.OCCUPIED
    assert blocked.provenance is TemporalSource.OBSERVED_NOW
    assert blocked.memory_candidates[0].provenance is TemporalSource.RECONSTRUCTED_MEMORY
    assert all(step.to_pose != Pose2D(3, 2) for step in replanned.steps)


def test_g2_2_future_hypothesis_supports_branch_but_not_current_truth() -> None:
    world = _world()
    world.hide_cell(Pose2D(6, 2))
    future_pose = Pose2D(6, 1)
    hypothesis = FutureHypothesis.create(
        1,
        Proposition("target", RelationType.AT, future_pose.cell_id()),
        0.8,
        metadata={"pose": future_pose.to_dict()},
    )
    geometry = observe_epistemic_geometry(
        world,
        1,
        _wide_sensor(),
        future_hypotheses=(hypothesis,),
    )
    plan = NowMindEpistemicPlanner(
        EpistemicPolicyConfig(scan_cost=10.0, verify_risk_threshold=0.5)
    ).plan(geometry, future_hypotheses=geometry.future_hypotheses)

    assert geometry.target_pose is None
    assert geometry.cell_at(future_pose).observed_occupancy is OccupancyState.FREE
    assert plan.goal == future_pose
    assert plan.conditional
    assert plan.assumptions[0].source is TemporalSource.HYPOTHETICAL_FUTURE

    world.move_entity("target", future_pose)
    confirmed = observe_epistemic_geometry(world, 2, _wide_sensor(), scan=True)
    assert confirmed.target_pose == future_pose
    assert hypothesis.provenance is TemporalSource.HYPOTHETICAL_FUTURE

    falsified_world = _world(target=Pose2D(6, 2))
    falsified_world.hide_cell(Pose2D(6, 2))
    falsified = observe_epistemic_geometry(falsified_world, 3, _wide_sensor(), scan=True)
    falsified_plan = NowMindEpistemicPlanner().plan(falsified)
    assert falsified.target_pose == Pose2D(6, 2)
    assert falsified_plan.goal == Pose2D(6, 2)


def test_g2_2_planner_selects_known_safe_conditional_and_verify_first_deterministically() -> None:
    safe_geometry = observe_epistemic_geometry(_world(), 1, _wide_sensor())
    planner = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0))
    safe_plan = planner.plan(safe_geometry)

    conditional_geometry = observe_epistemic_geometry(
        _hidden_shortcut_world(blocked=False),
        1,
        _wide_sensor(scan_cost=100.0),
        reconstructed_memories=_shortcut_memories(confidence=0.99),
    )
    conditional_planner = NowMindEpistemicPlanner(
        EpistemicPolicyConfig(scan_cost=100.0, verify_risk_threshold=0.5)
    )
    conditional_plan = conditional_planner.plan(
        conditional_geometry,
        memory_reconstructions=conditional_geometry.reconstructed_memories,
        history_record_count=100,
    )

    verify_geometry = observe_epistemic_geometry(
        _hidden_shortcut_world(blocked=True),
        1,
        _wide_sensor(scan_cost=1.0),
        reconstructed_memories=_shortcut_memories(confidence=0.74),
    )
    first_verify = planner.plan(
        verify_geometry,
        memory_reconstructions=verify_geometry.reconstructed_memories,
        history_record_count=100,
    )
    second_verify = planner.plan(
        verify_geometry,
        memory_reconstructions=verify_geometry.reconstructed_memories,
        history_record_count=100,
    )
    reactive = ReactiveEpistemicPlanner().plan(verify_geometry)

    assert safe_plan.decision_type is EpistemicDecisionType.KNOWN_SAFE
    assert safe_plan.first_step().action_type is not EpistemicActionType.SCAN
    assert conditional_plan.decision_type is EpistemicDecisionType.CONDITIONAL_SHORTCUT
    assert conditional_plan.conditional
    assert conditional_plan.first_step().action_type is not EpistemicActionType.SCAN
    assert first_verify.decision_type is EpistemicDecisionType.VERIFY_FIRST
    assert [step.action_type for step in first_verify.steps] == [
        step.action_type for step in second_verify.steps
    ]
    assert reactive.decision_type is EpistemicDecisionType.EXPLORE


def test_g2_2_hidden_dynamic_changes_remain_unknown_until_observed() -> None:
    world = _hidden_shortcut_world(blocked=False)
    assert _cell_state(world, Pose2D(3, 2)) is OccupancyState.UNKNOWN

    world.set_obstacle(Pose2D(3, 2), "unseen_new_blocker")
    world.hide_cell(Pose2D(3, 2))
    stale_geometry = observe_epistemic_geometry(
        world,
        2,
        _wide_sensor(),
        reconstructed_memories=_shortcut_memories(confidence=0.99),
    )
    stale_plan = NowMindEpistemicPlanner(
        EpistemicPolicyConfig(scan_cost=100.0, verify_risk_threshold=0.5)
    ).plan(
        stale_geometry,
        memory_reconstructions=stale_geometry.reconstructed_memories,
        history_record_count=50,
    )

    assert stale_geometry.cell_at(Pose2D(3, 2)).observed_occupancy is OccupancyState.UNKNOWN
    assert stale_plan.decision_type is EpistemicDecisionType.CONDITIONAL_SHORTCUT

    scanned = observe_epistemic_geometry(
        world,
        3,
        _wide_sensor(),
        reconstructed_memories=stale_geometry.reconstructed_memories,
        scan=True,
    )
    refreshed_plan = NowMindEpistemicPlanner().plan(
        scanned,
        memory_reconstructions=scanned.reconstructed_memories,
        history_record_count=50,
    )
    assert scanned.cell_at(Pose2D(3, 2)).observed_occupancy is OccupancyState.OCCUPIED
    assert all(step.to_pose != Pose2D(3, 2) for step in refreshed_plan.steps)

    target_world = _world()
    target_world.hide_cell(Pose2D(6, 2))
    target_world.move_entity("target", Pose2D(6, 1))
    target_world.hide_cell(Pose2D(6, 1))
    unobserved_target = observe_epistemic_geometry(target_world, 1, _wide_sensor())
    observed_target = observe_epistemic_geometry(target_world, 2, _wide_sensor(), scan=True)
    assert unobserved_target.target_pose is None
    assert observed_target.target_pose == Pose2D(6, 1)


def test_g2_2_long_history_cohorts_are_reproducible_and_source_labels_stay_typed() -> None:
    first = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 144)]
    second = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 144)]
    trials = generate_trials(DEFAULT_SEED, 144)

    assert first == second
    assert {trial.history_cohort for trial in trials} >= {"H0", "H10", "H50", "H100", "H500"}

    long_trial = next(trial for trial in trials if trial.history_cohort == "H500")
    geometry = observe_epistemic_geometry(
        long_trial.initial_world,
        1,
        long_trial.sensor_config,
        reconstructed_memories=long_trial.memory_reconstructions,
        future_hypotheses=long_trial.future_hypotheses,
        sensor_readings=long_trial.sensor_readings,
    )
    labels = {cell.provenance for cell in geometry.cells}
    memory_labels = {
        memory.provenance
        for cell in geometry.cells
        for memory in cell.memory_candidates
    }

    assert TemporalSource.RECONSTRUCTED_MEMORY not in labels
    assert memory_labels <= {TemporalSource.RECONSTRUCTED_MEMORY}

from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

from nowmind.epistemic import (
    EpistemicDecisionType,
    EpistemicPolicyConfig,
    EpistemicRecoveryState,
    NowMindEpistemicPlanner,
    SensorConfig,
    observe_epistemic_geometry,
)
from nowmind.geometry.relation import RelationType
from nowmind.spatial import OccupancyState, Pose2D, SpatialEntity, SpatialWorldState
from nowmind.temporal import Proposition, RetrievalCue, TemporalSource
from nowmind.temporal.memory import (
    IndexedMemoryStore,
    MemoryReconstruction,
    MemoryStore,
    MemoryTrace,
)


def _world(target: Pose2D = Pose2D(6, 2)) -> SpatialWorldState:
    return SpatialWorldState(
        7,
        5,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 2), "Agent"),
            SpatialEntity("target", "target", target, "Target"),
        ],
    )


def _sensor() -> SensorConfig:
    return SensorConfig(
        visibility_radius=10,
        scan_radius_bonus=3,
        scan_cost=1.0,
        line_of_sight_blocks=False,
    )


def _memory_target(pose: Pose2D, tag: str = "target") -> MemoryReconstruction:
    return MemoryReconstruction(
        uuid4(),
        2,
        Proposition("target", RelationType.AT, pose.cell_id()),
        (uuid4(),),
        (1,),
        0.9,
        0.9,
        (tag,),
    )


def _memory_cell(pose: Pose2D, state: OccupancyState = OccupancyState.FREE) -> MemoryReconstruction:
    return MemoryReconstruction(
        uuid4(),
        2,
        Proposition(pose.cell_id(), RelationType.OCCUPANCY, state.value),
        (uuid4(),),
        (1,),
        0.8,
        0.9,
        ("cell",),
    )


def _trace(source: str, relation: RelationType, target: str, cycle: int) -> MemoryTrace:
    return MemoryTrace.create(
        source_cycle_id=cycle,
        encoded_at_cycle_id=cycle,
        proposition=Proposition(source, relation, target),
        original_source=TemporalSource.OBSERVED_NOW,
        encoded_confidence=0.9,
    )


def test_g2_2_1_indexed_and_reference_retrieval_agree_semantically() -> None:
    traces = (
        _trace("target", RelationType.AT, Pose2D(6, 2).cell_id(), 1),
        _trace(Pose2D(2, 2).cell_id(), RelationType.OCCUPANCY, OccupancyState.FREE.value, 2),
        _trace("distractor", RelationType.INSIDE, "box", 3),
    )
    reference = MemoryStore(traces)
    indexed = IndexedMemoryStore(traces)
    cue = RetrievalCue.for_relation("target", RelationType.AT)

    reference_result = reference.retrieve(cue)
    indexed_result = indexed.retrieve_with_metrics(cue)

    assert [item.trace.proposition for item in indexed_result.retrieved] == [
        item.trace.proposition for item in reference_result
    ]
    assert indexed_result.metrics.stored_records == len(traces)
    assert indexed_result.metrics.records_scanned < len(traces)
    assert indexed_result.metrics.records_returned == 1


def test_g2_2_1_stale_target_disconfirmation_preserves_trace_and_reacquires() -> None:
    world = _world()
    world.hide_cell(Pose2D(6, 2))
    memory = _memory_target(Pose2D(2, 2), "stale_target")
    recovery = EpistemicRecoveryState()
    geometry = observe_epistemic_geometry(world, 1, _sensor(), reconstructed_memories=(memory,))
    update = recovery.update_from_geometry(geometry)
    plan = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0)).plan(
        geometry,
        memory_reconstructions=(memory,),
        disconfirmed_target_poses=recovery.disconfirmed_target_poses,
    )

    assert update.newly_disconfirmed_targets == (Pose2D(2, 2),)
    assert memory.proposition.target_id == Pose2D(2, 2).cell_id()
    assert plan.goal != Pose2D(2, 2)
    assert plan.decision_type is EpistemicDecisionType.EXPLORE

    scanned = observe_epistemic_geometry(world, 2, _sensor(), reconstructed_memories=(memory,), scan=True)
    reacquired = recovery.update_from_geometry(scanned, executed_steps=1)
    assert scanned.target_pose == Pose2D(6, 2)
    assert reacquired.target_reacquired
    assert recovery.target_reacquired


def test_g2_2_1_hidden_obstacle_recovery_waits_for_observation() -> None:
    world = _world()
    shortcut = Pose2D(3, 2)
    world.hide_cell(shortcut)
    memory = _memory_cell(shortcut, OccupancyState.FREE)
    recovery = EpistemicRecoveryState()
    before = observe_epistemic_geometry(world, 1, _sensor(), reconstructed_memories=(memory,))

    world.set_obstacle(shortcut, "hidden_new_obstacle")
    world.hide_cell(shortcut)
    still_hidden = observe_epistemic_geometry(world, 2, _sensor(), reconstructed_memories=(memory,))
    hidden_update = recovery.update_from_geometry(still_hidden)

    assert before.cell_at(shortcut).observed_occupancy is OccupancyState.UNKNOWN
    assert still_hidden.cell_at(shortcut).observed_occupancy is OccupancyState.UNKNOWN
    assert hidden_update.newly_invalidated_cells == ()

    scanned = observe_epistemic_geometry(world, 3, _sensor(), reconstructed_memories=(memory,), scan=True)
    observed_update = recovery.update_from_geometry(scanned)
    replanned = NowMindEpistemicPlanner().plan(
        scanned,
        memory_reconstructions=(memory,),
        invalidated_poses=recovery.invalidated_poses,
    )

    assert scanned.cell_at(shortcut).observed_occupancy is OccupancyState.OCCUPIED
    assert observed_update.newly_invalidated_cells == (shortcut,)
    assert all(step.to_pose != shortcut for step in replanned.steps)


def test_g2_2_1_hidden_target_move_does_not_leak_until_scan() -> None:
    world = _world(target=Pose2D(6, 2))
    world.hide_cell(Pose2D(6, 2))
    world.move_entity("target", Pose2D(6, 1))
    world.hide_cell(Pose2D(6, 1))

    local = observe_epistemic_geometry(world, 1, _sensor())
    scanned = observe_epistemic_geometry(world, 2, _sensor(), scan=True)

    assert local.target_pose is None
    assert scanned.target_pose == Pose2D(6, 1)


def test_g2_2_1_agent_occupied_hidden_memory_cell_can_disconfirm_target() -> None:
    old_target = Pose2D(6, 2)
    new_target = Pose2D(6, 1)
    world = _world(target=old_target)
    world.hide_cell(old_target)
    world.move_entity("target", new_target)
    world.hide_cell(new_target)
    world.move_entity("agent", old_target)
    memory = _memory_target(old_target, "moved_target")
    recovery = EpistemicRecoveryState()

    local = observe_epistemic_geometry(world, 1, _sensor(), reconstructed_memories=(memory,))
    update = recovery.update_from_geometry(local)

    assert local.cell_at(old_target).observed_occupancy is OccupancyState.FREE
    assert local.target_pose is None
    assert new_target not in local.visible_cells
    assert update.newly_disconfirmed_targets == (old_target,)


def test_g2_2_1_verification_is_skipped_after_scan_when_decision_cannot_change() -> None:
    world = _world()
    for pose in (Pose2D(2, 2), Pose2D(3, 2), Pose2D(4, 2), Pose2D(5, 2)):
        world.hide_cell(pose)
    memories = (
        _memory_cell(Pose2D(2, 2)),
        _memory_cell(Pose2D(3, 2)),
        _memory_cell(Pose2D(4, 2)),
        _memory_cell(Pose2D(5, 2)),
        _memory_target(Pose2D(6, 2)),
    )
    planner = NowMindEpistemicPlanner(EpistemicPolicyConfig(scan_cost=1.0))
    first = observe_epistemic_geometry(world, 1, _sensor(), reconstructed_memories=memories)
    verify = planner.plan(first, memory_reconstructions=memories)
    scanned = observe_epistemic_geometry(world, 2, _sensor(), reconstructed_memories=memories, scan=True)
    after_scan = planner.plan(scanned, memory_reconstructions=memories)

    assert verify.decision_type is EpistemicDecisionType.VERIFY_FIRST
    assert after_scan.decision_type is not EpistemicDecisionType.VERIFY_FIRST


def test_g2_2_1_runtime_does_not_import_benchmark_metadata() -> None:
    root = Path(__file__).parents[2] / "nowmind" / "epistemic"
    forbidden_terms = {"trial_id", "family", "expected_answer", "20260823"}
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert forbidden_terms.isdisjoint(set(text.split()))
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.module is None or not node.module.startswith("nowmind.evaluation")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("nowmind.evaluation")

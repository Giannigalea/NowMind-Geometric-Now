from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from nowmind.geometry.relation import RelationType
from nowmind.spatial import (
    AStarPlanner,
    ActionExecutor,
    ActionProposal,
    ChronologicalGeometricPlanner,
    ClosedLoopController,
    ConstraintCode,
    OccupancyState,
    Pose2D,
    SpatialCycleRunner,
    SpatialEntity,
    SpatialWorldState,
    Transformation,
    TransformationType,
    apply_transformation,
)
from nowmind.temporal import FutureHypothesis, Proposition, TemporalSource
from nowmind.temporal.memory import MemoryReconstruction


def _memory_cell(pose: Pose2D, state: OccupancyState) -> MemoryReconstruction:
    from uuid import uuid4

    return MemoryReconstruction(
        reconstruction_id=uuid4(),
        created_at_cycle_id=2,
        proposition=Proposition(
            source_id=pose.cell_id(),
            relation_type=RelationType.OCCUPANCY,
            target_id=state.value,
        ),
        source_trace_ids=(uuid4(),),
        historical_source_cycles=(1,),
        confidence=0.9,
        fidelity=0.9,
        distortion_tags=(),
    )


def _world(width: int = 5, height: int = 5) -> SpatialWorldState:
    return SpatialWorldState(
        width,
        height,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 0), "Agent"),
            SpatialEntity("target", "target", Pose2D(width - 1, height - 1), "Target"),
        ],
    )


def test_g2_1_spatial_geometry_derives_coordinates_occupancy_and_relations() -> None:
    world = _world()
    world.set_obstacle(Pose2D(2, 0))
    world.hide_cell(Pose2D(1, 1))
    geometry = world.observe(cycle_id=1)

    assert geometry.occupancy_at(Pose2D(0, 0)) is OccupancyState.FREE
    assert geometry.occupancy_at(Pose2D(2, 0)) is OccupancyState.OCCUPIED
    assert geometry.occupancy_at(Pose2D(1, 1)) is OccupancyState.UNKNOWN
    assert geometry.derived_relations
    assert any(
        relation.relation_type is RelationType.LEFT_OF
        and relation.source_id == "agent"
        and relation.target_id == "target"
        for relation in geometry.derived_relations
    )
    assert geometry.blocking_entity_at(Pose2D(2, 0)) is not None

    with pytest.raises(ValueError):
        SpatialWorldState(3, 3, [SpatialEntity("bad", "agent", Pose2D(9, 9))])


def test_g2_1_transformations_create_immutable_hypothetical_geometries() -> None:
    world = _world()
    geometry = world.observe(cycle_id=1)
    east = Transformation.create(TransformationType.MOVE_EAST, source_cycle_id=1)
    outcome = apply_transformation(geometry, east)

    assert outcome.valid
    assert outcome.from_pose == Pose2D(0, 0)
    assert outcome.to_pose == Pose2D(1, 0)
    assert outcome.hypothetical_geometry.provenance is TemporalSource.HYPOTHETICAL_FUTURE
    assert outcome.hypothetical_geometry.parent_id is None
    assert world.entity("agent").pose == Pose2D(0, 0)
    with pytest.raises(FrozenInstanceError):
        outcome.hypothetical_geometry.depth = 99  # type: ignore[misc]

    second = apply_transformation(outcome.hypothetical_geometry.geometry, east, parent=outcome.hypothetical_geometry)
    assert second.hypothetical_geometry.parent_id == outcome.hypothetical_geometry.hypothesis_id
    assert second.hypothetical_geometry.depth == 2


def test_g2_1_transformation_constraints_are_structured() -> None:
    world = _world()
    world.set_obstacle(Pose2D(1, 0))
    geometry = world.observe(cycle_id=1)

    blocked = apply_transformation(
        geometry,
        Transformation.create(TransformationType.MOVE_EAST, source_cycle_id=1),
    )
    assert not blocked.valid
    assert {violation.code for violation in blocked.violations} >= {
        ConstraintCode.COLLISION,
        ConstraintCode.BLOCKED,
    }

    out_of_bounds = apply_transformation(
        geometry,
        Transformation.create(TransformationType.MOVE_NORTH, source_cycle_id=1),
    )
    assert not out_of_bounds.valid
    assert out_of_bounds.violations[0].code is ConstraintCode.OUT_OF_BOUNDS
    for move in (
        TransformationType.MOVE_NORTH,
        TransformationType.MOVE_SOUTH,
        TransformationType.MOVE_EAST,
        TransformationType.MOVE_WEST,
    ):
        dx, dy = move.delta
        assert abs(dx) + abs(dy) == 1


def test_g2_1_planner_finds_routes_reports_no_route_and_is_deterministic() -> None:
    world = _world()
    geometry = world.observe(cycle_id=1)
    planner = AStarPlanner()
    first = planner.plan(geometry)
    second = planner.plan(geometry)

    assert first.valid
    assert [step.to_pose for step in first.steps] == [step.to_pose for step in second.steps]
    assert first.total_cost == len(first.steps)
    assert first.explanation
    assert first.rejected_alternatives

    blocked_world = SpatialWorldState(
        3,
        3,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 1)),
            SpatialEntity("target", "target", Pose2D(2, 1)),
            SpatialEntity("wall_a", "obstacle", Pose2D(1, 0), blocks_movement=True),
            SpatialEntity("wall_b", "obstacle", Pose2D(1, 1), blocks_movement=True),
            SpatialEntity("wall_c", "obstacle", Pose2D(1, 2), blocks_movement=True),
        ],
    )
    no_route = planner.plan(blocked_world.observe(cycle_id=1))
    assert not no_route.valid

    chronological = ChronologicalGeometricPlanner().plan(geometry)
    assert chronological.valid
    assert chronological.total_cost == first.total_cost


def test_g2_1_memory_assumptions_do_not_override_observation() -> None:
    blocked = SpatialWorldState(
        3,
        3,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 1)),
            SpatialEntity("target", "target", Pose2D(2, 1)),
            SpatialEntity("wall", "obstacle", Pose2D(1, 1), blocks_movement=True),
        ],
    )
    memory_free = (_memory_cell(Pose2D(1, 1), OccupancyState.FREE),)
    plan = AStarPlanner().plan(blocked.observe(1), memory_reconstructions=memory_free)
    assert all(step.to_pose != Pose2D(1, 1) for step in plan.steps)

    open_world = SpatialWorldState(
        3,
        3,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 1)),
            SpatialEntity("target", "target", Pose2D(2, 1)),
        ],
    )
    memory_blocked = (_memory_cell(Pose2D(1, 1), OccupancyState.OCCUPIED),)
    open_plan = AStarPlanner().plan(open_world.observe(1), memory_reconstructions=memory_blocked)
    assert open_plan.valid
    assert open_plan.steps[0].to_pose == Pose2D(1, 1)


def test_g2_1_unknown_cells_require_explicit_memory_assumptions() -> None:
    world = SpatialWorldState(
        3,
        3,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 1)),
            SpatialEntity("target", "target", Pose2D(2, 1)),
            SpatialEntity("wall_a", "obstacle", Pose2D(1, 0), blocks_movement=True),
            SpatialEntity("wall_b", "obstacle", Pose2D(1, 2), blocks_movement=True),
        ],
        hidden_cells=(Pose2D(1, 1),),
    )
    geometry = world.observe(1)
    no_memory = AStarPlanner().plan(geometry)
    with_memory = AStarPlanner().plan(
        geometry,
        memory_reconstructions=(_memory_cell(Pose2D(1, 1), OccupancyState.FREE),),
    )

    assert not no_memory.valid
    assert with_memory.valid
    assert with_memory.conditional
    assert with_memory.assumptions[0].source is TemporalSource.RECONSTRUCTED_MEMORY


def test_g2_1_future_hypotheses_never_become_current_observation() -> None:
    world = _world()
    future_pose = Pose2D(1, 4)
    hypothesis = FutureHypothesis.create(
        1,
        Proposition("target", RelationType.AT, future_pose.cell_id()),
        0.7,
        metadata={"pose": future_pose.to_dict()},
    )
    state = SpatialCycleRunner().run(world, future_hypotheses=(hypothesis,))
    plan = AStarPlanner().plan(state.spatial_geometry)

    assert state.temporal_now.future_hypotheses[0].provenance is TemporalSource.HYPOTHETICAL_FUTURE
    assert state.spatial_geometry.target().pose == Pose2D(4, 4)
    assert plan.goal == Pose2D(4, 4)

    world.move_entity("target", future_pose)
    confirmed = SpatialCycleRunner(next_cycle_id=2).run(world, future_hypotheses=(hypothesis,))
    assert confirmed.spatial_geometry.target().pose == future_pose
    assert hypothesis.provenance is TemporalSource.HYPOTHETICAL_FUTURE


def test_g2_1_action_executor_changes_world_only_one_step_then_fresh_observation() -> None:
    world = _world()
    controller = ClosedLoopController(world)
    first_state = controller.observe()
    plan = controller.plan_current()
    result, second_state = controller.execute_one_step(plan)

    assert result.success
    assert result.observation_required
    assert world.entity("agent").pose == plan.steps[0].to_pose
    assert second_state.temporal_now.now_id != first_state.temporal_now.now_id
    assert second_state.temporal_now.cycle_id == first_state.temporal_now.cycle_id + 1
    assert controller.history[-1]["fresh_now_id"] == str(second_state.temporal_now.now_id)

    later_step = plan.steps[min(1, len(plan.steps) - 1)].to_pose
    assert world.entity("agent").pose != later_step or len(plan.steps) == 1


def test_g2_1_replanning_reacts_to_obstacles_target_moves_memory_and_hypotheses() -> None:
    world = _world()
    geometry = world.observe(1)
    plan = AStarPlanner().plan(geometry)
    next_pose = plan.steps[0].to_pose
    world.set_obstacle(next_pose)
    updated = world.observe(2)
    replanned = AStarPlanner().plan(updated)
    assert replanned.steps
    assert replanned.steps[0].to_pose != next_pose

    world.move_entity("target", Pose2D(0, 4))
    moved_target = world.observe(3)
    moved_plan = AStarPlanner().plan(moved_target)
    assert moved_plan.goal == Pose2D(0, 4)

    hidden = SpatialWorldState(
        3,
        3,
        [
            SpatialEntity("agent", "agent", Pose2D(0, 1)),
            SpatialEntity("target", "target", Pose2D(2, 1)),
            SpatialEntity("wall_a", "obstacle", Pose2D(1, 0), blocks_movement=True),
            SpatialEntity("wall_b", "obstacle", Pose2D(1, 2), blocks_movement=True),
        ],
        hidden_cells=(Pose2D(1, 1),),
    )
    conditional = AStarPlanner().plan(
        hidden.observe(1),
        memory_reconstructions=(_memory_cell(Pose2D(1, 1), OccupancyState.FREE),),
    )
    assert conditional.conditional
    hidden.set_obstacle(Pose2D(1, 1))
    hidden.reveal_cell(Pose2D(1, 1))
    contradicted = AStarPlanner().plan(
        hidden.observe(2),
        memory_reconstructions=(_memory_cell(Pose2D(1, 1), OccupancyState.FREE),),
    )
    assert not contradicted.valid

    false_future = FutureHypothesis.create(
        1,
        Proposition("target", RelationType.AT, Pose2D(2, 2).cell_id()),
        0.7,
    )
    state = SpatialCycleRunner().run(_world(), future_hypotheses=(false_future,))
    current_plan = AStarPlanner().plan(state.spatial_geometry)
    assert current_plan.goal == state.spatial_geometry.target().pose

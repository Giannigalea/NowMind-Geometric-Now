from __future__ import annotations

from nowmind.core.cycle import CognitiveCycleRunner
from nowmind.demo.cli import main
from nowmind.demo.scenarios import all_scenarios
from nowmind.geometry.relation import RelationType
from nowmind.reasoning.query import Query, TruthStatus
from nowmind.reasoning.reasoner import answer
from nowmind.world.events import AddEntity, MoveRelation, SetRelation
from nowmind.world.model import WorldState


def test_move_object_scenario_has_no_stale_state() -> None:
    world = WorldState()
    world.apply(AddEntity("a", "object"))
    world.apply(AddEntity("b", "object"))
    world.apply(MoveRelation("a", "b", RelationType.LEFT_OF))
    runner = CognitiveCycleRunner()

    cycle_one = runner.run(world)
    world.apply(MoveRelation("a", "b", RelationType.RIGHT_OF))
    cycle_two = runner.run(world)

    assert answer(cycle_one, Query.relation("a", "b", RelationType.LEFT_OF)).status is TruthStatus.TRUE
    assert answer(cycle_two, Query.relation("a", "b", RelationType.RIGHT_OF)).status is TruthStatus.TRUE
    assert answer(cycle_two, Query.relation("a", "b", RelationType.LEFT_OF)).status is TruthStatus.UNKNOWN


def test_three_object_chain_scenario() -> None:
    world = WorldState()
    for entity_id in ("a", "b", "c"):
        world.apply(AddEntity(entity_id, "object"))
    world.apply(SetRelation("a", "b", RelationType.LEFT_OF))
    world.apply(SetRelation("b", "c", RelationType.LEFT_OF))
    now = CognitiveCycleRunner().run(world)

    result = answer(now, Query.explain("a", RelationType.LEFT_OF, "c"))

    assert result.status is TruthStatus.TRUE
    assert any(step.rule_id == "LEFT_TRANSITIVE" for step in result.explanation)


def test_nested_container_scenario() -> None:
    world = WorldState()
    world.apply(AddEntity("key", "object"))
    world.apply(AddEntity("box", "container"))
    world.apply(AddEntity("cabinet", "container"))
    world.apply(SetRelation("key", "box", RelationType.INSIDE))
    world.apply(SetRelation("box", "cabinet", RelationType.INSIDE))
    now = CognitiveCycleRunner().run(world)

    inside = answer(now, Query.explain("key", RelationType.INSIDE, "cabinet"))
    contains = answer(now, Query.relation("cabinet", "key", RelationType.CONTAINS))

    assert inside.status is TruthStatus.TRUE
    assert contains.status is TruthStatus.TRUE
    assert any(step.rule_id == "INSIDE_TRANSITIVE" for step in inside.explanation)


def test_current_contradiction_scenario() -> None:
    world = WorldState()
    world.apply(AddEntity("a", "object"))
    world.apply(AddEntity("b", "object"))
    world.apply(SetRelation("a", "b", RelationType.LEFT_OF))
    world.apply(SetRelation("a", "b", RelationType.RIGHT_OF))
    now = CognitiveCycleRunner().run(world)

    result = answer(now, Query.relation("a", "b", RelationType.LEFT_OF))

    assert result.status is TruthStatus.CONTRADICTORY
    assert result.issues


def test_demo_scenarios_and_cli_run(capsys) -> None:
    scenarios = all_scenarios()
    assert len(scenarios) == 4
    assert main() == 0
    output = capsys.readouterr().out
    assert "Demo 1 - State Change" in output
    assert "stale LEFT_OF(red_cube, blue_cube) present in cycle 2: False" in output
    assert "Demo 4 - Contradiction" in output


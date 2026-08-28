from __future__ import annotations

from dataclasses import dataclass

from nowmind.core.cycle import CognitiveCycleRunner
from nowmind.core.now_state import NowState
from nowmind.evaluation.recorder import ExperimentRecorder
from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.reasoning.query import Answer, Query, TruthStatus
from nowmind.reasoning.reasoner import answer
from nowmind.world.events import AddEntity, MoveRelation, SetRelation
from nowmind.world.model import WorldState


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    title: str
    lines: tuple[str, ...]


def state_change_demo() -> ScenarioResult:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.LEFT_OF))

    runner = CognitiveCycleRunner()
    recorder = ExperimentRecorder()

    cycle_one = runner.run(world)
    query_left = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    answer_one = answer(cycle_one, query_left)
    recorder.record(cycle_one, query_left, answer_one)

    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
    cycle_two = runner.run(world)
    query_right = Query.relation("red_cube", "blue_cube", RelationType.RIGHT_OF)
    answer_two = answer(cycle_two, query_right)
    recorder.record(cycle_two, query_right, answer_two)

    stale_left = cycle_two.geometry.find_relation(
        "red_cube",
        "blue_cube",
        RelationType.LEFT_OF,
    )

    return ScenarioResult(
        title="Demo 1 - State Change",
        lines=(
            _cycle_line(cycle_one),
            f"observed: {_format_relation(_first_observed(cycle_one))}",
            f"inferred inverse: {_format_relation(_first_inferred(cycle_one))}",
            f"query red_cube LEFT_OF blue_cube: {_format_answer(answer_one)}",
            "world event: move red_cube to the other side",
            _cycle_line(cycle_two),
            f"observed: {_format_relation(_first_observed(cycle_two))}",
            f"inferred inverse: {_format_relation(_first_inferred(cycle_two))}",
            f"query red_cube RIGHT_OF blue_cube: {_format_answer(answer_two)}",
            f"stale LEFT_OF(red_cube, blue_cube) present in cycle 2: {stale_left is not None}",
        ),
    )


def transitive_demo() -> ScenarioResult:
    world = WorldState()
    for entity_id in ("a", "b", "c"):
        world.apply(AddEntity(entity_id, "object", entity_id.upper()))
    world.apply(SetRelation("a", "b", RelationType.LEFT_OF))
    world.apply(SetRelation("b", "c", RelationType.LEFT_OF))

    now = CognitiveCycleRunner().run(world)
    query = Query.explain("a", RelationType.LEFT_OF, "c")
    result = answer(now, query)

    return ScenarioResult(
        title="Demo 2 - Transitive Reasoning",
        lines=(
            _cycle_line(now),
            "observed: LEFT_OF(a, b), LEFT_OF(b, c)",
            f"query a LEFT_OF c: {_format_answer(result)}",
            f"explanation: {_format_explanation(result)}",
        ),
    )


def containment_demo() -> ScenarioResult:
    world = WorldState()
    for entity_id, kind in (("key", "object"), ("box", "container"), ("cabinet", "container")):
        world.apply(AddEntity(entity_id, kind, entity_id))
    world.apply(SetRelation("key", "box", RelationType.INSIDE))
    world.apply(SetRelation("box", "cabinet", RelationType.INSIDE))

    now = CognitiveCycleRunner().run(world)
    inside_query = Query.explain("key", RelationType.INSIDE, "cabinet")
    contains_query = Query.relation("cabinet", "key", RelationType.CONTAINS)
    inside_answer = answer(now, inside_query)
    contains_answer = answer(now, contains_query)

    return ScenarioResult(
        title="Demo 3 - Nested Containment",
        lines=(
            _cycle_line(now),
            "observed: INSIDE(key, box), INSIDE(box, cabinet)",
            f"query key INSIDE cabinet: {_format_answer(inside_answer)}",
            f"explanation: {_format_explanation(inside_answer)}",
            f"query cabinet CONTAINS key: {_format_answer(contains_answer)}",
        ),
    )


def contradiction_demo() -> ScenarioResult:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(SetRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
    world.apply(SetRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))

    now = CognitiveCycleRunner().run(world)
    query = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    result = answer(now, query)

    issue_lines = tuple(f"issue: {issue.issue_type.value} - {issue.message}" for issue in result.issues)
    return ScenarioResult(
        title="Demo 4 - Contradiction",
        lines=(
            _cycle_line(now),
            "observed: LEFT_OF(red_cube, blue_cube), RIGHT_OF(red_cube, blue_cube)",
            f"query red_cube LEFT_OF blue_cube: {_format_answer(result)}",
            *issue_lines,
        ),
    )


def all_scenarios() -> tuple[ScenarioResult, ...]:
    return (
        state_change_demo(),
        transitive_demo(),
        containment_demo(),
        contradiction_demo(),
    )


def _cycle_line(now: NowState) -> str:
    return f"cycle_id={now.cycle_id} now_id={now.now_id}"


def _first_observed(now: NowState) -> Relation:
    for relation in now.geometry.relations:
        if relation.provenance is Provenance.OBSERVED_NOW:
            return relation
    raise RuntimeError("scenario has no observed relation")


def _first_inferred(now: NowState) -> Relation:
    for relation in now.geometry.relations:
        if relation.provenance is Provenance.INFERRED_NOW:
            return relation
    raise RuntimeError("scenario has no inferred relation")


def _format_relation(relation: Relation) -> str:
    return (
        f"{relation.relation_type.name}({relation.source_id}, {relation.target_id}) "
        f"[{relation.provenance.value}, confidence={relation.confidence:.2f}]"
    )


def _format_answer(result: Answer) -> str:
    if result.status is TruthStatus.TRUE:
        return f"TRUE confidence={result.confidence:.2f}"
    return result.status.value.upper()


def _format_explanation(result: Answer) -> str:
    if not result.explanation:
        return "observed directly"
    return " -> ".join(
        f"{step.rule_id}(premises={','.join(step.premises)} conclusion={step.conclusion})"
        for step in result.explanation
    )


from __future__ import annotations

import ast
import inspect
from tempfile import TemporaryDirectory
from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import pytest

from nowmind.core.cycle import CognitiveCycleRunner, run_cognitive_cycle
from nowmind.core.now_state import NowState
from nowmind.evaluation.recorder import ExperimentRecorder
from nowmind.geometry.builder import PresentGeometryBuilder
from nowmind.geometry.relation import RelationType
from nowmind.perception.adapter import PerceptionAdapter
from nowmind.reasoning.query import Query, TruthStatus
from nowmind.reasoning.reasoner import answer
from nowmind.world.events import AddEntity, MoveRelation
from nowmind.world.model import WorldState


def _simple_world() -> WorldState:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube"))
    world.apply(AddEntity("blue_cube", "cube"))
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
    return world


def test_fresh_now_ids_are_created_for_consecutive_cycles() -> None:
    runner = CognitiveCycleRunner()
    world = _simple_world()

    first = runner.run(world)
    second = runner.run(world)

    assert first.now_id != second.now_id
    assert first.cycle_id != second.cycle_id


def test_now_state_is_immutable() -> None:
    now = CognitiveCycleRunner().run(_simple_world())

    with pytest.raises(FrozenInstanceError):
        now.cycle_id = 99  # type: ignore[misc]


def test_now_state_has_no_previous_or_history_fields() -> None:
    forbidden = {
        "previous_now",
        "history",
        "histories",
        "memory",
        "memories",
        "conversation",
        "future_states",
        "identity_history",
    }

    assert forbidden.isdisjoint({field.name for field in fields(NowState)})


def test_cycle_runner_does_not_store_now_states() -> None:
    runner = CognitiveCycleRunner()
    world = _simple_world()
    first = runner.run(world)
    second = runner.run(world)

    assert first.now_id != second.now_id
    for field in fields(runner):
        value = getattr(runner, field.name)
        assert not isinstance(value, NowState)
        assert not (
            isinstance(value, (list, tuple))
            and any(isinstance(item, NowState) for item in value)
        )


def test_reasoning_and_building_api_have_no_history_argument() -> None:
    assert list(inspect.signature(answer).parameters) == ["now", "query"]
    assert list(inspect.signature(run_cognitive_cycle).parameters) == ["world", "cycle_id"]
    assert list(inspect.signature(PresentGeometryBuilder.build).parameters) == [
        "self",
        "observation",
    ]
    assert list(inspect.signature(PerceptionAdapter.observe).parameters) == [
        "self",
        "world",
        "cycle_id",
    ]


def test_runtime_modules_do_not_import_evaluation_history() -> None:
    root = Path(__file__).parents[2] / "nowmind"
    runtime_dirs = ["world", "perception", "geometry", "core", "reasoning"]

    for dirname in runtime_dirs:
        for path in (root / dirname).glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    assert node.module is None or not node.module.startswith("nowmind.evaluation")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not alias.name.startswith("nowmind.evaluation")


def test_world_change_rebuilds_geometry_without_stale_relation() -> None:
    runner = CognitiveCycleRunner()
    world = _simple_world()

    cycle_one = runner.run(world)
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
    cycle_two = runner.run(world)

    assert cycle_one.geometry.find_relation(
        "red_cube",
        "blue_cube",
        RelationType.LEFT_OF,
    )
    assert cycle_two.geometry.find_relation(
        "red_cube",
        "blue_cube",
        RelationType.RIGHT_OF,
    )
    assert cycle_two.geometry.find_relation(
        "red_cube",
        "blue_cube",
        RelationType.LEFT_OF,
    ) is None


def test_recorder_external_and_history_deletion_equivalence() -> None:
    world = _simple_world()
    now = CognitiveCycleRunner().run(world)
    query = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    before = answer(now, query)

    temp_root = Path(__file__).parents[2] / "tmp" / "pytest"
    temp_root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=temp_root) as temp_dir:
        log_path = Path(temp_dir) / "history.jsonl"
        recorder = ExperimentRecorder(log_path)
        recorder.record(now, query, before)
        assert recorder.history
        assert log_path.exists()

        recorder.delete_logs()
        after = answer(now, query)

        assert not recorder.history
        assert before.status is TruthStatus.TRUE
        assert after.status is before.status
        assert after.confidence == before.confidence

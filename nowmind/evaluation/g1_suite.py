from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nowmind.core.cycle import CognitiveCycleRunner, run_cognitive_cycle
from nowmind.core.now_state import NowState
from nowmind.evaluation.recorder import ExperimentRecorder
from nowmind.evaluation.serialization import (
    query_display,
    serialize_answer,
    serialize_cycle,
    serialize_query,
)
from nowmind.geometry.builder import PresentGeometryBuilder
from nowmind.geometry.relation import Provenance, RelationType
from nowmind.perception.adapter import PerceptionAdapter
from nowmind.reasoning.query import Query, TruthStatus
from nowmind.reasoning.reasoner import answer
from nowmind.world.events import AddEntity, MoveRelation, SetRelation
from nowmind.world.model import WorldState


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "g1"


@dataclass(frozen=True, slots=True)
class SuiteResult:
    artifacts_dir: Path
    demo_results: dict[str, Any]
    invariant_results: dict[str, Any]
    stale_state_experiment: dict[str, Any]
    metrics: dict[str, Any]
    pytest_returncode: int | None

    @property
    def passed(self) -> bool:
        return (
            self.invariant_results["summary"]["failed"] == 0
            and self.metrics["stale_state_contamination_count"] == 0
            and self.metrics["unknown_guess_count"] == 0
            and self.pytest_returncode in (None, 0)
        )


def run_suite(
    artifacts_dir: Path = DEFAULT_ARTIFACT_DIR,
    run_pytest: bool = False,
) -> SuiteResult:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    pytest_returncode = _write_pytest_results(artifacts_dir, run_pytest)
    demo_results = build_demo_results()
    invariant_results = build_invariant_results()
    stale_state = build_stale_state_experiment()
    metrics = compute_metrics(demo_results, stale_state)

    _write_json(artifacts_dir / "g1_demo_results.json", demo_results)
    _write_json(artifacts_dir / "g1_invariant_results.json", invariant_results)
    _write_json(artifacts_dir / "g1_stale_state_experiment.json", stale_state)
    _write_json(artifacts_dir / "g1_metrics.json", metrics)

    return SuiteResult(
        artifacts_dir=artifacts_dir,
        demo_results=demo_results,
        invariant_results=invariant_results,
        stale_state_experiment=stale_state,
        metrics=metrics,
        pytest_returncode=pytest_returncode,
    )


def build_demo_results() -> dict[str, Any]:
    scenarios = [
        _fresh_now_scenario(),
        _transitive_scenario(),
        _containment_scenario(),
        _contradiction_scenario(),
        _history_firewall_scenario(),
    ]
    return {
        "schema": "nowmind.g1.demo_results.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "scenarios": scenarios,
    }


def build_stale_state_experiment() -> dict[str, Any]:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
    runner = CognitiveCycleRunner()

    cycle_one = runner.run(world)
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
    cycle_two = runner.run(world)

    stale_relation = cycle_two.geometry.find_relation(
        "red_cube",
        "blue_cube",
        RelationType.LEFT_OF,
    )
    current_relation = cycle_two.geometry.find_relation(
        "red_cube",
        "blue_cube",
        RelationType.RIGHT_OF,
    )

    return {
        "schema": "nowmind.g1.stale_state_experiment.v1",
        "cycle_1_relation": "red_cube LEFT_OF blue_cube",
        "world_event": "move red_cube to RIGHT_OF blue_cube",
        "cycle_2_relation": "red_cube RIGHT_OF blue_cube",
        "cycle_1": serialize_cycle(
            cycle_one,
            Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF),
            answer(cycle_one, Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)),
        ),
        "cycle_2": serialize_cycle(
            cycle_two,
            Query.relation("red_cube", "blue_cube", RelationType.RIGHT_OF),
            answer(cycle_two, Query.relation("red_cube", "blue_cube", RelationType.RIGHT_OF)),
        ),
        "stale_state_contamination": stale_relation is not None,
        "current_relation_present": current_relation is not None,
        "fresh_now_ids": str(cycle_one.now_id) != str(cycle_two.now_id),
    }


def build_invariant_results() -> dict[str, Any]:
    checks = [
        _check_now_state_immutable(),
        _check_now_state_has_no_history_fields(),
        _check_new_now_id_each_cycle(),
        _check_world_distinct_from_now(),
        _check_perception_reads_world(),
        _check_geometry_rebuilt_from_observation(),
        _check_no_stale_relation(),
        _check_reasoner_signature(),
        _check_runtime_import_firewall(),
        _check_recorder_external(),
        _check_provenance_distinct(),
        _check_g2_features_absent(),
    ]
    failed = sum(1 for check in checks if check["status"] != "PASS")
    return {
        "schema": "nowmind.g1.invariant_results.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
    }


def compute_metrics(
    demo_results: dict[str, Any],
    stale_state_experiment: dict[str, Any],
) -> dict[str, Any]:
    scenarios = demo_results["scenarios"]
    expected_queries = []
    inference_expectations = []
    contradiction_expectations = []
    unknown_guess_count = 0

    for scenario in scenarios:
        expected_queries.extend(scenario.get("expected_queries", []))
        inference_expectations.extend(scenario.get("expected_inferences", []))
        contradiction_expectations.extend(scenario.get("expected_contradictions", []))

    correct_queries = sum(1 for query in expected_queries if query["passed"])
    correct_inferences = sum(1 for item in inference_expectations if item["passed"])
    detected_contradictions = sum(1 for item in contradiction_expectations if item["passed"])
    for query in expected_queries:
        if query["expected_status"] in {"unknown", "contradictory"} and query[
            "actual_status"
        ] in {"true", "false"}:
            unknown_guess_count += 1

    stale_count = 1 if stale_state_experiment["stale_state_contamination"] else 0
    return {
        "schema": "nowmind.g1.metrics.v1",
        "scenario_count": len(scenarios),
        "query_accuracy": _rate(correct_queries, len(expected_queries)),
        "inference_accuracy": _rate(correct_inferences, len(inference_expectations)),
        "contradiction_detection_rate": _rate(
            detected_contradictions,
            len(contradiction_expectations),
        ),
        "stale_state_contamination_count": stale_count,
        "stale_state_contamination_rate": _rate(stale_count, 1),
        "unknown_guess_count": unknown_guess_count,
        "definitions": {
            "scenario_count": "Number of canonical G1.1 scenarios executed.",
            "query_accuracy": "Expected query statuses matched divided by expected query count.",
            "inference_accuracy": "Expected inference-rule/evidence checks passed divided by inference expectation count.",
            "contradiction_detection_rate": "Contradiction scenarios returning structured contradiction divided by contradiction expectation count.",
            "stale_state_contamination_count": "Focused stale-state experiment count where a cycle-1-only relation survived in cycle 2.",
            "stale_state_contamination_rate": "stale_state_contamination_count divided by one focused stale-state experiment.",
            "unknown_guess_count": "Expected UNKNOWN/CONTRADICTORY queries that were incorrectly returned as TRUE/FALSE.",
        },
    }


def _fresh_now_scenario() -> dict[str, Any]:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
    runner = CognitiveCycleRunner()
    recorder = ExperimentRecorder()

    cycle_one = runner.run(world)
    query_one = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    answer_one = answer(cycle_one, query_one)
    recorder.record(cycle_one, query_one, answer_one)

    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
    cycle_two = runner.run(world)
    query_two = Query.relation("red_cube", "blue_cube", RelationType.RIGHT_OF)
    answer_two = answer(cycle_two, query_two)
    recorder.record(cycle_two, query_two, answer_two)
    stale_query = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    stale_answer = answer(cycle_two, stale_query)

    return {
        "scenario_id": "fresh_now_stale_state",
        "title": "Fresh Now / stale-state test",
        "cycles": [
            serialize_cycle(cycle_one, query_one, answer_one),
            serialize_cycle(cycle_two, query_two, answer_two),
        ],
        "additional_queries": [
            {
                "cycle_id": cycle_two.cycle_id,
                "query": serialize_query(stale_query),
                "answer": serialize_answer(stale_answer),
            }
        ],
        "expected_queries": [
            _expected(query_one, answer_one, TruthStatus.TRUE),
            _expected(query_two, answer_two, TruthStatus.TRUE),
            _expected(stale_query, stale_answer, TruthStatus.UNKNOWN),
        ],
        "expected_inferences": [
            {
                "description": "Cycle 2 infers blue_cube LEFT_OF red_cube",
                "passed": cycle_two.geometry.find_relation(
                    "blue_cube",
                    "red_cube",
                    RelationType.LEFT_OF,
                )
                is not None,
            }
        ],
        "expected_contradictions": [],
        "external_history": [record.to_dict() for record in recorder.history],
    }


def _transitive_scenario() -> dict[str, Any]:
    world = WorldState()
    for entity_id in ("a", "b", "c"):
        world.apply(AddEntity(entity_id, "object", entity_id.upper()))
    world.apply(SetRelation("a", "b", RelationType.LEFT_OF))
    world.apply(SetRelation("b", "c", RelationType.LEFT_OF))
    now = CognitiveCycleRunner().run(world)
    query = Query.explain("a", RelationType.LEFT_OF, "c")
    result = answer(now, query)
    rule_present = any(step.rule_id == "LEFT_TRANSITIVE" for step in result.explanation)
    return {
        "scenario_id": "geometric_inference",
        "title": "Geometric inference",
        "cycles": [serialize_cycle(now, query, result)],
        "expected_queries": [_expected(query, result, TruthStatus.TRUE)],
        "expected_inferences": [
            {"description": "A LEFT_OF C uses LEFT_TRANSITIVE", "passed": rule_present}
        ],
        "expected_contradictions": [],
    }


def _containment_scenario() -> dict[str, Any]:
    world = WorldState()
    for entity_id, kind in (("key", "object"), ("box", "container"), ("cabinet", "container")):
        world.apply(AddEntity(entity_id, kind, entity_id))
    world.apply(SetRelation("key", "box", RelationType.INSIDE))
    world.apply(SetRelation("box", "cabinet", RelationType.INSIDE))
    now = CognitiveCycleRunner().run(world)
    query = Query.explain("key", RelationType.INSIDE, "cabinet")
    result = answer(now, query)
    rule_present = any(step.rule_id == "INSIDE_TRANSITIVE" for step in result.explanation)
    return {
        "scenario_id": "nested_containment",
        "title": "Nested containment",
        "cycles": [serialize_cycle(now, query, result)],
        "expected_queries": [_expected(query, result, TruthStatus.TRUE)],
        "expected_inferences": [
            {
                "description": "key INSIDE cabinet uses INSIDE_TRANSITIVE",
                "passed": rule_present,
            }
        ],
        "expected_contradictions": [],
    }


def _contradiction_scenario() -> dict[str, Any]:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(SetRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
    world.apply(SetRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
    now = CognitiveCycleRunner().run(world)
    query = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    result = answer(now, query)
    contradiction_detected = result.status is TruthStatus.CONTRADICTORY and bool(result.issues)
    return {
        "scenario_id": "current_contradiction",
        "title": "Current contradiction",
        "cycles": [serialize_cycle(now, query, result)],
        "expected_queries": [_expected(query, result, TruthStatus.CONTRADICTORY)],
        "expected_inferences": [],
        "expected_contradictions": [
            {
                "description": "Conflicting current facts produce structured contradiction",
                "passed": contradiction_detected,
            }
        ],
    }


def _history_firewall_scenario() -> dict[str, Any]:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(SetRelation("red_cube", "blue_cube", RelationType.RIGHT_OF))
    now = CognitiveCycleRunner().run(world)
    query = Query.relation("red_cube", "blue_cube", RelationType.RIGHT_OF)
    before = answer(now, query)
    recorder = ExperimentRecorder()
    recorder.record(now, query, before)
    history_before_delete = [record.to_dict() for record in recorder.history]
    recorder.delete_logs()
    after = answer(now, query)
    unchanged = before.status is after.status and before.confidence == after.confidence
    return {
        "scenario_id": "history_firewall",
        "title": "History firewall",
        "cycles": [serialize_cycle(now, query, before)],
        "history_before_delete": history_before_delete,
        "history_after_delete": [record.to_dict() for record in recorder.history],
        "answer_after_history_delete": serialize_answer(after),
        "message": (
            "Current reasoning is unchanged because external experiment history "
            "is not a cognitive input."
        ),
        "expected_queries": [
            _expected(query, before, TruthStatus.TRUE),
            {
                "query": query_display(query),
                "expected_status": "true",
                "actual_status": after.status.value,
                "passed": unchanged,
            },
        ],
        "expected_inferences": [],
        "expected_contradictions": [],
    }


def _expected(query: Query, result, expected_status: TruthStatus) -> dict[str, Any]:
    return {
        "query": query_display(query),
        "expected_status": expected_status.value,
        "actual_status": result.status.value,
        "passed": result.status is expected_status,
    }


def _check_now_state_immutable() -> dict[str, Any]:
    return _pass_fail(
        "NowState is immutable",
        getattr(NowState, "__dataclass_params__").frozen is True,
        "tests/architecture/test_now_firewall.py::test_now_state_is_immutable",
    )


def _check_now_state_has_no_history_fields() -> dict[str, Any]:
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
    field_names = {field.name for field in dataclass_fields(NowState)}
    return _pass_fail(
        "NowState has no previous/history/memory reference",
        forbidden.isdisjoint(field_names),
        "tests/architecture/test_now_firewall.py::test_now_state_has_no_previous_or_history_fields",
    )


def _check_new_now_id_each_cycle() -> dict[str, Any]:
    world = _audit_world()
    runner = CognitiveCycleRunner()
    first = runner.run(world)
    second = runner.run(world)
    return _pass_fail(
        "Each cycle creates a new now_id",
        first.now_id != second.now_id,
        "tests/architecture/test_now_firewall.py::test_fresh_now_ids_are_created_for_consecutive_cycles",
    )


def _check_world_distinct_from_now() -> dict[str, Any]:
    world = _audit_world()
    now = CognitiveCycleRunner().run(world)
    return _pass_fail(
        "WorldState is distinct from NowState",
        isinstance(world, WorldState) and isinstance(now, NowState) and world is not now,
        "docs/GEOMETRIC_NOW_G1_SPEC.md section 4",
    )


def _check_perception_reads_world() -> dict[str, Any]:
    world = _audit_world()
    observation = PerceptionAdapter().observe(world, 1)
    return _pass_fail(
        "Perception reads current world state",
        observation.world_version == world.world_version
        and len(observation.observed_relations) == len(world.relations),
        "tests/architecture/test_reasoning_and_building_api_have_no_history_argument",
    )


def _check_geometry_rebuilt_from_observation() -> dict[str, Any]:
    world = _audit_world()
    observation = PerceptionAdapter().observe(world, 1)
    geometry = PresentGeometryBuilder().build(observation)
    return _pass_fail(
        "Present Geometry is rebuilt from current observation",
        geometry.world_version == observation.world_version
        and geometry.cycle_id == observation.cycle_id,
        "tests/architecture/test_world_change_rebuilds_geometry_without_stale_relation",
    )


def _check_no_stale_relation() -> dict[str, Any]:
    experiment = build_stale_state_experiment()
    return _pass_fail(
        "No stale relation survives by previous-cycle carryover",
        experiment["stale_state_contamination"] is False,
        "tests/scenarios/test_g1_scenarios.py::test_move_object_scenario_has_no_stale_state",
    )


def _check_reasoner_signature() -> dict[str, Any]:
    import inspect

    return _pass_fail(
        "Reasoner receives only current NowState plus query",
        list(inspect.signature(answer).parameters) == ["now", "query"],
        "tests/architecture/test_reasoning_and_building_api_have_no_history_argument",
    )


def _check_runtime_import_firewall() -> dict[str, Any]:
    runtime_dirs = ["world", "perception", "geometry", "core", "reasoning"]
    root = PROJECT_ROOT / "nowmind"
    violations: list[str] = []
    for dirname in runtime_dirs:
        for path in (root / dirname).glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and (
                    node.module or ""
                ).startswith("nowmind.evaluation"):
                    violations.append(str(path.relative_to(PROJECT_ROOT)))
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("nowmind.evaluation"):
                            violations.append(str(path.relative_to(PROJECT_ROOT)))
    return _pass_fail(
        "Runtime cognitive packages do not import evaluation history",
        not violations,
        "tests/architecture/test_runtime_modules_do_not_import_evaluation_history",
        {"violations": violations},
    )


def _check_recorder_external() -> dict[str, Any]:
    world = _audit_world()
    now = CognitiveCycleRunner().run(world)
    query = Query.relation("red_cube", "blue_cube", RelationType.LEFT_OF)
    result = answer(now, query)
    recorder = ExperimentRecorder()
    recorder.record(now, query, result)
    before = result.status
    recorder.delete_logs()
    after = answer(now, query)
    return _pass_fail(
        "ExperimentRecorder remains external to cognition",
        before is after.status and not recorder.history,
        "tests/architecture/test_recorder_external_and_history_deletion_equivalence",
    )


def _check_provenance_distinct() -> dict[str, Any]:
    now = CognitiveCycleRunner().run(_audit_world())
    provenances = {relation.provenance for relation in now.geometry.relations}
    return _pass_fail(
        "Observed and inferred relations retain distinct provenance",
        Provenance.OBSERVED_NOW in provenances and Provenance.INFERRED_NOW in provenances,
        "tests/unit/test_geometry_relations.py::test_inverse_left_right_is_inferred",
    )


def _check_g2_features_absent() -> dict[str, Any]:
    forbidden_paths = [
        PROJECT_ROOT / "nowmind" / name
        for name in ("memory", "retrieval", "prediction", "identity", "veto", "llm")
    ]
    dependency_text = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    forbidden_dependencies = {"openai", "google-genai", "langchain", "chromadb"}
    return _pass_fail(
        "Predictions, memories, identities, Veto Gate, and LLM state are absent",
        not any(path.exists() for path in forbidden_paths)
        and forbidden_dependencies.isdisjoint(dependency_text.split()),
        "SECOND_CODEX_TASK_G1_1.md section 13",
    )


def _audit_world() -> WorldState:
    world = WorldState()
    world.apply(AddEntity("red_cube", "cube", "red cube"))
    world.apply(AddEntity("blue_cube", "cube", "blue cube"))
    world.apply(MoveRelation("red_cube", "blue_cube", RelationType.LEFT_OF))
    return world


def _pass_fail(
    name: str,
    passed: bool,
    evidence: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "evidence": evidence,
        "details": details or {},
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_pytest_results(artifacts_dir: Path, run_pytest: bool) -> int | None:
    command = [sys.executable, "-m", "pytest"]
    path = artifacts_dir / "g1_test_results.txt"
    if not run_pytest:
        path.write_text(
            "Command: python -m pytest\n"
            "Result: not run in this programmatic invocation.\n",
            encoding="utf-8",
        )
        return None

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    path.write_text(
        "\n".join(
            [
                f"Command: {sys.executable} -m pytest",
                f"Return code: {completed.returncode}",
                "",
                "STDOUT:",
                completed.stdout,
                "",
                "STDERR:",
                completed.stderr,
            ]
        ),
        encoding="utf-8",
    )
    return completed.returncode


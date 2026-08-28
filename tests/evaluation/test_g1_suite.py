from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from nowmind.evaluation.g1_suite import (
    PROJECT_ROOT,
    build_stale_state_experiment,
    run_suite,
)


def _project_temp_dir() -> TemporaryDirectory:
    temp_root = PROJECT_ROOT / "tmp" / "pytest"
    temp_root.mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(dir=temp_root)


def test_experiment_runner_derives_metrics_correctly() -> None:
    with _project_temp_dir() as temp_dir:
        result = run_suite(Path(temp_dir), run_pytest=False)

        assert result.passed
        assert result.metrics["scenario_count"] == 5
        assert result.metrics["query_accuracy"] == 1.0
        assert result.metrics["inference_accuracy"] == 1.0
        assert result.metrics["contradiction_detection_rate"] == 1.0
        assert result.metrics["stale_state_contamination_count"] == 0
        assert result.metrics["stale_state_contamination_rate"] == 0.0
        assert result.metrics["unknown_guess_count"] == 0


def test_stale_state_experiment_uses_two_fresh_nows() -> None:
    experiment = build_stale_state_experiment()

    assert experiment["fresh_now_ids"] is True
    assert experiment["cycle_1"]["now_id"] != experiment["cycle_2"]["now_id"]
    assert experiment["stale_state_contamination"] is False
    assert experiment["current_relation_present"] is True


def test_evidence_json_has_stable_documented_structure() -> None:
    with _project_temp_dir() as temp_dir:
        result = run_suite(Path(temp_dir), run_pytest=False)
        artifact_dir = result.artifacts_dir

        expected_files = {
            "g1_test_results.txt",
            "g1_demo_results.json",
            "g1_invariant_results.json",
            "g1_stale_state_experiment.json",
            "g1_metrics.json",
        }
        assert expected_files.issubset({path.name for path in artifact_dir.iterdir()})

        demo = json.loads((artifact_dir / "g1_demo_results.json").read_text(encoding="utf-8"))
        invariants = json.loads(
            (artifact_dir / "g1_invariant_results.json").read_text(encoding="utf-8")
        )
        stale = json.loads(
            (artifact_dir / "g1_stale_state_experiment.json").read_text(encoding="utf-8")
        )

        assert demo["schema"] == "nowmind.g1.demo_results.v1"
        assert len(demo["scenarios"]) == 5
        for scenario in demo["scenarios"]:
            assert {"scenario_id", "title", "cycles", "expected_queries"}.issubset(
                scenario
            )
            for cycle in scenario["cycles"]:
                assert {
                    "cycle_id",
                    "now_id",
                    "observed_relations",
                    "inferred_relations",
                    "query",
                    "answer",
                    "validation",
                }.issubset(cycle)

        assert invariants["schema"] == "nowmind.g1.invariant_results.v1"
        assert invariants["summary"]["failed"] == 0
        assert stale["schema"] == "nowmind.g1.stale_state_experiment.v1"
        assert stale["stale_state_contamination"] is False


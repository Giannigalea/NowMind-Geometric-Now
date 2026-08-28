from __future__ import annotations

import json

from nowmind.evaluation.g2_benchmark import (
    DEFAULT_SEED,
    DEFAULT_TRIAL_COUNT,
    generate_trials,
    run_benchmark,
)


def test_g2_benchmark_generation_is_reproducible() -> None:
    first = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 54)]
    second = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 54)]

    assert first == second


def test_g2_default_benchmark_has_minimum_trials_and_all_families(tmp_path) -> None:
    result = run_benchmark(artifacts_dir=tmp_path, seed=DEFAULT_SEED, trial_count=DEFAULT_TRIAL_COUNT)

    assert result.passed
    assert result.trial_count >= 1000
    assert result.invariant_results["summary"]["failed"] == 0
    assert set(result.metrics) == {
        "NowMindTemporalGeometry",
        "NaivePersistentState",
        "ChronologicalRecordReasoner",
    }
    config = json.loads((tmp_path / "g2_seed_and_config.json").read_text(encoding="utf-8"))
    assert config["trial_count"] == DEFAULT_TRIAL_COUNT
    assert len(config["families"]) == 18
    assert all(
        key in result.metrics["NowMindTemporalGeometry"]
        for key in (
            "current_state_accuracy",
            "past_state_accuracy",
            "future_query_accuracy",
            "temporal_source_classification_accuracy",
            "overall_query_accuracy",
            "stale_memory_as_current_count",
            "false_memory_contamination_count",
            "prediction_as_fact_count",
        )
    )
    assert result.failures["NaivePersistentState"]
    assert (tmp_path / "g2_trial_results.jsonl").exists()
    assert (tmp_path / "g2_baseline_rules.md").exists()


def test_g2_benchmark_invariant_failure_is_reported(tmp_path) -> None:
    result = run_benchmark(artifacts_dir=tmp_path, seed=DEFAULT_SEED, trial_count=18)

    assert not result.passed
    assert result.invariant_results["summary"]["failed"] >= 1

from __future__ import annotations

import json

from nowmind.evaluation.g2_1_benchmark import (
    DEFAULT_SEED,
    DEFAULT_TRIAL_COUNT,
    FAMILIES,
    SYSTEM_IDS,
    generate_trials,
    run_benchmark,
)


def test_g2_1_benchmark_generation_is_reproducible() -> None:
    first = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 80)]
    second = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 80)]

    assert first == second
    assert {trial.difficulty for trial in generate_trials(DEFAULT_SEED, 80)} == {
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
    }
    assert {trial.family for trial in generate_trials(DEFAULT_SEED, 80)} == set(FAMILIES)


def test_g2_1_default_benchmark_configuration_meets_minimum() -> None:
    assert DEFAULT_TRIAL_COUNT >= 2000


def test_g2_1_benchmark_writes_required_artifacts_and_derived_metrics(tmp_path) -> None:
    result = run_benchmark(artifacts_dir=tmp_path, seed=DEFAULT_SEED, trial_count=80)

    assert not result.passed
    assert result.invariant_results["summary"]["failed"] == 1
    assert set(result.metrics) == set(SYSTEM_IDS)
    assert all(
        key in result.metrics["N_NowMindPossibilityGeometry"]
        for key in (
            "planning_success_rate",
            "goal_reached_rate",
            "valid_plan_rate",
            "invalid_action_rate",
            "collision_count",
            "collision_rate",
            "path_efficiency",
            "optimality_gap_vs_oracle",
            "mean_replans",
            "replan_success_rate",
            "dynamic_change_recovery_rate",
            "stale_memory_planning_error_count",
            "false_memory_planning_error_count",
            "prediction_as_fact_planning_error_count",
            "unsupported_assumption_count",
            "conditional_plan_rate",
            "assumption_validation_success_rate",
            "hypothesis_confirmation_violations",
            "observation_after_action_rate",
            "mean_planning_time_ms",
        )
    )
    config = json.loads((tmp_path / "g2_1_seed_and_config.json").read_text(encoding="utf-8"))
    assert config["trial_count"] == 80
    assert config["minimum_trial_count"] == 2000
    assert len(config["families"]) == 16
    assert (tmp_path / "g2_1_trial_results.jsonl").exists()
    assert (tmp_path / "g2_1_failure_samples.json").exists()
    assert (tmp_path / "g2_1_baseline_rules.md").exists()
    assert (tmp_path / "g2_1_oracle_gap.json").exists()

    first_line = (tmp_path / "g2_1_trial_results.jsonl").read_text(encoding="utf-8").splitlines()[0]
    first_trial = json.loads(first_line)
    assert "plans" not in first_trial["systems"]["N_NowMindPossibilityGeometry"]
    assert first_trial["systems"]["N_NowMindPossibilityGeometry"]["plan_attempts"] >= 0

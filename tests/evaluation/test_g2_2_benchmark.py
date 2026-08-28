from __future__ import annotations

import json

from nowmind.evaluation.g2_2_benchmark import (
    DEFAULT_SEED,
    DEFAULT_TRIAL_COUNT,
    FAMILIES,
    HISTORY_COHORTS,
    MINIMUM_TRIAL_COUNT,
    SYSTEM_IDS,
    generate_trials,
    run_benchmark,
)


def test_g2_2_default_benchmark_configuration_meets_minimum() -> None:
    assert DEFAULT_TRIAL_COUNT >= MINIMUM_TRIAL_COUNT
    assert MINIMUM_TRIAL_COUNT >= 3000


def test_g2_2_benchmark_generation_is_reproducible_and_covers_required_axes() -> None:
    first = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 144)]
    second = [trial.to_public_dict() for trial in generate_trials(DEFAULT_SEED, 144)]
    trials = generate_trials(DEFAULT_SEED, 144)

    assert first == second
    assert {trial.family for trial in trials} == set(FAMILIES)
    assert {trial.difficulty for trial in trials} == {"D1", "D2", "D3", "D4", "D5", "D6"}
    assert {trial.history_cohort for trial in trials} == {f"H{count}" for count in HISTORY_COHORTS}


def test_g2_2_benchmark_writes_required_artifacts_and_derived_metrics(tmp_path) -> None:
    result = run_benchmark(artifacts_dir=tmp_path, seed=DEFAULT_SEED, trial_count=24)

    assert not result.passed
    assert result.invariant_results["summary"]["failed"] == 1
    assert set(result.metrics) == set(SYSTEM_IDS)
    assert all(
        key in result.metrics["N_NowMindEpistemicGeometry"]
        for key in (
            "goal_reached_rate",
            "goal_reached_ci95_low",
            "goal_reached_ci95_high",
            "planning_success_rate",
            "collision_rate",
            "invalid_action_rate",
            "path_efficiency",
            "optimality_gap_vs_oracle",
            "verification_action_rate",
            "useful_verification_rate",
            "wasted_verification_rate",
            "verification_prevented_failure_count",
            "unknown_correctly_preserved_rate",
            "unsupported_certainty_rate",
            "memory_use_rate",
            "memory_helped_success_count",
            "memory_harmed_success_count",
            "stale_memory_planning_error_rate",
            "false_memory_planning_error_rate",
            "memory_as_observation_violation_count",
            "prediction_as_fact_violation_count",
            "hidden_change_recovery_rate",
            "target_reacquisition_rate",
            "exploration_success_rate",
            "mean_history_records_available",
            "mean_evidence_items_inspected",
            "mean_memory_traces_retrieved",
            "mean_planning_time_ms",
            "p95_planning_time_ms",
        )
    )

    config = json.loads((tmp_path / "g2_2_seed_and_config.json").read_text(encoding="utf-8"))
    assert config["seed"] == DEFAULT_SEED
    assert config["trial_count"] == 24
    assert config["minimum_trial_count"] == MINIMUM_TRIAL_COUNT
    assert config["families"] == list(FAMILIES)
    assert config["history_cohorts"] == [f"H{count}" for count in HISTORY_COHORTS]

    first_line = (tmp_path / "g2_2_trial_results.jsonl").read_text(encoding="utf-8").splitlines()[0]
    first_trial = json.loads(first_line)
    assert set(first_trial["systems"]) == set(SYSTEM_IDS)
    assert "plans" not in first_trial["systems"]["N_NowMindEpistemicGeometry"]
    assert first_trial["systems"]["N_NowMindEpistemicGeometry"]["plan_attempts"] >= 0

    for filename in (
        "g2_2_metrics.json",
        "g2_2_metrics_by_family.json",
        "g2_2_metrics_by_difficulty.json",
        "g2_2_history_scaling.json",
        "g2_2_trial_results.jsonl",
        "g2_2_failure_samples.json",
        "g2_2_invariant_results.json",
        "g2_2_seed_and_config.json",
        "g2_2_baseline_rules.md",
        "g2_2_benchmark_summary.md",
        "g2_2_pairwise_comparison.json",
    ):
        assert (tmp_path / filename).exists()

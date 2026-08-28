from __future__ import annotations

import json

from nowmind.evaluation.g2_3_benchmark import (
    DEFAULT_SEED,
    CONDITIONS,
    FAMILIES,
    REGIMES,
    generate_trials,
    run_g2_3_benchmark,
)


def test_g2_3_trial_generation_is_paired_and_reproducible() -> None:
    first = [trial.public_dict() for trial in generate_trials(DEFAULT_SEED, 34, "test", "a")]
    second = [trial.public_dict() for trial in generate_trials(DEFAULT_SEED, 34, "test", "a")]

    assert first == second
    assert {trial["family"] for trial in first} == set(FAMILIES)


def test_g2_3_benchmark_writes_required_artifacts(tmp_path) -> None:
    result = run_g2_3_benchmark(tmp_path, calibration_count=6, final_count=18)

    required = {
        "g2_3_model_manifest.json",
        "g2_3_prompt_templates.md",
        "g2_3_calibration_results.json",
        "g2_3_metrics.json",
        "g2_3_metrics_by_family.json",
        "g2_3_metrics_by_history.json",
        "g2_3_pairwise_n_vs_c.json",
        "g2_3_proposal_vs_validated.json",
        "g2_3_trial_results.jsonl",
        "g2_3_failure_samples.json",
        "g2_3_prompt_fairness_results.json",
        "g2_3_seed_and_config.json",
        "g2_3_summary.md",
    }

    assert result.invariants["summary"]["failed"] == 0
    assert required.issubset({path.name for path in tmp_path.iterdir()})

    config = json.loads((tmp_path / "g2_3_seed_and_config.json").read_text(encoding="utf-8"))
    assert set(config["conditions"]) == set(CONDITIONS)
    assert set(config["regimes"]) == set(REGIMES)

    fairness = json.loads((tmp_path / "g2_3_prompt_fairness_results.json").read_text(encoding="utf-8"))
    assert fairness["summary"]["failed"] == 0

    pairwise = json.loads((tmp_path / "g2_3_pairwise_n_vs_c.json").read_text(encoding="utf-8"))
    assert pairwise

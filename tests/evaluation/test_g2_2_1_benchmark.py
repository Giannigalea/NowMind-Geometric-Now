from __future__ import annotations

import json

from nowmind.evaluation import g2_2_1_benchmark
from nowmind.evaluation.g2_2_1_benchmark import (
    G2_2_1_HOLDOUT_SEED,
    G2_2_1_HOLDOUT_TRIAL_COUNT,
    generate_holdout_trials,
    run_g2_2_1_benchmark,
)
from nowmind.evaluation.g2_2_benchmark import DEFAULT_SEED, generate_trials


def test_g2_2_1_holdout_seed_and_trial_ids_differ_from_v1() -> None:
    v1 = generate_trials(DEFAULT_SEED, 48)
    holdout = generate_holdout_trials(G2_2_1_HOLDOUT_SEED, 48)

    assert G2_2_1_HOLDOUT_SEED != DEFAULT_SEED
    assert G2_2_1_HOLDOUT_TRIAL_COUNT >= 2000
    assert {trial.trial_id for trial in v1}.isdisjoint({trial.trial_id for trial in holdout})
    assert all(trial.trial_id.startswith("g2_2_1_holdout_") for trial in holdout)


def test_g2_2_1_benchmark_writes_required_artifacts(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(g2_2_1_benchmark, "G2_2_V1_TRIAL_COUNT", 24)
    monkeypatch.setattr(g2_2_1_benchmark, "G2_2_1_HOLDOUT_TRIAL_COUNT", 24)

    result = run_g2_2_1_benchmark(tmp_path, holdout_trial_count=24)

    assert result["v1"].trial_count == 24
    assert result["holdout"].trial_count == 24
    assert result["invariants"]["summary"]["failed"] == 0

    for filename in (
        "g2_2_1_metrics_v1_regression.json",
        "g2_2_1_metrics_holdout.json",
        "g2_2_1_history_scaling.json",
        "g2_2_1_retrieval_metrics.json",
        "g2_2_1_recovery_metrics.json",
        "g2_2_1_verification_metrics.json",
        "g2_2_1_pairwise_comparison.json",
        "g2_2_1_failure_samples.json",
        "g2_2_1_invariant_results.json",
        "g2_2_1_holdout_seed_and_config.json",
        "g2_2_1_summary.md",
    ):
        assert (tmp_path / filename).exists()

    config = json.loads((tmp_path / "g2_2_1_holdout_seed_and_config.json").read_text(encoding="utf-8"))
    assert config["seed"] != DEFAULT_SEED
    assert config["trial_count"] == 24

    retrieval = json.loads((tmp_path / "g2_2_1_retrieval_metrics.json").read_text(encoding="utf-8"))
    assert "records_scanned" in retrieval["definitions"]
    assert "mean_records_scanned" in retrieval["holdout"]["N_NowMindEpistemicGeometry"]

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from typing import Any

from nowmind.evaluation.g2_2_benchmark import (
    DEFAULT_SEED as G2_2_V1_SEED,
    DEFAULT_TRIAL_COUNT as G2_2_V1_TRIAL_COUNT,
    FAMILIES,
    HISTORY_COHORTS,
    SYSTEM_IDS,
    BenchmarkResult,
    generate_trials,
    run_benchmark,
)


G2_2_1_HOLDOUT_SEED = 202608231
G2_2_1_HOLDOUT_TRIAL_COUNT = 2000
DEFAULT_ARTIFACT_DIR = Path("artifacts") / "g2_2_1"


def generate_holdout_trials(
    seed: int = G2_2_1_HOLDOUT_SEED,
    trial_count: int = G2_2_1_HOLDOUT_TRIAL_COUNT,
):
    return tuple(
        replace(
            trial,
            trial_id=f"g2_2_1_holdout_{index:05d}_{trial.family}",
        )
        for index, trial in enumerate(generate_trials(seed, trial_count))
    )


def run_g2_2_1_benchmark(
    artifacts_dir: Path = DEFAULT_ARTIFACT_DIR,
    holdout_seed: int = G2_2_1_HOLDOUT_SEED,
    holdout_trial_count: int = G2_2_1_HOLDOUT_TRIAL_COUNT,
) -> dict[str, Any]:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    holdout_trials = generate_holdout_trials(holdout_seed, holdout_trial_count)
    _write_json(
        artifacts_dir / "g2_2_1_holdout_seed_and_config.json",
        {
            "seed": holdout_seed,
            "trial_count": holdout_trial_count,
            "v1_seed": G2_2_V1_SEED,
            "v1_trial_count": G2_2_V1_TRIAL_COUNT,
            "families": list(FAMILIES),
            "history_cohorts": [f"H{count}" for count in HISTORY_COHORTS],
            "trial_id_prefix": "g2_2_1_holdout_",
            "note": "Config written before holdout evaluation; runtime code must not inspect seed, trial id, family, or expected answer.",
        },
    )

    v1_result = run_benchmark(
        artifacts_dir=artifacts_dir / "v1_regression_raw",
        seed=G2_2_V1_SEED,
        trial_count=G2_2_V1_TRIAL_COUNT,
    )
    holdout_result = run_benchmark(
        artifacts_dir=artifacts_dir / "holdout_raw",
        seed=holdout_seed,
        trial_count=holdout_trial_count,
        trials=holdout_trials,
    )
    invariants = _invariant_results(v1_result, holdout_result)
    retrieval_metrics = _retrieval_metrics(v1_result, holdout_result)
    recovery_metrics = _recovery_metrics(v1_result, holdout_result)
    verification_metrics = _verification_metrics(v1_result, holdout_result)

    _write_json(artifacts_dir / "g2_2_1_metrics_v1_regression.json", v1_result.metrics)
    _write_json(artifacts_dir / "g2_2_1_metrics_holdout.json", holdout_result.metrics)
    _write_json(artifacts_dir / "g2_2_1_history_scaling.json", holdout_result.history_scaling)
    _write_json(artifacts_dir / "g2_2_1_retrieval_metrics.json", retrieval_metrics)
    _write_json(artifacts_dir / "g2_2_1_recovery_metrics.json", recovery_metrics)
    _write_json(artifacts_dir / "g2_2_1_verification_metrics.json", verification_metrics)
    _write_json(artifacts_dir / "g2_2_1_pairwise_comparison.json", holdout_result.pairwise_comparison)
    _write_json(artifacts_dir / "g2_2_1_failure_samples.json", holdout_result.failures)
    _write_json(artifacts_dir / "g2_2_1_invariant_results.json", invariants)
    (artifacts_dir / "g2_2_1_summary.md").write_text(
        _summary(v1_result, holdout_result, invariants),
        encoding="utf-8",
    )
    return {
        "v1": v1_result,
        "holdout": holdout_result,
        "invariants": invariants,
    }


def _retrieval_metrics(v1_result: BenchmarkResult, holdout_result: BenchmarkResult) -> dict[str, Any]:
    keys = (
        "mean_records_scanned",
        "mean_index_candidates_considered",
        "mean_records_returned",
        "mean_reconstructions_created",
        "mean_effective_evidence_used",
        "mean_legacy_evidence_items_inspected",
        "mean_evidence_items_inspected",
    )
    return {
        "definitions": {
            "records_scanned": "records examined after index narrowing",
            "index_candidates_considered": "candidate records returned by trace/reconstruction indices",
            "records_returned": "records passed to current reconstruction/planning",
            "reconstructions_created": "current reconstructions supplied to planning",
            "effective_evidence_used": "planning assumptions actually used in the selected plan",
            "legacy_evidence_items_inspected": "pre-G2.2.1 planner-side evidence counter retained for comparison",
        },
        "v1_regression": _select(v1_result.metrics, keys),
        "holdout": _select(holdout_result.metrics, keys),
        "holdout_history_scaling": {
            cohort: _select(systems, keys)
            for cohort, systems in holdout_result.history_scaling.items()
        },
    }


def _recovery_metrics(v1_result: BenchmarkResult, holdout_result: BenchmarkResult) -> dict[str, Any]:
    keys = (
        "hidden_change_recovery_rate",
        "hidden_obstacle_recovery_rate",
        "hidden_target_recovery_rate",
        "target_reacquisition_rate",
        "target_reacquisition_attempts",
        "target_reacquisition_success_rate",
        "mean_cells_explored_for_reacquisition",
        "mean_steps_to_reacquire",
        "mean_disconfirmed_targets",
        "mean_invalidated_poses",
    )
    return {
        "v1_regression": _select(v1_result.metrics, keys),
        "holdout": _select(holdout_result.metrics, keys),
    }


def _verification_metrics(v1_result: BenchmarkResult, holdout_result: BenchmarkResult) -> dict[str, Any]:
    keys = (
        "verification_action_rate",
        "useful_verification_rate",
        "wasted_verification_rate",
        "verification_prevented_likely_failure_count",
        "verification_enabled_shorter_route_count",
        "verification_confirmed_useful_memory_count",
        "verification_wasted_safe_dominated_count",
        "verification_wasted_no_decision_change_count",
    )
    return {
        "v1_regression": _select(v1_result.metrics, keys),
        "holdout": _select(holdout_result.metrics, keys),
    }


def _invariant_results(v1_result: BenchmarkResult, holdout_result: BenchmarkResult) -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    v1_ids = set()
    holdout_ids = set()
    holdout_families = set()
    with (v1_result.artifacts_dir / "g2_2_trial_results.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            v1_ids.add(json.loads(line)["trial"]["trial_id"])
    with (holdout_result.artifacts_dir / "g2_2_trial_results.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            trial = json.loads(line)["trial"]
            holdout_ids.add(trial["trial_id"])
            holdout_families.add(trial["family"])

    add("G2.2.1-v1-trial-count", v1_result.trial_count == G2_2_V1_TRIAL_COUNT, str(v1_result.trial_count))
    add("G2.2.1-v1-seed", v1_result.seed == G2_2_V1_SEED, str(v1_result.seed))
    add("G2.2.1-holdout-minimum", holdout_result.trial_count >= G2_2_1_HOLDOUT_TRIAL_COUNT, str(holdout_result.trial_count))
    add("G2.2.1-holdout-seed-differs", holdout_result.seed != G2_2_V1_SEED, str(holdout_result.seed))
    add("G2.2.1-non-overlapping-trial-ids", not (v1_ids & holdout_ids), str(len(v1_ids & holdout_ids)))
    add("G2.2.1-holdout-trial-ids", len(holdout_ids) == holdout_result.trial_count, str(len(holdout_ids)))
    add("G2.2.1-holdout-families", holdout_families == set(FAMILIES), str(len(holdout_families)))
    add("G2.2.1-systems", set(holdout_result.metrics) == set(SYSTEM_IDS), ",".join(sorted(holdout_result.metrics)))
    add("G2.2.1-memory-not-observation", _source_count(holdout_result, "memory_as_observation_violation_count") == 0, "0 expected")
    add("G2.2.1-prediction-not-fact", _source_count(holdout_result, "prediction_as_fact_violation_count") == 0, "0 expected")
    failed = sum(1 for check in checks if not check["passed"])
    return {"checks": checks, "summary": {"passed": len(checks) - failed, "failed": failed}}


def _source_count(result: BenchmarkResult, key: str) -> float:
    return sum(system_metrics.get(key, 0.0) for system_metrics in result.metrics.values())


def _select(metrics: dict[str, dict[str, float]], keys: tuple[str, ...]) -> dict[str, dict[str, float]]:
    return {
        system: {key: values.get(key, 0.0) for key in keys}
        for system, values in metrics.items()
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _summary(
    v1_result: BenchmarkResult,
    holdout_result: BenchmarkResult,
    invariants: dict[str, Any],
) -> str:
    lines = [
        "# G2.2.1 Epistemic Recovery & Retrieval Summary",
        "",
        f"- v1 seed: `{v1_result.seed}`",
        f"- v1 trial_count: `{v1_result.trial_count}`",
        f"- holdout seed: `{holdout_result.seed}`",
        f"- holdout trial_count: `{holdout_result.trial_count}`",
        f"- invariants: `{invariants['summary']['passed']} passed, {invariants['summary']['failed']} failed`",
        "",
        "## Holdout Aggregate",
    ]
    for system, values in holdout_result.metrics.items():
        lines.append(f"### {system}")
        lines.append(f"- goal_reached_rate: {values['goal_reached_rate']:.3f}")
        lines.append(f"- records_scanned: {values.get('mean_records_scanned', 0.0):.1f}")
        lines.append(f"- hidden_change_recovery_rate: {values.get('hidden_change_recovery_rate', 0.0):.3f}")
        lines.append(f"- target_reacquisition_rate: {values.get('target_reacquisition_rate', 0.0):.3f}")
        lines.append(f"- wasted_verification_rate: {values.get('wasted_verification_rate', 0.0):.3f}")
        lines.append("")
    return "\n".join(lines)

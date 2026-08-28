from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nowmind.evaluation import g2_3_benchmark as bench
from nowmind.modeling import COMMON_SYSTEM_INSTRUCTION
from nowmind.modeling.backend import OllamaBackend
from nowmind.modeling.representation import stable_hash


DEFAULT_MODEL = "qwen3:1.7b"
DEFAULT_OUTPUT_DIR = Path("artifacts") / "g2_3_1" / "qwen3_1_7b"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run G2.3.1 real-model trials with checkpoints.")
    parser.add_argument("phase", choices=("calibration", "evaluation"))
    parser.add_argument("--count", type=int, default=bench.DEFAULT_CALIBRATION_COUNT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--context-size", type=int, default=2048)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    args = parser.parse_args()

    backend = OllamaBackend(
        args.model,
        context_size=args.context_size,
        num_predict=args.num_predict,
        think=False if args.model.lower().startswith("qwen3") else None,
        timeout_seconds=args.timeout_seconds,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.phase == "calibration":
        run_phase(
            args.phase,
            args.output_dir,
            backend,
            bench.generate_trials(bench.DEFAULT_SEED, args.count, "calibration", "g2_3_cal"),
            args.count,
        )
        return 0

    calibration_path = args.output_dir / "calibration_results.json"
    if not calibration_path.exists():
        raise SystemExit(f"Calibration artifact is required before evaluation: {calibration_path}")
    frozen_manifest_path = args.output_dir / "frozen_experiment_manifest.json"
    if not frozen_manifest_path.exists():
        write_frozen_manifest(frozen_manifest_path, backend, args.count, calibration_path)
    run_phase(
        args.phase,
        args.output_dir,
        backend,
        bench.generate_trials(bench.DEFAULT_SEED + 1, args.count, "evaluation", "g2_3_eval"),
        args.count,
    )
    return 0


def run_phase(
    phase: str,
    output_dir: Path,
    backend: OllamaBackend,
    trials: tuple[bench.G23Trial, ...],
    count: int,
) -> None:
    rows_path = output_dir / f"{phase}_trial_results.jsonl"
    completed = completed_trial_ids(rows_path)
    started = perf_counter()
    rows: list[dict[str, Any]] = read_rows(rows_path)
    for index, trial in enumerate(trials, start=1):
        if trial.trial_id in completed:
            print(f"{phase} {index}/{count} trial={trial.trial_id} skipped=already_complete", flush=True)
            continue
        trial_rows = []
        trial_started = perf_counter()
        for regime in bench.REGIMES:
            for condition in bench.CONDITIONS:
                trial_rows.append(bench._run_condition(trial, regime, condition, backend))
        append_rows(rows_path, trial_rows)
        rows.extend(trial_rows)
        completed.add(trial.trial_id)
        elapsed = perf_counter() - started
        trial_elapsed = perf_counter() - trial_started
        errors = sum(1 for row in trial_rows if row.get("error"))
        parses = sum(1 for row in trial_rows if row.get("parse_success"))
        print(
            f"{phase} {index}/{count} trial={trial.trial_id} "
            f"seconds={trial_elapsed:.1f} elapsed={elapsed:.1f} rows={len(rows)} parses={parses}/8 errors={errors}",
            flush=True,
        )
    write_phase_artifacts(phase, output_dir, backend, rows, count, perf_counter() - started)


def completed_trial_ids(rows_path: Path) -> set[str]:
    counts: dict[str, int] = {}
    for row in read_rows(rows_path):
        trial_id = str(row["trial"]["trial_id"])
        counts[trial_id] = counts.get(trial_id, 0) + 1
    return {trial_id for trial_id, row_count in counts.items() if row_count == len(bench.REGIMES) * len(bench.CONDITIONS)}


def read_rows(rows_path: Path) -> list[dict[str, Any]]:
    if not rows_path.exists():
        return []
    rows = []
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_rows(rows_path: Path, rows: list[dict[str, Any]]) -> None:
    with rows_path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()


def write_phase_artifacts(
    phase: str,
    output_dir: Path,
    backend: OllamaBackend,
    rows: list[dict[str, Any]],
    count: int,
    wall_clock_seconds: float,
) -> None:
    model_manifest = sanitized_model_manifest(backend)
    metrics = bench._aggregate(rows)
    metrics_by_family = bench._aggregate_by(rows, "family")
    metrics_by_history = bench._aggregate_by(rows, "history_cohort")
    pairwise = bench._pairwise_n_vs_c(rows)
    proposal_vs_validated = bench._proposal_vs_validated(rows)
    fairness = bench._fairness_results(rows)
    invariants = bench._invariant_results(rows, fairness, model_manifest)
    failures = bench._failure_samples(rows)
    summary = {
        "schema": f"nowmind.g2_3_1.{phase}_results.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "requested_paired_trial_count": count,
        "completed_paired_trial_count": len(completed_trial_ids(output_dir / f"{phase}_trial_results.jsonl")),
        "row_count": len(rows),
        "model_call_count": sum(1 for row in rows if row["backend"] != "symbolic"),
        "wall_clock_seconds_this_invocation": round(wall_clock_seconds, 3),
        "estimated_seconds_per_pair_this_invocation": round(wall_clock_seconds / max(1, count), 3),
        "context_overflow_count": sum(1 for row in rows if row["context_overflow"]),
        "error_count": sum(1 for row in rows if row.get("error")),
        "model_manifest": model_manifest,
        "metrics": metrics,
        "metrics_by_family": metrics_by_family,
        "metrics_by_history": metrics_by_history,
        "pairwise_n_vs_c": pairwise,
        "proposal_vs_validated": proposal_vs_validated,
        "prompt_fairness_results": fairness,
        "invariant_results": invariants,
    }
    bench._write_json(output_dir / f"{phase}_results.json", summary)
    if phase == "calibration":
        bench._write_json(output_dir / "calibration_results.json", summary)
    else:
        bench._write_json(output_dir / "g2_3_model_manifest.json", model_manifest)
        bench._write_json(output_dir / "g2_3_metrics.json", metrics)
        bench._write_json(output_dir / "g2_3_metrics_by_family.json", metrics_by_family)
        bench._write_json(output_dir / "g2_3_metrics_by_history.json", metrics_by_history)
        bench._write_json(output_dir / "g2_3_pairwise_n_vs_c.json", pairwise)
        bench._write_json(output_dir / "g2_3_proposal_vs_validated.json", proposal_vs_validated)
        bench._write_json(output_dir / "g2_3_failure_samples.json", failures)
        bench._write_json(output_dir / "g2_3_prompt_fairness_results.json", fairness)
        bench._write_json(output_dir / "g2_3_invariant_results.json", invariants)
        bench._write_json(
            output_dir / "g2_3_seed_and_config.json",
            seed_and_config(count),
        )
        (output_dir / "g2_3_prompt_templates.md").write_text(
            bench._prompt_templates_markdown(),
            encoding="utf-8",
        )
        (output_dir / "g2_3_summary.md").write_text(
            bench._summary(model_manifest, metrics, pairwise, invariants, count),
            encoding="utf-8",
        )


def write_frozen_manifest(
    path: Path,
    backend: OllamaBackend,
    final_count: int,
    calibration_path: Path,
) -> None:
    manifest = {
        "schema": "nowmind.g2_3_1.frozen_experiment_manifest.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_policy": "Written after calibration and before final evaluation rows for this count.",
        "selected_final_paired_trial_count": final_count,
        "seed": bench.DEFAULT_SEED,
        "evaluation_seed": bench.DEFAULT_SEED + 1,
        "calibration_artifact": str(calibration_path).replace("\\", "/"),
        "benchmark_constants": seed_and_config(final_count),
        "model_manifest": sanitized_model_manifest(backend),
        "prompt_templates_hash": stable_hash(bench._prompt_templates_markdown()),
        "system_instruction_hash": stable_hash(COMMON_SYSTEM_INSTRUCTION),
    }
    bench._write_json(path, manifest)


def seed_and_config(final_count: int) -> dict[str, Any]:
    return {
        "seed": bench.DEFAULT_SEED,
        "calibration_count": bench.DEFAULT_CALIBRATION_COUNT,
        "final_count": final_count,
        "families": list(bench.FAMILIES),
        "history_cohorts": [f"H{count}" for count in bench.HISTORY_COHORTS],
        "regimes": list(bench.REGIMES),
        "conditions": list(bench.CONDITIONS),
        "fixed_token_budget": bench.FIXED_TOKEN_BUDGET,
        "system_instruction_hash": stable_hash(COMMON_SYSTEM_INSTRUCTION),
    }


def sanitized_model_manifest(backend: OllamaBackend) -> dict[str, Any]:
    selected = backend.manifest()
    selected["digest"] = model_digest(selected["model"])
    return {
        "selected": selected,
        "available_backends": {
            "mock": True,
            "ollama": True,
            "symbolic_reference": True,
        },
        "symbolic_reference": bench._symbolic_manifest(),
        "ollama": {
            "executable": "ollama.exe",
            "base_url": selected["base_url"],
            "api_path": selected["api_path"],
            "models": [
                {
                    "name": selected["model"],
                    "digest": selected["digest"],
                }
            ],
            "available": True,
            "note": "Temporary CPU/AVX2 diagnostic server; no cloud backend.",
        },
        "local_model_runtime_prerequisite": None,
    }


def model_digest(model: str) -> str:
    if model == "qwen3:1.7b":
        return "8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7"
    if model == "gemma3:1b":
        return "8648f39daa8f"
    if model == "qwen3:0.6b":
        return "7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435"
    return "recorded-in-local-ollama-model-store"


if __name__ == "__main__":
    raise SystemExit(main())

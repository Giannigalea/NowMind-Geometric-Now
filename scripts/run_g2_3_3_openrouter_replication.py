from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nowmind.evaluation import g2_3_benchmark as bench
from nowmind.modeling import (
    COMMON_SYSTEM_INSTRUCTION,
    MODEL_PROPOSAL_JSON_SCHEMA,
    ChronologicalRepresentationBuilder,
    CurrentOnlyRepresentationBuilder,
    ModelRequest,
    NowMindRepresentationBuilder,
    OpenRouterBackend,
    parse_model_output,
)
from nowmind.modeling import validation as validation_module
from nowmind.modeling.representation import stable_hash


OUTPUT_DIR = Path("artifacts") / "g2_3_3"
DISCOVERY_PATH = OUTPUT_DIR / "free_model_discovery.json"
QUOTA_PATH = OUTPUT_DIR / "free_quota_manifest.json"
PROTOCOL_PATH = OUTPUT_DIR / "frozen_protocol_manifest.json"
RUN_STATE_PATH = OUTPUT_DIR / "run_state.json"
REGIMES = ("A_EQUAL_INFORMATION", "B_FIXED_BUDGET")
CONDITIONS = ("N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL")
MODEL_DISCOVERY_URL = "https://openrouter.ai/api/v1/models?output_modalities=text&sort=pricing-low-to-high"
AUTH_KEY_URL = "https://openrouter.ai/api/v1/auth/key"
LOCAL_BASELINE = {
    "model": "qwen3:0.6b",
    "regime_a": {"c_better": 8, "n_better": 0, "tied": 242},
    "regime_b": {"c_better": 0, "n_better": 0, "tied": 250},
    "regime_b_fairness_failures": 0,
}


class RateLimitStop(RuntimeError):
    pass


class BatchComplete(RuntimeError):
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Run G2.3.3 free OpenRouter replication.")
    parser.add_argument("command", choices=("discover", "smoke", "calibrate", "run", "analyze", "all"))
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--max-models", type=int, default=3)
    parser.add_argument("--smoke-count", type=int, default=5)
    parser.add_argument("--calibration-count", type=int, default=5)
    parser.add_argument("--final-count", type=int, default=250)
    parser.add_argument("--request-batch-size", type=int, default=None)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.command in {"discover", "all"}:
        discovery = discover_free_models()
        write_json(DISCOVERY_PATH, discovery)
        write_json(QUOTA_PATH, discover_quota())
        write_json(PROTOCOL_PATH, frozen_protocol_manifest(args.final_count))
        write_model_selection_doc(discovery)
    else:
        discovery = read_json(DISCOVERY_PATH)

    selected = args.models or [item["id"] for item in discovery.get("selected_models", [])[: args.max_models]]
    if not selected:
        raise SystemExit("No selected free OpenRouter models are available.")
    if args.command in {"smoke", "all"}:
        for model in selected:
            run_smoke(model, args.timeout_seconds, args.num_predict, args.smoke_count, args.request_batch_size)
    if args.command in {"calibrate", "all"}:
        for model in selected:
            run_regimes(
                model,
                args.calibration_count,
                "calibration",
                "g2_3_3_cal",
                args.timeout_seconds,
                args.num_predict,
                args.request_batch_size,
            )
    if args.command in {"run", "all"}:
        for model in selected:
            run_regimes(
                model,
                args.final_count,
                "evaluation",
                "g2_3_eval",
                args.timeout_seconds,
                args.num_predict,
                args.request_batch_size,
            )
    if args.command in {"analyze", "all"}:
        write_cross_model_analysis(selected)
    return 0


def discover_free_models() -> dict[str, Any]:
    data = get_json(MODEL_DISCOVERY_URL)
    models = list(data.get("data", []))
    free = [summarize_model(model) for model in models if is_free_text_model(model)]
    selected = select_models(free)
    if not selected:
        raise SystemExit("No exact free text-generation OpenRouter model passed the $0/$0 gate.")
    return {
        "schema": "nowmind.g2_3_3.free_model_discovery.v1",
        "created_at": utc_now(),
        "source": MODEL_DISCOVERY_URL,
        "hard_gate": "pricing.prompt == 0 and pricing.completion == 0; openrouter/free rejected",
        "free_model_count": len(free),
        "free_models": free,
        "selected_models": selected,
    }


def summarize_model(model: Mapping[str, Any]) -> dict[str, Any]:
    params = list(model.get("supported_parameters") or [])
    architecture = model.get("architecture") if isinstance(model.get("architecture"), Mapping) else {}
    return {
        "id": model.get("id"),
        "name": model.get("name"),
        "family": model_family(str(model.get("id", ""))),
        "canonical_slug": model.get("canonical_slug"),
        "context_length": model.get("context_length"),
        "structured_output_support": "structured_outputs" in params or "response_format" in params,
        "supports_structured_outputs_parameter": "structured_outputs" in params,
        "supports_response_format": "response_format" in params,
        "supported_parameters": params,
        "current_price": {
            "input": str((model.get("pricing") or {}).get("prompt")),
            "output": str((model.get("pricing") or {}).get("completion")),
        },
        "input_modalities": list(architecture.get("input_modalities") or []),
        "output_modalities": list(architecture.get("output_modalities") or []),
        "top_provider": model.get("top_provider"),
        "per_request_limits": model.get("per_request_limits"),
        "reasoning": model.get("reasoning"),
    }


def is_free_text_model(model: Mapping[str, Any]) -> bool:
    model_id = str(model.get("id", ""))
    if model_id == "openrouter/free" or model_id.endswith("/free"):
        return False
    if not model_id.endswith(":free"):
        return False
    pricing = model.get("pricing") if isinstance(model.get("pricing"), Mapping) else {}
    try:
        free_price = float(pricing.get("prompt")) == 0.0 and float(pricing.get("completion")) == 0.0
    except (TypeError, ValueError):
        return False
    architecture = model.get("architecture") if isinstance(model.get("architecture"), Mapping) else {}
    outputs = set(architecture.get("output_modalities") or [])
    inputs = set(architecture.get("input_modalities") or [])
    return free_price and "text" in inputs and "text" in outputs


def select_models(free: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usable = [
        model
        for model in free
        if int(model.get("context_length") or 0) >= 12000
        and model.get("structured_output_support")
    ]
    preferred = (
        "qwen",
        "z-ai",
        "nvidia",
        "google",
        "minimax",
        "liquid",
        "dots",
        "cohere",
    )
    selected: list[dict[str, Any]] = []
    for family in preferred:
        choices = [model for model in usable if model["family"] == family and model not in selected]
        if choices:
            selected.append(sorted(choices, key=lambda item: int(item.get("context_length") or 0), reverse=True)[0])
        if len(selected) == 3:
            break
    if not any(model["family"] == "qwen" for model in selected):
        for model in selected:
            model["selection_note"] = "No exact $0/$0 Qwen-family model was present in live OpenRouter metadata."
    return selected


def discover_quota() -> dict[str, Any]:
    try:
        data = get_json(AUTH_KEY_URL)
        key_data = data.get("data", data) if isinstance(data, Mapping) else {}
        return {
            "schema": "nowmind.g2_3_3.free_quota_manifest.v1",
            "created_at": utc_now(),
            "source": AUTH_KEY_URL,
            "status": "success",
            "account_limit": key_data.get("limit") if isinstance(key_data, Mapping) else None,
            "usage": key_data.get("usage") if isinstance(key_data, Mapping) else None,
            "limit_remaining": key_data.get("limit_remaining") if isinstance(key_data, Mapping) else None,
            "rate_limit": key_data.get("rate_limit") if isinstance(key_data, Mapping) else None,
            "raw_fields": sorted(key_data.keys()) if isinstance(key_data, Mapping) else [],
            "note": "OpenRouter model metadata exposes per_request_limits; HTTP 429 is treated as quota exhaustion.",
        }
    except Exception as exc:
        return {
            "schema": "nowmind.g2_3_3.free_quota_manifest.v1",
            "created_at": utc_now(),
            "source": AUTH_KEY_URL,
            "status": "failed",
            "error": str(exc),
        }


def frozen_protocol_manifest(final_count: int) -> dict[str, Any]:
    trials = bench.generate_trials(bench.DEFAULT_SEED + 1, final_count, "evaluation", "g2_3_eval")
    trial_ids = [trial.trial_id for trial in trials]
    return {
        "schema": "nowmind.g2_3_3.frozen_protocol_manifest.v1",
        "created_at": utc_now(),
        "frozen_from": "G2.3.2",
        "trial_count": final_count,
        "trial_ids": trial_ids,
        "trial_ids_hash": stable_hash(trial_ids),
        "local_g2_3_2_regime_b_file": "artifacts/g2_3_2/g2_3_2_regime_b_trial_results.jsonl",
        "common_system_instruction_hash": stable_hash(COMMON_SYSTEM_INSTRUCTION),
        "n_builder_hash": source_hash(NowMindRepresentationBuilder),
        "c_builder_hash": source_hash(ChronologicalRepresentationBuilder),
        "r_builder_hash": source_hash(CurrentOnlyRepresentationBuilder),
        "regime_a_template_hash": stable_hash("A_EQUAL_INFORMATION:no_truncation"),
        "regime_b_template_hash": stable_hash(f"B_FIXED_BUDGET:{bench.FIXED_TOKEN_BUDGET}:corrected_final_input_gate"),
        "output_schema_hash": stable_hash(MODEL_PROPOSAL_JSON_SCHEMA),
        "validator_hash": source_hash(validation_module.validate_model_proposal),
        "scoring_hash": stable_hash(inspect.getsource(bench._score_proposal) + inspect.getsource(bench._score_validated)),
        "corrected_budget_hash": stable_hash(inspect.getsource(NowMindRepresentationBuilder.build) + inspect.getsource(ChronologicalRepresentationBuilder.build)),
    }


def run_smoke(
    model: str,
    timeout_seconds: int,
    num_predict: int,
    smoke_count: int = 5,
    request_batch_size: int | None = None,
) -> None:
    safe = safe_model_slug(model)
    model_dir = OUTPUT_DIR / safe
    model_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    rows_path = model_dir / "smoke_results.jsonl"
    done = completed_keys(rows_path)
    spent = 0
    checks = [
        ("basic_structured_json", "temporal_present_vs_stale_memory"),
        ("temporal_current_vs_memory", "temporal_current_unknown_memory"),
        ("hypothetical_vs_current", "temporal_future_vs_current"),
        ("spatial_relation", "spatial_relative_position"),
        ("action_choice", "action_choose_next_move"),
    ]
    for index, (check, family) in enumerate(checks[:smoke_count]):
        trial = next(
            trial for trial in bench.generate_trials(bench.DEFAULT_SEED + 1, 250, "evaluation", "g2_3_eval")
            if trial.family == family
        )
        key = row_key(model, "A_EQUAL_INFORMATION", trial.trial_id, "N_NOWMIND_STRUCTURED")
        if key in done:
            continue
        row = run_cloud_condition(model, trial, "A_EQUAL_INFORMATION", "N_NOWMIND_STRUCTURED", timeout_seconds, num_predict)
        row["g2_3_3"]["smoke_check"] = check
        if is_rate_limited(row):
            write_json(model_dir / "smoke.json", {"model": model, "status": "paused_rate_limit", "rows": rows})
            update_run_state(model, "paused_rate_limit", f"Smoke stopped on {check}")
            raise RateLimitStop(f"Rate limit during smoke for {model}")
        if row.get("error"):
            rows.append({"check": check, "row": row})
            append_rows(rows_path, [row])
            status = "stopped_privacy_policy" if is_privacy_policy_error(row) else "stopped_error"
            write_smoke_summary(model, status, smoke_count)
            update_run_state(model, status, f"Smoke stopped on {check}: {row['error']}")
            raise SystemExit(f"Smoke stopped for {model}: {row['error']}")
        if not row["g2_3_3"]["output_schema_guard"]["passed"]:
            rows.append({"check": check, "row": row})
            append_rows(rows_path, [row])
            issues = ",".join(row["g2_3_3"]["output_schema_guard"]["issues"])
            write_smoke_summary(model, "stopped_schema_invalid", smoke_count)
            update_run_state(model, "stopped_schema_invalid", f"Smoke stopped on {check}: {issues}")
            raise SystemExit(f"Smoke stopped for {model}: schema invalid ({issues})")
        rows.append({"check": check, "row": row})
        append_rows(rows_path, [row])
        done.add(key)
        spent += 1
        if request_batch_size is not None and spent >= request_batch_size:
            write_smoke_summary(model, "paused_batch_complete", smoke_count)
            update_run_state(model, "paused_batch_complete", f"Smoke batch completed after {spent} new request(s).")
            raise BatchComplete(f"Smoke batch complete for {model}: {spent} new request(s).")
    write_smoke_summary(model, "complete", smoke_count)


def write_smoke_summary(model: str, status: str, smoke_count: int) -> None:
    model_dir = OUTPUT_DIR / safe_model_slug(model)
    rows = read_rows(model_dir / "smoke_results.jsonl")
    parsed = sum(1 for row in rows if row["parse_success"])
    schema_valid = sum(
        1
        for row in rows
        if row.get("g2_3_3", {}).get("output_schema_guard", {}).get("passed")
    )
    write_json(
        model_dir / "smoke.json",
        {
            "schema": "nowmind.g2_3_3.smoke.v1",
            "created_at": utc_now(),
            "model": model,
            "status": status,
            "target_checks": smoke_count,
            "completed_checks": len(rows),
            "parse_success": parsed,
            "schema_success": schema_valid,
            "transport_errors": sum(1 for row in rows if row.get("error")),
            "rows": rows,
        },
    )


def run_regimes(
    model: str,
    count: int,
    split: str,
    prefix: str,
    timeout_seconds: int,
    num_predict: int,
    request_batch_size: int | None = None,
) -> None:
    trials = bench.generate_trials(bench.DEFAULT_SEED + 1, count, split, prefix)
    safe = safe_model_slug(model)
    model_dir = OUTPUT_DIR / safe
    model_dir.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    spent = 0
    for regime in REGIMES:
        path = model_dir / ("calibration.jsonl" if split == "calibration" else f"{regime.lower()}_results.jsonl")
        done = completed_keys(path)
        for index, trial in enumerate(trials, start=1):
            trial_rows = []
            for condition in CONDITIONS:
                key = row_key(model, regime, trial.trial_id, condition)
                if key in done:
                    continue
                row = run_cloud_condition(model, trial, regime, condition, timeout_seconds, num_predict)
                if is_rate_limited(row):
                    update_run_state(
                        model,
                        "paused_rate_limit",
                        f"{split} stopped at {regime} {trial.trial_id} {condition}",
                    )
                    write_cross_model_analysis([model])
                    raise RateLimitStop("OpenRouter quota/rate limit reached; run is resumable.")
                if row.get("error"):
                    update_run_state(model, "stopped_error", str(row["error"]))
                    write_cross_model_analysis([model])
                    raise SystemExit(f"OpenRouter model error for {model}: {row['error']}")
                trial_rows.append(row)
                append_rows(path, [row])
                done.add(key)
                spent += 1
                if request_batch_size is not None and spent >= request_batch_size:
                    if split == "calibration":
                        rows = read_rows(model_dir / "calibration.jsonl")
                        write_json(model_dir / "calibration.json", summarize_rows(model, rows, "calibration"))
                    else:
                        write_model_artifacts(model)
                    update_run_state(
                        model,
                        "paused_batch_complete",
                        f"{split} batch completed after {spent} new request(s).",
                    )
                    raise BatchComplete(f"{split} batch complete for {model}: {spent} new request(s).")
            if trial_rows:
                print(
                    f"{model} {split} {regime} {index}/{count} "
                    f"rows={len(trial_rows)} elapsed={perf_counter() - started:.1f}s",
                    flush=True,
                )
    if split == "calibration":
        rows = read_rows(model_dir / "calibration.jsonl")
        write_json(model_dir / "calibration.json", summarize_rows(model, rows, "calibration"))
    else:
        write_model_artifacts(model)


def run_cloud_condition(
    model: str,
    trial: bench.G23Trial,
    regime: str,
    condition: str,
    timeout_seconds: int,
    num_predict: int,
) -> dict[str, Any]:
    native_json_schema = model_supports_native_json_schema(model)
    backend = OpenRouterBackend(
        model,
        timeout_seconds=timeout_seconds,
        native_json_schema=native_json_schema,
    )
    row = bench._run_condition(
        trial,
        regime,
        condition,
        backend,
        repair_attempts=0,
        num_predict=num_predict,
    )
    row["g2_3_3"] = {
        "row_key": row_key(model, regime, trial.trial_id, condition),
        "synthetic_payload_guard": synthetic_payload_guard(row),
        "effective_provider": effective_provider(row),
        "provider_match_required": True,
        "price_gate": "verified_free_by_discovery",
        "json_compatibility_mode": "native_json_schema"
        if native_json_schema
        else "prompt_only_json",
    }
    row["g2_3_3"]["output_schema_guard"] = output_schema_guard(row)
    if not row["g2_3_3"]["synthetic_payload_guard"]["passed"]:
        raise SystemExit("Synthetic-only payload guard failed before recording a cloud row.")
    return row


def write_model_artifacts(model: str) -> None:
    safe = safe_model_slug(model)
    model_dir = OUTPUT_DIR / safe
    model_dir.mkdir(parents=True, exist_ok=True)
    for path in (
        model_dir / "calibration.jsonl",
        model_dir / "a_equal_information_results.jsonl",
        model_dir / "b_fixed_budget_results.jsonl",
    ):
        path.touch(exist_ok=True)
    if not (model_dir / "calibration.json").exists():
        write_json(model_dir / "calibration.json", summarize_rows(model, [], "calibration"))
    if not (model_dir / "smoke.json").exists():
        write_json(
            model_dir / "smoke.json",
            {
                "schema": "nowmind.g2_3_3.smoke.v1",
                "created_at": utc_now(),
                "model": model,
                "status": "not_started",
                "checks": 0,
                "parse_success": 0,
                "transport_errors": 0,
                "rows": [],
            },
        )
    rows = []
    for regime in REGIMES:
        rows.extend(read_rows(model_dir / f"{regime.lower()}_results.jsonl"))
    metrics = bench._aggregate(rows) if rows else {}
    pairwise = pairwise_provider_safe(rows)
    provider_manifest = provider_manifest_for_rows(model, rows)
    write_json(model_dir / "metrics.json", metrics)
    write_json(model_dir / "pairwise.json", pairwise)
    write_json(model_dir / "provider_manifest.json", provider_manifest)
    (model_dir / "statistical_summary.md").write_text(statistical_summary(model, pairwise), encoding="utf-8")


def write_cross_model_analysis(models: list[str]) -> None:
    completed = []
    for model in models:
        write_model_artifacts(model)
        model_dir = OUTPUT_DIR / safe_model_slug(model)
        completed.append(
            {
                "model": model,
                "pairwise": read_json(model_dir / "pairwise.json") if (model_dir / "pairwise.json").exists() else {},
                "metrics": read_json(model_dir / "metrics.json") if (model_dir / "metrics.json").exists() else {},
                "provider_manifest": read_json(model_dir / "provider_manifest.json") if (model_dir / "provider_manifest.json").exists() else {},
            }
        )
    summary = {
        "schema": "nowmind.g2_3_3.cross_model_summary.v1",
        "created_at": utc_now(),
        "local_baseline": LOCAL_BASELINE,
        "models": completed,
    }
    write_json(OUTPUT_DIR / "g2_3_3_cross_model_summary.json", summary)
    (OUTPUT_DIR / "g2_3_3_cross_model_summary.md").write_text(cross_model_markdown(summary), encoding="utf-8")
    Path("docs/G2_3_3_CROSS_MODEL_INTERPRETATION.md").write_text(cross_model_interpretation(summary), encoding="utf-8")


def pairwise_provider_safe(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_key[(str(row["model"]), row["regime"], row["trial"]["trial_id"])][row["condition"]] = row
    results: dict[str, Any] = {}
    for mode in ("proposal", "validated"):
        buckets: dict[str, dict[str, int]] = {}
        skipped = 0
        for (model, regime, _), conditions in by_key.items():
            if "N_NOWMIND_STRUCTURED" not in conditions or "C_CHRONOLOGICAL" not in conditions:
                continue
            n = conditions["N_NOWMIND_STRUCTURED"]
            c = conditions["C_CHRONOLOGICAL"]
            if effective_provider(n) != effective_provider(c):
                skipped += 1
                continue
            key = f"{model}|{regime}|{mode}"
            bucket = buckets.setdefault(key, {"n_better": 0, "c_better": 0, "tied": 0, "provider_mismatch_skipped": 0})
            n_correct = bool(n[f"{mode}_score"]["correct"])
            c_correct = bool(c[f"{mode}_score"]["correct"])
            if n_correct and not c_correct:
                bucket["n_better"] += 1
            elif c_correct and not n_correct:
                bucket["c_better"] += 1
            else:
                bucket["tied"] += 1
        for bucket in buckets.values():
            bucket["provider_mismatch_skipped"] += skipped
        results.update(buckets)
    return results


def provider_manifest_for_rows(model: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    providers = defaultdict(int)
    mismatches = 0
    by_trial_regime: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for row in rows:
        provider = effective_provider(row)
        providers[provider] += 1
        by_trial_regime[(row["regime"], row["trial"]["trial_id"])][row["condition"]] = provider
    for providers_by_condition in by_trial_regime.values():
        if {"N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL"} <= set(providers_by_condition):
            mismatches += int(providers_by_condition["N_NOWMIND_STRUCTURED"] != providers_by_condition["C_CHRONOLOGICAL"])
    return {
        "schema": "nowmind.g2_3_3.provider_manifest.v1",
        "model": model,
        "provider_request": {
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
        },
        "provider_counts": dict(sorted(providers.items())),
        "paired_provider_mismatches": mismatches,
        "note": "If OpenRouter does not report actual provider, rows use unreported_provider_fallback_disabled.",
    }


def summarize_rows(model: str, rows: list[dict[str, Any]], split: str) -> dict[str, Any]:
    return {
        "schema": "nowmind.g2_3_3.calibration.v1",
        "created_at": utc_now(),
        "model": model,
        "split": split,
        "row_count": len(rows),
        "parse_success": sum(1 for row in rows if row.get("parse_success")),
        "errors": sum(1 for row in rows if row.get("error")),
        "provider_manifest": provider_manifest_for_rows(model, rows),
    }


def write_model_selection_doc(discovery: Mapping[str, Any]) -> None:
    lines = [
        "# G2.3.3 Free Model Selection",
        "",
        f"Date: {utc_now()}",
        "",
        "Only exact OpenRouter models with current input price `0` and output price `0` are eligible. `openrouter/free` is rejected because it is a random router.",
        "",
        f"Discovered exact free text models: `{discovery['free_model_count']}`",
        "",
        "## Selected Models",
        "",
    ]
    for model in discovery.get("selected_models", []):
        lines.append(
            f"- `{model['id']}` family={model['family']} context={model['context_length']} "
            f"price=input `{model['current_price']['input']}` output `{model['current_price']['output']}` "
            f"structured={model['structured_output_support']}"
        )
    if not any(model.get("family") == "qwen" for model in discovery.get("selected_models", [])):
        lines.extend(["", "No exact Qwen-family `$0/$0` model was present in the live metadata at discovery time."])
    lines.extend(
        [
            "",
            "Provider settings for all model calls request fallback disabled, required parameters enabled, and data collection denied. If a model cannot run under those settings, it is stopped rather than silently relaxed.",
            "",
        ]
    )
    Path("docs/G2_3_3_FREE_MODEL_SELECTION.md").write_text("\n".join(lines), encoding="utf-8")


def cross_model_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# G2.3.3 Cross-Model Summary",
        "",
        "Local baseline: `qwen3:0.6b` G2.3.2, Regime A C=8/N=0/T=242, Regime B C=0/N=0/T=250.",
        "",
    ]
    for model in summary.get("models", []):
        lines.append(f"## {model['model']}")
        pairwise = model.get("pairwise", {})
        if not pairwise:
            lines.append("")
            lines.append("No completed paired result yet.")
            lines.append("")
            continue
        for key, value in pairwise.items():
            lines.append(f"- `{key}` N={value['n_better']} C={value['c_better']} tied={value['tied']} skipped_provider={value.get('provider_mismatch_skipped', 0)}")
        lines.append("")
    return "\n".join(lines)


def cross_model_interpretation(summary: Mapping[str, Any]) -> str:
    lines = [
        "# G2.3.3 Cross-Model Interpretation",
        "",
        "This document interprets only completed, provider-compatible OpenRouter rows. The frozen local baseline remains unchanged.",
        "",
    ]
    any_completed = False
    for model in summary.get("models", []):
        pairwise = model.get("pairwise", {})
        completed = bool(pairwise)
        any_completed = any_completed or completed
        lines.append(f"## {model['model']}")
        if not completed:
            lines.append("")
            lines.append("No completed provider-compatible paired result yet.")
            lines.append("")
            continue
        for key, value in pairwise.items():
            if value["n_better"] > value["c_better"]:
                verdict = "NowMind advantage in this slice"
            elif value["c_better"] > value["n_better"]:
                verdict = "Chronological advantage in this slice"
            else:
                verdict = "No N/C difference in this slice"
            lines.append(f"- `{key}`: {verdict}; N={value['n_better']}, C={value['c_better']}, ties={value['tied']}.")
        lines.append("")
    if not any_completed:
        lines.append("No cross-model evidence is complete enough yet to say whether the Regime-A chronology advantage persists, disappears, or reverses.")
    lines.append("")
    lines.append("Do not claim NowMind superiority unless paired evidence supports it. Do not infer a general capability threshold from a single free model or an incomplete quota-limited run.")
    lines.append("")
    return "\n".join(lines)


def statistical_summary(model: str, pairwise: Mapping[str, Any]) -> str:
    lines = ["# G2.3.3 Statistical Summary", "", f"Model: `{model}`", ""]
    if not pairwise:
        lines.append("No completed provider-compatible N/C pairs yet.")
        return "\n".join(lines) + "\n"
    for key, values in pairwise.items():
        n = int(values["n_better"])
        c = int(values["c_better"])
        tied = int(values["tied"])
        discordant = n + c
        p = exact_two_sided_binomial(n, discordant) if discordant else 1.0
        lines.extend(
            [
                f"- `{key}`",
                f"  N better: `{n}`",
                f"  C better: `{c}`",
                f"  Ties: `{tied}`",
                f"  Exact paired binomial p-value: `{p:.6f}`",
            ]
        )
    return "\n".join(lines) + "\n"


def exact_two_sided_binomial(n_better: int, discordant: int) -> float:
    if discordant == 0:
        return 1.0
    observed = binomial_mass(discordant, n_better)
    return min(1.0, sum(binomial_mass(discordant, value) for value in range(discordant + 1) if binomial_mass(discordant, value) <= observed + 1e-15))


def binomial_mass(total: int, successes: int) -> float:
    import math

    return math.comb(total, successes) * (0.5 ** total)


def synthetic_payload_guard(row: Mapping[str, Any]) -> dict[str, Any]:
    text = json.dumps(row.get("representation", {}), sort_keys=True)
    forbidden = ["sk-or-v1-", "PCT_Book", "reference/", "personal", "Jonathan"]
    hits = [item for item in forbidden if item in text]
    return {"passed": not hits, "forbidden_hits": hits}


def is_rate_limited(row: Mapping[str, Any]) -> bool:
    error_text = str(row.get("error") or "")
    response = row.get("model_response", {})
    metadata = response.get("provider_metadata", {}) if isinstance(response, Mapping) else {}
    return "HTTP 429" in error_text or "rate limit" in error_text.lower() or bool(metadata.get("rate_limited"))


def is_privacy_policy_error(row: Mapping[str, Any]) -> bool:
    error_text = str(row.get("error") or "").lower()
    return "data policy" in error_text or "privacy" in error_text


def output_schema_guard(row: Mapping[str, Any]) -> dict[str, Any]:
    parsed = row.get("parsed_output")
    if not isinstance(parsed, Mapping):
        return {"passed": False, "issues": ["missing_parsed_output"]}
    issues = []
    if parsed.get("status") not in {
        "TRUE",
        "FALSE",
        "UNKNOWN",
        "CONTRADICTORY",
        "ANSWER",
        "ACTION",
    }:
        issues.append("invalid_status")
    if parsed.get("source_used") not in {
        "observed_now",
        "inferred_now",
        "reconstructed_memory",
        "hypothetical_future",
        "mixed",
        "none",
    }:
        issues.append("invalid_source_used")
    if not isinstance(parsed.get("assumptions"), list):
        issues.append("invalid_assumptions")
    if not isinstance(parsed.get("explanation"), list):
        issues.append("invalid_explanation")
    return {"passed": not issues, "issues": issues}


def model_supports_native_json_schema(model: str) -> bool:
    discovery = read_json(DISCOVERY_PATH)
    for item in discovery.get("free_models", []):
        if item.get("id") == model:
            return bool(item.get("supports_response_format"))
    return True


def completed_keys(path: Path) -> set[str]:
    return {
        str(row.get("g2_3_3", {}).get("row_key"))
        for row in read_rows(path)
        if row.get("g2_3_3", {}).get("row_key")
        and row.get("parse_success")
        and not row.get("error")
        and row.get("g2_3_3", {}).get("output_schema_guard", {}).get("passed")
    }


def row_key(model: str, regime: str, trial_id: str, condition: str) -> str:
    return "|".join([model, regime, trial_id, condition])


def effective_provider(row: Mapping[str, Any]) -> str:
    response = row.get("model_response", {}) if isinstance(row.get("model_response"), Mapping) else {}
    metadata = response.get("provider_metadata", {}) if isinstance(response, Mapping) else {}
    provider = metadata.get("provider")
    if provider:
        return str(provider)
    return "unreported_provider_fallback_disabled"


def model_family(model_id: str) -> str:
    prefix = model_id.split("/", 1)[0]
    if "qwen" in model_id.lower():
        return "qwen"
    return prefix


def source_hash(obj: Any) -> str:
    return hashlib.sha256(inspect.getsource(obj).encode("utf-8")).hexdigest()


def safe_model_slug(model: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in model).strip("_")


def get_json(url: str) -> dict[str, Any]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    req = request.Request(url, headers={"Authorization": f"Bearer {api_key}"}, method="GET")
    with request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def append_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()


def update_run_state(model: str, status: str, detail: str) -> None:
    state = read_json(RUN_STATE_PATH)
    state.setdefault("schema", "nowmind.g2_3_3.run_state.v1")
    state.setdefault("models", {})
    state["updated_at"] = utc_now()
    state["models"][model] = {"status": status, "detail": detail, "updated_at": utc_now()}
    write_json(RUN_STATE_PATH, state)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BatchComplete as exc:
        print(str(exc), flush=True)
        raise SystemExit(0)
    except RateLimitStop as exc:
        print(str(exc), flush=True)
        raise SystemExit(75)

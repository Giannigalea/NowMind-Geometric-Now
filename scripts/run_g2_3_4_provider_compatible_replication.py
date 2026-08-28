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
from urllib import error, parse, request

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
)
from nowmind.modeling import validation as validation_module
from nowmind.modeling.representation import stable_hash


OUTPUT_DIR = Path("artifacts") / "g2_3_4"
REDISCOVERY_PATH = OUTPUT_DIR / "free_model_rediscovery.json"
SELECTION_PATH = OUTPUT_DIR / "model_selection.json"
PROTOCOL_PATH = OUTPUT_DIR / "frozen_protocol_manifest.json"
RUN_STATE_PATH = OUTPUT_DIR / "run_state.json"
MODEL_DISCOVERY_URL = "https://openrouter.ai/api/v1/models?output_modalities=text&sort=pricing-low-to-high"
AUTH_KEY_URL = "https://openrouter.ai/api/v1/auth/key"
REGIMES = ("A_EQUAL_INFORMATION", "B_FIXED_BUDGET")
CONDITIONS = ("N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL")
LOCAL_BASELINE = {
    "model": "qwen3:0.6b",
    "regime_a": {"c_better": 8, "n_better": 0, "tied": 242},
    "regime_b": {"c_better": 0, "n_better": 0, "tied": 250},
    "regime_b_fairness_failures": 0,
}
STATUS_PRIORITY = {
    "stopped_privacy_policy": 0,
    "paused_rate_limit": 1,
    "stopped_schema_invalid": 2,
    "stopped_error": 3,
}
SMOKE_CHECKS = (
    ("basic_json", "temporal_present_vs_stale_memory"),
    ("current_vs_memory", "temporal_current_unknown_memory"),
    ("hypothetical_vs_current", "temporal_future_vs_current"),
    ("action_output", "action_choose_next_move"),
)


class RateLimitStop(RuntimeError):
    pass


class BatchComplete(RuntimeError):
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Run G2.3.4 provider-compatible free OpenRouter replication.")
    parser.add_argument("command", choices=("discover", "smoke", "calibrate", "run", "analyze", "all"))
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--max-models", type=int, default=3)
    parser.add_argument("--smoke-count", type=int, default=4)
    parser.add_argument("--calibration-count", type=int, default=5)
    parser.add_argument("--final-count", type=int, default=250)
    parser.add_argument("--request-batch-size", type=int, default=None)
    parser.add_argument("--num-predict", type=int, default=512)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.command in {"discover", "all"}:
        rediscovery = rediscover_free_models()
        write_json(REDISCOVERY_PATH, rediscovery)
        write_json(SELECTION_PATH, build_model_selection(rediscovery))
        write_json(PROTOCOL_PATH, frozen_protocol_manifest(args.final_count))
        write_json(OUTPUT_DIR / "free_quota_manifest.json", discover_quota())
        write_protocol_doc(rediscovery)
        write_model_selection_doc(rediscovery)
    else:
        rediscovery = read_json(REDISCOVERY_PATH)

    selected = args.models or [item["id"] for item in rediscovery.get("selected_models", [])[: args.max_models]]
    if not selected:
        raise SystemExit("No exact-free G2.3.4 models are selected.")
    try:
        if args.command in {"smoke", "all"}:
            for model in selected:
                run_smoke(model, args.timeout_seconds, args.num_predict, args.smoke_count, args.request_batch_size)
        if args.command in {"calibrate", "all"}:
            for model in selected:
                run_regimes(model, args.calibration_count, "calibration", "g2_3_4_cal", args.timeout_seconds, args.num_predict, args.request_batch_size)
        if args.command in {"run", "all"}:
            for model in selected:
                run_regimes(model, args.final_count, "evaluation", "g2_3_eval", args.timeout_seconds, args.num_predict, args.request_batch_size)
        if args.command in {"analyze", "all"}:
            write_summary(selected)
    except BatchComplete as exc:
        print(str(exc), flush=True)
        return 0
    except RateLimitStop as exc:
        print(str(exc), flush=True)
        return 75
    return 0


def rediscover_free_models() -> dict[str, Any]:
    models = list(get_json(MODEL_DISCOVERY_URL).get("data", []))
    g233_state = read_json(Path("artifacts") / "g2_3_3" / "run_state.json").get("models", {})
    providers = providers_by_slug()
    free = []
    for model in models:
        if not is_free_text_model(model):
            continue
        summary = summarize_model(model)
        endpoint_data = endpoint_summary(str(summary["id"]))
        summary["endpoints"] = endpoint_data["endpoints"]
        summary["endpoint_lookup_status"] = endpoint_data["status"]
        summary["g2_3_3_status"] = g233_state.get(summary["id"], {}).get("status")
        summary["requires_data_collection_inferred"] = summary["g2_3_3_status"] == "stopped_privacy_policy"
        summary["provider_pinning_possible"] = bool(endpoint_data["endpoints"])
        for endpoint in summary["endpoints"]:
            endpoint["provider_terms_url"] = providers.get(endpoint.get("provider_tag"), {}).get("terms_of_service_url")
            endpoint["provider_privacy_url"] = providers.get(endpoint.get("provider_tag"), {}).get("privacy_policy_url")
        free.append(summary)
    selected = select_models(free)
    return {
        "schema": "nowmind.g2_3_4.free_model_rediscovery.v1",
        "created_at": utc_now(),
        "source": MODEL_DISCOVERY_URL,
        "privacy_rule": "provider data_collection may be allow for synthetic benchmark prompts only",
        "hard_gate": "exact :free model ID; pricing.prompt == 0; pricing.completion == 0; openrouter/free rejected",
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
        "supports_response_format": "response_format" in params,
        "supported_parameters": params,
        "current_price": {
            "input": str((model.get("pricing") or {}).get("prompt")),
            "output": str((model.get("pricing") or {}).get("completion")),
        },
        "input_modalities": list(architecture.get("input_modalities") or []),
        "output_modalities": list(architecture.get("output_modalities") or []),
        "top_provider": model.get("top_provider"),
        "reasoning": model.get("reasoning"),
    }


def endpoint_summary(model_id: str) -> dict[str, Any]:
    try:
        author, slug = model_id.split("/", 1)
        url = f"https://openrouter.ai/api/v1/models/{parse.quote(author)}/{parse.quote(slug, safe=':')}/endpoints"
        data = get_json(url).get("data", {})
        endpoints = []
        for endpoint in data.get("endpoints", []) if isinstance(data, Mapping) else []:
            pricing = endpoint.get("pricing") if isinstance(endpoint.get("pricing"), Mapping) else {}
            params = list(endpoint.get("supported_parameters") or [])
            endpoints.append(
                {
                    "provider_name": endpoint.get("provider_name"),
                    "provider_tag": endpoint.get("tag"),
                    "context_length": endpoint.get("context_length"),
                    "max_completion_tokens": endpoint.get("max_completion_tokens"),
                    "pricing": {
                        "prompt": str(pricing.get("prompt")),
                        "completion": str(pricing.get("completion")),
                    },
                    "supports_response_format": "response_format" in params,
                    "supports_structured_outputs": "structured_outputs" in params,
                    "supports_required_parameters": bool(params),
                    "required_parameters_supported": params,
                    "uptime_last_30m": endpoint.get("uptime_last_30m"),
                    "latency_p50_ms": (endpoint.get("latency_last_30m") or {}).get("p50")
                    if isinstance(endpoint.get("latency_last_30m"), Mapping)
                    else None,
                    "throughput_p50": (endpoint.get("throughput_last_30m") or {}).get("p50")
                    if isinstance(endpoint.get("throughput_last_30m"), Mapping)
                    else None,
                }
            )
        return {"status": "success", "endpoints": endpoints}
    except Exception as exc:
        return {"status": f"failed: {exc}", "endpoints": []}


def providers_by_slug() -> dict[str, Any]:
    try:
        data = get_json("https://openrouter.ai/api/v1/providers").get("data", [])
    except Exception:
        return {}
    return {str(item.get("slug")): item for item in data if isinstance(item, Mapping)}


def select_models(free: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usable = [
        item
        for item in free
        if int(item.get("context_length") or 0) >= 12000
        and item.get("provider_pinning_possible")
    ]
    return sorted(
        usable,
        key=lambda item: (
            STATUS_PRIORITY.get(str(item.get("g2_3_3_status")), 4),
            0 if item.get("structured_output_support") else 1,
            -int(item.get("context_length") or 0),
            str(item.get("id")),
        ),
    )


def build_model_selection(rediscovery: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "nowmind.g2_3_4.model_selection.v1",
        "created_at": utc_now(),
        "selection_order": [
            "previously blocked only by G2.3.3 privacy routing",
            "adequate context",
            "structured-output support when available",
            "pinnable provider endpoint",
            "stable schema-compatible smoke output",
        ],
        "selected_models": rediscovery.get("selected_models", []),
    }


def run_smoke(
    model: str,
    timeout_seconds: int,
    num_predict: int,
    smoke_count: int = 4,
    request_batch_size: int | None = None,
) -> None:
    model_dir = OUTPUT_DIR / safe_model_slug(model)
    model_dir.mkdir(parents=True, exist_ok=True)
    rows_path = model_dir / "smoke_results.jsonl"
    done = completed_keys(rows_path)
    spent = 0
    for check, family in SMOKE_CHECKS[:smoke_count]:
        trial = next(
            trial for trial in bench.generate_trials(bench.DEFAULT_SEED + 1, 250, "evaluation", "g2_3_eval")
            if trial.family == family
        )
        key = row_key(model, pinned_provider(model), "A_EQUAL_INFORMATION", trial.trial_id, "N_NOWMIND_STRUCTURED")
        if key in done:
            continue
        row = run_cloud_condition(model, trial, "A_EQUAL_INFORMATION", "N_NOWMIND_STRUCTURED", timeout_seconds, num_predict)
        row["g2_3_4"]["smoke_check"] = check
        append_rows(rows_path, [row])
        if is_rate_limited(row):
            write_smoke_summary(model, "paused_rate_limit", smoke_count)
            update_run_state(model, "paused_rate_limit", f"Smoke stopped on {check}")
            raise RateLimitStop(f"Rate limit during smoke for {model}")
        if row.get("error"):
            write_smoke_summary(model, "stopped_error", smoke_count)
            update_run_state(model, "stopped_error", f"Smoke stopped on {check}: {row['error']}")
            raise SystemExit(f"Smoke stopped for {model}: {row['error']}")
        if not row["g2_3_4"]["output_schema_guard"]["passed"]:
            issues = ",".join(row["g2_3_4"]["output_schema_guard"]["issues"])
            write_smoke_summary(model, "stopped_schema_invalid", smoke_count)
            update_run_state(model, "stopped_schema_invalid", f"Smoke stopped on {check}: {issues}")
            raise SystemExit(f"Smoke stopped for {model}: schema invalid ({issues})")
        done.add(key)
        spent += 1
        if request_batch_size is not None and spent >= request_batch_size:
            write_smoke_summary(model, "paused_batch_complete", smoke_count)
            update_run_state(model, "paused_batch_complete", f"Smoke batch completed after {spent} request(s).")
            raise BatchComplete(f"Smoke batch complete for {model}: {spent} request(s).")
    write_smoke_summary(model, "complete", smoke_count)
    update_run_state(model, "smoke_complete", f"Smoke completed {smoke_count} checks.")


def run_regimes(
    model: str,
    count: int,
    split: str,
    prefix: str,
    timeout_seconds: int,
    num_predict: int,
    request_batch_size: int | None,
) -> None:
    trials = bench.generate_trials(bench.DEFAULT_SEED + 1, count, split, prefix)
    model_dir = OUTPUT_DIR / safe_model_slug(model)
    model_dir.mkdir(parents=True, exist_ok=True)
    spent = 0
    started = perf_counter()
    provider = pinned_provider(model)
    for regime in REGIMES:
        path = model_dir / ("calibration.jsonl" if split == "calibration" else f"{regime.lower()}_results.jsonl")
        done = completed_keys(path)
        for index, trial in enumerate(trials, start=1):
            for condition in CONDITIONS:
                key = row_key(model, provider, regime, trial.trial_id, condition)
                if key in done:
                    continue
                row = run_cloud_condition(model, trial, regime, condition, timeout_seconds, num_predict)
                append_rows(path, [row])
                if is_rate_limited(row):
                    write_summary([model])
                    update_run_state(model, "paused_rate_limit", f"{split} stopped at {regime} {trial.trial_id} {condition}")
                    raise RateLimitStop("OpenRouter quota/rate limit reached; run is resumable.")
                if row.get("error"):
                    write_summary([model])
                    update_run_state(model, "stopped_error", str(row["error"]))
                    raise SystemExit(f"OpenRouter model error for {model}: {row['error']}")
                if not row["g2_3_4"]["output_schema_guard"]["passed"]:
                    write_summary([model])
                    update_run_state(model, "stopped_schema_invalid", ",".join(row["g2_3_4"]["output_schema_guard"]["issues"]))
                    raise SystemExit(f"OpenRouter schema invalid for {model}")
                done.add(key)
                spent += 1
                if request_batch_size is not None and spent >= request_batch_size:
                    write_model_artifacts(model)
                    update_run_state(model, "paused_batch_complete", f"{split} batch completed after {spent} request(s).")
                    raise BatchComplete(f"{split} batch complete for {model}: {spent} request(s).")
            print(f"{model} {split} {regime} {index}/{count} elapsed={perf_counter() - started:.1f}s", flush=True)
    write_model_artifacts(model)
    update_run_state(model, f"{split}_complete", f"{split} completed count={count}.")


def run_cloud_condition(
    model: str,
    trial: bench.G23Trial,
    regime: str,
    condition: str,
    timeout_seconds: int,
    num_predict: int,
) -> dict[str, Any]:
    rediscovery = read_json(REDISCOVERY_PATH)
    provider = pinned_provider(model)
    native_json_schema = model_supports_response_format(model, rediscovery)
    reasoning_config = reasoning_config_for_model(model, rediscovery)
    context_size = context_size_for_model(model, rediscovery)
    backend = OpenRouterBackend(
        model,
        provider=provider,
        timeout_seconds=timeout_seconds,
        data_collection="allow",
        native_json_schema=native_json_schema,
        reasoning_config=reasoning_config,
        context_size=context_size,
    )
    row = bench._run_condition(
        trial,
        regime,
        condition,
        backend,
        repair_attempts=0,
        num_predict=num_predict,
    )
    row["g2_3_4"] = {
        "row_key": row_key(model, provider, regime, trial.trial_id, condition),
        "synthetic_payload_guard": synthetic_payload_guard(row),
        "output_schema_guard": output_schema_guard(row),
        "effective_provider": effective_provider(row),
        "pinned_provider": provider,
        "provider_match_required": True,
        "provider_fallback_disabled": True,
        "data_collection": "allow",
        "privacy_relaxation_scope": "synthetic_benchmark_only",
        "price_gate": price_gate_for_model(model, rediscovery),
        "reasoning_config": reasoning_config,
        "context_size": context_size,
        "json_compatibility_mode": "native_json_schema" if native_json_schema else "prompt_only_json",
        "prompt_hash": row.get("prompt_hash"),
    }
    if not row["g2_3_4"]["synthetic_payload_guard"]["passed"]:
        raise SystemExit("Synthetic-only payload guard failed before recording a cloud row.")
    if not provider_matches(row, model, rediscovery) and not row.get("error"):
        row["error"] = f"provider_mismatch: pinned={provider} effective={effective_provider(row)}"
    return row


def write_smoke_summary(model: str, status: str, smoke_count: int) -> None:
    model_dir = OUTPUT_DIR / safe_model_slug(model)
    rows = read_rows(model_dir / "smoke_results.jsonl")
    write_json(
        model_dir / "smoke.json",
        {
            "schema": "nowmind.g2_3_4.smoke.v1",
            "created_at": utc_now(),
            "model": model,
            "pinned_provider": pinned_provider(model),
            "status": status,
            "target_checks": smoke_count,
            "completed_checks": len(rows),
            "parse_success": sum(1 for row in rows if row.get("parse_success")),
            "schema_success": sum(1 for row in rows if row.get("g2_3_4", {}).get("output_schema_guard", {}).get("passed")),
            "transport_errors": sum(1 for row in rows if row.get("error")),
            "rows": rows,
        },
    )


def write_model_artifacts(model: str) -> None:
    model_dir = OUTPUT_DIR / safe_model_slug(model)
    model_dir.mkdir(parents=True, exist_ok=True)
    for path in (
        model_dir / "calibration.jsonl",
        model_dir / "a_equal_information_results.jsonl",
        model_dir / "b_fixed_budget_results.jsonl",
    ):
        path.touch(exist_ok=True)
    rows = []
    for regime in REGIMES:
        rows.extend(read_rows(model_dir / f"{regime.lower()}_results.jsonl"))
    calibration = read_rows(model_dir / "calibration.jsonl")
    write_json(model_dir / "calibration.json", summarize_rows(model, calibration, "calibration"))
    write_json(model_dir / "metrics.json", bench._aggregate(rows) if rows else {})
    pairwise = pairwise_provider_safe(rows)
    write_json(model_dir / "pairwise.json", pairwise)
    write_json(model_dir / "provider_manifest.json", provider_manifest_for_rows(model, rows + calibration))
    (model_dir / "statistical_summary.md").write_text(statistical_summary(model, pairwise), encoding="utf-8")


def write_summary(models: list[str]) -> None:
    completed = []
    for model in models:
        write_model_artifacts(model)
        model_dir = OUTPUT_DIR / safe_model_slug(model)
        completed.append(
            {
                "model": model,
                "smoke": read_json(model_dir / "smoke.json"),
                "calibration": read_json(model_dir / "calibration.json"),
                "pairwise": read_json(model_dir / "pairwise.json"),
                "metrics": read_json(model_dir / "metrics.json"),
                "provider_manifest": read_json(model_dir / "provider_manifest.json"),
            }
        )
    summary = {
        "schema": "nowmind.g2_3_4.summary.v1",
        "created_at": utc_now(),
        "local_baseline": LOCAL_BASELINE,
        "models": completed,
    }
    write_json(OUTPUT_DIR / "g2_3_4_summary.json", summary)
    (OUTPUT_DIR / "g2_3_4_summary.md").write_text(summary_markdown(summary), encoding="utf-8")
    Path("docs/G2_3_4_CROSS_MODEL_INTERPRETATION.md").write_text(cross_model_interpretation(summary), encoding="utf-8")


def pairwise_provider_safe(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        if not row.get("g2_3_4", {}).get("output_schema_guard", {}).get("passed"):
            continue
        by_key[(str(row["model"]), row["regime"], row["trial"]["trial_id"])][row["condition"]] = row
    results: dict[str, Any] = {}
    for mode in ("proposal", "validated"):
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
            bucket = results.setdefault(key, {"n_better": 0, "c_better": 0, "tied": 0, "provider_mismatch_skipped": 0})
            n_correct = bool(n[f"{mode}_score"]["correct"])
            c_correct = bool(c[f"{mode}_score"]["correct"])
            if n_correct and not c_correct:
                bucket["n_better"] += 1
            elif c_correct and not n_correct:
                bucket["c_better"] += 1
            else:
                bucket["tied"] += 1
        for value in results.values():
            value["provider_mismatch_skipped"] += skipped
    return results


def provider_manifest_for_rows(model: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    providers = defaultdict(int)
    for row in rows:
        providers[effective_provider(row)] += 1
    return {
        "schema": "nowmind.g2_3_4.provider_manifest.v1",
        "model": model,
        "pinned_provider": pinned_provider(model),
        "provider_request": {
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "allow",
            "only": [pinned_provider(model)],
            "order": [pinned_provider(model)],
        },
        "provider_counts": dict(sorted(providers.items())),
    }


def summarize_rows(model: str, rows: list[dict[str, Any]], split: str) -> dict[str, Any]:
    return {
        "schema": "nowmind.g2_3_4.calibration.v1",
        "created_at": utc_now(),
        "model": model,
        "split": split,
        "row_count": len(rows),
        "parse_success": sum(1 for row in rows if row.get("parse_success")),
        "schema_success": sum(1 for row in rows if row.get("g2_3_4", {}).get("output_schema_guard", {}).get("passed")),
        "errors": sum(1 for row in rows if row.get("error")),
        "provider_manifest": provider_manifest_for_rows(model, rows),
    }


def summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# G2.3.4 Summary",
        "",
        "Local baseline: `qwen3:0.6b`, Regime A C=8/N=0/T=242, Regime B C=0/N=0/T=250.",
        "",
    ]
    for item in summary.get("models", []):
        lines.append(f"## {item['model']}")
        smoke = item.get("smoke", {})
        lines.append(f"- Smoke: `{smoke.get('status', 'not_started')}`, schema `{smoke.get('schema_success', 0)}/{smoke.get('target_checks', 0)}`")
        calibration = item.get("calibration", {})
        lines.append(f"- Calibration rows: `{calibration.get('row_count', 0)}`, schema `{calibration.get('schema_success', 0)}`")
        pairwise = item.get("pairwise", {})
        if not pairwise:
            lines.append("- No completed provider-compatible N/C pairwise result yet.")
        for key, values in pairwise.items():
            lines.append(f"- `{key}` N={values['n_better']} C={values['c_better']} tied={values['tied']} skipped_provider={values.get('provider_mismatch_skipped', 0)}")
        lines.append("")
    return "\n".join(lines)


def cross_model_interpretation(summary: Mapping[str, Any]) -> str:
    lines = [
        "# G2.3.4 Cross-Model Interpretation",
        "",
        "Interpret only schema-valid, provider-compatible OpenRouter pairs. G2.3.3 remains preserved as the strict-privacy negative result.",
        "",
    ]
    any_pairs = False
    for item in summary.get("models", []):
        pairwise = item.get("pairwise", {})
        lines.append(f"## {item['model']}")
        if not pairwise:
            lines.append("")
            lines.append("No completed provider-compatible paired result yet.")
            lines.append("")
            continue
        any_pairs = True
        for key, values in pairwise.items():
            if values["n_better"] > values["c_better"]:
                verdict = "NowMind advantage in this slice"
            elif values["c_better"] > values["n_better"]:
                verdict = "Chronological advantage in this slice"
            else:
                verdict = "No N/C difference in this slice"
            lines.append(f"- `{key}`: {verdict}; N={values['n_better']}, C={values['c_better']}, ties={values['tied']}.")
        lines.append("")
    if not any_pairs:
        lines.append("No G2.3.4 cross-model evidence is complete enough yet to say whether the Regime-A chronology advantage persists, disappears, or reverses.")
    lines.append("")
    lines.append("Do not claim NowMind superiority unless paired evidence supports it. Do not infer a general capability threshold from one exact-free model.")
    lines.append("")
    return "\n".join(lines)


def statistical_summary(model: str, pairwise: Mapping[str, Any]) -> str:
    lines = ["# G2.3.4 Statistical Summary", "", f"Model: `{model}`", ""]
    if not pairwise:
        lines.append("No completed provider-compatible N/C pairs yet.")
        return "\n".join(lines) + "\n"
    for key, values in pairwise.items():
        n = int(values["n_better"])
        c = int(values["c_better"])
        tied = int(values["tied"])
        discordant = n + c
        p_value = exact_two_sided_binomial(n, discordant) if discordant else 1.0
        lines.extend(
            [
                f"- `{key}`",
                f"  N better: `{n}`",
                f"  C better: `{c}`",
                f"  Ties: `{tied}`",
                f"  Exact paired binomial p-value: `{p_value:.6f}`",
            ]
        )
    return "\n".join(lines) + "\n"


def frozen_protocol_manifest(final_count: int) -> dict[str, Any]:
    trials = bench.generate_trials(bench.DEFAULT_SEED + 1, final_count, "evaluation", "g2_3_eval")
    trial_ids = [trial.trial_id for trial in trials]
    return {
        "schema": "nowmind.g2_3_4.frozen_protocol_manifest.v1",
        "created_at": utc_now(),
        "frozen_from": "G2.3.2 with only G2.3.4 provider data_collection relaxed",
        "trial_count": final_count,
        "trial_ids": trial_ids,
        "trial_ids_hash": stable_hash(trial_ids),
        "common_system_instruction_hash": stable_hash(COMMON_SYSTEM_INSTRUCTION),
        "n_builder_hash": source_hash(NowMindRepresentationBuilder),
        "c_builder_hash": source_hash(ChronologicalRepresentationBuilder),
        "r_builder_hash": source_hash(CurrentOnlyRepresentationBuilder),
        "regime_a_template_hash": stable_hash("A_EQUAL_INFORMATION:no_truncation"),
        "regime_b_template_hash": stable_hash(f"B_FIXED_BUDGET:{bench.FIXED_TOKEN_BUDGET}:corrected_final_input_gate"),
        "output_schema_hash": stable_hash(MODEL_PROPOSAL_JSON_SCHEMA),
        "validator_hash": source_hash(validation_module.validate_model_proposal),
        "scoring_hash": stable_hash(inspect.getsource(bench._score_proposal) + inspect.getsource(bench._score_validated)),
        "local_baseline": LOCAL_BASELINE,
    }


def write_protocol_doc(rediscovery: Mapping[str, Any]) -> None:
    lines = [
        "# G2.3.4 Protocol",
        "",
        "G2.3.4 preserves G2.3.3 as an unchanged negative strict-privacy result and writes only under `artifacts/g2_3_4/`.",
        "",
        "The only relaxed operational constraint is provider privacy routing: requests use `data_collection=allow` for synthetic benchmark prompts only.",
        "",
        "Frozen local reference: `qwen3:0.6b`, Regime A C=8/N=0/T=242, Regime B C=0/N=0/T=250.",
        "",
        "Frozen scientific controls: 250 G2.3.2 trial IDs, Regime A semantics, corrected Regime B budget, common instruction, representation builders, output schema, scoring, validator, expected answers, exact `$0/$0` model gate, provider consistency, and fallback disabled.",
        "",
        f"Rediscovered exact-free text models: `{rediscovery.get('free_model_count')}`.",
        "",
    ]
    Path("docs/G2_3_4_PROTOCOL.md").write_text("\n".join(lines), encoding="utf-8")


def write_model_selection_doc(rediscovery: Mapping[str, Any]) -> None:
    lines = [
        "# G2.3.4 Model Selection",
        "",
        f"Date: {utc_now()}",
        "",
        "Only exact OpenRouter `:free` text models with live input price `0` and output price `0` are eligible. `openrouter/free` remains rejected.",
        "",
        "Provider privacy routing is relaxed to `data_collection=allow` only for synthetic benchmark prompts. Provider fallback remains disabled and provider pinning is required where the endpoint exposes a provider tag.",
        "",
        "## Selected Priority Order",
        "",
    ]
    for model in rediscovery.get("selected_models", []):
        endpoint = (model.get("endpoints") or [{}])[0]
        lines.append(
            f"- `{model['id']}` family={model['family']} provider=`{endpoint.get('provider_tag')}` "
            f"g2_3_3_status=`{model.get('g2_3_3_status')}` price=input `{model['current_price']['input']}` output `{model['current_price']['output']}` "
            f"structured={model['structured_output_support']}"
        )
    Path("docs/G2_3_4_MODEL_SELECTION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_free_text_model(model: Mapping[str, Any]) -> bool:
    model_id = str(model.get("id", ""))
    if model_id == "openrouter/free" or model_id.endswith("/free"):
        return False
    if not model_id.endswith(":free"):
        return False
    pricing = model.get("pricing") if isinstance(model.get("pricing"), Mapping) else {}
    try:
        is_free = float(pricing.get("prompt")) == 0.0 and float(pricing.get("completion")) == 0.0
    except (TypeError, ValueError):
        return False
    architecture = model.get("architecture") if isinstance(model.get("architecture"), Mapping) else {}
    return is_free and "text" in set(architecture.get("input_modalities") or []) and "text" in set(architecture.get("output_modalities") or [])


def pinned_provider(model: str) -> str:
    rediscovery = read_json(REDISCOVERY_PATH)
    for item in rediscovery.get("free_models", []):
        if item.get("id") == model and item.get("endpoints"):
            return str(item["endpoints"][0]["provider_tag"])
    raise SystemExit(f"No pinnable provider endpoint found for {model}")


def pinned_provider_name(model: str, rediscovery: Mapping[str, Any]) -> str | None:
    for item in rediscovery.get("free_models", []):
        if item.get("id") == model and item.get("endpoints"):
            name = item["endpoints"][0].get("provider_name")
            return str(name) if name else None
    return None


def provider_matches(row: Mapping[str, Any], model: str, rediscovery: Mapping[str, Any]) -> bool:
    effective = effective_provider(row).lower()
    accepted = {pinned_provider(model).lower()}
    display_name = pinned_provider_name(model, rediscovery)
    if display_name:
        accepted.add(display_name.lower())
    return effective in accepted


def model_supports_response_format(model: str, rediscovery: Mapping[str, Any]) -> bool:
    for item in rediscovery.get("free_models", []):
        if item.get("id") == model:
            return bool(item.get("supports_response_format"))
    return True


def context_size_for_model(model: str, rediscovery: Mapping[str, Any]) -> int | None:
    for item in rediscovery.get("free_models", []):
        if item.get("id") != model:
            continue
        endpoint = (item.get("endpoints") or [{}])[0]
        endpoint_context = endpoint.get("context_length")
        model_context = item.get("context_length")
        for value in (endpoint_context, model_context):
            if isinstance(value, int) and value > 0:
                return value
    return None


def reasoning_config_for_model(model: str, rediscovery: Mapping[str, Any]) -> dict[str, Any]:
    for item in rediscovery.get("free_models", []):
        if item.get("id") != model:
            continue
        reasoning = item.get("reasoning") if isinstance(item.get("reasoning"), Mapping) else {}
        efforts = list(reasoning.get("supported_efforts") or [])
        if "none" in efforts and not reasoning.get("mandatory"):
            return {"effort": "none", "exclude": True}
        if "low" in efforts:
            return {"effort": "low", "exclude": True}
        if "minimal" in efforts:
            return {"effort": "minimal", "exclude": True}
        return {"exclude": True}
    return {"exclude": True}


def price_gate_for_model(model: str, rediscovery: Mapping[str, Any]) -> dict[str, Any]:
    for item in rediscovery.get("free_models", []):
        if item.get("id") == model:
            price = item.get("current_price", {})
            return {
                "passed": price.get("input") == "0" and price.get("output") == "0",
                "input": price.get("input"),
                "output": price.get("output"),
            }
    return {"passed": False, "input": None, "output": None}


def synthetic_payload_guard(row: Mapping[str, Any]) -> dict[str, Any]:
    text = json.dumps(row.get("representation", {}), sort_keys=True)
    forbidden = [
        "sk-or-v1-",
        "PCT_Book",
        "reference/",
        "personal",
        "Jonathan",
        "jonat",
        "D:/",
        "D:\\",
        "C:/Users",
        "C:\\Users",
        ".codex",
        "AGENTS.md",
        "FIRST_CODEX_TASK",
    ]
    hits = [item for item in forbidden if item in text]
    return {"passed": not hits, "forbidden_hits": hits}


def output_schema_guard(row: Mapping[str, Any]) -> dict[str, Any]:
    raw = str(row.get("raw_output") or "")
    try:
        data = json.loads(extract_json_object(raw))
    except Exception as exc:
        return {"passed": False, "issues": [f"json_parse_failure:{exc}"]}
    issues = []
    required = {"status", "answer", "source_used", "confidence", "action", "assumptions", "explanation"}
    missing = sorted(required - set(data))
    issues.extend(f"missing_{item}" for item in missing)
    if data.get("status") not in {"TRUE", "FALSE", "UNKNOWN", "CONTRADICTORY", "ANSWER", "ACTION"}:
        issues.append("invalid_status")
    if data.get("answer") is not None and not isinstance(data.get("answer"), str):
        issues.append("invalid_answer")
    if data.get("source_used") not in {"observed_now", "inferred_now", "reconstructed_memory", "hypothetical_future", "mixed", "none"}:
        issues.append("invalid_source_used")
    confidence = data.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        issues.append("invalid_confidence")
    if data.get("action") is not None and not isinstance(data.get("action"), str):
        issues.append("invalid_action")
    if not isinstance(data.get("assumptions"), list) or not all(isinstance(item, str) for item in data.get("assumptions", [])):
        issues.append("invalid_assumptions")
    if not isinstance(data.get("explanation"), list) or not all(isinstance(item, str) for item in data.get("explanation", [])):
        issues.append("invalid_explanation")
    return {"passed": not issues, "issues": issues}


def extract_json_object(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def completed_keys(path: Path) -> set[str]:
    return {
        str(row.get("g2_3_4", {}).get("row_key"))
        for row in read_rows(path)
        if row.get("g2_3_4", {}).get("row_key")
        and row.get("parse_success")
        and not row.get("error")
        and row.get("g2_3_4", {}).get("output_schema_guard", {}).get("passed")
    }


def row_key(model: str, provider: str, regime: str, trial_id: str, condition: str) -> str:
    return "|".join([model, provider, regime, trial_id, condition])


def effective_provider(row: Mapping[str, Any]) -> str:
    response = row.get("model_response", {}) if isinstance(row.get("model_response"), Mapping) else {}
    metadata = response.get("provider_metadata", {}) if isinstance(response, Mapping) else {}
    return str(metadata.get("provider") or "unreported_provider")


def is_rate_limited(row: Mapping[str, Any]) -> bool:
    error_text = str(row.get("error") or "")
    response = row.get("model_response", {}) if isinstance(row.get("model_response"), Mapping) else {}
    metadata = response.get("provider_metadata", {}) if isinstance(response, Mapping) else {}
    return "HTTP 429" in error_text or "rate limit" in error_text.lower() or bool(metadata.get("rate_limited"))


def discover_quota() -> dict[str, Any]:
    try:
        data = get_json(AUTH_KEY_URL)
        key_data = data.get("data", data) if isinstance(data, Mapping) else {}
        return {
            "schema": "nowmind.g2_3_4.free_quota_manifest.v1",
            "created_at": utc_now(),
            "source": AUTH_KEY_URL,
            "status": "success",
            "account_limit": key_data.get("limit") if isinstance(key_data, Mapping) else None,
            "usage": key_data.get("usage") if isinstance(key_data, Mapping) else None,
            "limit_remaining": key_data.get("limit_remaining") if isinstance(key_data, Mapping) else None,
            "rate_limit": key_data.get("rate_limit") if isinstance(key_data, Mapping) else None,
            "is_free_tier": key_data.get("is_free_tier") if isinstance(key_data, Mapping) else None,
        }
    except Exception as exc:
        return {"schema": "nowmind.g2_3_4.free_quota_manifest.v1", "created_at": utc_now(), "status": "failed", "error": str(exc)}


def exact_two_sided_binomial(n_better: int, discordant: int) -> float:
    if discordant == 0:
        return 1.0
    observed = binomial_mass(discordant, n_better)
    return min(1.0, sum(binomial_mass(discordant, value) for value in range(discordant + 1) if binomial_mass(discordant, value) <= observed + 1e-15))


def binomial_mass(total: int, successes: int) -> float:
    import math

    return math.comb(total, successes) * (0.5 ** total)


def model_family(model_id: str) -> str:
    if "qwen" in model_id.lower():
        return "qwen"
    return model_id.split("/", 1)[0]


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
    state.setdefault("schema", "nowmind.g2_3_4.run_state.v1")
    state.setdefault("models", {})
    state["updated_at"] = utc_now()
    state["models"][model] = {"status": status, "detail": detail, "updated_at": utc_now()}
    write_json(RUN_STATE_PATH, state)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())

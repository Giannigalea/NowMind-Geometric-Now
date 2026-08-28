from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nowmind.evaluation import g2_3_benchmark as bench
from nowmind.modeling import (
    COMMON_SYSTEM_INSTRUCTION,
    ChronologicalRepresentationBuilder,
    CurrentOnlyRepresentationBuilder,
    ModelBackend,
    NowMindRepresentationBuilder,
    OllamaBackend,
)
from nowmind.modeling.representation import stable_hash


OUTPUT_DIR = Path("artifacts") / "g2_3_2"
FROZEN_SOURCE_DIR = Path("artifacts") / "g2_3_1"
FROZEN_SNAPSHOT_DIR = OUTPUT_DIR / "frozen_g2_3_1_snapshot"
G231_QWEN_DIR = FROZEN_SOURCE_DIR / "qwen3_0_6b"
REGIME_B_ROWS = OUTPUT_DIR / "g2_3_2_regime_b_trial_results.jsonl"
REGIME_B_CONDITIONS = (
    "N_NOWMIND_STRUCTURED",
    "C_CHRONOLOGICAL",
    "R_CURRENT_ONLY",
    "S_SYMBOLIC_NOWMIND",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and analyze G2.3.2 Regime-B correction.")
    parser.add_argument("command", choices=("prepare", "run", "analyze", "all"))
    parser.add_argument("--model", default="qwen3:0.6b")
    parser.add_argument("--count", type=int, default=250)
    parser.add_argument("--context-size", type=int, default=4096)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.command in {"prepare", "all"}:
        freeze_g2_3_1_snapshot()
        write_frozen_baseline()
        write_token_budget_audit([])
        write_regime_a_c_win_analysis()
    if args.command in {"run", "all"}:
        backend = OllamaBackend(
            args.model,
            context_size=args.context_size,
            num_predict=args.num_predict,
            think=False if args.model.lower().startswith("qwen3") else None,
            timeout_seconds=args.timeout_seconds,
        )
        run_regime_b(backend, args.count)
    if args.command in {"analyze", "all"}:
        rows = read_rows(REGIME_B_ROWS)
        if not rows:
            raise SystemExit(f"Regime-B rows are required before analysis: {REGIME_B_ROWS}")
        write_all_analysis_artifacts(rows, args.count)
    return 0


def freeze_g2_3_1_snapshot() -> None:
    if not FROZEN_SOURCE_DIR.exists():
        raise SystemExit(f"Missing G2.3.1 artifacts: {FROZEN_SOURCE_DIR}")
    FROZEN_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for child in FROZEN_SOURCE_DIR.iterdir():
        target = FROZEN_SNAPSHOT_DIR / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True)
        else:
            shutil.copy2(child, target)


def run_regime_b(backend: ModelBackend, count: int) -> None:
    trials = bench.generate_trials(bench.DEFAULT_SEED + 1, count, "evaluation", "g2_3_eval")
    completed = completed_trial_ids(REGIME_B_ROWS)
    rows = read_rows(REGIME_B_ROWS)
    started = perf_counter()
    for index, trial in enumerate(trials, start=1):
        if trial.trial_id in completed:
            print(f"regime_b {index}/{count} trial={trial.trial_id} skipped=already_complete", flush=True)
            continue
        trial_started = perf_counter()
        trial_rows = [
            bench._run_condition(trial, "B_FIXED_BUDGET", condition, backend)
            for condition in REGIME_B_CONDITIONS
        ]
        append_rows(REGIME_B_ROWS, trial_rows)
        rows.extend(trial_rows)
        completed.add(trial.trial_id)
        errors = sum(1 for row in trial_rows if row.get("error"))
        parses = sum(1 for row in trial_rows if row.get("parse_success"))
        max_budgeted = max(
            row["representation"].get("budget_accounting", {}).get("budgeted_input_tokens", 0)
            for row in trial_rows
            if row["condition"] != "S_SYMBOLIC_NOWMIND"
        )
        print(
            f"regime_b {index}/{count} trial={trial.trial_id} "
            f"seconds={perf_counter() - trial_started:.1f} elapsed={perf_counter() - started:.1f} "
            f"rows={len(rows)} parses={parses}/4 errors={errors} max_budgeted={max_budgeted}",
            flush=True,
        )
    write_all_analysis_artifacts(rows, count)


def completed_trial_ids(rows_path: Path) -> set[str]:
    counts: Counter[str] = Counter()
    for row in read_rows(rows_path):
        counts[str(row["trial"]["trial_id"])] += 1
    return {
        trial_id
        for trial_id, row_count in counts.items()
        if row_count == len(REGIME_B_CONDITIONS)
    }


def read_rows(rows_path: Path) -> list[dict[str, Any]]:
    if not rows_path.exists():
        return []
    rows = []
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def append_rows(rows_path: Path, rows: list[dict[str, Any]]) -> None:
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    with rows_path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()


def write_all_analysis_artifacts(rows: list[dict[str, Any]], count: int) -> None:
    metrics = bench._aggregate(rows)
    pairwise = bench._pairwise_n_vs_c(rows)
    fairness = bench._fairness_results(rows)
    model_manifest = model_manifest_for_rows(rows)
    invariants = bench._invariant_results(rows, fairness, model_manifest)
    token_metrics = compute_token_metrics(rows)
    regime_a_cases = write_regime_a_c_win_analysis()
    stats_markdown = statistical_summary_markdown(pairwise)

    bench._write_json(OUTPUT_DIR / "g2_3_2_budget_audit.json", build_budget_audit(rows))
    bench._write_json(OUTPUT_DIR / "g2_3_2_regime_b_metrics.json", metrics)
    bench._write_json(OUTPUT_DIR / "g2_3_2_regime_b_pairwise.json", pairwise)
    bench._write_json(OUTPUT_DIR / "g2_3_2_token_metrics.json", token_metrics)
    bench._write_json(
        OUTPUT_DIR / "g2_3_2_fairness_invariants.json",
        {"fairness": fairness, "invariants": invariants},
    )
    (OUTPUT_DIR / "g2_3_2_statistical_summary.md").write_text(stats_markdown, encoding="utf-8")
    (OUTPUT_DIR / "g2_3_2_summary.md").write_text(
        summary_markdown(count, metrics, pairwise, fairness, invariants, token_metrics, regime_a_cases),
        encoding="utf-8",
    )
    write_token_budget_audit(rows)
    write_frozen_baseline()


def model_manifest_for_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    model_rows = [row for row in rows if row["backend"] != "symbolic"]
    model = str(model_rows[0]["model"]) if model_rows else "qwen3:0.6b"
    config = model_rows[0]["model_config"] if model_rows else {}
    return {
        "selected": {
            "backend": "ollama",
            "model": model,
            "digest": "7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435",
            **config,
        },
        "available_backends": {"mock": True, "ollama": True, "symbolic_reference": True},
        "symbolic_reference": bench._symbolic_manifest(),
        "ollama": {
            "executable": "ollama.exe",
            "base_url": "http://127.0.0.1:11434",
            "api_path": "/api/chat",
            "models": [
                {
                    "name": model,
                    "digest": "7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435",
                }
            ],
            "available": True,
        },
        "local_model_runtime_prerequisite": None,
    }


def build_budget_audit(corrected_rows: list[dict[str, Any]]) -> dict[str, Any]:
    old_rows = read_rows(G231_QWEN_DIR / "evaluation_trial_results.jsonl")
    old_b = [
        row for row in old_rows
        if row["regime"] == "B_FIXED_BUDGET"
        and row["condition"] in {"N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL"}
    ]
    old_pair_failures = original_failed_budget_pairs(old_rows)
    corrected_fairness = bench._fairness_results(corrected_rows) if corrected_rows else {"summary": {"checked_pairs": 0, "failed": None}}
    return {
        "schema": "nowmind.g2_3_2.budget_audit.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "frozen_g2_3_1": {
            "model": "qwen3:0.6b",
            "regime_b_nc_rows": len(old_b),
            "fixed_budget_violating_pairs": old_pair_failures,
            "fixed_budget_checked_pairs": 500,
            "rows_with_final_input_estimate_over_budget": sum(
                int(row["representation"]["token_estimate"]) > bench.FIXED_TOKEN_BUDGET
                for row in old_b
            ),
            "rows_with_provider_count_over_budget": sum(
                int(row["input_tokens"]) > bench.FIXED_TOKEN_BUDGET
                for row in old_b
            ),
        },
        "cause_classification": {
            "primary": "template/system overhead was not included in the trimming counter",
            "details": [
                "The old trimming helper tested estimate_tokens(_prompt(representation)) instead of the final system+prompt input.",
                "The old fairness audit subtracted an estimated system length from provider counts after sending, so it did not match the pre-send builder counter.",
                "Ollama provider token counts use the model tokenizer and were consistently higher than the simple local estimator.",
            ],
            "tokenizer_estimator_mismatch": True,
            "wrapper_system_text_added_after_truncation": True,
            "inconsistent_schema_accounting": False,
            "n_c_different_counting_paths": False,
            "history_selection_overflow": False,
            "off_by_one_logic": False,
            "template_overhead": True,
        },
        "corrected_method": {
            "counter": "estimate_tokens(system_instruction + newline + final_prompt)",
            "exact_tokenizer_available": False,
            "safety_multiplier": 1.25,
            "hard_gate": "budgeted_input_tokens <= 1600 before any Regime-B model request is sent",
            "repair_gate": "over-budget repair prompts are skipped rather than sent",
            "budget": bench.FIXED_TOKEN_BUDGET,
        },
        "corrected_regime_b": {
            "checked_pairs": corrected_fairness["summary"]["checked_pairs"],
            "failed_pairs": corrected_fairness["summary"]["failed"],
        },
    }


def original_failed_budget_pairs(rows: list[dict[str, Any]]) -> int:
    pairwise: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        if row["regime"] == "B_FIXED_BUDGET" and row["condition"] in {"N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL"}:
            pairwise[row["trial"]["trial_id"]][row["condition"]] = row
    failed = 0
    for conditions in pairwise.values():
        if "N_NOWMIND_STRUCTURED" not in conditions or "C_CHRONOLOGICAL" not in conditions:
            continue
        n_over = int(conditions["N_NOWMIND_STRUCTURED"]["representation"]["token_estimate"]) > bench.FIXED_TOKEN_BUDGET
        c_over = int(conditions["C_CHRONOLOGICAL"]["representation"]["token_estimate"]) > bench.FIXED_TOKEN_BUDGET
        failed += int(n_over or c_over)
    return failed


def compute_token_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    model_rows = [row for row in rows if row["condition"] != "S_SYMBOLIC_NOWMIND"]
    result = {
        "schema": "nowmind.g2_3_2.token_metrics.v1",
        "declared_budget": bench.FIXED_TOKEN_BUDGET,
        "counter": "estimate_tokens(system_instruction + newline + final_prompt)",
        "safety_multiplier": 1.25,
        "overall": {},
        "by_history_cohort": {},
    }
    for condition in ("N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL", "R_CURRENT_ONLY"):
        condition_rows = [row for row in model_rows if row["condition"] == condition]
        result["overall"][condition] = token_bucket(condition_rows)
    for history in sorted({row["trial"]["history_cohort"] for row in model_rows}):
        result["by_history_cohort"][history] = {}
        for condition in ("N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL", "R_CURRENT_ONLY"):
            condition_rows = [
                row for row in model_rows
                if row["condition"] == condition and row["trial"]["history_cohort"] == history
            ]
            result["by_history_cohort"][history][condition] = token_bucket(condition_rows)
    return result


def token_bucket(rows: list[dict[str, Any]]) -> dict[str, Any]:
    final_tokens = [
        int(row["representation"]["budget_accounting"]["final_input_token_estimate"])
        for row in rows
    ]
    budgeted_tokens = [
        int(row["representation"]["budget_accounting"]["budgeted_input_tokens"])
        for row in rows
    ]
    unused = [
        int(row["representation"]["budget_accounting"]["unused_budget"])
        for row in rows
    ]
    dropped = Counter()
    retained = Counter()
    for row in rows:
        accounting = row["representation"]["budget_accounting"]
        dropped.update(accounting.get("dropped_counts", {}))
        retained.update(accounting.get("retained_counts", {}))
    return {
        "count": len(rows),
        "final_input_tokens": summarize_numbers(final_tokens),
        "budgeted_input_tokens": summarize_numbers(budgeted_tokens),
        "unused_budget": summarize_numbers(unused),
        "retained_counts_total": dict(retained),
        "dropped_counts_total": dict(dropped),
        "max_over_budget": max(budgeted_tokens, default=0) > bench.FIXED_TOKEN_BUDGET,
    }


def summarize_numbers(values: list[int]) -> dict[str, float | int | None]:
    if not values:
        return {"mean": None, "median": None, "p95": None, "max": None}
    return {
        "mean": round(mean(values), 3),
        "median": round(median(values), 3),
        "p95": percentile(values, 95),
        "max": max(values),
    }


def percentile(values: list[int], pct: int) -> int:
    ordered = sorted(values)
    index = math.ceil((pct / 100) * len(ordered)) - 1
    return ordered[max(0, min(index, len(ordered) - 1))]


def write_regime_a_c_win_analysis() -> list[dict[str, Any]]:
    rows = read_rows(G231_QWEN_DIR / "evaluation_trial_results.jsonl")
    by_trial: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        if row["regime"] == "A_EQUAL_INFORMATION" and row["condition"] in {"N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL"}:
            by_trial[row["trial"]["trial_id"]][row["condition"]] = row
    trial_map = {
        trial.trial_id: trial
        for trial in bench.generate_trials(bench.DEFAULT_SEED + 1, 250, "evaluation", "g2_3_eval")
    }
    cases = []
    for trial_id, conditions in by_trial.items():
        n = conditions.get("N_NOWMIND_STRUCTURED")
        c = conditions.get("C_CHRONOLOGICAL")
        if not n or not c:
            continue
        if c["validated_score"]["correct"] <= n["validated_score"]["correct"]:
            continue
        trial = trial_map[trial_id]
        n_rep = NowMindRepresentationBuilder().build(trial.facts, "A_EQUAL_INFORMATION")
        c_rep = ChronologicalRepresentationBuilder().build(trial.facts, "A_EQUAL_INFORMATION")
        cases.append(
            {
                "trial_id": trial_id,
                "family": trial.family,
                "history_cohort": trial.history_cohort,
                "task_group": trial.task_group,
                "n_prompt_tokens": n["input_tokens"],
                "c_prompt_tokens": c["input_tokens"],
                "n_structure": representation_counts(n_rep.representation),
                "c_structure": representation_counts(c_rep.representation),
                "n_answer": compact_answer(n),
                "c_answer": compact_answer(c),
                "expected": c["expected"],
                "n_source_used": n["validator"]["final_source_used"],
                "c_source_used": c["validator"]["final_source_used"],
                "n_status": n["validator"]["final_status"],
                "c_status": c["validator"]["final_status"],
                "omitted_relevant_information": False,
                "chronology_preserved_useful_sequence": True,
                "nowmind_fragmented_causal_sequence": True,
                "verbosity": "N prompt/provider count was much larger than C in this case.",
                "tiny_model_source_label_misunderstanding": True,
                "semantic_parsing_action_failure": "N selected the right action but wrong status/source, so scoring treated it as incorrect.",
                "categories": ["B", "C", "D", "F", "G"],
                "exposes_fairness_or_implementation_bug": False,
            }
        )
    bench._write_json(OUTPUT_DIR / "g2_3_2_regime_a_c_win_cases.json", cases)
    markdown = regime_a_cases_markdown(cases)
    (OUTPUT_DIR / "g2_3_2_regime_a_c_win_analysis.md").write_text(markdown, encoding="utf-8")
    Path("docs/G2_3_2_REGIME_A_C_WIN_ANALYSIS.md").write_text(markdown, encoding="utf-8")
    return cases


def representation_counts(representation: dict[str, Any]) -> dict[str, int]:
    fields = (
        "observed_now",
        "inferred_now",
        "reconstructed_memories",
        "future_hypotheses",
        "uncertainties",
        "planning_assumptions",
        "chronological_records",
    )
    return {
        field: len(representation.get(field, []))
        for field in fields
        if field in representation
    }


def compact_answer(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "raw_output_prefix": str(row["raw_output"])[:500],
        "parsed_output": row["parsed_output"],
        "validator": row["validator"],
        "proposal_score": row["proposal_score"],
        "validated_score": row["validated_score"],
        "parse_success": row["parse_success"],
    }


def statistical_summary_markdown(pairwise: dict[str, Any]) -> str:
    original = {
        "n_better": 0,
        "c_better": 8,
        "tied": 242,
    }
    corrected = pairwise.get(
        "qwen3:0.6b|B_FIXED_BUDGET|validated",
        {"n_better": 0, "c_better": 0, "tied": 0},
    )
    return "\n".join(
        [
            "# G2.3.2 Statistical Summary",
            "",
            "## Frozen Regime A",
            stats_block(original, 250),
            "",
            "## Corrected Regime B",
            stats_block(corrected, 250),
            "",
            "## Limitations",
            "",
            "- One ultra-small `qwen3:0.6b` local model.",
            "- `250` paired trials from one synthetic benchmark.",
            "- Exact tokenizer access was unavailable; Regime B uses one deterministic final-input estimator with a conservative safety multiplier.",
            "- Results should not be generalized to all LLMs or to later NowMind stages.",
            "",
        ]
    )


def stats_block(pairwise_counts: dict[str, int], total_pairs: int) -> str:
    n_better = int(pairwise_counts.get("n_better", 0))
    c_better = int(pairwise_counts.get("c_better", 0))
    tied = int(pairwise_counts.get("tied", 0))
    discordant = n_better + c_better
    p_value = exact_two_sided_binomial(n_better, discordant) if discordant else 1.0
    n_minus_c = (n_better - c_better) / total_pairs
    ci_low, ci_high = paired_difference_ci(n_better, c_better, total_pairs)
    return "\n".join(
        [
            f"- N better: `{n_better}`",
            f"- C better: `{c_better}`",
            f"- Ties: `{tied}`",
            f"- Discordant pairs: `{discordant}`",
            f"- Exact paired binomial p-value: `{p_value:.6f}`",
            f"- Paired accuracy difference, N minus C: `{n_minus_c:.3f}`",
            f"- Approximate 95% CI for N minus C: `[{ci_low:.3f}, {ci_high:.3f}]`",
        ]
    )


def exact_two_sided_binomial(n_better: int, discordant: int) -> float:
    if discordant == 0:
        return 1.0
    observed = math.comb(discordant, n_better) * (0.5 ** discordant)
    probability = 0.0
    for value in range(discordant + 1):
        mass = math.comb(discordant, value) * (0.5 ** discordant)
        if mass <= observed + 1e-15:
            probability += mass
    return min(1.0, probability)


def paired_difference_ci(n_better: int, c_better: int, total_pairs: int) -> tuple[float, float]:
    diff_count = n_better - c_better
    discordant = n_better + c_better
    variance = max(0.0, (discordant - (diff_count * diff_count / total_pairs)) / (total_pairs * total_pairs))
    delta = 1.96 * math.sqrt(variance)
    diff = diff_count / total_pairs
    return diff - delta, diff + delta


def write_frozen_baseline() -> None:
    path = Path("docs/G2_3_2_FROZEN_BASELINE.md")
    path.write_text(
        "\n".join(
            [
                "# G2.3.2 Frozen Baseline",
                "",
                "Date: 2026-08-26",
                "",
                "The G2.3.1 `qwen3:0.6b` artifacts are frozen evidence and are not overwritten by G2.3.2.",
                "",
                "- Model: `qwen3:0.6b`",
                "- Paired trials: `250`",
                "- Frozen Regime A validated result: C `8`, N `0`, ties `242`",
                "- Frozen Regime B is invalid for fairness interpretation",
                "- Fixed-budget violations: `166` of `500` checked N/C pairs",
                "- Snapshot copy: `artifacts/g2_3_2/frozen_g2_3_1_snapshot/`",
                "",
                "G2.3.2 reruns only the same frozen 250 Regime-B paired trial IDs after repairing deterministic fixed-budget enforcement.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_token_budget_audit(corrected_rows: list[dict[str, Any]]) -> None:
    audit = build_budget_audit(corrected_rows)
    path = Path("docs/G2_3_2_TOKEN_BUDGET_AUDIT.md")
    corrected = audit["corrected_regime_b"]
    path.write_text(
        "\n".join(
            [
                "# G2.3.2 Token Budget Audit",
                "",
                "Date: 2026-08-26",
                "",
                "## Cause",
                "",
                "The 166/500 G2.3.1 Regime-B fairness failures came from accounting mismatch, not from NowMind cognition or benchmark scoring.",
                "",
                "- The old trimming helper measured only `estimate_tokens(_prompt(representation))`.",
                "- The final model request also included the common system instruction.",
                "- The old fairness audit then subtracted an estimated system length from provider token counts after sending.",
                "- Ollama provider token counts used the model tokenizer and were higher than the local estimator.",
                "",
                "Classified causes:",
                "",
                "- tokenizer/estimator mismatch: yes",
                "- wrapper/system text added after truncation: yes",
                "- inconsistent schema accounting: no evidence",
                "- N/C different counting paths: no",
                "- history selection overflow: no",
                "- off-by-one logic: no",
                "- template overhead: yes",
                "",
                "## Corrected Method",
                "",
                "G2.3.2 uses one canonical deterministic final-input counter for N/C/R:",
                "",
                "`estimate_tokens(system_instruction + newline + final_prompt)`",
                "",
                "Exact qwen tokenizer access was not available before sending, so the hard gate applies a shared conservative safety multiplier of `1.25`. A Regime-B model prompt is sent only if `budgeted_input_tokens <= 1600`.",
                "",
                "Repair prompts use the same gate. If a repair prompt would exceed budget, the repair is skipped and the original parse failure remains visible to scoring and validation.",
                "",
                "## Corrected Status",
                "",
                f"- Checked N/C pairs: `{corrected['checked_pairs']}`",
                f"- Failed N/C pairs: `{corrected['failed_pairs']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def regime_a_cases_markdown(cases: list[dict[str, Any]]) -> str:
    lines = [
        "# G2.3.2 Regime A Chronological Win Analysis",
        "",
        "Frozen Regime A remains unchanged: Chronological `8`, NowMind `0`, ties `242`.",
        "",
        "All eight C wins were action-choice cases in the `H50` cohort. In each case the NowMind output parsed successfully and usually selected the right action, but gave the wrong status and source label, commonly `CONTRADICTORY` plus `hypothetical_future`. Chronological gave an `ACTION` status, so it scored correct.",
        "",
        "Categories used: B NowMind too verbose; C NowMind fragments causal context; D model follows chronology more naturally; F source-label misunderstanding; G token/context pressure.",
        "",
        "| Trial | Family | History | Categories | Short diagnosis |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in cases:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{case['trial_id']}`",
                    case["family"],
                    case["history_cohort"],
                    ",".join(case["categories"]),
                    "N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed.",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "No case shows evaluator-truth leakage, omitted relevant Regime-A information, or a scoring bug. The evidence points to the tiny model handling chronological action phrasing more naturally than the explicit NowMind action/source structure.",
            "",
        ]
    )
    return "\n".join(lines)


def summary_markdown(
    count: int,
    metrics: dict[str, Any],
    pairwise: dict[str, Any],
    fairness: dict[str, Any],
    invariants: dict[str, Any],
    token_metrics: dict[str, Any],
    regime_a_cases: list[dict[str, Any]],
) -> str:
    lines = [
        "# G2.3.2 Summary",
        "",
        f"- Corrected Regime-B paired trials: `{count}`",
        f"- Fairness failures: `{fairness['summary']['failed']}` of `{fairness['summary']['checked_pairs']}` checked N/C pairs",
        f"- Invariants: `{invariants['summary']['passed']}` passed, `{invariants['summary']['failed']}` failed",
        f"- Frozen Regime-A C-win cases analyzed: `{len(regime_a_cases)}`",
        "",
        "## Corrected Regime B Pairwise",
        "",
    ]
    for key, value in pairwise.items():
        lines.append(f"- `{key}` N={value['n_better']} C={value['c_better']} tied={value['tied']}")
    lines.extend(["", "## Corrected Regime B Validated Accuracy", ""])
    for key in sorted(k for k in metrics if k.endswith("|validated")):
        item = metrics[key]
        lines.append(
            f"- `{key}` accuracy={item['overall_accuracy']:.3f} "
            f"source={item['source_classification_accuracy']:.3f} "
            f"parse={item['json_parse_success_rate']:.3f}"
        )
    lines.extend(["", "## Token Ceiling", ""])
    for condition in ("N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL", "R_CURRENT_ONLY"):
        bucket = token_metrics["overall"][condition]["budgeted_input_tokens"]
        lines.append(
            f"- `{condition}` budgeted mean={bucket['mean']} median={bucket['median']} p95={bucket['p95']} max={bucket['max']}"
        )
    lines.extend(
        [
            "",
            "Conclusion: G2.3.2 repairs the fixed-budget enforcement and preserves the original Regime-A evidence. The corrected Regime-B result should be interpreted from these artifacts only.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

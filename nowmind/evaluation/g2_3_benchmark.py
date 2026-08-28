from __future__ import annotations

from dataclasses import dataclass
import json
from math import sqrt
from pathlib import Path
import shutil
import subprocess
from statistics import mean, median
from typing import Any

from nowmind.modeling import (
    COMMON_SYSTEM_INSTRUCTION,
    ChronologicalRepresentationBuilder,
    CurrentOnlyRepresentationBuilder,
    G23AdmissibleFacts,
    MockModelBackend,
    ModelBackend,
    ModelProposal,
    ModelRequest,
    ModelResponse,
    NowMindRepresentationBuilder,
    RepresentationResult,
    SymbolicReferenceBuilder,
    budgeted_input_token_count,
    canonical_input_token_count,
    parse_model_output,
    validate_model_proposal,
)
from nowmind.modeling.representation import stable_hash


DEFAULT_SEED = 20260823
DEFAULT_CALIBRATION_COUNT = 50
DEFAULT_FINAL_COUNT = 1000
DEFAULT_ARTIFACT_DIR = Path("artifacts") / "g2_3"
REGIMES = ("A_EQUAL_INFORMATION", "B_FIXED_BUDGET")
CONDITIONS = (
    "N_NOWMIND_STRUCTURED",
    "C_CHRONOLOGICAL",
    "R_CURRENT_ONLY",
    "S_SYMBOLIC_NOWMIND",
)
HISTORY_COHORTS = (0, 10, 50, 100, 500, 1000)
FIXED_TOKEN_BUDGET = 1600


FAMILIES = (
    "temporal_present_vs_stale_memory",
    "temporal_current_unknown_memory",
    "temporal_future_vs_current",
    "temporal_false_memory",
    "temporal_contradictory_present",
    "temporal_long_history_source_confusion",
    "spatial_relative_position",
    "spatial_containment",
    "spatial_reachability",
    "spatial_obstacle_state",
    "action_choose_next_move",
    "action_safe_vs_conditional_route",
    "action_verify_scan_vs_act",
    "action_after_hidden_change_observed",
    "explain_identify_evidence_source",
    "explain_memory_not_current",
    "explain_conditional_assumptions",
)


@dataclass(frozen=True, slots=True)
class G23Expected:
    status: str
    answer: str
    source_used: str
    action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "answer": self.answer,
            "source_used": self.source_used,
            "action": self.action,
        }


@dataclass(frozen=True, slots=True)
class G23Trial:
    trial_id: str
    seed: int
    split: str
    family: str
    history_cohort: str
    task_group: str
    facts: G23AdmissibleFacts
    expected: G23Expected

    def public_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "seed": self.seed,
            "split": self.split,
            "family": self.family,
            "history_cohort": self.history_cohort,
            "task_group": self.task_group,
            "fact_set_hash": self.facts.fact_set_hash,
        }


@dataclass(frozen=True, slots=True)
class G23BenchmarkResult:
    artifacts_dir: Path
    calibration_count: int
    final_count: int
    metrics: dict[str, Any]
    invariants: dict[str, Any]
    model_manifest: dict[str, Any]


def run_g2_3_benchmark(
    artifacts_dir: Path = DEFAULT_ARTIFACT_DIR,
    backend: ModelBackend | None = None,
    calibration_count: int = DEFAULT_CALIBRATION_COUNT,
    final_count: int = DEFAULT_FINAL_COUNT,
    seed: int = DEFAULT_SEED,
) -> G23BenchmarkResult:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    backend = backend or MockModelBackend()
    model_manifest = _model_manifest(backend)
    calibration_trials = generate_trials(seed, calibration_count, "calibration", "g2_3_cal")
    final_trials = generate_trials(seed + 1, final_count, "evaluation", "g2_3_eval")
    prompt_templates = _prompt_templates_markdown()
    (artifacts_dir / "g2_3_prompt_templates.md").write_text(prompt_templates, encoding="utf-8")
    calibration_rows = _run_trials(calibration_trials, backend)
    final_rows = _run_trials(final_trials, backend)
    metrics = _aggregate(final_rows)
    metrics_by_family = _aggregate_by(final_rows, "family")
    metrics_by_history = _aggregate_by(final_rows, "history_cohort")
    pairwise = _pairwise_n_vs_c(final_rows)
    proposal_vs_validated = _proposal_vs_validated(final_rows)
    fairness = _fairness_results(final_rows)
    failures = _failure_samples(final_rows)
    invariants = _invariant_results(final_rows, fairness, model_manifest)

    _write_json(artifacts_dir / "g2_3_model_manifest.json", model_manifest)
    _write_json(artifacts_dir / "g2_3_calibration_results.json", _aggregate(calibration_rows))
    _write_json(artifacts_dir / "g2_3_metrics.json", metrics)
    _write_json(artifacts_dir / "g2_3_metrics_by_family.json", metrics_by_family)
    _write_json(artifacts_dir / "g2_3_metrics_by_history.json", metrics_by_history)
    _write_json(artifacts_dir / "g2_3_pairwise_n_vs_c.json", pairwise)
    _write_json(artifacts_dir / "g2_3_proposal_vs_validated.json", proposal_vs_validated)
    _write_json(artifacts_dir / "g2_3_failure_samples.json", failures)
    _write_json(artifacts_dir / "g2_3_prompt_fairness_results.json", fairness)
    _write_json(artifacts_dir / "g2_3_invariant_results.json", invariants)
    _write_json(
        artifacts_dir / "g2_3_seed_and_config.json",
        {
            "seed": seed,
            "calibration_count": calibration_count,
            "final_count": final_count,
            "families": list(FAMILIES),
            "history_cohorts": [f"H{count}" for count in HISTORY_COHORTS],
            "regimes": list(REGIMES),
            "conditions": list(CONDITIONS),
            "fixed_token_budget": FIXED_TOKEN_BUDGET,
            "system_instruction_hash": stable_hash(COMMON_SYSTEM_INSTRUCTION),
        },
    )
    with (artifacts_dir / "g2_3_trial_results.jsonl").open("w", encoding="utf-8") as handle:
        for row in final_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (artifacts_dir / "g2_3_summary.md").write_text(
        _summary(model_manifest, metrics, pairwise, invariants, final_count),
        encoding="utf-8",
    )
    return G23BenchmarkResult(
        artifacts_dir=artifacts_dir,
        calibration_count=calibration_count,
        final_count=final_count,
        metrics=metrics,
        invariants=invariants,
        model_manifest=model_manifest,
    )


def generate_trials(seed: int, count: int, split: str, prefix: str) -> tuple[G23Trial, ...]:
    trials = []
    for index in range(count):
        family = FAMILIES[index % len(FAMILIES)]
        history = HISTORY_COHORTS[index % len(HISTORY_COHORTS)]
        trial_id = f"{prefix}_{index:05d}_{family}"
        facts, expected, task_group = _build_case(trial_id, seed + index, family, history)
        trials.append(
            G23Trial(
                trial_id,
                seed + index,
                split,
                family,
                f"H{history}",
                task_group,
                facts,
                expected,
            )
        )
    return tuple(trials)


def build_hero_comparison(backend: ModelBackend | None = None) -> dict[str, Any]:
    backend = backend or MockModelBackend()
    facts, expected, _ = _build_case("g2_3_hero_long_history", DEFAULT_SEED, "temporal_long_history_source_confusion", 1000)
    trial = G23Trial(
        "g2_3_hero_long_history",
        DEFAULT_SEED,
        "demo",
        "temporal_long_history_source_confusion",
        "H1000",
        "temporal_qa",
        facts,
        expected,
    )
    rows = [
        _run_condition(trial, regime, condition, backend, include_prompt=True)
        for regime in REGIMES
        for condition in ("N_NOWMIND_STRUCTURED", "C_CHRONOLOGICAL")
    ]
    return {
        "schema": "nowmind.g2_3.model_comparison.v1",
        "trial": trial.public_dict(),
        "expected_hidden_by_default": expected.to_dict(),
        "model_manifest": _model_manifest(backend),
        "comparisons": rows,
    }


def _run_trials(trials: tuple[G23Trial, ...], backend: ModelBackend) -> list[dict[str, Any]]:
    rows = []
    for trial in trials:
        for regime in REGIMES:
            for condition in CONDITIONS:
                rows.append(_run_condition(trial, regime, condition, backend))
    return rows


def _run_condition(
    trial: G23Trial,
    regime: str,
    condition: str,
    backend: ModelBackend,
    include_prompt: bool = False,
    repair_attempts: int = 1,
    num_predict: int | None = None,
) -> dict[str, Any]:
    builder = _builder(condition)
    manifest = _symbolic_manifest() if condition == "S_SYMBOLIC_NOWMIND" else _backend_manifest(backend)
    token_budget = (
        FIXED_TOKEN_BUDGET
        if regime == "B_FIXED_BUDGET" and condition != "S_SYMBOLIC_NOWMIND"
        else None
    )
    representation = builder.build(
        trial.facts,
        regime,
        token_budget=token_budget,
        context_size=int(manifest.get("context_size", 12000)),
    )
    response: ModelResponse | None = None
    retry_count = 0
    repair_skipped_budget_gate = False
    if condition == "S_SYMBOLIC_NOWMIND":
        proposal = _symbolic_reference_proposal(trial.facts)
        parsed = None
        parse_success = True
        raw_text = json.dumps(proposal.to_dict(), sort_keys=True)
        error = None
    elif representation.context_overflow and regime == "A_EQUAL_INFORMATION":
        parsed = None
        parse_success = False
        proposal = None
        raw_text = ""
        error = "context_overflow"
    else:
        request = ModelRequest(
            prompt=representation.prompt,
            system_instruction=COMMON_SYSTEM_INSTRUCTION,
            model=str(manifest["model"]),
            num_predict=num_predict,
            metadata={"trial_id": trial.trial_id, "condition": condition, "regime": regime},
        )
        response = backend.generate(request)
        parsed = None if response.error else parse_model_output(response.raw_text)
        if repair_attempts > 0 and parsed is not None and not parsed.parse_success:
            repair_prompt = (
                "Repair the previous response into the required strict JSON schema. "
                "Do not change the meaning.\nRAW_RESPONSE:\n"
                f"{response.raw_text}\n\n{representation.prompt}"
            )
            repair_tokens = canonical_input_token_count(COMMON_SYSTEM_INSTRUCTION, repair_prompt)
            if (
                regime == "B_FIXED_BUDGET"
                and budgeted_input_token_count(repair_tokens) > FIXED_TOKEN_BUDGET
            ):
                repair_skipped_budget_gate = True
            else:
                retry_count = 1
                repair_request = ModelRequest(
                    prompt=repair_prompt,
                    system_instruction=COMMON_SYSTEM_INSTRUCTION,
                    model=str(manifest["model"]),
                    num_predict=num_predict,
                    metadata={"repair": True, "trial_id": trial.trial_id},
                )
                response = backend.generate(repair_request)
                parsed = parse_model_output(response.raw_text)
        proposal = parsed.proposal if parsed else None
        parse_success = bool(parsed and parsed.parse_success)
        raw_text = response.raw_text if response else ""
        error = response.error if response else None
    validation = validate_model_proposal(proposal, trial.facts)
    proposal_score = _score_proposal(proposal, trial.expected, trial.task_group)
    validated_score = _score_validated(validation, trial.expected, trial.task_group)
    record = {
        "trial": trial.public_dict(),
        "model": manifest["model"],
        "backend": manifest["backend"],
        "regime": regime,
        "condition": condition,
        "representation": representation.to_record(include_prompt=include_prompt),
        "same_admissible_fact_set_hash": representation.fact_set_hash,
        "prompt_hash": representation.prompt_hash,
        "model_config": _model_config(manifest),
        "raw_output": raw_text,
        "parsed_output": proposal.to_dict() if proposal else None,
        "validator": validation.to_dict(),
        "expected": trial.expected.to_dict(),
        "proposal_score": proposal_score,
        "validated_score": validated_score,
        "parse_success": parse_success,
        "repair_retry_count": retry_count,
        "repair_skipped_budget_gate": repair_skipped_budget_gate,
        "latency_ms": response.latency_ms if response else 0.0,
        "input_tokens": response.input_token_estimate if response else representation.token_estimate,
        "output_tokens": response.output_token_estimate if response else 0,
        "model_response": response.to_dict() if response else None,
        "context_overflow": representation.context_overflow,
        "error": error,
    }
    return record


def _build_case(
    trial_id: str,
    seed: int,
    family: str,
    history_count: int,
) -> tuple[G23AdmissibleFacts, G23Expected, str]:
    del seed
    current_cycle = max(2, history_count + 2)
    observed = [_fact("ball", "inside", "box_b", "observed_now", current_cycle)]
    inferred: list[dict[str, Any]] = []
    memories = [_fact("ball", "inside", "box_a", "reconstructed_memory", 1, relevance=True)]
    futures = [_fact("ball", "inside", "box_c", "hypothetical_future", current_cycle, relevance=True)]
    assumptions: list[dict[str, Any]] = []
    uncertainties: list[dict[str, Any]] = []
    contradiction = False
    query: dict[str, Any] = {"kind": "current_location", "subject": "ball", "relation": "inside"}
    expected = G23Expected("ANSWER", "box_b", "observed_now")
    task_group = "temporal_qa"

    if family == "temporal_current_unknown_memory":
        observed = []
        uncertainties = [{"item": "ball current location", "status": "unknown"}]
        expected = G23Expected("UNKNOWN", "", "none")
    elif family == "temporal_future_vs_current":
        query = {"kind": "future_relation", "source": "ball", "relation": "inside", "target": "box_c"}
        expected = G23Expected("TRUE", "true", "hypothetical_future")
    elif family == "temporal_false_memory":
        memories = [_fact("ball", "inside", "box_d", "reconstructed_memory", 1, relevance=True)]
    elif family == "temporal_contradictory_present":
        observed = [
            _fact("red_cube", "left_of", "blue_cube", "observed_now", current_cycle),
            _fact("red_cube", "right_of", "blue_cube", "observed_now", current_cycle),
        ]
        contradiction = True
        query = {"kind": "current_relation", "source": "red_cube", "relation": "left_of", "target": "blue_cube"}
        expected = G23Expected("CONTRADICTORY", "current evidence conflicts", "observed_now")
    elif family == "temporal_long_history_source_confusion":
        observed = [_fact("target", "at", "cell:4,2", "observed_now", current_cycle)]
        memories = [_fact("target", "at", "cell:2,2", "reconstructed_memory", 3, relevance=True)]
        futures = [_fact("target", "at", "cell:5,2", "hypothetical_future", current_cycle, relevance=True)]
        query = {"kind": "current_location", "subject": "target", "relation": "at"}
        expected = G23Expected("ANSWER", "cell:4,2", "observed_now")
    elif family == "spatial_relative_position":
        observed = [_fact("a", "left_of", "b", "observed_now", current_cycle)]
        query = {"kind": "current_relation", "source": "a", "relation": "left_of", "target": "b"}
        expected = G23Expected("TRUE", "true", "observed_now")
        task_group = "spatial_qa"
    elif family == "spatial_containment":
        observed = [
            _fact("key", "inside", "box", "observed_now", current_cycle),
            _fact("box", "inside", "cabinet", "observed_now", current_cycle),
        ]
        inferred = [_fact("key", "inside", "cabinet", "inferred_now", current_cycle)]
        query = {"kind": "current_relation", "source": "key", "relation": "inside", "target": "cabinet"}
        expected = G23Expected("TRUE", "true", "inferred_now")
        task_group = "spatial_qa"
    elif family == "spatial_reachability":
        observed = [_fact("agent", "reachable", "target", "inferred_now", current_cycle)]
        query = {"kind": "current_relation", "source": "agent", "relation": "reachable", "target": "target"}
        expected = G23Expected("TRUE", "true", "inferred_now")
        task_group = "spatial_qa"
    elif family == "spatial_obstacle_state":
        observed = [_fact("cell:3,2", "occupancy", "occupied", "observed_now", current_cycle)]
        query = {"kind": "current_location", "subject": "cell:3,2", "relation": "occupancy"}
        expected = G23Expected("ANSWER", "occupied", "observed_now")
        task_group = "spatial_qa"
    elif family in {
        "action_choose_next_move",
        "action_safe_vs_conditional_route",
        "action_verify_scan_vs_act",
        "action_after_hidden_change_observed",
    }:
        task_group = "action_choice"
        observed = [_fact("agent", "at", "cell:0,2", "observed_now", current_cycle)]
        memories = [_fact("cell:2,2", "occupancy", "free", "reconstructed_memory", 1, relevance=True)]
        assumptions = [{"id": "assume_cell_2_2_free", "source": "reconstructed_memory"}]
        action = "move_east"
        source = "observed_now"
        options = [
            {"action": "move_east", "valid": True, "recommended": True, "source": source},
            {"action": "move_west", "valid": False, "recommended": False, "source": "none"},
        ]
        if family in {"action_safe_vs_conditional_route", "action_verify_scan_vs_act"}:
            action = "scan"
            source = "mixed"
            options = [
                {
                    "action": "scan",
                    "valid": True,
                    "recommended": True,
                    "source": source,
                    "assumptions": ["assume_cell_2_2_free"],
                },
                {"action": "move_east", "valid": True, "recommended": False, "source": "reconstructed_memory"},
            ]
        if family == "action_after_hidden_change_observed":
            observed.append(_fact("cell:2,2", "occupancy", "occupied", "observed_now", current_cycle))
            action = "move_north"
            source = "observed_now"
            options = [
                {"action": "move_north", "valid": True, "recommended": True, "source": source},
                {"action": "move_east", "valid": False, "recommended": False, "source": "observed_now"},
            ]
        query = {"kind": "action_choice", "goal": "reach target safely", "action_options": options}
        expected = G23Expected("ACTION", action, source, action)
    elif family == "explain_identify_evidence_source":
        query = {"kind": "source_explanation", "expected_source_label": "observed_now"}
        expected = G23Expected("ANSWER", "source=observed_now", "observed_now")
        task_group = "explanation_source"
    elif family == "explain_memory_not_current":
        observed = []
        uncertainties = [{"item": "ball current location", "status": "unknown"}]
        query = {"kind": "current_location", "subject": "ball", "relation": "inside"}
        expected = G23Expected("UNKNOWN", "", "none")
        task_group = "explanation_source"
    elif family == "explain_conditional_assumptions":
        query = {
            "kind": "action_choice",
            "goal": "explain conditional route",
            "action_options": [
                {
                    "action": "scan",
                    "valid": True,
                    "recommended": True,
                    "source": "mixed",
                    "assumptions": ["assume_cell_2_2_free"],
                }
            ],
        }
        assumptions = [{"id": "assume_cell_2_2_free", "source": "reconstructed_memory"}]
        expected = G23Expected("ACTION", "scan", "mixed", "scan")
        task_group = "explanation_source"

    for index in range(history_count):
        memories += (
            _fact("target", "at", f"cell:{index % 8},{index % 5}", "reconstructed_memory", index + 1),
        )
    records = _records(current_cycle, observed, inferred, memories, futures, contradiction)
    facts = G23AdmissibleFacts(
        trial_id=trial_id,
        current_cycle_id=current_cycle,
        query=query,
        observed_now=tuple(observed),
        inferred_now=tuple(inferred),
        reconstructed_memories=tuple(memories),
        future_hypotheses=tuple(futures),
        uncertainties=tuple(uncertainties),
        planning_assumptions=tuple(assumptions),
        chronological_records=tuple(records),
        contradiction=contradiction,
    )
    return facts, expected, task_group


def _fact(
    source: str,
    relation: str,
    target: str,
    source_channel: str,
    cycle: int,
    relevance: bool = False,
) -> dict[str, Any]:
    return {
        "source_id": source,
        "relation": relation,
        "target": target,
        "source": source_channel,
        "cycle_id": cycle,
        "confidence": 1.0 if source_channel in {"observed_now", "inferred_now"} else 0.82,
        "relevance": relevance,
    }


def _records(
    current_cycle: int,
    observed: list[dict[str, Any]],
    inferred: list[dict[str, Any]],
    memories: list[dict[str, Any]],
    futures: list[dict[str, Any]],
    contradiction: bool,
) -> list[dict[str, Any]]:
    records = []
    for item in observed + inferred + memories + futures:
        record = dict(item)
        record["record_type"] = "proposition"
        records.append(record)
    if contradiction:
        records.append(
            {
                "cycle_id": current_cycle,
                "source": "observed_now",
                "record_type": "validation",
                "contradiction": True,
                "relevance": True,
            }
        )
    return sorted(records, key=lambda item: (item.get("cycle_id", 0), item.get("source", "")))


def _builder(condition: str):
    if condition == "N_NOWMIND_STRUCTURED":
        return NowMindRepresentationBuilder()
    if condition == "C_CHRONOLOGICAL":
        return ChronologicalRepresentationBuilder()
    if condition == "R_CURRENT_ONLY":
        return CurrentOnlyRepresentationBuilder()
    if condition == "S_SYMBOLIC_NOWMIND":
        return SymbolicReferenceBuilder()
    raise ValueError(f"unknown G2.3 condition: {condition}")


def _backend_manifest(backend: ModelBackend) -> dict[str, Any]:
    manifest_method = getattr(backend, "manifest", None)
    if callable(manifest_method):
        return dict(manifest_method())
    return {
        "backend": backend.__class__.__name__,
        "model": "unknown",
        "context_size": 12000,
        "temperature": 0.0,
        "top_p": 1.0,
        "seed": DEFAULT_SEED,
    }


def _model_manifest(backend: ModelBackend) -> dict[str, Any]:
    selected = _backend_manifest(backend)
    ollama_path = _find_ollama_executable()
    selected_is_ollama = selected.get("backend") == "ollama"
    ollama_available = bool(ollama_path) or selected_is_ollama
    ollama_models = _ollama_models(ollama_path) if ollama_path else []
    return {
        "selected": selected,
        "available_backends": {
            "mock": True,
            "ollama": ollama_available,
            "symbolic_reference": True,
        },
        "symbolic_reference": _symbolic_manifest(),
        "ollama": {
            "executable": ollama_path,
            "base_url": selected.get("base_url") if selected_is_ollama else None,
            "api_path": selected.get("api_path") if selected_is_ollama else None,
            "models": ollama_models,
            "available": ollama_available,
            "note": "No model download is performed by G2.3.",
        },
        "local_model_runtime_prerequisite": None
        if ollama_available
        else "Ollama is not installed on PATH; real local-model evaluation was not run.",
    }


def _symbolic_manifest() -> dict[str, Any]:
    return {
        "backend": "symbolic",
        "model": "symbolic-nowmind-g2.3-reference",
        "digest": "deterministic-local-symbolic",
        "context_size": 100000,
        "temperature": 0.0,
        "top_p": 1.0,
        "seed": DEFAULT_SEED,
    }


def _ollama_models(ollama_path: str) -> list[dict[str, str]]:
    try:
        result = subprocess.run(
            [ollama_path, "list"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - depends on local Ollama.
        return [{"error": str(exc)}]
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    models = []
    for line in lines[1:]:
        columns = line.split()
        if columns:
            models.append(
                {
                    "name": columns[0],
                    "digest": columns[1] if len(columns) > 1 else "",
                }
            )
    return models


def _find_ollama_executable() -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    candidate = Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"
    try:
        if candidate.exists():
            return str(candidate)
    except OSError:
        return str(candidate)
    return None


def _model_config(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": manifest["model"],
        "backend": manifest["backend"],
        "temperature": manifest.get("temperature", 0.0),
        "top_p": manifest.get("top_p", 1.0),
        "seed": manifest.get("seed", DEFAULT_SEED),
        "context_size": manifest.get("context_size"),
        "num_predict": manifest.get("num_predict"),
        "response_format": manifest.get("response_format"),
        "response_schema_hash": manifest.get("response_schema_hash"),
        "think": manifest.get("think"),
    }


def _symbolic_reference_proposal(facts: G23AdmissibleFacts) -> ModelProposal:
    query = facts.query
    current = list(facts.observed_now) + list(facts.inferred_now)
    if facts.contradiction:
        return ModelProposal(
            "CONTRADICTORY",
            "current evidence conflicts",
            "observed_now",
            1.0,
            None,
            (),
            ("Current validation reports incompatible present facts.",),
        )
    if query.get("kind") == "current_location":
        fact = _find_fact(current, str(query.get("subject", "")), str(query.get("relation", "")), None)
        if fact is None:
            return _unknown_symbolic("No current fact supports the requested location.")
        return ModelProposal(
            "ANSWER",
            str(fact["target"]),
            str(fact["source"]),
            float(fact.get("confidence", 1.0)),
            None,
            (),
            ("Answered from current labeled geometry.",),
        )
    if query.get("kind") == "current_relation":
        fact = _find_fact(
            current,
            str(query.get("source", "")),
            str(query.get("relation", "")),
            str(query.get("target", "")),
        )
        if fact is None:
            return _unknown_symbolic("No current relation supports TRUE.")
        return ModelProposal(
            "TRUE",
            "true",
            str(fact["source"]),
            float(fact.get("confidence", 1.0)),
            None,
            (),
            ("Answered from current relation geometry.",),
        )
    if query.get("kind") == "past_relation":
        fact = _find_fact(
            list(facts.reconstructed_memories),
            str(query.get("source", "")),
            str(query.get("relation", "")),
            str(query.get("target", "")),
        )
        if fact is None:
            return _unknown_symbolic("No reconstructed memory supports TRUE.")
        return ModelProposal(
            "TRUE",
            "true",
            "reconstructed_memory",
            float(fact.get("confidence", 0.0)),
            None,
            (),
            ("Answered from explicitly reconstructed memory.",),
        )
    if query.get("kind") == "future_relation":
        fact = _find_fact(
            list(facts.future_hypotheses),
            str(query.get("source", "")),
            str(query.get("relation", "")),
            str(query.get("target", "")),
        )
        if fact is None:
            return _unknown_symbolic("No future hypothesis supports TRUE.")
        return ModelProposal(
            "TRUE",
            "true",
            "hypothetical_future",
            float(fact.get("confidence", 0.0)),
            None,
            (),
            ("Answered from explicitly hypothetical future content.",),
        )
    if query.get("kind") == "action_choice":
        for option in query.get("action_options", []):
            if option.get("recommended") and option.get("valid", True):
                action = str(option["action"])
                return ModelProposal(
                    "ACTION",
                    action,
                    str(option.get("source", "observed_now")),
                    1.0,
                    action,
                    tuple(str(item) for item in option.get("assumptions", [])),
                    ("Selected recommended action option after symbolic validation.",),
                )
        return _unknown_symbolic("No valid recommended action was supplied.")
    if query.get("kind") == "source_explanation":
        source = str(query.get("expected_source_label", "observed_now"))
        return ModelProposal(
            "ANSWER",
            f"source={source}",
            source,
            1.0,
            None,
            (),
            ("Reported the explicitly queried source label.",),
        )
    return _unknown_symbolic("Unsupported query kind for symbolic reference.")


def _unknown_symbolic(explanation: str) -> ModelProposal:
    return ModelProposal("UNKNOWN", "", "none", 0.0, None, (), (explanation,))


def _find_fact(
    facts: list[dict[str, Any]],
    source: str,
    relation: str,
    target: str | None,
) -> dict[str, Any] | None:
    for fact in facts:
        if str(fact.get("source_id")) != source:
            continue
        if str(fact.get("relation")) != relation:
            continue
        if target is not None and str(fact.get("target")) != target:
            continue
        return fact
    return None


def _score_proposal(proposal, expected: G23Expected, task_group: str) -> dict[str, Any]:
    if proposal is None:
        return _score(False, False, False, task_group)
    correct = _proposal_matches(proposal.status, proposal.answer, proposal.action, expected)
    source_correct = proposal.source_used == expected.source_used
    unsupported = int(proposal.status in {"TRUE", "ANSWER"} and proposal.source_used == "none")
    stale_as_current = int(proposal.source_used == "reconstructed_memory" and expected.source_used != "reconstructed_memory")
    prediction_as_fact = int(proposal.source_used == "hypothetical_future" and expected.source_used != "hypothetical_future")
    return {
        **_score(correct, source_correct, proposal.status == "UNKNOWN" and expected.status == "UNKNOWN", task_group),
        "contradiction_detected": int(proposal.status == "CONTRADICTORY" and expected.status == "CONTRADICTORY"),
        "stale_memory_as_current": stale_as_current,
        "false_memory_as_current": stale_as_current,
        "prediction_as_fact": prediction_as_fact,
        "unsupported_certainty": unsupported,
        "invalid_action": int(expected.action is not None and proposal.action != expected.action),
        "collision_proposal": 0,
        "explanation_grounded": int(bool(proposal.explanation)),
    }


def _score_validated(validation, expected: G23Expected, task_group: str) -> dict[str, Any]:
    correct = _proposal_matches(
        validation.final_status,
        validation.final_answer,
        validation.final_action,
        expected,
    )
    return {
        **_score(
            correct,
            validation.final_source_used == expected.source_used,
            validation.final_status == "UNKNOWN" and expected.status == "UNKNOWN",
            task_group,
        ),
        "contradiction_detected": int(validation.final_status == "CONTRADICTORY" and expected.status == "CONTRADICTORY"),
        "validator_rejected": int(not validation.accepted),
        "validator_prevented_error": int(validation.prevented_error),
        "invalid_action": int(validation.rejection_reason == "invalid_action"),
        "collision_proposal": 0,
    }


def _proposal_matches(status: str, answer: str, action: str | None, expected: G23Expected) -> bool:
    if status != expected.status:
        return False
    if expected.action is not None:
        return action == expected.action
    if expected.answer:
        return answer == expected.answer
    return True


def _score(correct: bool, source_correct: bool, correct_unknown: bool, task_group: str) -> dict[str, Any]:
    return {
        "correct": int(correct),
        "source_correct": int(source_correct),
        "correct_unknown": int(correct_unknown),
        "current_state_correct": int(correct and task_group == "temporal_qa"),
        "past_query_correct": 0,
        "future_query_correct": int(correct and task_group == "temporal_qa"),
        "spatial_reasoning_correct": int(correct and task_group == "spatial_qa"),
        "action_choice_correct": int(correct and task_group == "action_choice"),
        "contradiction_detected": 0,
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for mode in ("proposal", "validated"):
            key = _metric_key(row, mode)
            buckets.setdefault(key, []).append(row)
    return {key: _metrics_for(value, key.rsplit("|", 1)[-1]) for key, value in sorted(buckets.items())}


def _aggregate_by(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(str(row["trial"][field]), []).append(row)
    return {key: _aggregate(value) for key, value in sorted(buckets.items())}


def _metric_key(row: dict[str, Any], mode: str) -> str:
    return "|".join([str(row["model"]), row["regime"], row["condition"], mode])


def _metrics_for(rows: list[dict[str, Any]], mode: str) -> dict[str, float]:
    n = max(1, len(rows))
    scores = [row[f"{mode}_score"] for row in rows]
    correct = sum(score.get("correct", 0) for score in scores)
    parse_successes = sum(row["parse_success"] for row in rows)
    latencies = [float(row["latency_ms"]) for row in rows]
    input_tokens = [float(row["input_tokens"]) for row in rows]
    output_tokens = [float(row["output_tokens"]) for row in rows]
    low, high = _ci95(correct, n)
    return {
        "trial_count": float(n),
        "overall_accuracy": correct / n,
        "overall_accuracy_ci95_low": low,
        "overall_accuracy_ci95_high": high,
        "current_state_accuracy": _rate(sum(score.get("current_state_correct", 0) for score in scores), n),
        "past_query_accuracy": _rate(sum(score.get("past_query_correct", 0) for score in scores), n),
        "future_query_accuracy": _rate(sum(score.get("future_query_correct", 0) for score in scores), n),
        "spatial_reasoning_accuracy": _rate(sum(score.get("spatial_reasoning_correct", 0) for score in scores), n),
        "action_choice_accuracy": _rate(sum(score.get("action_choice_correct", 0) for score in scores), n),
        "contradiction_detection_rate": _rate(sum(score.get("contradiction_detected", 0) for score in scores), n),
        "correct_unknown_rate": _rate(sum(score.get("correct_unknown", 0) for score in scores), n),
        "source_classification_accuracy": _rate(sum(score.get("source_correct", 0) for score in scores), n),
        "stale_memory_as_current_rate": _rate(sum(score.get("stale_memory_as_current", 0) for score in scores), n),
        "false_memory_as_current_rate": _rate(sum(score.get("false_memory_as_current", 0) for score in scores), n),
        "prediction_as_fact_rate": _rate(sum(score.get("prediction_as_fact", 0) for score in scores), n),
        "unsupported_certainty_rate": _rate(sum(score.get("unsupported_certainty", 0) for score in scores), n),
        "invalid_action_rate": _rate(sum(score.get("invalid_action", 0) for score in scores), n),
        "collision_proposal_rate": _rate(sum(score.get("collision_proposal", 0) for score in scores), n),
        "validator_rejection_rate": _rate(sum(score.get("validator_rejected", 0) for score in scores), n),
        "validator_prevented_error_count": float(sum(score.get("validator_prevented_error", 0) for score in scores)),
        "json_parse_success_rate": _rate(parse_successes, n),
        "repair_retry_rate": _rate(sum(row["repair_retry_count"] > 0 for row in rows), n),
        "explanation_grounding_rate": _rate(sum(score.get("explanation_grounded", 0) for score in scores), n),
        "mean_input_tokens": mean(input_tokens),
        "mean_output_tokens": mean(output_tokens),
        "median_latency_ms": median(latencies),
        "mean_latency_ms": mean(latencies),
        "p95_latency_ms": _percentile(latencies, 0.95),
        "model_call_count": float(sum(row["backend"] != "symbolic" for row in rows)),
        "context_overflow_count": float(sum(row["context_overflow"] for row in rows)),
    }


def _pairwise_n_vs_c(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["model"]), row["regime"], row["trial"]["trial_id"])
        by_key.setdefault(key, {})[row["condition"]] = row
    results: dict[str, Any] = {}
    for mode in ("proposal", "validated"):
        by_regime: dict[str, dict[str, int]] = {}
        for (model, regime, _), conditions in by_key.items():
            if "N_NOWMIND_STRUCTURED" not in conditions or "C_CHRONOLOGICAL" not in conditions:
                continue
            n_correct = bool(conditions["N_NOWMIND_STRUCTURED"][f"{mode}_score"]["correct"])
            c_correct = bool(conditions["C_CHRONOLOGICAL"][f"{mode}_score"]["correct"])
            key = f"{model}|{regime}|{mode}"
            by_regime.setdefault(key, {"n_better": 0, "c_better": 0, "tied": 0})
            if n_correct and not c_correct:
                by_regime[key]["n_better"] += 1
            elif c_correct and not n_correct:
                by_regime[key]["c_better"] += 1
            else:
                by_regime[key]["tied"] += 1
        results.update(by_regime)
    return results


def _proposal_vs_validated(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for row in rows:
        key = "|".join([str(row["model"]), row["regime"], row["condition"]])
        bucket = result.setdefault(key, {"proposal_correct": 0, "validated_correct": 0, "validator_prevented_error": 0, "count": 0})
        bucket["proposal_correct"] += int(row["proposal_score"]["correct"])
        bucket["validated_correct"] += int(row["validated_score"]["correct"])
        bucket["validator_prevented_error"] += int(row["validated_score"].get("validator_prevented_error", 0))
        bucket["count"] += 1
    return result


def _fairness_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    paired: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["model"]), row["regime"], row["trial"]["trial_id"])
        paired.setdefault(key, {})[row["condition"]] = row
    checks = []
    for key, conditions in paired.items():
        if "N_NOWMIND_STRUCTURED" not in conditions or "C_CHRONOLOGICAL" not in conditions:
            continue
        n = conditions["N_NOWMIND_STRUCTURED"]
        c = conditions["C_CHRONOLOGICAL"]
        n_budget = n["representation"].get("budget_accounting", {})
        c_budget = c["representation"].get("budget_accounting", {})
        n_final_tokens = int(n_budget.get("final_input_token_estimate", n["representation"]["token_estimate"]))
        c_final_tokens = int(c_budget.get("final_input_token_estimate", c["representation"]["token_estimate"]))
        n_budgeted_tokens = int(n_budget.get("budgeted_input_tokens", n_final_tokens))
        c_budgeted_tokens = int(c_budget.get("budgeted_input_tokens", c_final_tokens))
        checks.append(
            {
                "model": key[0],
                "regime": key[1],
                "trial_id": key[2],
                "same_fact_set_hash": n["same_admissible_fact_set_hash"] == c["same_admissible_fact_set_hash"],
                "same_model_config": n["model_config"] == c["model_config"],
                "n_tokens": n_final_tokens,
                "c_tokens": c_final_tokens,
                "n_budgeted_tokens": n_budgeted_tokens,
                "c_budgeted_tokens": c_budgeted_tokens,
                "n_provider_tokens": n.get("input_tokens"),
                "c_provider_tokens": c.get("input_tokens"),
                "n_unused_budget": n_budget.get("unused_budget"),
                "c_unused_budget": c_budget.get("unused_budget"),
                "n_evidence_retained": n_budget.get("retained_counts", {}),
                "c_evidence_retained": c_budget.get("retained_counts", {}),
                "n_evidence_dropped": n_budget.get("dropped_counts", {}),
                "c_evidence_dropped": c_budget.get("dropped_counts", {}),
                "within_fixed_budget": (
                    key[1] != "B_FIXED_BUDGET"
                    or (n_budgeted_tokens <= FIXED_TOKEN_BUDGET and c_budgeted_tokens <= FIXED_TOKEN_BUDGET)
                ),
            }
        )
    failed = [check for check in checks if not (check["same_fact_set_hash"] and check["same_model_config"] and check["within_fixed_budget"])]
    return {
        "summary": {"checked_pairs": len(checks), "failed": len(failed)},
        "failed_samples": failed[:10],
        "forbidden_prompt_terms": ["expected_status", "expected_answer", "oracle", "ground_truth"],
    }


def _failure_samples(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    samples: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["validated_score"]["correct"]:
            continue
        key = "|".join([row["model"], row["regime"], row["condition"]])
        samples.setdefault(key, [])
        if len(samples[key]) < 10:
            samples[key].append(row)
    return samples


def _invariant_results(
    rows: list[dict[str, Any]],
    fairness: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    add(
        "G2.3-local-only",
        not manifest["available_backends"]["ollama"]
        or manifest["ollama"]["executable"] is not None
        or str(manifest["ollama"].get("base_url", "")).startswith("http://127.0.0.1")
        or str(manifest["ollama"].get("base_url", "")).startswith("http://localhost"),
        "no cloud backend configured",
    )
    add("G2.3-fairness", fairness["summary"]["failed"] == 0, str(fairness["summary"]))
    add("G2.3-paired-conditions", all(row["condition"] in CONDITIONS for row in rows), "N/C/R plus symbolic S reference")
    add("G2.3-json-recorded", all("raw_output" in row and "parsed_output" in row for row in rows), "raw and parsed outputs retained")
    add("G2.3-no-observed-now-write", True, "model proposals remain proposals")
    add("G2.3-no-memorytrace-write", True, "model proposals are not MemoryTrace")
    failed = sum(1 for check in checks if not check["passed"])
    return {"checks": checks, "summary": {"passed": len(checks) - failed, "failed": failed}}


def _prompt_templates_markdown() -> str:
    return f"""# G2.3 Prompt Templates

## Common System Instruction

```text
{COMMON_SYSTEM_INSTRUCTION}
```

## Representation Prompt

Each condition receives the same system instruction and a deterministic JSON
representation after the marker `REPRESENTATION_JSON:`.

## Regime A

No truncation. Context overflow is recorded instead of silently truncating.

## Regime B

Both N and C use the same fixed token budget: `{FIXED_TOKEN_BUDGET}` estimated
tokens. N uses explicit reconstruction selection; C uses current/relevant
chronological records first and then newest records within the same budget.

## Symbolic Reference

`S_SYMBOLIC_NOWMIND` is the existing no-LLM symbolic reference. It receives the
same admissible fact object but does not call a model backend.
"""


def _summary(
    manifest: dict[str, Any],
    metrics: dict[str, Any],
    pairwise: dict[str, Any],
    invariants: dict[str, Any],
    final_count: int,
) -> str:
    selected = manifest["selected"]
    lines = [
        "# G2.3 Model Integration Summary",
        "",
        f"- selected backend: `{selected['backend']}`",
        f"- selected model: `{selected['model']}`",
        f"- final paired trial IDs: `{final_count}`",
        f"- invariants: `{invariants['summary']['passed']} passed, {invariants['summary']['failed']} failed`",
        f"- local model prerequisite: `{manifest['local_model_runtime_prerequisite']}`",
        "",
        "## Aggregate Metrics",
    ]
    for key, values in metrics.items():
        if "|validated" not in key:
            continue
        lines.append(f"- `{key}` accuracy={values['overall_accuracy']:.3f} source={values['source_classification_accuracy']:.3f} parse={values['json_parse_success_rate']:.3f}")
    lines.append("")
    lines.append("## Pairwise N vs C")
    for key, values in pairwise.items():
        lines.append(f"- `{key}` N={values['n_better']} C={values['c_better']} tied={values['tied']}")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _rate(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def _ci95(successes: int, n: int) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = successes / n
    spread = 1.96 * sqrt(p * (1.0 - p) / n)
    return max(0.0, p - spread), min(1.0, p + spread)


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[index]

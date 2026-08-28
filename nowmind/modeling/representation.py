from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from math import ceil
from typing import Any, Iterable

from nowmind.modeling.backend import estimate_tokens


COMMON_SYSTEM_INSTRUCTION = """Use only supplied evidence.
Distinguish current observation, memory, and hypothetical future.
Do not promote memory or predictions to current fact.
Return UNKNOWN when current evidence is insufficient.
For action tasks, propose only actions supported by supplied state.
Return strict JSON with status, answer, source_used, confidence, action, assumptions, and explanation."""


FIXED_BUDGET_SAFETY_MULTIPLIER = 1.25


@dataclass(frozen=True, slots=True)
class G23AdmissibleFacts:
    trial_id: str
    current_cycle_id: int
    query: dict[str, Any]
    observed_now: tuple[dict[str, Any], ...] = ()
    inferred_now: tuple[dict[str, Any], ...] = ()
    reconstructed_memories: tuple[dict[str, Any], ...] = ()
    future_hypotheses: tuple[dict[str, Any], ...] = ()
    uncertainties: tuple[dict[str, Any], ...] = ()
    planning_assumptions: tuple[dict[str, Any], ...] = ()
    chronological_records: tuple[dict[str, Any], ...] = ()
    contradiction: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "current_cycle_id": self.current_cycle_id,
            "query": self.query,
            "observed_now": list(self.observed_now),
            "inferred_now": list(self.inferred_now),
            "reconstructed_memories": list(self.reconstructed_memories),
            "future_hypotheses": list(self.future_hypotheses),
            "uncertainties": list(self.uncertainties),
            "planning_assumptions": list(self.planning_assumptions),
            "chronological_records": list(self.chronological_records),
            "contradiction": self.contradiction,
        }

    @property
    def fact_set_hash(self) -> str:
        return stable_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class RepresentationResult:
    condition: str
    regime: str
    prompt: str
    representation: dict[str, Any]
    fact_set_hash: str
    prompt_hash: str
    token_estimate: int
    context_overflow: bool
    truncated: bool
    budget: int | None = None
    budget_accounting: dict[str, Any] = field(default_factory=dict)

    def to_record(self, include_prompt: bool = False) -> dict[str, Any]:
        record = {
            "condition": self.condition,
            "regime": self.regime,
            "fact_set_hash": self.fact_set_hash,
            "prompt_hash": self.prompt_hash,
            "token_estimate": self.token_estimate,
            "context_overflow": self.context_overflow,
            "truncated": self.truncated,
            "budget": self.budget,
            "final_input_token_estimate": self.token_estimate,
            "budget_accounting": self.budget_accounting,
        }
        if include_prompt:
            record["prompt"] = self.prompt
            record["representation"] = self.representation
        return record


class NowMindRepresentationBuilder:
    condition = "N_NOWMIND_STRUCTURED"

    def build(
        self,
        facts: G23AdmissibleFacts,
        regime: str,
        token_budget: int | None = None,
        context_size: int = 12000,
    ) -> RepresentationResult:
        representation = {
            "condition": self.condition,
            "trial_id": facts.trial_id,
            "current_cycle_id": facts.current_cycle_id,
            "query": facts.query,
            "observed_now": list(facts.observed_now),
            "inferred_now": list(facts.inferred_now),
            "reconstructed_memories": list(facts.reconstructed_memories),
            "future_hypotheses": list(facts.future_hypotheses),
            "uncertainties": list(facts.uncertainties),
            "planning_assumptions": list(facts.planning_assumptions),
            "contradiction": facts.contradiction,
        }
        truncated = False
        original_counts = _count_budgeted_fields(
            representation,
            (
                "reconstructed_memories",
                "future_hypotheses",
                "planning_assumptions",
                "uncertainties",
            ),
        )
        if regime == "B_FIXED_BUDGET" and token_budget is not None:
            representation, truncated = _fit_budget(
                representation,
                token_budget,
                ordered_fields=(
                    "reconstructed_memories",
                    "future_hypotheses",
                    "planning_assumptions",
                    "uncertainties",
                ),
            )
        budget_accounting = _budget_accounting(
            representation,
            token_budget,
            original_counts,
            retained_policy="preserve current observation/query/source labels; trim reconstructed memories, hypotheses, assumptions, and uncertainties by existing order",
        )
        return _result(
            self.condition,
            regime,
            facts,
            representation,
            context_size,
            token_budget,
            truncated,
            budget_accounting,
        )


class ChronologicalRepresentationBuilder:
    condition = "C_CHRONOLOGICAL"

    def build(
        self,
        facts: G23AdmissibleFacts,
        regime: str,
        token_budget: int | None = None,
        context_size: int = 12000,
    ) -> RepresentationResult:
        records = list(facts.chronological_records)
        representation = {
            "condition": self.condition,
            "trial_id": facts.trial_id,
            "current_cycle_id": facts.current_cycle_id,
            "query": facts.query,
            "chronological_records": records,
            "contradiction": facts.contradiction,
            "selection_policy": "complete chronological record" if regime != "B_FIXED_BUDGET" else "current and relevant records first, then newest records within budget",
        }
        truncated = False
        original_counts = {"chronological_records": len(records)}
        if regime == "B_FIXED_BUDGET" and token_budget is not None:
            current = [record for record in records if record.get("cycle_id") == facts.current_cycle_id]
            relevant = [
                record
                for record in records
                if record.get("relevance") and record not in current
            ]
            newest = [
                record
                for record in reversed(records)
                if record not in current and record not in relevant
            ]
            retained = _budgeted_records(
                {**representation, "chronological_records": []},
                current + relevant + newest,
                token_budget,
            )
            retained_ids = {_record_identity(record) for record in retained}
            representation["chronological_records"] = [
                record for record in records if _record_identity(record) in retained_ids
            ]
            truncated = len(representation["chronological_records"]) < len(records)
        budget_accounting = _budget_accounting(
            representation,
            token_budget,
            original_counts,
            retained_policy="preserve current and query-relevant records, then newest records; emit retained records in chronological order",
        )
        return _result(
            self.condition,
            regime,
            facts,
            representation,
            context_size,
            token_budget,
            truncated,
            budget_accounting,
        )


class CurrentOnlyRepresentationBuilder:
    condition = "R_CURRENT_ONLY"

    def build(
        self,
        facts: G23AdmissibleFacts,
        regime: str,
        token_budget: int | None = None,
        context_size: int = 12000,
    ) -> RepresentationResult:
        representation = {
            "condition": self.condition,
            "trial_id": facts.trial_id,
            "current_cycle_id": facts.current_cycle_id,
            "query": facts.query,
            "observed_now": list(facts.observed_now),
            "inferred_now": list(facts.inferred_now),
            "uncertainties": list(facts.uncertainties),
            "contradiction": facts.contradiction,
        }
        return _result(
            self.condition,
            regime,
            facts,
            representation,
            context_size,
            token_budget,
            False,
            _budget_accounting(representation, token_budget, {}, retained_policy="current observation/query only"),
        )


class SymbolicReferenceBuilder:
    condition = "S_SYMBOLIC_NOWMIND"

    def build(
        self,
        facts: G23AdmissibleFacts,
        regime: str,
        token_budget: int | None = None,
        context_size: int = 12000,
    ) -> RepresentationResult:
        representation = {
            "condition": self.condition,
            "trial_id": facts.trial_id,
            "current_cycle_id": facts.current_cycle_id,
            "query": facts.query,
            "observed_now": list(facts.observed_now),
            "inferred_now": list(facts.inferred_now),
            "reconstructed_memories": list(facts.reconstructed_memories),
            "future_hypotheses": list(facts.future_hypotheses),
            "uncertainties": list(facts.uncertainties),
            "planning_assumptions": list(facts.planning_assumptions),
            "contradiction": facts.contradiction,
            "reference_mode": "deterministic no-llm symbolic faculty",
        }
        return _result(
            self.condition,
            regime,
            facts,
            representation,
            context_size,
            token_budget,
            False,
            _budget_accounting(representation, token_budget, {}, retained_policy="symbolic reference"),
        )


def stable_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _result(
    condition: str,
    regime: str,
    facts: G23AdmissibleFacts,
    representation: dict[str, Any],
    context_size: int,
    budget: int | None,
    truncated: bool,
    budget_accounting: dict[str, Any],
) -> RepresentationResult:
    prompt = _prompt(representation)
    tokens = canonical_input_token_count(COMMON_SYSTEM_INSTRUCTION, prompt)
    if budget is not None and budgeted_input_token_count(tokens) > budget:
        raise ValueError(
            f"Regime B prompt exceeds fixed budget after deterministic trimming: "
            f"{budgeted_input_token_count(tokens)} > {budget}"
        )
    budget_accounting = {
        **budget_accounting,
        "counter": "estimate_tokens(system_instruction + newline + final_prompt)",
        "exact_tokenizer_available": False,
        "safety_multiplier": FIXED_BUDGET_SAFETY_MULTIPLIER,
        "final_input_token_estimate": tokens,
        "budgeted_input_tokens": budgeted_input_token_count(tokens),
        "unused_budget": None if budget is None else budget - budgeted_input_token_count(tokens),
    }
    return RepresentationResult(
        condition=condition,
        regime=regime,
        prompt=prompt,
        representation=representation,
        fact_set_hash=facts.fact_set_hash,
        prompt_hash=stable_hash({"system": COMMON_SYSTEM_INSTRUCTION, "prompt": prompt}),
        token_estimate=tokens,
        context_overflow=tokens > context_size,
        truncated=truncated,
        budget=budget,
        budget_accounting=budget_accounting,
    )


def _prompt(representation: dict[str, Any]) -> str:
    return (
        "Analyze the supplied representation and return strict JSON only.\n"
        "REPRESENTATION_JSON:\n"
        f"{canonical_json(representation)}"
    )


def canonical_input_token_count(system_instruction: str, prompt: str) -> int:
    return estimate_tokens(system_instruction + "\n" + prompt)


def budgeted_input_token_count(final_input_tokens: int) -> int:
    return ceil(final_input_tokens * FIXED_BUDGET_SAFETY_MULTIPLIER)


def _fit_budget(
    representation: dict[str, Any],
    budget: int,
    ordered_fields: Iterable[str],
) -> tuple[dict[str, Any], bool]:
    result = dict(representation)
    truncated = False
    for field_name in ordered_fields:
        values = list(result.get(field_name, []))
        kept = _budgeted_prefix({**result, field_name: []}, field_name, values, budget)
        truncated = truncated or len(kept) < len(values)
        result[field_name] = kept
    if budgeted_input_token_count(canonical_input_token_count(COMMON_SYSTEM_INSTRUCTION, _prompt(result))) > budget:
        for field_name in ordered_fields:
            result[field_name] = []
        truncated = True
    return result, truncated


def _budgeted_records(base: dict[str, Any], records: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    return _budgeted_prefix(base, "chronological_records", records, budget)


def _budgeted_prefix(
    base: dict[str, Any],
    field_name: str,
    values: list[dict[str, Any]],
    budget: int,
) -> list[dict[str, Any]]:
    if not values:
        return []
    if _within_budget(_prompt({**base, field_name: values}), budget):
        return list(values)
    low = 0
    high = len(values)
    while low < high:
        midpoint = (low + high + 1) // 2
        candidate = values[:midpoint]
        if _within_budget(_prompt({**base, field_name: candidate}), budget):
            low = midpoint
        else:
            high = midpoint - 1
    return list(values[:low])


def _within_budget(prompt: str, budget: int) -> bool:
    tokens = canonical_input_token_count(COMMON_SYSTEM_INSTRUCTION, prompt)
    return budgeted_input_token_count(tokens) <= budget


def _count_budgeted_fields(
    representation: dict[str, Any],
    field_names: Iterable[str],
) -> dict[str, int]:
    return {field_name: len(list(representation.get(field_name, []))) for field_name in field_names}


def _budget_accounting(
    representation: dict[str, Any],
    budget: int | None,
    original_counts: dict[str, int],
    retained_policy: str,
) -> dict[str, Any]:
    retained = _count_budgeted_fields(representation, original_counts.keys())
    return {
        "declared_budget": budget,
        "retained_policy": retained_policy,
        "original_counts": original_counts,
        "retained_counts": retained,
        "dropped_counts": {
            field_name: original_counts[field_name] - retained.get(field_name, 0)
            for field_name in original_counts
        },
    }


def _record_identity(record: dict[str, Any]) -> str:
    return stable_hash(record)

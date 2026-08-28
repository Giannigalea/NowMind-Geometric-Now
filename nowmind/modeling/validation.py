from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nowmind.modeling.proposal import ModelProposal
from nowmind.modeling.representation import G23AdmissibleFacts


@dataclass(frozen=True, slots=True)
class ValidationResult:
    accepted: bool
    final_status: str
    final_answer: str
    final_action: str | None
    final_source_used: str = "none"
    rejection_reason: str | None = None
    prevented_error: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "final_status": self.final_status,
            "final_answer": self.final_answer,
            "final_action": self.final_action,
            "final_source_used": self.final_source_used,
            "rejection_reason": self.rejection_reason,
            "prevented_error": self.prevented_error,
        }


def validate_model_proposal(
    proposal: ModelProposal | None,
    facts: G23AdmissibleFacts,
) -> ValidationResult:
    if proposal is None:
        return ValidationResult(False, "UNKNOWN", "", None, "none", "parse_failure", True)
    query = facts.query
    if proposal.action is not None:
        valid_actions = {
            str(option["action"])
            for option in query.get("action_options", [])
            if option.get("valid", True)
        }
        if proposal.action not in valid_actions:
            return ValidationResult(
                False,
                "UNKNOWN",
                "",
                None,
                "none",
                "invalid_action",
                True,
            )
    if _current_query(query) and proposal.status in {"TRUE", "ANSWER"}:
        if proposal.source_used in {"reconstructed_memory", "hypothetical_future"}:
            return ValidationResult(
                False,
                "UNKNOWN",
                "",
                None,
                "none",
                "temporal_source_violation",
                True,
            )
        if proposal.answer and not _current_supports_answer(proposal, facts):
            return ValidationResult(
                False,
                "UNKNOWN",
                "",
                None,
                "none",
                "unsupported_current_claim",
                True,
            )
    return ValidationResult(
        True,
        proposal.status,
        proposal.answer,
        proposal.action,
        proposal.source_used,
    )


def _current_query(query: dict[str, Any]) -> bool:
    return query.get("kind") in {"current_location", "current_relation"}


def _current_supports_answer(proposal: ModelProposal, facts: G23AdmissibleFacts) -> bool:
    query = facts.query
    if proposal.status == "TRUE" and query.get("kind") == "current_relation":
        current = list(facts.observed_now) + list(facts.inferred_now)
        return any(
            str(fact.get("source_id")) == str(query.get("source"))
            and str(fact.get("relation")) == str(query.get("relation"))
            and str(fact.get("target")) == str(query.get("target"))
            for fact in current
        )
    if proposal.status == "TRUE":
        return True
    if proposal.status == "ANSWER" and not proposal.answer:
        return False
    current = list(facts.observed_now) + list(facts.inferred_now)
    return any(str(fact.get("target")) == proposal.answer for fact in current)

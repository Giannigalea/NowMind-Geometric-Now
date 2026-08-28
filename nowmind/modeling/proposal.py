from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True, slots=True)
class ModelProposal:
    status: str
    answer: str
    source_used: str
    confidence: float
    action: str | None
    assumptions: tuple[str, ...]
    explanation: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "answer": self.answer,
            "source_used": self.source_used,
            "confidence": self.confidence,
            "action": self.action,
            "assumptions": list(self.assumptions),
            "explanation": list(self.explanation),
        }


@dataclass(frozen=True, slots=True)
class ParsedModelOutput:
    proposal: ModelProposal | None
    parse_success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "parse_success": self.parse_success,
            "error": self.error,
        }


def parse_model_output(raw_text: str) -> ParsedModelOutput:
    try:
        data = json.loads(_extract_json_object(raw_text))
        answer = data.get("answer", "")
        if answer is None:
            answer = ""
        proposal = ModelProposal(
            status=str(data.get("status", "UNKNOWN")).upper(),
            answer=str(answer),
            source_used=str(data.get("source_used", "none")),
            confidence=float(data.get("confidence", 0.0)),
            action=data.get("action") if data.get("action") is None else str(data.get("action")),
            assumptions=tuple(str(item) for item in data.get("assumptions", [])),
            explanation=tuple(str(item) for item in data.get("explanation", [])),
        )
        return ParsedModelOutput(proposal, True)
    except Exception as exc:
        return ParsedModelOutput(None, False, str(exc))


def _extract_json_object(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nowmind.geometry.relation import RelationType
from nowmind.reasoning.query import TruthStatus
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource


class TemporalIntent(str, Enum):
    NOW = "now"
    PAST = "past"
    POSSIBLE_FUTURE = "possible_future"
    SOURCE = "source"


@dataclass(frozen=True, slots=True)
class TemporalQuery:
    source_id: str
    relation_type: RelationType
    target_id: str | None = None
    intent: TemporalIntent = TemporalIntent.NOW
    target_cycle_id: int | None = None

    @classmethod
    def relation(
        cls,
        source_id: str,
        relation_type: RelationType,
        target_id: str | None,
        intent: TemporalIntent = TemporalIntent.NOW,
        target_cycle_id: int | None = None,
    ) -> TemporalQuery:
        return cls(source_id, relation_type, target_id, intent, target_cycle_id)

    def display(self) -> str:
        relation = self.relation_type.name
        target = self.target_id or "?"
        return f"{self.intent.value}: {self.source_id} {relation} {target}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "relation_type": self.relation_type.value,
            "target_id": self.target_id,
            "intent": self.intent.value,
            "target_cycle_id": self.target_cycle_id,
            "display": self.display(),
        }


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    evidence_id: str
    source: TemporalSource
    cycle_id: int
    proposition: Proposition
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source": self.source.value,
            "cycle_id": self.cycle_id,
            "proposition": self.proposition.to_dict(),
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class TemporalAnswer:
    status: TruthStatus
    query: TemporalQuery
    confidence: float
    source: TemporalSource | None
    propositions: tuple[Proposition, ...] = field(default_factory=tuple)
    evidence: tuple[EvidenceReference, ...] = field(default_factory=tuple)
    explanation: tuple[str, ...] = field(default_factory=tuple)
    context: tuple[EvidenceReference, ...] = field(default_factory=tuple)
    uncertainty_notes: tuple[str, ...] = field(default_factory=tuple)
    contradictions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("answer confidence must be within [0, 1]")
        object.__setattr__(self, "propositions", tuple(self.propositions))
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "explanation", tuple(self.explanation))
        object.__setattr__(self, "context", tuple(self.context))
        object.__setattr__(self, "uncertainty_notes", tuple(self.uncertainty_notes))
        object.__setattr__(self, "contradictions", tuple(self.contradictions))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "query": self.query.to_dict(),
            "confidence": self.confidence,
            "source": self.source.value if self.source else None,
            "propositions": [item.to_dict() for item in self.propositions],
            "evidence": [item.to_dict() for item in self.evidence],
            "explanation": list(self.explanation),
            "context": [item.to_dict() for item in self.context],
            "uncertainty_notes": list(self.uncertainty_notes),
            "contradictions": list(self.contradictions),
        }

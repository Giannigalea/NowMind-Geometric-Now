from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID, uuid4

from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource


@dataclass(frozen=True, slots=True)
class FutureHypothesis:
    """Present content about a possible future, never an observation."""

    hypothesis_id: UUID
    created_at_cycle_id: int
    proposition: Proposition
    confidence: float
    generator_id: str
    metadata: Mapping[str, Any]
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("future confidence must be within [0, 1]")
        if self.provenance is not TemporalSource.HYPOTHETICAL_FUTURE:
            raise ValueError("future hypotheses must use HYPOTHETICAL_FUTURE provenance")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @classmethod
    def create(
        cls,
        created_at_cycle_id: int,
        proposition: Proposition,
        confidence: float,
        generator_id: str = "manual_g2_hypothesis",
        metadata: dict[str, Any] | None = None,
    ) -> FutureHypothesis:
        return cls(
            hypothesis_id=uuid4(),
            created_at_cycle_id=created_at_cycle_id,
            proposition=proposition,
            confidence=confidence,
            generator_id=generator_id,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": str(self.hypothesis_id),
            "created_at_cycle_id": self.created_at_cycle_id,
            "proposition": self.proposition.to_dict(),
            "confidence": self.confidence,
            "generator_id": self.generator_id,
            "metadata": dict(self.metadata),
            "provenance": self.provenance.value,
        }

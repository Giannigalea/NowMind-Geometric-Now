from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from nowmind.geometry.present_geometry import PresentGeometry
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction


@dataclass(frozen=True, slots=True)
class TemporalNowState:
    """Fresh G2 cognitive state with explicit temporal-source channels."""

    now_id: UUID
    cycle_id: int
    created_at: datetime
    present_geometry: PresentGeometry
    reconstructed_memories: tuple[MemoryReconstruction, ...] = field(default_factory=tuple)
    future_hypotheses: tuple[FutureHypothesis, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "reconstructed_memories",
            tuple(self.reconstructed_memories),
        )
        object.__setattr__(
            self,
            "future_hypotheses",
            tuple(self.future_hypotheses),
        )

    @classmethod
    def create(
        cls,
        present_geometry: PresentGeometry,
        reconstructed_memories: tuple[MemoryReconstruction, ...] = (),
        future_hypotheses: tuple[FutureHypothesis, ...] = (),
    ) -> TemporalNowState:
        return cls(
            now_id=uuid4(),
            cycle_id=present_geometry.cycle_id,
            created_at=datetime.now(UTC),
            present_geometry=present_geometry,
            reconstructed_memories=tuple(reconstructed_memories),
            future_hypotheses=tuple(future_hypotheses),
        )

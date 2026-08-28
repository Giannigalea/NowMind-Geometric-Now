from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from nowmind.geometry.present_geometry import PresentGeometry


@dataclass(frozen=True, slots=True)
class NowState:
    """Immutable representation of one fresh current Now."""

    now_id: UUID
    cycle_id: int
    created_at: datetime
    geometry: PresentGeometry

    @classmethod
    def create(cls, geometry: PresentGeometry) -> NowState:
        return cls(
            now_id=uuid4(),
            cycle_id=geometry.cycle_id,
            created_at=datetime.now(UTC),
            geometry=geometry,
        )


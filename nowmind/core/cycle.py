from __future__ import annotations

from dataclasses import dataclass, field

from nowmind.core.now_state import NowState
from nowmind.geometry.builder import PresentGeometryBuilder
from nowmind.perception.adapter import PerceptionAdapter
from nowmind.world.model import WorldState


def run_cognitive_cycle(world: WorldState, cycle_id: int) -> NowState:
    """Construct a fresh NowState from current world observation only."""

    observation = PerceptionAdapter().observe(world, cycle_id)
    geometry = PresentGeometryBuilder().build(observation)
    return NowState.create(geometry)


@dataclass(slots=True)
class CognitiveCycleRunner:
    """Convenience cycle clock that never stores prior NowState objects."""

    next_cycle_id: int = 1
    perception: PerceptionAdapter = field(default_factory=PerceptionAdapter)
    builder: PresentGeometryBuilder = field(default_factory=PresentGeometryBuilder)

    def run(self, world: WorldState) -> NowState:
        cycle_id = self.next_cycle_id
        self.next_cycle_id += 1
        observation = self.perception.observe(world, cycle_id)
        geometry = self.builder.build(observation)
        return NowState.create(geometry)


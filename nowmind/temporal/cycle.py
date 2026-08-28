from __future__ import annotations

from dataclasses import dataclass, field

from nowmind.geometry.builder import PresentGeometryBuilder
from nowmind.perception.adapter import PerceptionAdapter
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import (
    MemoryReconstructor,
    MemoryStore,
    ReconstructionDistortion,
    RetrievalCue,
    encode_present_geometry,
)
from nowmind.temporal.now_state import TemporalNowState
from nowmind.world.model import WorldState


def run_temporal_cycle(
    world: WorldState,
    cycle_id: int,
    memory_store: MemoryStore | None = None,
    memory_cue: RetrievalCue | None = None,
    future_hypotheses: tuple[FutureHypothesis, ...] = (),
) -> TemporalNowState:
    runner = TemporalCycleRunner(next_cycle_id=cycle_id, memory_store=memory_store)
    return runner.run(
        world,
        memory_cue=memory_cue,
        future_hypotheses=future_hypotheses,
        encode_after=False,
    )


@dataclass(slots=True)
class TemporalCycleRunner:
    """G2 cycle runner that stores traces, never prior NowState objects."""

    next_cycle_id: int = 1
    memory_store: MemoryStore | None = None
    perception: PerceptionAdapter = field(default_factory=PerceptionAdapter)
    builder: PresentGeometryBuilder = field(default_factory=PresentGeometryBuilder)
    reconstructor: MemoryReconstructor = field(default_factory=MemoryReconstructor)
    include_inferred_memory: bool = False

    def __post_init__(self) -> None:
        if self.memory_store is None:
            self.memory_store = MemoryStore()

    def run(
        self,
        world: WorldState,
        memory_cue: RetrievalCue | None = None,
        future_hypotheses: tuple[FutureHypothesis, ...] = (),
        encode_after: bool = True,
        reconstruction_limit: int | None = None,
        distortion: ReconstructionDistortion | None = None,
    ) -> TemporalNowState:
        cycle_id = self.next_cycle_id
        self.next_cycle_id += 1
        observation = self.perception.observe(world, cycle_id)
        geometry = self.builder.build(observation)
        reconstructed = ()
        if memory_cue is not None:
            reconstructed = self.reconstructor.retrieve_and_reconstruct(
                self.memory_store_or_raise,
                memory_cue,
                current_cycle_id=cycle_id,
                limit=reconstruction_limit,
                distortion=distortion,
            )
        temporal_now = TemporalNowState.create(
            present_geometry=geometry,
            reconstructed_memories=reconstructed,
            future_hypotheses=future_hypotheses,
        )
        if encode_after:
            self.encode_current_state(temporal_now)
        return temporal_now

    @property
    def memory_store_or_raise(self) -> MemoryStore:
        if self.memory_store is None:
            raise RuntimeError("memory_store was not initialized")
        return self.memory_store

    def encode_current_state(self, now: TemporalNowState) -> None:
        self.memory_store_or_raise.extend(
            encode_present_geometry(
                now.present_geometry,
                include_inferred=self.include_inferred_memory,
            )
        )

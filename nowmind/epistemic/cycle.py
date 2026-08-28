from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from nowmind.spatial.model import SpatialWorldState
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.now_state import TemporalNowState

from nowmind.epistemic.execution import EpistemicActionExecutionResult, EpistemicActionExecutor
from nowmind.epistemic.model import (
    EpistemicGeometry,
    SensorConfig,
    SensorReading,
    observe_epistemic_geometry,
)
from nowmind.epistemic.planning import EpistemicPlan, EpistemicPlanner


@dataclass(frozen=True, slots=True)
class EpistemicCycleState:
    epistemic_geometry: EpistemicGeometry
    temporal_now: TemporalNowState

    def to_dict(self) -> dict[str, Any]:
        return {
            "epistemic_geometry": self.epistemic_geometry.to_dict(),
            "temporal_now": {
                "now_id": str(self.temporal_now.now_id),
                "cycle_id": self.temporal_now.cycle_id,
                "created_at": self.temporal_now.created_at.isoformat(),
                "reconstructed_memories": [
                    memory.to_dict() for memory in self.temporal_now.reconstructed_memories
                ],
                "future_hypotheses": [
                    hypothesis.to_dict() for hypothesis in self.temporal_now.future_hypotheses
                ],
            },
        }


@dataclass(slots=True)
class EpistemicCycleRunner:
    sensor_config: SensorConfig = field(default_factory=SensorConfig)
    next_cycle_id: int = 1

    def run(
        self,
        world: SpatialWorldState,
        reconstructed_memories: Iterable[MemoryReconstruction] = (),
        future_hypotheses: Iterable[FutureHypothesis] = (),
        scan: bool = False,
        sensor_readings: Iterable[SensorReading] = (),
    ) -> EpistemicCycleState:
        cycle_id = self.next_cycle_id
        self.next_cycle_id += 1
        geometry = observe_epistemic_geometry(
            world,
            cycle_id,
            self.sensor_config,
            reconstructed_memories=reconstructed_memories,
            future_hypotheses=future_hypotheses,
            scan=scan,
            sensor_readings=sensor_readings,
        )
        temporal_now = TemporalNowState.create(
            present_geometry=geometry.to_present_geometry(),
            reconstructed_memories=geometry.reconstructed_memories,
            future_hypotheses=geometry.future_hypotheses,
        )
        return EpistemicCycleState(geometry, temporal_now)


@dataclass(slots=True)
class EpistemicClosedLoopController:
    world: SpatialWorldState
    planner: EpistemicPlanner
    cycle_runner: EpistemicCycleRunner = field(default_factory=EpistemicCycleRunner)
    executor: EpistemicActionExecutor = field(default_factory=EpistemicActionExecutor)
    reconstructed_memories: tuple[MemoryReconstruction, ...] = ()
    future_hypotheses: tuple[FutureHypothesis, ...] = ()
    current_state: EpistemicCycleState | None = None
    current_plan: EpistemicPlan | None = None
    history_record_count: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def observe(self, scan: bool = False) -> EpistemicCycleState:
        self.current_state = self.cycle_runner.run(
            self.world,
            reconstructed_memories=self.reconstructed_memories,
            future_hypotheses=self.future_hypotheses,
            scan=scan,
        )
        return self.current_state

    def plan_current(self) -> EpistemicPlan:
        state = self.current_state or self.observe()
        self.current_plan = self.planner.plan(
            state.epistemic_geometry,
            memory_reconstructions=state.temporal_now.reconstructed_memories,
            future_hypotheses=state.temporal_now.future_hypotheses,
            history_record_count=self.history_record_count,
        )
        return self.current_plan

    def execute_one_step(self) -> tuple[EpistemicActionExecutionResult, EpistemicCycleState]:
        plan = self.current_plan or self.plan_current()
        result = self.executor.execute(self.world, plan)
        observed = self.observe(scan=result.information_action)
        self.history.append(
            {
                "plan": plan.to_dict(),
                "execution": result.to_dict(),
                "fresh_now_id": str(observed.temporal_now.now_id),
                "fresh_cycle_id": observed.temporal_now.cycle_id,
            }
        )
        self.current_plan = None
        return result, observed

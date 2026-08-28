from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from nowmind.spatial.execution import ActionExecutionResult, ActionExecutor
from nowmind.spatial.model import SpatialGeometry, SpatialWorldState
from nowmind.spatial.planning import AStarPlanner, ActionProposal, Plan
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.now_state import TemporalNowState


@dataclass(frozen=True, slots=True)
class SpatialCycleState:
    spatial_geometry: SpatialGeometry
    temporal_now: TemporalNowState

    def to_dict(self) -> dict[str, Any]:
        return {
            "spatial_geometry": self.spatial_geometry.to_dict(),
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
class SpatialCycleRunner:
    next_cycle_id: int = 1

    def run(
        self,
        world: SpatialWorldState,
        reconstructed_memories: Iterable[MemoryReconstruction] = (),
        future_hypotheses: Iterable[FutureHypothesis] = (),
    ) -> SpatialCycleState:
        cycle_id = self.next_cycle_id
        self.next_cycle_id += 1
        spatial_geometry = world.observe(cycle_id)
        temporal_now = TemporalNowState.create(
            present_geometry=spatial_geometry.to_present_geometry(),
            reconstructed_memories=tuple(reconstructed_memories),
            future_hypotheses=tuple(future_hypotheses),
        )
        return SpatialCycleState(spatial_geometry, temporal_now)


@dataclass(slots=True)
class ClosedLoopController:
    world: SpatialWorldState
    planner: AStarPlanner = field(default_factory=AStarPlanner)
    cycle_runner: SpatialCycleRunner = field(default_factory=SpatialCycleRunner)
    executor: ActionExecutor = field(default_factory=ActionExecutor)
    reconstructed_memories: tuple[MemoryReconstruction, ...] = ()
    future_hypotheses: tuple[FutureHypothesis, ...] = ()
    current_state: SpatialCycleState | None = None
    last_plan: Plan | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def observe(self) -> SpatialCycleState:
        self.current_state = self.cycle_runner.run(
            self.world,
            reconstructed_memories=self.reconstructed_memories,
            future_hypotheses=self.future_hypotheses,
        )
        return self.current_state

    def plan_current(self) -> Plan:
        state = self.current_state or self.observe()
        self.last_plan = self.planner.plan(
            state.spatial_geometry,
            memory_reconstructions=state.temporal_now.reconstructed_memories,
        )
        return self.last_plan

    def execute_one_step(self, plan: Plan | None = None) -> tuple[ActionExecutionResult, SpatialCycleState]:
        plan = plan or self.last_plan or self.plan_current()
        proposal = ActionProposal.from_plan(plan)
        if proposal is None:
            raise ValueError("cannot execute a plan with no first step")
        result = self.executor.execute(self.world, proposal)
        observed = self.observe()
        self.history.append(
            {
                "proposal": proposal.to_dict(),
                "execution": result.to_dict(),
                "fresh_now_id": str(observed.temporal_now.now_id),
                "fresh_cycle_id": observed.temporal_now.cycle_id,
            }
        )
        return result, observed

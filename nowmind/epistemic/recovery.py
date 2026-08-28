from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nowmind.geometry.relation import RelationType
from nowmind.spatial.model import OccupancyState, Pose2D
from nowmind.temporal.memory import MemoryReconstruction

from nowmind.epistemic.model import EpistemicGeometry, pose_from_cell_id


@dataclass(slots=True)
class EpistemicRecoveryUpdate:
    newly_disconfirmed_targets: tuple[Pose2D, ...] = ()
    newly_invalidated_cells: tuple[Pose2D, ...] = ()
    target_reacquired: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "newly_disconfirmed_targets": [
                pose.to_dict() for pose in self.newly_disconfirmed_targets
            ],
            "newly_invalidated_cells": [
                pose.to_dict() for pose in self.newly_invalidated_cells
            ],
            "target_reacquired": self.target_reacquired,
        }


@dataclass(slots=True)
class EpistemicRecoveryState:
    """Current-cycle recovery bookkeeping, separate from historical memory."""

    disconfirmed_target_poses: set[Pose2D] = field(default_factory=set)
    invalidated_poses: set[Pose2D] = field(default_factory=set)
    reacquisition_attempts: int = 0
    reacquisition_successes: int = 0
    cells_explored: int = 0
    steps_to_reacquire: list[int] = field(default_factory=list)
    _attempt_active: bool = False
    _attempt_start_step: int = 0
    _seen_reacquisition: bool = False

    def update_from_geometry(
        self,
        geometry: EpistemicGeometry,
        executed_steps: int = 0,
    ) -> EpistemicRecoveryUpdate:
        newly_disconfirmed: list[Pose2D] = []
        newly_invalidated: list[Pose2D] = []
        visible = set(geometry.visible_cells)

        for memory in geometry.reconstructed_memories:
            pose = _target_pose_from_memory(memory)
            if pose is None or pose not in visible:
                continue
            if geometry.target_pose == pose:
                continue
            if pose not in self.disconfirmed_target_poses:
                self.disconfirmed_target_poses.add(pose)
                newly_disconfirmed.append(pose)

        for cell in geometry.cells:
            if cell.observed_occupancy is not OccupancyState.OCCUPIED:
                continue
            if not any(_memory_says_free(memory) for memory in cell.memory_candidates):
                continue
            if cell.pose not in self.invalidated_poses:
                self.invalidated_poses.add(cell.pose)
                newly_invalidated.append(cell.pose)

        if newly_disconfirmed and not self._attempt_active and geometry.target_pose is None:
            self._attempt_active = True
            self._attempt_start_step = executed_steps
            self.reacquisition_attempts += 1

        target_reacquired = False
        if self._attempt_active and geometry.target_pose is not None:
            self._attempt_active = False
            self.reacquisition_successes += 1
            self.steps_to_reacquire.append(max(0, executed_steps - self._attempt_start_step))
            target_reacquired = True
            self._seen_reacquisition = True

        return EpistemicRecoveryUpdate(
            newly_disconfirmed_targets=tuple(newly_disconfirmed),
            newly_invalidated_cells=tuple(newly_invalidated),
            target_reacquired=target_reacquired,
        )

    def record_exploration_step(self, pose: Pose2D) -> None:
        self.cells_explored += 1

    @property
    def target_reacquired(self) -> bool:
        return self._seen_reacquisition

    def to_dict(self) -> dict[str, Any]:
        return {
            "disconfirmed_target_poses": [
                pose.to_dict() for pose in sorted(self.disconfirmed_target_poses)
            ],
            "invalidated_poses": [
                pose.to_dict() for pose in sorted(self.invalidated_poses)
            ],
            "reacquisition_attempts": self.reacquisition_attempts,
            "reacquisition_successes": self.reacquisition_successes,
            "cells_explored": self.cells_explored,
            "steps_to_reacquire": list(self.steps_to_reacquire),
            "target_reacquired": self.target_reacquired,
        }


def _target_pose_from_memory(memory: MemoryReconstruction) -> Pose2D | None:
    if memory.proposition.source_id != "target":
        return None
    if memory.proposition.relation_type is not RelationType.AT:
        return None
    return pose_from_cell_id(memory.proposition.target_id)


def _memory_says_free(memory: MemoryReconstruction) -> bool:
    return (
        memory.proposition.relation_type is RelationType.OCCUPANCY
        and memory.proposition.target_id == OccupancyState.FREE.value
    )

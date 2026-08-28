from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from nowmind.spatial.model import Pose2D, SpatialWorldState
from nowmind.spatial.planning import ActionProposal
from nowmind.spatial.transformations import ConstraintCode, ConstraintViolation


@dataclass(frozen=True, slots=True)
class ActionExecutionResult:
    result_id: UUID
    proposal_id: UUID
    success: bool
    collision: bool
    before_pose: Pose2D
    attempted_pose: Pose2D
    after_pose: Pose2D
    violations: tuple[ConstraintViolation, ...]
    world_version: int
    observation_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "violations", tuple(self.violations))

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": str(self.result_id),
            "proposal_id": str(self.proposal_id),
            "success": self.success,
            "collision": self.collision,
            "before_pose": self.before_pose.to_dict(),
            "attempted_pose": self.attempted_pose.to_dict(),
            "after_pose": self.after_pose.to_dict(),
            "violations": [violation.to_dict() for violation in self.violations],
            "world_version": self.world_version,
            "observation_required": self.observation_required,
        }


class ActionExecutor:
    """Applies one concrete action to the external world."""

    def execute(
        self,
        world: SpatialWorldState,
        proposal: ActionProposal,
        actor_id: str = "agent",
    ) -> ActionExecutionResult:
        actor = world.entity(actor_id)
        dx, dy = proposal.step.transformation.transformation_type.delta
        before = actor.pose
        attempted = before.moved(dx, dy)
        violations: list[ConstraintViolation] = []
        collision = False
        if not world.in_bounds(attempted):
            violations.append(
                ConstraintViolation(
                    ConstraintCode.OUT_OF_BOUNDS,
                    "executor rejected an action outside world bounds",
                    attempted,
                    actor_id,
                )
            )
        elif world.is_blocked_truth(attempted):
            collision = True
            violations.append(
                ConstraintViolation(
                    ConstraintCode.COLLISION,
                    "executor detected a real-world blocking cell",
                    attempted,
                    actor_id,
                )
            )
        if violations:
            return ActionExecutionResult(
                result_id=uuid4(),
                proposal_id=proposal.proposal_id,
                success=False,
                collision=collision,
                before_pose=before,
                attempted_pose=attempted,
                after_pose=before,
                violations=tuple(violations),
                world_version=world.world_version,
            )
        world.move_entity(actor_id, attempted)
        return ActionExecutionResult(
            result_id=uuid4(),
            proposal_id=proposal.proposal_id,
            success=True,
            collision=False,
            before_pose=before,
            attempted_pose=attempted,
            after_pose=attempted,
            violations=(),
            world_version=world.world_version,
        )

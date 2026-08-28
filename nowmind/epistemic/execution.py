from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from nowmind.spatial.model import Pose2D, SpatialWorldState
from nowmind.spatial.transformations import ConstraintCode, ConstraintViolation

from nowmind.epistemic.planning import EpistemicActionType, EpistemicPlan, EpistemicPlanStep


@dataclass(frozen=True, slots=True)
class EpistemicActionExecutionResult:
    result_id: UUID
    plan_id: UUID
    action_type: EpistemicActionType
    success: bool
    collision: bool
    information_action: bool
    before_pose: Pose2D
    attempted_pose: Pose2D
    after_pose: Pose2D
    cost: float
    violations: tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    world_version_before: int = 0
    world_version_after: int = 0
    observation_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "violations", tuple(self.violations))

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": str(self.result_id),
            "plan_id": str(self.plan_id),
            "action_type": self.action_type.value,
            "success": self.success,
            "collision": self.collision,
            "information_action": self.information_action,
            "before_pose": self.before_pose.to_dict(),
            "attempted_pose": self.attempted_pose.to_dict(),
            "after_pose": self.after_pose.to_dict(),
            "cost": self.cost,
            "violations": [violation.to_dict() for violation in self.violations],
            "world_version_before": self.world_version_before,
            "world_version_after": self.world_version_after,
            "observation_required": self.observation_required,
        }


class EpistemicActionExecutor:
    """Executes one epistemic action against the external spatial world."""

    def execute(
        self,
        world: SpatialWorldState,
        plan: EpistemicPlan,
        actor_id: str = "agent",
    ) -> EpistemicActionExecutionResult:
        step = plan.first_step()
        if step is None:
            raise ValueError("cannot execute an empty epistemic plan")
        return self.execute_step(world, plan.plan_id, step, actor_id=actor_id)

    def execute_step(
        self,
        world: SpatialWorldState,
        plan_id: UUID,
        step: EpistemicPlanStep,
        actor_id: str = "agent",
    ) -> EpistemicActionExecutionResult:
        actor = world.entity(actor_id)
        before = actor.pose
        world_version_before = world.world_version
        if step.action_type is EpistemicActionType.SCAN:
            return EpistemicActionExecutionResult(
                result_id=uuid4(),
                plan_id=plan_id,
                action_type=step.action_type,
                success=True,
                collision=False,
                information_action=True,
                before_pose=before,
                attempted_pose=before,
                after_pose=before,
                cost=step.cost,
                violations=(),
                world_version_before=world_version_before,
                world_version_after=world.world_version,
            )

        dx, dy = step.action_type.delta
        attempted = before.moved(dx, dy)
        violations: list[ConstraintViolation] = []
        collision = False
        if not world.in_bounds(attempted):
            violations.append(
                ConstraintViolation(
                    ConstraintCode.OUT_OF_BOUNDS,
                    "epistemic executor rejected out-of-bounds movement",
                    attempted,
                    actor_id,
                )
            )
        elif world.is_blocked_truth(attempted):
            collision = True
            violations.append(
                ConstraintViolation(
                    ConstraintCode.COLLISION,
                    "epistemic executor detected hidden physical blockage",
                    attempted,
                    actor_id,
                )
            )
        if violations:
            return EpistemicActionExecutionResult(
                result_id=uuid4(),
                plan_id=plan_id,
                action_type=step.action_type,
                success=False,
                collision=collision,
                information_action=False,
                before_pose=before,
                attempted_pose=attempted,
                after_pose=before,
                cost=step.cost,
                violations=tuple(violations),
                world_version_before=world_version_before,
                world_version_after=world.world_version,
            )
        world.move_entity(actor_id, attempted)
        return EpistemicActionExecutionResult(
            result_id=uuid4(),
            plan_id=plan_id,
            action_type=step.action_type,
            success=True,
            collision=False,
            information_action=False,
            before_pose=before,
            attempted_pose=attempted,
            after_pose=attempted,
            cost=step.cost,
            violations=(),
            world_version_before=world_version_before,
            world_version_after=world.world_version,
        )

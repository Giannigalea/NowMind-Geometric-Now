from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from nowmind.geometry.relation import RelationType
from nowmind.spatial.model import OccupancyState, Pose2D
from nowmind.temporal.memory import MemoryReconstruction

from nowmind.epistemic.model import EpistemicGeometry, pose_from_cell_id


@dataclass(frozen=True, slots=True)
class EpistemicRetrievalMetrics:
    stored_records: int
    records_scanned: int
    index_candidates_considered: int
    records_returned: int
    reconstructions_created: int
    effective_evidence_used: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "stored_records": self.stored_records,
            "records_scanned": self.records_scanned,
            "index_candidates_considered": self.index_candidates_considered,
            "records_returned": self.records_returned,
            "reconstructions_created": self.reconstructions_created,
            "effective_evidence_used": self.effective_evidence_used,
        }


@dataclass(frozen=True, slots=True)
class EpistemicRetrievalResult:
    reconstructions: tuple[MemoryReconstruction, ...]
    metrics: EpistemicRetrievalMetrics


def retrieve_relevant_reconstructions(
    geometry: EpistemicGeometry,
    reconstructions: Iterable[MemoryReconstruction],
    disconfirmed_target_poses: Iterable[Pose2D] = (),
    invalidated_poses: Iterable[Pose2D] = (),
    indexed: bool = True,
) -> EpistemicRetrievalResult:
    memories = tuple(reconstructions)
    disconfirmed = frozenset(disconfirmed_target_poses)
    invalidated = frozenset(invalidated_poses)
    if not memories:
        return EpistemicRetrievalResult(
            (),
            EpistemicRetrievalMetrics(0, 0, 0, 0, 0),
        )

    envelope = _planning_envelope(geometry, memories, disconfirmed)
    relevant_unknowns = (geometry.unknown_cells - invalidated) & envelope
    if indexed:
        candidate_ids = {
            index
            for index, memory in enumerate(memories)
            if _could_be_relevant(memory, geometry, relevant_unknowns, disconfirmed)
        }
        candidates = [memories[index] for index in sorted(candidate_ids)]
        records_scanned = len(candidates)
        index_candidates = len(candidates)
    else:
        candidates = list(memories)
        records_scanned = len(memories)
        index_candidates = len(memories)

    returned = tuple(
        memory
        for memory in candidates
        if _is_relevant(memory, geometry, relevant_unknowns, disconfirmed)
    )
    return EpistemicRetrievalResult(
        returned,
        EpistemicRetrievalMetrics(
            stored_records=len(memories),
            records_scanned=records_scanned,
            index_candidates_considered=index_candidates,
            records_returned=len(returned),
            reconstructions_created=len(returned),
        ),
    )


def _could_be_relevant(
    memory: MemoryReconstruction,
    geometry: EpistemicGeometry,
    relevant_unknowns: frozenset[Pose2D],
    disconfirmed_target_poses: frozenset[Pose2D],
) -> bool:
    proposition = memory.proposition
    if proposition.source_id == "target" and proposition.relation_type is RelationType.AT:
        pose = pose_from_cell_id(proposition.target_id)
        return pose is not None and geometry.in_bounds(pose) and pose not in disconfirmed_target_poses
    if proposition.relation_type is RelationType.OCCUPANCY:
        pose = pose_from_cell_id(proposition.source_id)
        return pose is not None and pose in relevant_unknowns
    return False


def _planning_envelope(
    geometry: EpistemicGeometry,
    memories: tuple[MemoryReconstruction, ...],
    disconfirmed_target_poses: frozenset[Pose2D],
) -> frozenset[Pose2D]:
    goals = []
    if geometry.target_pose is not None:
        goals.append(geometry.target_pose)
    for memory in memories:
        if memory.proposition.source_id != "target":
            continue
        if memory.proposition.relation_type is not RelationType.AT:
            continue
        pose = pose_from_cell_id(memory.proposition.target_id)
        if pose is None or pose in disconfirmed_target_poses or not geometry.in_bounds(pose):
            continue
        if pose in geometry.visible_cells and geometry.target_pose != pose:
            continue
        goals.append(pose)
    if not goals:
        return frozenset()

    poses = set()
    margin = max(2, geometry.sensor_config.scan_radius_bonus + 1)
    for goal in goals:
        direct = geometry.agent_pose.manhattan_distance(goal)
        for cell in geometry.cells:
            detour = (
                geometry.agent_pose.manhattan_distance(cell.pose)
                + cell.pose.manhattan_distance(goal)
                - direct
            )
            if detour <= margin:
                poses.add(cell.pose)
    return frozenset(poses)


def _is_relevant(
    memory: MemoryReconstruction,
    geometry: EpistemicGeometry,
    relevant_unknowns: frozenset[Pose2D],
    disconfirmed_target_poses: frozenset[Pose2D],
) -> bool:
    proposition = memory.proposition
    if proposition.source_id == "target" and proposition.relation_type is RelationType.AT:
        pose = pose_from_cell_id(proposition.target_id)
        if pose is None or not geometry.in_bounds(pose):
            return False
        if pose in disconfirmed_target_poses:
            return False
        return not (pose in geometry.visible_cells and geometry.target_pose != pose)
    if proposition.relation_type is RelationType.OCCUPANCY:
        if proposition.target_id not in {OccupancyState.FREE.value, OccupancyState.OCCUPIED.value}:
            return False
        pose = pose_from_cell_id(proposition.source_id)
        return pose is not None and pose in relevant_unknowns
    return False

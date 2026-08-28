from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable

from nowmind.geometry.entity import Entity
from nowmind.geometry.present_geometry import PresentGeometry
from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.geometry.validation import ValidationResult
from nowmind.spatial.model import OccupancyState, Pose2D, SpatialWorldState
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.source import TemporalSource


class ObservationQuality(str, Enum):
    DIRECT = "direct"
    SCANNED = "scanned"
    CONTRADICTORY = "contradictory"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SensorConfig:
    visibility_radius: int = 3
    scan_radius_bonus: int = 3
    scan_cost: float = 2.0
    move_cost: float = 1.0
    obstacle_confidence: float = 0.92
    free_confidence: float = 0.88
    target_confidence: float = 0.9
    line_of_sight_blocks: bool = True

    def __post_init__(self) -> None:
        if self.visibility_radius < 0:
            raise ValueError("visibility radius cannot be negative")
        if self.scan_radius_bonus < 0:
            raise ValueError("scan radius bonus cannot be negative")
        for name in ("obstacle_confidence", "free_confidence", "target_confidence"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [0, 1]")


@dataclass(frozen=True, slots=True)
class SensorReading:
    pose: Pose2D
    occupancy: OccupancyState
    confidence: float
    sensor_id: str = "sensor"

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("sensor reading confidence must be within [0, 1]")

    def to_dict(self) -> dict[str, Any]:
        return {
            "pose": self.pose.to_dict(),
            "occupancy": self.occupancy.value,
            "confidence": self.confidence,
            "sensor_id": self.sensor_id,
        }


@dataclass(frozen=True, slots=True)
class EpistemicCell:
    pose: Pose2D
    observed_occupancy: OccupancyState
    observation_confidence: float | None
    memory_candidates: tuple[MemoryReconstruction, ...] = field(default_factory=tuple)
    future_candidates: tuple[FutureHypothesis, ...] = field(default_factory=tuple)
    sensor_readings: tuple[SensorReading, ...] = field(default_factory=tuple)
    quality: ObservationQuality = ObservationQuality.UNKNOWN
    provenance: TemporalSource | None = None

    def __post_init__(self) -> None:
        if self.observation_confidence is not None and not 0.0 <= self.observation_confidence <= 1.0:
            raise ValueError("observation confidence must be within [0, 1]")
        if self.observed_occupancy is OccupancyState.UNKNOWN and self.provenance is TemporalSource.OBSERVED_NOW:
            raise ValueError("unknown cells must not be represented as observed facts")
        object.__setattr__(self, "memory_candidates", tuple(self.memory_candidates))
        object.__setattr__(self, "future_candidates", tuple(self.future_candidates))
        object.__setattr__(self, "sensor_readings", tuple(self.sensor_readings))

    @property
    def is_known_free(self) -> bool:
        return self.observed_occupancy is OccupancyState.FREE

    @property
    def is_known_blocked(self) -> bool:
        return self.observed_occupancy is OccupancyState.OCCUPIED

    @property
    def is_unknown(self) -> bool:
        return self.observed_occupancy is OccupancyState.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return {
            "pose": self.pose.to_dict(),
            "observed_occupancy": self.observed_occupancy.value,
            "observation_confidence": self.observation_confidence,
            "quality": self.quality.value,
            "provenance": self.provenance.value if self.provenance else None,
            "memory_candidates": [memory.to_dict() for memory in self.memory_candidates],
            "future_candidates": [future.to_dict() for future in self.future_candidates],
            "sensor_readings": [reading.to_dict() for reading in self.sensor_readings],
        }


@dataclass(frozen=True, slots=True)
class EpistemicGeometry:
    width: int
    height: int
    cycle_id: int
    world_version: int
    agent_pose: Pose2D
    target_pose: Pose2D | None
    cells: tuple[EpistemicCell, ...]
    visible_cells: tuple[Pose2D, ...]
    sensor_config: SensorConfig
    scan_used: bool = False
    reconstructed_memories: tuple[MemoryReconstruction, ...] = field(default_factory=tuple)
    future_hypotheses: tuple[FutureHypothesis, ...] = field(default_factory=tuple)
    _cell_index: dict[Pose2D, EpistemicCell] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("epistemic geometry dimensions must be positive")
        if len(self.cells) != self.width * self.height:
            raise ValueError("epistemic geometry must contain exactly one cell per grid cell")
        object.__setattr__(self, "cells", tuple(self.cells))
        object.__setattr__(self, "visible_cells", tuple(sorted(self.visible_cells)))
        object.__setattr__(self, "reconstructed_memories", tuple(self.reconstructed_memories))
        object.__setattr__(self, "future_hypotheses", tuple(self.future_hypotheses))
        object.__setattr__(
            self,
            "_cell_index",
            MappingProxyType({cell.pose: cell for cell in self.cells}),
        )

    def in_bounds(self, pose: Pose2D) -> bool:
        return 0 <= pose.x < self.width and 0 <= pose.y < self.height

    @property
    def cell_map(self) -> dict[Pose2D, EpistemicCell]:
        return dict(self._cell_index)

    def cell_at(self, pose: Pose2D) -> EpistemicCell:
        if not self.in_bounds(pose):
            return EpistemicCell(
                pose=pose,
                observed_occupancy=OccupancyState.OCCUPIED,
                observation_confidence=1.0,
                quality=ObservationQuality.DIRECT,
                provenance=TemporalSource.OBSERVED_NOW,
            )
        return self._cell_index[pose]

    def occupancy_at(self, pose: Pose2D) -> OccupancyState:
        return self.cell_at(pose).observed_occupancy

    @property
    def known_free(self) -> frozenset[Pose2D]:
        return frozenset(cell.pose for cell in self.cells if cell.is_known_free)

    @property
    def known_blocked(self) -> frozenset[Pose2D]:
        return frozenset(cell.pose for cell in self.cells if cell.is_known_blocked)

    @property
    def unknown_cells(self) -> frozenset[Pose2D]:
        return frozenset(cell.pose for cell in self.cells if cell.is_unknown)

    def to_present_geometry(self) -> PresentGeometry:
        entities = [
            Entity("agent", "agent", "Agent", {"x": self.agent_pose.x, "y": self.agent_pose.y})
        ]
        if self.target_pose is not None:
            entities.append(
                Entity(
                    "target",
                    "target",
                    "Target",
                    {"x": self.target_pose.x, "y": self.target_pose.y},
                )
            )
        relations: list[Relation] = []
        for index, cell in enumerate(self.cells):
            if cell.provenance is not TemporalSource.OBSERVED_NOW:
                continue
            relations.append(
                Relation(
                    relation_id=f"e{index:04d}",
                    source_id=cell.pose.cell_id(),
                    target_id=cell.observed_occupancy.value,
                    relation_type=RelationType.OCCUPANCY,
                    confidence=cell.observation_confidence or 0.0,
                    provenance=Provenance.OBSERVED_NOW,
                    rule_id="EPISTEMIC_SENSOR_OBSERVATION",
                )
            )
        return PresentGeometry(
            cycle_id=self.cycle_id,
            world_version=self.world_version,
            entities=tuple(entities),
            relations=tuple(relations),
            validation=ValidationResult(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "cycle_id": self.cycle_id,
            "world_version": self.world_version,
            "agent_pose": self.agent_pose.to_dict(),
            "target_pose": self.target_pose.to_dict() if self.target_pose else None,
            "visible_cells": [pose.to_dict() for pose in self.visible_cells],
            "scan_used": self.scan_used,
            "sensor_config": {
                "visibility_radius": self.sensor_config.visibility_radius,
                "scan_radius_bonus": self.sensor_config.scan_radius_bonus,
                "scan_cost": self.sensor_config.scan_cost,
                "line_of_sight_blocks": self.sensor_config.line_of_sight_blocks,
            },
            "cells": [cell.to_dict() for cell in self.cells],
            "unknown_cell_count": len(self.unknown_cells),
            "known_free_count": len(self.known_free),
            "known_blocked_count": len(self.known_blocked),
        }


def observe_epistemic_geometry(
    world: SpatialWorldState,
    cycle_id: int,
    sensor_config: SensorConfig,
    reconstructed_memories: Iterable[MemoryReconstruction] = (),
    future_hypotheses: Iterable[FutureHypothesis] = (),
    scan: bool = False,
    sensor_readings: Iterable[SensorReading] = (),
) -> EpistemicGeometry:
    memories = tuple(reconstructed_memories)
    futures = tuple(future_hypotheses)
    readings_by_pose: dict[Pose2D, list[SensorReading]] = {}
    for reading in sensor_readings:
        readings_by_pose.setdefault(reading.pose, []).append(reading)

    agent_pose = world.entity("agent").pose
    target_truth = world.entity("target").pose
    radius = sensor_config.visibility_radius + (sensor_config.scan_radius_bonus if scan else 0)
    visible: set[Pose2D] = set()
    cells: list[EpistemicCell] = []
    memory_by_pose = _memories_by_pose(memories)
    future_by_pose = _futures_by_pose(futures)

    for y in range(world.height):
        for x in range(world.width):
            pose = Pose2D(x, y)
            within_range = agent_pose.manhattan_distance(pose) <= radius
            hidden_by_fog = pose in world.hidden_cells and pose != agent_pose and not scan
            has_sight = (
                not sensor_config.line_of_sight_blocks
                or _has_line_of_sight(world, agent_pose, pose)
            )
            observed = within_range and has_sight and not hidden_by_fog
            readings = tuple(readings_by_pose.get(pose, ()))
            if readings:
                cell = _cell_from_readings(
                    pose,
                    readings,
                    memory_by_pose.get(pose, ()),
                    future_by_pose.get(pose, ()),
                )
            elif observed:
                visible.add(pose)
                blocked = world.is_blocked_truth(pose)
                occupancy = OccupancyState.OCCUPIED if blocked else OccupancyState.FREE
                confidence = (
                    sensor_config.obstacle_confidence
                    if blocked
                    else sensor_config.free_confidence
                )
                cell = EpistemicCell(
                    pose=pose,
                    observed_occupancy=occupancy,
                    observation_confidence=confidence,
                    memory_candidates=memory_by_pose.get(pose, ()),
                    future_candidates=future_by_pose.get(pose, ()),
                    quality=ObservationQuality.SCANNED if scan else ObservationQuality.DIRECT,
                    provenance=TemporalSource.OBSERVED_NOW,
                )
            else:
                cell = EpistemicCell(
                    pose=pose,
                    observed_occupancy=OccupancyState.UNKNOWN,
                    observation_confidence=None,
                    memory_candidates=memory_by_pose.get(pose, ()),
                    future_candidates=future_by_pose.get(pose, ()),
                    quality=ObservationQuality.UNKNOWN,
                    provenance=None,
                )
            cells.append(cell)

    target_pose = target_truth if target_truth in visible else None
    return EpistemicGeometry(
        width=world.width,
        height=world.height,
        cycle_id=cycle_id,
        world_version=world.world_version,
        agent_pose=agent_pose,
        target_pose=target_pose,
        cells=tuple(cells),
        visible_cells=tuple(visible),
        sensor_config=sensor_config,
        scan_used=scan,
        reconstructed_memories=memories,
        future_hypotheses=futures,
    )


def pose_from_cell_id(cell_id: str) -> Pose2D | None:
    if not cell_id.startswith("cell:"):
        return None
    try:
        raw_x, raw_y = cell_id.removeprefix("cell:").split(",", 1)
        return Pose2D(int(raw_x), int(raw_y))
    except ValueError:
        return None


def _memories_by_pose(
    memories: tuple[MemoryReconstruction, ...],
) -> dict[Pose2D, tuple[MemoryReconstruction, ...]]:
    result: dict[Pose2D, list[MemoryReconstruction]] = {}
    for memory in memories:
        pose = pose_from_cell_id(memory.proposition.source_id)
        if pose is None and memory.proposition.source_id == "target":
            pose = pose_from_cell_id(memory.proposition.target_id)
        if pose is not None:
            result.setdefault(pose, []).append(memory)
    return {pose: tuple(items) for pose, items in result.items()}


def _futures_by_pose(
    futures: tuple[FutureHypothesis, ...],
) -> dict[Pose2D, tuple[FutureHypothesis, ...]]:
    result: dict[Pose2D, list[FutureHypothesis]] = {}
    for future in futures:
        pose = None
        raw_pose = future.metadata.get("pose")
        if isinstance(raw_pose, dict):
            pose = Pose2D(int(raw_pose["x"]), int(raw_pose["y"]))
        if pose is None:
            pose = pose_from_cell_id(future.proposition.target_id)
        if pose is not None:
            result.setdefault(pose, []).append(future)
    return {pose: tuple(items) for pose, items in result.items()}


def _cell_from_readings(
    pose: Pose2D,
    readings: tuple[SensorReading, ...],
    memories: tuple[MemoryReconstruction, ...],
    futures: tuple[FutureHypothesis, ...],
) -> EpistemicCell:
    states = {reading.occupancy for reading in readings}
    strongest = max(readings, key=lambda reading: (reading.confidence, reading.sensor_id))
    if len(states) > 1:
        return EpistemicCell(
            pose=pose,
            observed_occupancy=OccupancyState.UNKNOWN,
            observation_confidence=strongest.confidence,
            memory_candidates=memories,
            future_candidates=futures,
            sensor_readings=readings,
            quality=ObservationQuality.CONTRADICTORY,
            provenance=None,
        )
    return EpistemicCell(
        pose=pose,
        observed_occupancy=strongest.occupancy,
        observation_confidence=strongest.confidence,
        memory_candidates=memories,
        future_candidates=futures,
        sensor_readings=readings,
        quality=ObservationQuality.DIRECT,
        provenance=TemporalSource.OBSERVED_NOW,
    )


def _has_line_of_sight(world: SpatialWorldState, origin: Pose2D, target: Pose2D) -> bool:
    if origin == target:
        return True
    dx = target.x - origin.x
    dy = target.y - origin.y
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return True
    for step in range(1, steps):
        x = origin.x + round(dx * step / steps)
        y = origin.y + round(dy * step / steps)
        pose = Pose2D(x, y)
        if pose == origin or pose == target:
            continue
        if world.is_blocked_truth(pose):
            return False
    return True

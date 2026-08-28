from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping
from uuid import UUID, uuid4

from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.geometry.present_geometry import PresentGeometry
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def temporal_source_from_g1(provenance: Provenance) -> TemporalSource:
    if provenance is Provenance.OBSERVED_NOW:
        return TemporalSource.OBSERVED_NOW
    if provenance is Provenance.INFERRED_NOW:
        return TemporalSource.INFERRED_NOW
    raise ValueError(f"Unsupported G1 provenance: {provenance!r}")


@dataclass(frozen=True, slots=True)
class MemoryTrace:
    """Stored trace of a proposition. It is not a stored NowState."""

    trace_id: UUID
    source_cycle_id: int
    encoded_at_cycle_id: int
    proposition: Proposition
    original_source: TemporalSource
    encoded_confidence: float
    trace_strength: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.encoded_confidence <= 1.0:
            raise ValueError("encoded_confidence must be within [0, 1]")
        if not 0.0 <= self.trace_strength <= 1.0:
            raise ValueError("trace_strength must be within [0, 1]")
        if self.original_source not in {
            TemporalSource.OBSERVED_NOW,
            TemporalSource.INFERRED_NOW,
        }:
            raise ValueError("memory traces may encode observed/inferred current facts only")
        copied = dict(self.metadata)
        for value in copied.values():
            class_name = value.__class__.__name__
            if class_name in {"NowState", "TemporalNowState"}:
                raise ValueError("MemoryTrace metadata must not contain NowState objects")
        object.__setattr__(self, "metadata", MappingProxyType(copied))

    @classmethod
    def create(
        cls,
        source_cycle_id: int,
        encoded_at_cycle_id: int,
        proposition: Proposition,
        original_source: TemporalSource,
        encoded_confidence: float,
        trace_strength: float = 1.0,
        metadata: Mapping[str, Any] | None = None,
    ) -> MemoryTrace:
        return cls(
            trace_id=uuid4(),
            source_cycle_id=source_cycle_id,
            encoded_at_cycle_id=encoded_at_cycle_id,
            proposition=proposition,
            original_source=original_source,
            encoded_confidence=encoded_confidence,
            trace_strength=trace_strength,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": str(self.trace_id),
            "source_cycle_id": self.source_cycle_id,
            "encoded_at_cycle_id": self.encoded_at_cycle_id,
            "proposition": self.proposition.to_dict(),
            "original_source": self.original_source.value,
            "encoded_confidence": self.encoded_confidence,
            "trace_strength": self.trace_strength,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RetrievalCue:
    source_id: str | None = None
    relation_type: RelationType | None = None
    target_id: str | None = None
    temporal_intent: str | None = None

    @classmethod
    def for_relation(
        cls,
        source_id: str,
        relation_type: RelationType,
        target_id: str | None = None,
        temporal_intent: str | None = None,
    ) -> RetrievalCue:
        return cls(source_id, relation_type, target_id, temporal_intent)


@dataclass(frozen=True, slots=True)
class RetrievedTrace:
    trace: MemoryTrace
    score: float


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    stored_records: int
    records_scanned: int
    index_candidates_considered: int
    records_returned: int
    reconstructions_created: int = 0
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
class RetrievalResult:
    retrieved: tuple[RetrievedTrace, ...]
    metrics: RetrievalMetrics


class MemoryStore:
    """Explicit in-memory store containing MemoryTrace records only."""

    def __init__(self, traces: Iterable[MemoryTrace] | None = None) -> None:
        self._traces: list[MemoryTrace] = []
        for trace in traces or ():
            self.add(trace)

    def add(self, trace: MemoryTrace) -> MemoryTrace:
        if not isinstance(trace, MemoryTrace):
            raise TypeError("MemoryStore stores MemoryTrace objects only")
        self._traces.append(trace)
        return trace

    def extend(self, traces: Iterable[MemoryTrace]) -> None:
        for trace in traces:
            self.add(trace)

    @property
    def traces(self) -> tuple[MemoryTrace, ...]:
        return tuple(self._traces)

    def clear(self) -> None:
        self._traces.clear()

    def retrieve(self, cue: RetrievalCue, limit: int | None = None) -> tuple[RetrievedTrace, ...]:
        if cue.source_id is None and cue.relation_type is None and cue.target_id is None:
            return ()
        scored: list[RetrievedTrace] = []
        for trace in self._traces:
            score = _score_trace(trace, cue)
            if score > 0.0:
                scored.append(RetrievedTrace(trace, score))
        scored.sort(
            key=lambda item: (
                -item.score,
                -item.trace.encoded_at_cycle_id,
                str(item.trace.trace_id),
            )
        )
        if limit is not None:
            scored = scored[:limit]
        return tuple(scored)


class IndexedMemoryStore(MemoryStore):
    """MemoryTrace store with trace-metadata indices only."""

    def __init__(self, traces: Iterable[MemoryTrace] | None = None) -> None:
        self._by_source: dict[str, set[UUID]] = {}
        self._by_relation: dict[RelationType, set[UUID]] = {}
        self._by_target: dict[str, set[UUID]] = {}
        self._by_source_relation: dict[tuple[str, RelationType], set[UUID]] = {}
        self._trace_by_id: dict[UUID, MemoryTrace] = {}
        super().__init__(traces)

    def add(self, trace: MemoryTrace) -> MemoryTrace:
        trace = super().add(trace)
        proposition = trace.proposition
        self._trace_by_id[trace.trace_id] = trace
        self._by_source.setdefault(proposition.source_id, set()).add(trace.trace_id)
        self._by_relation.setdefault(proposition.relation_type, set()).add(trace.trace_id)
        self._by_target.setdefault(proposition.target_id, set()).add(trace.trace_id)
        self._by_source_relation.setdefault(
            (proposition.source_id, proposition.relation_type),
            set(),
        ).add(trace.trace_id)
        return trace

    def clear(self) -> None:
        super().clear()
        self._by_source.clear()
        self._by_relation.clear()
        self._by_target.clear()
        self._by_source_relation.clear()
        self._trace_by_id.clear()

    def retrieve(self, cue: RetrievalCue, limit: int | None = None) -> tuple[RetrievedTrace, ...]:
        return self.retrieve_with_metrics(cue, limit=limit).retrieved

    def retrieve_with_metrics(
        self,
        cue: RetrievalCue,
        limit: int | None = None,
    ) -> RetrievalResult:
        if cue.source_id is None and cue.relation_type is None and cue.target_id is None:
            return RetrievalResult(
                (),
                RetrievalMetrics(
                    stored_records=len(self.traces),
                    records_scanned=0,
                    index_candidates_considered=0,
                    records_returned=0,
                ),
            )
        candidate_ids: set[UUID] = set()
        if cue.source_id is not None and cue.relation_type is not None:
            candidate_ids.update(
                self._by_source_relation.get((cue.source_id, cue.relation_type), set())
            )
        if cue.source_id is not None:
            candidate_ids.update(self._by_source.get(cue.source_id, set()))
        if cue.relation_type is not None:
            candidate_ids.update(self._by_relation.get(cue.relation_type, set()))
        if cue.target_id is not None:
            candidate_ids.update(self._by_target.get(cue.target_id, set()))

        scored = []
        for trace_id in candidate_ids:
            trace = self._trace_by_id[trace_id]
            score = _score_trace(trace, cue)
            if score > 0.0:
                scored.append(RetrievedTrace(trace, score))
        scored.sort(
            key=lambda item: (
                -item.score,
                -item.trace.encoded_at_cycle_id,
                str(item.trace.trace_id),
            )
        )
        if limit is not None:
            scored = scored[:limit]
        retrieved = tuple(scored)
        return RetrievalResult(
            retrieved,
            RetrievalMetrics(
                stored_records=len(self.traces),
                records_scanned=len(candidate_ids),
                index_candidates_considered=len(candidate_ids),
                records_returned=len(retrieved),
                effective_evidence_used=len(retrieved),
            ),
        )


def _score_trace(trace: MemoryTrace, cue: RetrievalCue) -> float:
    score = 0.0
    requested = 0
    if cue.source_id is not None:
        requested += 1
        if trace.proposition.source_id == cue.source_id:
            score += 1.0
    if cue.relation_type is not None:
        requested += 1
        if trace.proposition.relation_type is cue.relation_type:
            score += 1.0
    if cue.target_id is not None:
        requested += 1
        if trace.proposition.target_id == cue.target_id:
            score += 1.0
    if requested == 0:
        return 0.0
    return score / requested


@dataclass(frozen=True, slots=True)
class ReconstructionDistortion:
    """Experiment-controlled reconstruction distortion."""

    omit: bool = False
    substitute_source_id: str | None = None
    substitute_target_id: str | None = None
    substitute_relation_type: RelationType | None = None
    confidence_multiplier: float = 1.0
    fidelity: float = 1.0
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.confidence_multiplier < 0.0:
            raise ValueError("confidence multiplier cannot be negative")
        if not 0.0 <= self.fidelity <= 1.0:
            raise ValueError("fidelity must be within [0, 1]")
        object.__setattr__(self, "tags", tuple(self.tags))


@dataclass(frozen=True, slots=True)
class MemoryReconstruction:
    reconstruction_id: UUID
    created_at_cycle_id: int
    proposition: Proposition
    source_trace_ids: tuple[UUID, ...]
    historical_source_cycles: tuple[int, ...]
    confidence: float
    fidelity: float
    distortion_tags: tuple[str, ...]
    provenance: TemporalSource = TemporalSource.RECONSTRUCTED_MEMORY

    def __post_init__(self) -> None:
        if self.provenance is not TemporalSource.RECONSTRUCTED_MEMORY:
            raise ValueError("reconstructions must use RECONSTRUCTED_MEMORY provenance")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("reconstruction confidence must be within [0, 1]")
        if not 0.0 <= self.fidelity <= 1.0:
            raise ValueError("reconstruction fidelity must be within [0, 1]")
        object.__setattr__(self, "source_trace_ids", tuple(self.source_trace_ids))
        object.__setattr__(
            self,
            "historical_source_cycles",
            tuple(self.historical_source_cycles),
        )
        object.__setattr__(self, "distortion_tags", tuple(self.distortion_tags))

    def to_dict(self) -> dict[str, Any]:
        return {
            "reconstruction_id": str(self.reconstruction_id),
            "created_at_cycle_id": self.created_at_cycle_id,
            "proposition": self.proposition.to_dict(),
            "source_trace_ids": [str(trace_id) for trace_id in self.source_trace_ids],
            "historical_source_cycles": list(self.historical_source_cycles),
            "confidence": self.confidence,
            "fidelity": self.fidelity,
            "distortion_tags": list(self.distortion_tags),
            "provenance": self.provenance.value,
        }


class MemoryReconstructor:
    """Deterministically creates present reconstructions from retrieved traces."""

    def __init__(self, decay_factor: float = 0.94, min_strength: float = 0.2) -> None:
        if not 0.0 <= decay_factor <= 1.0:
            raise ValueError("decay_factor must be within [0, 1]")
        if not 0.0 <= min_strength <= 1.0:
            raise ValueError("min_strength must be within [0, 1]")
        self.decay_factor = decay_factor
        self.min_strength = min_strength

    def reconstruct(
        self,
        retrieved: Iterable[RetrievedTrace],
        current_cycle_id: int,
        distortion: ReconstructionDistortion | None = None,
    ) -> tuple[MemoryReconstruction, ...]:
        reconstructions: list[MemoryReconstruction] = []
        distortion = distortion or ReconstructionDistortion()
        if distortion.omit:
            return ()
        for item in retrieved:
            trace = item.trace
            proposition = _distorted_proposition(trace.proposition, distortion)
            age = max(0, current_cycle_id - trace.encoded_at_cycle_id)
            decayed_strength = max(
                self.min_strength,
                trace.trace_strength * (self.decay_factor**age),
            )
            fidelity = distortion.fidelity
            confidence = _clamp(
                trace.encoded_confidence
                * decayed_strength
                * fidelity
                * distortion.confidence_multiplier
            )
            reconstructions.append(
                MemoryReconstruction(
                    reconstruction_id=uuid4(),
                    created_at_cycle_id=current_cycle_id,
                    proposition=proposition,
                    source_trace_ids=(trace.trace_id,),
                    historical_source_cycles=(trace.source_cycle_id,),
                    confidence=confidence,
                    fidelity=fidelity,
                    distortion_tags=distortion.tags,
                )
            )
        return tuple(reconstructions)

    def retrieve_and_reconstruct(
        self,
        store: MemoryStore,
        cue: RetrievalCue,
        current_cycle_id: int,
        limit: int | None = None,
        distortion: ReconstructionDistortion | None = None,
    ) -> tuple[MemoryReconstruction, ...]:
        return self.reconstruct(
            store.retrieve(cue, limit=limit),
            current_cycle_id=current_cycle_id,
            distortion=distortion,
        )


def _distorted_proposition(
    proposition: Proposition,
    distortion: ReconstructionDistortion,
) -> Proposition:
    return Proposition(
        source_id=distortion.substitute_source_id or proposition.source_id,
        relation_type=distortion.substitute_relation_type or proposition.relation_type,
        target_id=distortion.substitute_target_id or proposition.target_id,
        value=proposition.value,
        unit=proposition.unit,
    )


def encode_present_geometry(
    geometry: PresentGeometry,
    include_inferred: bool = False,
    trace_strength: float = 1.0,
    metadata: Mapping[str, Any] | None = None,
) -> tuple[MemoryTrace, ...]:
    traces: list[MemoryTrace] = []
    for relation in geometry.relations:
        if relation.provenance is Provenance.INFERRED_NOW and not include_inferred:
            continue
        if relation.provenance not in {Provenance.OBSERVED_NOW, Provenance.INFERRED_NOW}:
            continue
        traces.append(
            trace_from_relation(
                relation,
                source_cycle_id=geometry.cycle_id,
                encoded_at_cycle_id=geometry.cycle_id,
                trace_strength=trace_strength,
                metadata=metadata,
            )
        )
    return tuple(traces)


def trace_from_relation(
    relation: Relation,
    source_cycle_id: int,
    encoded_at_cycle_id: int,
    trace_strength: float = 1.0,
    metadata: Mapping[str, Any] | None = None,
) -> MemoryTrace:
    return MemoryTrace.create(
        source_cycle_id=source_cycle_id,
        encoded_at_cycle_id=encoded_at_cycle_id,
        proposition=Proposition.from_relation(relation),
        original_source=temporal_source_from_g1(relation.provenance),
        encoded_confidence=relation.confidence,
        trace_strength=trace_strength,
        metadata=metadata,
    )

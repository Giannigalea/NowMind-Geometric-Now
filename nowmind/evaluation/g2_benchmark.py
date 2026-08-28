from __future__ import annotations

import ast
import json
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from uuid import NAMESPACE_URL, UUID, uuid5

from nowmind.geometry.builder import PresentGeometryBuilder
from nowmind.geometry.relation import Provenance, RelationType
from nowmind.perception.adapter import PerceptionAdapter
from nowmind.reasoning.query import TruthStatus
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.now_state import TemporalNowState
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.query import EvidenceReference, TemporalAnswer, TemporalIntent, TemporalQuery
from nowmind.temporal.reasoner import TemporalReasoner
from nowmind.temporal.source import TemporalSource, source_label
from nowmind.world.events import AddEntity, SetRelation
from nowmind.world.model import WorldState


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "g2"
DEFAULT_SEED = 20260823
DEFAULT_TRIAL_COUNT = 1000
BENCHMARK_VERSION = "g2_temporal_source_benchmark_v1"


@dataclass(frozen=True, slots=True)
class TemporalRecord:
    cycle_id: int
    source: TemporalSource
    proposition: Proposition
    confidence: float
    record_id: str
    false_memory: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "source": self.source.value,
            "proposition": self.proposition.to_dict(),
            "confidence": self.confidence,
            "record_id": self.record_id,
            "false_memory": self.false_memory,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkTrial:
    trial_id: str
    family_id: str
    seed: int
    query: TemporalQuery
    temporal_now: TemporalNowState
    records: tuple[TemporalRecord, ...]
    expected_status: TruthStatus
    expected_source: TemporalSource | None
    expected_propositions: tuple[Proposition, ...]
    world_event_sequence: tuple[str, ...]
    false_memory_targets: tuple[str, ...] = field(default_factory=tuple)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "family_id": self.family_id,
            "seed": self.seed,
            "query": self.query.to_dict(),
            "expected_status": self.expected_status.value,
            "expected_source": source_label(self.expected_source),
            "expected_propositions": [
                proposition.to_dict() for proposition in self.expected_propositions
            ],
            "world_event_sequence": list(self.world_event_sequence),
            "current_observation": [
                record.to_dict()
                for record in self.records
                if record.source in {TemporalSource.OBSERVED_NOW, TemporalSource.INFERRED_NOW}
            ],
            "memory_reconstructions": [
                record.to_dict()
                for record in self.records
                if record.source is TemporalSource.RECONSTRUCTED_MEMORY
            ],
            "future_hypotheses": [
                record.to_dict()
                for record in self.records
                if record.source is TemporalSource.HYPOTHETICAL_FUTURE
            ],
            "false_memory_targets": list(self.false_memory_targets),
        }


@dataclass(frozen=True, slots=True)
class SystemOutput:
    system_id: str
    status: TruthStatus
    source: TemporalSource | None
    propositions: tuple[Proposition, ...]
    confidence: float
    explanation: str

    @classmethod
    def from_temporal_answer(
        cls,
        system_id: str,
        answer: TemporalAnswer,
    ) -> SystemOutput:
        return cls(
            system_id=system_id,
            status=answer.status,
            source=answer.source,
            propositions=answer.propositions,
            confidence=answer.confidence,
            explanation="; ".join(answer.explanation or answer.uncertainty_notes),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_id": self.system_id,
            "status": self.status.value,
            "source": source_label(self.source),
            "propositions": [proposition.to_dict() for proposition in self.propositions],
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    artifacts_dir: Path
    seed: int
    trial_count: int
    metrics: dict[str, dict[str, Any]]
    confusion_matrices: dict[str, dict[str, dict[str, int]]]
    invariant_results: dict[str, Any]
    failures: dict[str, list[dict[str, Any]]]

    @property
    def passed(self) -> bool:
        return self.invariant_results["summary"]["failed"] == 0


def run_benchmark(
    artifacts_dir: Path = DEFAULT_ARTIFACT_DIR,
    seed: int = DEFAULT_SEED,
    trial_count: int = DEFAULT_TRIAL_COUNT,
) -> BenchmarkResult:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    trials = generate_trials(seed=seed, trial_count=trial_count)
    systems = {
        "NowMindTemporalGeometry": _run_nowmind,
        "NaivePersistentState": _run_naive_persistent_state,
        "ChronologicalRecordReasoner": _run_chronological_record_reasoner,
    }
    outputs_by_system: dict[str, list[SystemOutput]] = {system: [] for system in systems}
    failures: dict[str, list[dict[str, Any]]] = {system: [] for system in systems}
    trial_rows: list[dict[str, Any]] = []

    for trial in trials:
        row = {"trial": trial.to_public_dict(), "systems": {}}
        for system_id, runner in systems.items():
            output = runner(trial)
            outputs_by_system[system_id].append(output)
            correct = _is_correct(output, trial)
            row["systems"][system_id] = {
                **output.to_dict(),
                "correct": correct,
            }
            if not correct and len(failures[system_id]) < 40:
                failures[system_id].append(_failure_sample(trial, output))
        trial_rows.append(row)

    metrics = {
        system_id: _compute_metrics(trials, outputs)
        for system_id, outputs in outputs_by_system.items()
    }
    confusion = {
        system_id: _source_confusion_matrix(trials, outputs)
        for system_id, outputs in outputs_by_system.items()
    }
    invariants = _build_invariant_results(trials, outputs_by_system)
    result = BenchmarkResult(
        artifacts_dir=artifacts_dir,
        seed=seed,
        trial_count=len(trials),
        metrics=metrics,
        confusion_matrices=confusion,
        invariant_results=invariants,
        failures=failures,
    )
    _write_artifacts(result, trials, trial_rows)
    return result


def generate_trials(seed: int, trial_count: int) -> tuple[BenchmarkTrial, ...]:
    rng = random.Random(seed)
    families = _family_generators()
    trials: list[BenchmarkTrial] = []
    for index in range(trial_count):
        family_id, generator = families[index % len(families)]
        trial_seed = rng.randint(1, 2_000_000_000)
        trial_rng = random.Random(trial_seed)
        trials.append(generator(index, trial_seed, trial_rng))
    return tuple(trials)


def _family_generators() -> tuple[tuple[str, Callable[[int, int, random.Random], BenchmarkTrial]], ...]:
    return (
        ("F1_stale_memory_after_update", _trial_f1),
        ("F2_false_memory", _trial_f2),
        ("F3_confidence_inversion", _trial_f3),
        ("F4_no_current_visibility", _trial_f4),
        ("F5_future_conflict", _trial_f5),
        ("F6_multiple_future_hypotheses", _trial_f6),
        ("F7_multiple_old_memories", _trial_f7),
        ("F8_distractors", _trial_f8),
        ("F9_contradictory_current_evidence", _trial_f9),
        ("F10_nested_containment_over_time", _trial_f10),
        ("F11_spatial_direction_changes", _trial_f11),
        ("F12_memory_age", _trial_f12),
        ("F13_hypothesis_matches_past", _trial_f13),
        ("F14_multiple_moves", _trial_f14),
        ("F15_inferred_present_vs_memory", _trial_f15),
        ("F16_occlusion", _trial_f16),
        ("F17_prediction_later_confirmed", _trial_f17),
        ("F18_prediction_later_falsified", _trial_f18),
    )


def _trial_f1(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F1_stale_memory_after_update",
        current_target="box_b",
        memory_targets=("box_a",),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_b",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("cycle 1: ball in box_a", "cycle 2: ball moved to box_b"),
    )


def _trial_f2(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F2_false_memory",
        current_target="box_b",
        memory_targets=("box_d",),
        false_memory_targets=("box_d",),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_b",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("current: ball in box_b", "injected false memory: ball in box_d"),
    )


def _trial_f3(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    current_confidence = rng.uniform(0.55, 0.75)
    memory_confidence = rng.uniform(0.85, 0.99)
    return _inside_trial(
        index,
        seed,
        "F3_confidence_inversion",
        current_target="box_b",
        current_confidence=current_confidence,
        memory_targets=("box_a",),
        memory_confidences=(memory_confidence,),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_b",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("current observation moderate confidence: B", "memory high confidence: A"),
    )


def _trial_f4(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F4_no_current_visibility",
        current_target=None,
        memory_targets=("box_a",),
        query_intent=TemporalIntent.NOW,
        expected_status=TruthStatus.UNKNOWN,
        expected_targets=(),
        expected_source=None,
        events=("current observation hidden", "memory reconstructs A"),
    )


def _trial_f5(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F5_future_conflict",
        current_target="box_b",
        future_targets=("box_c",),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_b",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("current: B", "hypothesis: C"),
    )


def _trial_f6(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F6_multiple_future_hypotheses",
        current_target="box_b",
        future_targets=("box_c", "box_d"),
        future_confidences=(0.6, 0.4),
        query_intent=TemporalIntent.POSSIBLE_FUTURE,
        expected_targets=("box_c", "box_d"),
        expected_source=TemporalSource.HYPOTHETICAL_FUTURE,
        events=("current: B", "hypotheses: C and D"),
    )


def _trial_f7(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F7_multiple_old_memories",
        current_target="box_c",
        memory_targets=("box_a", "box_b"),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_c",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("past: A", "past: B", "current: C"),
    )


def _trial_f8(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    trial = _inside_trial(
        index,
        seed,
        "F8_distractors",
        current_target="box_b",
        memory_targets=("box_a",),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_b",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("current: B", "irrelevant distractor relations present"),
        distractors=True,
    )
    return trial


def _trial_f9(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F9_contradictory_current_evidence",
        current_target=("box_b", "box_c"),
        memory_targets=("box_a",),
        query_intent=TemporalIntent.NOW,
        expected_status=TruthStatus.CONTRADICTORY,
        expected_targets=(),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("current conflicting observations: B and C"),
    )


def _trial_f10(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    current = (
        Proposition("key", RelationType.INSIDE, "box_b"),
        Proposition("box_b", RelationType.INSIDE, "cabinet"),
    )
    memories = (Proposition("key", RelationType.INSIDE, "box_a"),)
    query = TemporalQuery.relation("key", RelationType.INSIDE, "cabinet", TemporalIntent.NOW)
    return _build_trial(
        index,
        seed,
        "F10_nested_containment_over_time",
        query,
        current,
        memories,
        (),
        expected_status=TruthStatus.TRUE,
        expected_source=TemporalSource.INFERRED_NOW,
        expected_propositions=(Proposition("key", RelationType.INSIDE, "cabinet"),),
        events=("past: key in box_a", "current: key in box_b inside cabinet"),
    )


def _trial_f11(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    query = TemporalQuery.relation("a", RelationType.RIGHT_OF, "b", TemporalIntent.NOW)
    return _build_trial(
        index,
        seed,
        "F11_spatial_direction_changes",
        query,
        (Proposition("a", RelationType.RIGHT_OF, "b"),),
        (Proposition("a", RelationType.LEFT_OF, "b"),),
        (),
        expected_status=TruthStatus.TRUE,
        expected_source=TemporalSource.OBSERVED_NOW,
        expected_propositions=(Proposition("a", RelationType.RIGHT_OF, "b"),),
        events=("past: a left_of b", "current: a right_of b"),
    )


def _trial_f12(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    query = TemporalQuery.relation("ball", RelationType.INSIDE, "box_a", TemporalIntent.PAST)
    return _inside_trial(
        index,
        seed,
        "F12_memory_age",
        current_target=None,
        memory_targets=("box_a",),
        memory_cycles=(1,),
        query_intent=TemporalIntent.PAST,
        query_target="box_a",
        expected_targets=("box_a",),
        expected_source=TemporalSource.RECONSTRUCTED_MEMORY,
        events=("old memory: A with deterministic age degradation",),
        query_override=query,
    )


def _trial_f13(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F13_hypothesis_matches_past",
        current_target="box_b",
        memory_targets=("box_a",),
        future_targets=("box_a",),
        query_intent=TemporalIntent.POSSIBLE_FUTURE,
        query_target="box_a",
        expected_targets=("box_a",),
        expected_source=TemporalSource.HYPOTHETICAL_FUTURE,
        events=("past memory: A", "current: B", "future hypothesis also says A"),
    )


def _trial_f14(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    sequence = tuple(rng.choice(("box_a", "box_b", "box_c", "box_d")) for _ in range(5))
    current = sequence[-1]
    memories = tuple(sequence[:-1])
    return _inside_trial(
        index,
        seed,
        "F14_multiple_moves",
        current_target=current,
        memory_targets=memories,
        query_intent=TemporalIntent.NOW,
        expected_targets=(current,),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=tuple(f"cycle {i + 1}: ball in {target}" for i, target in enumerate(sequence)),
    )


def _trial_f15(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    query = TemporalQuery.relation("a", RelationType.LEFT_OF, "c", TemporalIntent.NOW)
    return _build_trial(
        index,
        seed,
        "F15_inferred_present_vs_memory",
        query,
        (
            Proposition("a", RelationType.LEFT_OF, "b"),
            Proposition("b", RelationType.LEFT_OF, "c"),
        ),
        (Proposition("a", RelationType.RIGHT_OF, "c"),),
        (),
        expected_status=TruthStatus.TRUE,
        expected_source=TemporalSource.INFERRED_NOW,
        expected_propositions=(Proposition("a", RelationType.LEFT_OF, "c"),),
        events=("past memory: a right_of c", "current observation implies a left_of c"),
    )


def _trial_f16(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F16_occlusion",
        current_target=None,
        memory_targets=("box_b",),
        query_intent=TemporalIntent.NOW,
        expected_status=TruthStatus.UNKNOWN,
        expected_targets=(),
        expected_source=None,
        events=("current fact removed from visibility", "latest memory says B"),
    )


def _trial_f17(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F17_prediction_later_confirmed",
        current_target="box_c",
        future_targets=("box_c",),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_c",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("previous hypothesis: C", "later real observation confirms C"),
    )


def _trial_f18(index: int, seed: int, rng: random.Random) -> BenchmarkTrial:
    return _inside_trial(
        index,
        seed,
        "F18_prediction_later_falsified",
        current_target="box_d",
        future_targets=("box_c",),
        query_intent=TemporalIntent.NOW,
        expected_targets=("box_d",),
        expected_source=TemporalSource.OBSERVED_NOW,
        events=("previous hypothesis: C", "actual later observation: D"),
    )


def _inside_trial(
    index: int,
    seed: int,
    family_id: str,
    current_target: str | tuple[str, ...] | None,
    memory_targets: tuple[str, ...] = (),
    future_targets: tuple[str, ...] = (),
    query_intent: TemporalIntent = TemporalIntent.NOW,
    query_target: str | None = None,
    expected_status: TruthStatus = TruthStatus.TRUE,
    expected_targets: tuple[str, ...] = (),
    expected_source: TemporalSource | None = TemporalSource.OBSERVED_NOW,
    events: tuple[str, ...] = (),
    current_confidence: float = 1.0,
    memory_confidences: tuple[float, ...] | None = None,
    future_confidences: tuple[float, ...] | None = None,
    memory_cycles: tuple[int, ...] | None = None,
    false_memory_targets: tuple[str, ...] = (),
    distractors: bool = False,
    query_override: TemporalQuery | None = None,
) -> BenchmarkTrial:
    current: list[Proposition] = []
    current_confidences: list[float] = []
    targets = current_target if isinstance(current_target, tuple) else (current_target,)
    for target in targets:
        if target is not None:
            current.append(Proposition("ball", RelationType.INSIDE, target))
            current_confidences.append(current_confidence)
    if distractors:
        current.append(Proposition("spoon", RelationType.INSIDE, "box_d"))
        current_confidences.append(1.0)
    memories = tuple(Proposition("ball", RelationType.INSIDE, target) for target in memory_targets)
    futures = tuple(Proposition("ball", RelationType.INSIDE, target) for target in future_targets)
    query = query_override or TemporalQuery.relation(
        "ball",
        RelationType.INSIDE,
        query_target,
        query_intent,
    )
    expected = tuple(
        Proposition("ball", RelationType.INSIDE, target) for target in expected_targets
    )
    return _build_trial(
        index,
        seed,
        family_id,
        query,
        tuple(current),
        memories,
        futures,
        expected_status=expected_status,
        expected_source=expected_source,
        expected_propositions=expected,
        events=events,
        current_confidences=tuple(current_confidences),
        memory_confidences=memory_confidences,
        future_confidences=future_confidences,
        memory_cycles=memory_cycles,
        false_memory_targets=false_memory_targets,
    )


def _build_trial(
    index: int,
    seed: int,
    family_id: str,
    query: TemporalQuery,
    current_propositions: tuple[Proposition, ...],
    memory_propositions: tuple[Proposition, ...],
    future_propositions: tuple[Proposition, ...],
    expected_status: TruthStatus,
    expected_source: TemporalSource | None,
    expected_propositions: tuple[Proposition, ...],
    events: tuple[str, ...],
    current_confidences: tuple[float, ...] | None = None,
    memory_confidences: tuple[float, ...] | None = None,
    future_confidences: tuple[float, ...] | None = None,
    memory_cycles: tuple[int, ...] | None = None,
    false_memory_targets: tuple[str, ...] = (),
) -> BenchmarkTrial:
    trial_id = f"g2-{index:05d}-{family_id}"
    cycle_id = 10
    current_confidences = current_confidences or tuple(1.0 for _ in current_propositions)
    memory_confidences = memory_confidences or tuple(0.95 for _ in memory_propositions)
    future_confidences = future_confidences or tuple(0.6 for _ in future_propositions)
    memory_cycles = memory_cycles or tuple(range(1, len(memory_propositions) + 1))
    geometry = _geometry_from_propositions(
        cycle_id=cycle_id,
        propositions=current_propositions,
        confidences=current_confidences,
    )
    memories = tuple(
        MemoryReconstruction(
            reconstruction_id=_stable_uuid(trial_id, "memory", str(i)),
            created_at_cycle_id=cycle_id,
            proposition=proposition,
            source_trace_ids=(_stable_uuid(trial_id, "trace", str(i)),),
            historical_source_cycles=(memory_cycles[i],),
            confidence=memory_confidences[i],
            fidelity=0.96,
            distortion_tags=(
                ("injected_false_memory",)
                if proposition.target_id in false_memory_targets
                else ()
            ),
        )
        for i, proposition in enumerate(memory_propositions)
    )
    futures = tuple(
        FutureHypothesis(
            hypothesis_id=_stable_uuid(trial_id, "future", str(i)),
            created_at_cycle_id=cycle_id,
            proposition=proposition,
            confidence=future_confidences[i],
            generator_id="benchmark_symbolic_hypothesis",
            metadata={"benchmark_family": family_id},
        )
        for i, proposition in enumerate(future_propositions)
    )
    temporal_now = TemporalNowState(
        now_id=_stable_uuid(trial_id, "now"),
        cycle_id=cycle_id,
        created_at=datetime(2026, 8, 23, tzinfo=UTC),
        present_geometry=geometry,
        reconstructed_memories=memories,
        future_hypotheses=futures,
    )
    records = _records_from_now(
        trial_id,
        temporal_now,
        false_memory_targets=false_memory_targets,
    )
    return BenchmarkTrial(
        trial_id=trial_id,
        family_id=family_id,
        seed=seed,
        query=query,
        temporal_now=temporal_now,
        records=records,
        expected_status=expected_status,
        expected_source=expected_source,
        expected_propositions=expected_propositions,
        world_event_sequence=events,
        false_memory_targets=false_memory_targets,
    )


def _geometry_from_propositions(
    cycle_id: int,
    propositions: tuple[Proposition, ...],
    confidences: tuple[float, ...],
):
    world = WorldState()
    entity_ids: set[str] = {"ball", "key", "a", "b", "c", "spoon"}
    for proposition in propositions:
        entity_ids.add(proposition.source_id)
        entity_ids.add(proposition.target_id)
    for box in ("box_a", "box_b", "box_c", "box_d", "cabinet"):
        entity_ids.add(box)
    for entity_id in sorted(entity_ids):
        kind = "container" if entity_id.startswith("box") or entity_id == "cabinet" else "object"
        world.apply(AddEntity(entity_id, kind, entity_id))
    for proposition, confidence in zip(propositions, confidences, strict=True):
        world.apply(
            SetRelation(
                proposition.source_id,
                proposition.target_id,
                proposition.relation_type,
                confidence,
            )
        )
    observation = PerceptionAdapter().observe(world, cycle_id)
    return PresentGeometryBuilder().build(observation)


def _records_from_now(
    trial_id: str,
    now: TemporalNowState,
    false_memory_targets: tuple[str, ...],
) -> tuple[TemporalRecord, ...]:
    records: list[TemporalRecord] = []
    for relation in now.present_geometry.relations:
        source = (
            TemporalSource.OBSERVED_NOW
            if relation.provenance is Provenance.OBSERVED_NOW
            else TemporalSource.INFERRED_NOW
        )
        records.append(
            TemporalRecord(
                cycle_id=now.cycle_id,
                source=source,
                proposition=Proposition.from_relation(relation),
                confidence=relation.confidence,
                record_id=f"{trial_id}:{relation.relation_id}",
            )
        )
    for memory in now.reconstructed_memories:
        records.append(
            TemporalRecord(
                cycle_id=memory.historical_source_cycles[0],
                source=TemporalSource.RECONSTRUCTED_MEMORY,
                proposition=memory.proposition,
                confidence=memory.confidence,
                record_id=f"{trial_id}:{memory.reconstruction_id}",
                false_memory=memory.proposition.target_id in false_memory_targets,
            )
        )
    for future in now.future_hypotheses:
        records.append(
            TemporalRecord(
                cycle_id=future.created_at_cycle_id,
                source=TemporalSource.HYPOTHETICAL_FUTURE,
                proposition=future.proposition,
                confidence=future.confidence,
                record_id=f"{trial_id}:{future.hypothesis_id}",
            )
        )
    return tuple(records)


def _run_nowmind(trial: BenchmarkTrial) -> SystemOutput:
    answer = TemporalReasoner(reliability_threshold=0.5).answer(
        trial.temporal_now,
        trial.query,
    )
    return SystemOutput.from_temporal_answer("NowMindTemporalGeometry", answer)


def _run_naive_persistent_state(trial: BenchmarkTrial) -> SystemOutput:
    matching = _matching_records(trial.records, trial.query, allowed_sources=None)
    if trial.query.intent is TemporalIntent.POSSIBLE_FUTURE:
        futures = [
            record
            for record in matching
            if record.source is TemporalSource.HYPOTHETICAL_FUTURE
        ]
        if futures:
            return _output_from_records("NaivePersistentState", futures, "Uses matching future records.")
    if not matching:
        return SystemOutput(
            "NaivePersistentState",
            TruthStatus.UNKNOWN,
            None,
            (),
            0.0,
            "No matching persistent record.",
        )
    chosen = matching[-1]
    return SystemOutput(
        "NaivePersistentState",
        TruthStatus.TRUE,
        chosen.source,
        (chosen.proposition,),
        chosen.confidence,
        "Deliberately simple persistent belief chose the latest matching incoming record.",
    )


def _run_chronological_record_reasoner(trial: BenchmarkTrial) -> SystemOutput:
    if trial.query.intent is TemporalIntent.NOW:
        current = _matching_records(
            trial.records,
            trial.query,
            allowed_sources={TemporalSource.OBSERVED_NOW, TemporalSource.INFERRED_NOW},
        )
        conflict = _record_target_conflict(current, trial.query)
        if conflict:
            return SystemOutput(
                "ChronologicalRecordReasoner",
                TruthStatus.CONTRADICTORY,
                TemporalSource.OBSERVED_NOW,
                (),
                0.0,
                conflict,
            )
        if current:
            return _output_from_records(
                "ChronologicalRecordReasoner",
                [max(current, key=lambda item: item.confidence)],
                "NOW query used current chronological records only.",
            )
        return SystemOutput(
            "ChronologicalRecordReasoner",
            TruthStatus.UNKNOWN,
            None,
            (),
            0.0,
            "No current chronological record.",
        )
    if trial.query.intent is TemporalIntent.PAST:
        records = _matching_records(
            trial.records,
            trial.query,
            allowed_sources={TemporalSource.RECONSTRUCTED_MEMORY},
        )
        if records:
            return _output_from_records(
                "ChronologicalRecordReasoner",
                [max(records, key=lambda item: item.confidence)],
                "PAST query used reconstructed historical records.",
            )
    if trial.query.intent is TemporalIntent.POSSIBLE_FUTURE:
        records = _matching_records(
            trial.records,
            trial.query,
            allowed_sources={TemporalSource.HYPOTHETICAL_FUTURE},
        )
        if records:
            return _output_from_records(
                "ChronologicalRecordReasoner",
                records,
                "Future query preserved all matching hypothesis records.",
            )
    return SystemOutput(
        "ChronologicalRecordReasoner",
        TruthStatus.UNKNOWN,
        None,
        (),
        0.0,
        "No matching source-safe chronological record.",
    )


def _matching_records(
    records: tuple[TemporalRecord, ...],
    query: TemporalQuery,
    allowed_sources: set[TemporalSource] | None,
) -> list[TemporalRecord]:
    matches = []
    for record in records:
        if allowed_sources is not None and record.source not in allowed_sources:
            continue
        if not record.proposition.matches(
            source_id=query.source_id,
            relation_type=query.relation_type,
            target_id=query.target_id,
        ):
            continue
        matches.append(record)
    return matches


def _record_target_conflict(records: list[TemporalRecord], query: TemporalQuery) -> str | None:
    if query.relation_type is not RelationType.INSIDE:
        return None
    observed = [record for record in records if record.source is TemporalSource.OBSERVED_NOW]
    targets = sorted({record.proposition.target_id for record in observed})
    if len(targets) <= 1:
        return None
    return f"Conflicting current targets: {', '.join(targets)}"


def _output_from_records(
    system_id: str,
    records: list[TemporalRecord],
    explanation: str,
) -> SystemOutput:
    confidence = max(record.confidence for record in records)
    source = records[0].source if records else None
    return SystemOutput(
        system_id,
        TruthStatus.TRUE,
        source,
        tuple(record.proposition for record in records),
        confidence,
        explanation,
    )


def _is_correct(output: SystemOutput, trial: BenchmarkTrial) -> bool:
    if output.status is not trial.expected_status:
        return False
    if output.status is not TruthStatus.TRUE:
        return output.source is trial.expected_source
    if output.source is not trial.expected_source:
        return False
    return _proposition_keys(output.propositions) == _proposition_keys(
        trial.expected_propositions
    )


def _compute_metrics(
    trials: tuple[BenchmarkTrial, ...],
    outputs: list[SystemOutput],
) -> dict[str, Any]:
    by_intent = {
        TemporalIntent.NOW: [],
        TemporalIntent.PAST: [],
        TemporalIntent.POSSIBLE_FUTURE: [],
    }
    correct_by_intent = {key: 0 for key in by_intent}
    correct_total = 0
    source_correct = 0
    stale_memory_as_current = 0
    false_memory_contamination = 0
    prediction_as_fact = 0
    unsupported_current_claim = 0
    expected_unknown = 0
    correct_unknown = 0
    expected_contradictions = 0
    detected_contradictions = 0

    for trial, output in zip(trials, outputs, strict=True):
        correct = _is_correct(output, trial)
        correct_total += int(correct)
        if output.source is trial.expected_source:
            source_correct += 1
        if trial.query.intent in by_intent:
            by_intent[trial.query.intent].append(trial)
            correct_by_intent[trial.query.intent] += int(correct)
        output_targets = {proposition.target_id for proposition in output.propositions}
        memory_targets = {
            record.proposition.target_id
            for record in trial.records
            if record.source is TemporalSource.RECONSTRUCTED_MEMORY
        }
        future_targets = {
            record.proposition.target_id
            for record in trial.records
            if record.source is TemporalSource.HYPOTHETICAL_FUTURE
        }
        if trial.query.intent is TemporalIntent.NOW and output.status is TruthStatus.TRUE:
            if output.source is TemporalSource.RECONSTRUCTED_MEMORY or (
                output_targets & memory_targets
                and not output_targets
                <= {item.target_id for item in trial.expected_propositions}
            ):
                stale_memory_as_current += 1
            if output_targets & set(trial.false_memory_targets):
                false_memory_contamination += 1
            if output.source is TemporalSource.HYPOTHETICAL_FUTURE or (
                output_targets & future_targets
                and not output_targets
                <= {item.target_id for item in trial.expected_propositions}
            ):
                prediction_as_fact += 1
        if trial.expected_status is TruthStatus.UNKNOWN:
            expected_unknown += 1
            if output.status is TruthStatus.UNKNOWN:
                correct_unknown += 1
            elif trial.query.intent is TemporalIntent.NOW:
                unsupported_current_claim += 1
        if trial.expected_status is TruthStatus.CONTRADICTORY:
            expected_contradictions += 1
            if output.status is TruthStatus.CONTRADICTORY:
                detected_contradictions += 1

    return {
        "current_state_accuracy": _rate(
            correct_by_intent[TemporalIntent.NOW],
            len(by_intent[TemporalIntent.NOW]),
        ),
        "past_state_accuracy": _rate(
            correct_by_intent[TemporalIntent.PAST],
            len(by_intent[TemporalIntent.PAST]),
        ),
        "future_query_accuracy": _rate(
            correct_by_intent[TemporalIntent.POSSIBLE_FUTURE],
            len(by_intent[TemporalIntent.POSSIBLE_FUTURE]),
        ),
        "temporal_source_classification_accuracy": _rate(source_correct, len(trials)),
        "stale_memory_as_current_count": stale_memory_as_current,
        "stale_memory_as_current_rate": _rate(stale_memory_as_current, len(trials)),
        "false_memory_contamination_count": false_memory_contamination,
        "false_memory_contamination_rate": _rate(false_memory_contamination, len(trials)),
        "prediction_as_fact_count": prediction_as_fact,
        "prediction_as_fact_rate": _rate(prediction_as_fact, len(trials)),
        "unsupported_current_claim_count": unsupported_current_claim,
        "unsupported_current_claim_rate": _rate(unsupported_current_claim, len(trials)),
        "correct_unknown_rate": _rate(correct_unknown, expected_unknown),
        "contradiction_detection_rate": _rate(
            detected_contradictions,
            expected_contradictions,
        ),
        "overall_query_accuracy": _rate(correct_total, len(trials)),
    }


def _source_confusion_matrix(
    trials: tuple[BenchmarkTrial, ...],
    outputs: list[SystemOutput],
) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = {}
    for trial, output in zip(trials, outputs, strict=True):
        expected = source_label(trial.expected_source)
        actual = source_label(output.source)
        matrix.setdefault(expected, {})
        matrix[expected][actual] = matrix[expected].get(actual, 0) + 1
    return matrix


def _build_invariant_results(
    trials: tuple[BenchmarkTrial, ...],
    outputs_by_system: dict[str, list[SystemOutput]],
) -> dict[str, Any]:
    family_ids = {trial.family_id for trial in trials}
    required_families = {family_id for family_id, _ in _family_generators()}
    checks = [
        _pass_fail("Minimum 1,000 trials generated", len(trials) >= 1000),
        _pass_fail("All required families represented", required_families <= family_ids),
        _pass_fail(
            "Both baselines evaluated",
            {"NaivePersistentState", "ChronologicalRecordReasoner"} <= set(outputs_by_system),
        ),
        _pass_fail("Metrics derive from trial outputs", all(outputs_by_system.values())),
        _pass_fail("Temporal runtime does not import evaluation", _temporal_import_firewall()),
    ]
    failed = sum(1 for check in checks if check["status"] != "PASS")
    return {
        "schema": "nowmind.g2.invariant_results.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
    }


def _temporal_import_firewall() -> bool:
    root = PROJECT_ROOT / "nowmind" / "temporal"
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (
                node.module or ""
            ).startswith("nowmind.evaluation"):
                return False
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("nowmind.evaluation"):
                        return False
    return True


def _write_artifacts(
    result: BenchmarkResult,
    trials: tuple[BenchmarkTrial, ...],
    trial_rows: list[dict[str, Any]],
) -> None:
    config = {
        "schema": "nowmind.g2.seed_and_config.v1",
        "benchmark_version": BENCHMARK_VERSION,
        "seed": result.seed,
        "trial_count": result.trial_count,
        "family_count": len(_family_generators()),
        "families": [family_id for family_id, _ in _family_generators()],
        "difficulty": {
            "distractors": "family-specific",
            "memory_confidence": "0.85-0.99 for confidence inversion; otherwise fixed",
            "observation_confidence": "0.55-0.75 for confidence inversion; otherwise fixed",
            "sequence_length": "5 for F14, family-specific elsewhere",
        },
    }
    _write_json(result.artifacts_dir / "g2_metrics.json", result.metrics)
    _write_json(result.artifacts_dir / "g2_source_confusion_matrix.json", result.confusion_matrices)
    _write_json(result.artifacts_dir / "g2_failure_samples.json", result.failures)
    _write_json(result.artifacts_dir / "g2_invariant_results.json", result.invariant_results)
    _write_json(result.artifacts_dir / "g2_seed_and_config.json", config)
    _write_jsonl(result.artifacts_dir / "g2_trial_results.jsonl", trial_rows)
    (result.artifacts_dir / "g2_baseline_rules.md").write_text(_baseline_rules(), encoding="utf-8")
    (result.artifacts_dir / "g2_benchmark_summary.md").write_text(
        _summary_markdown(result, trials),
        encoding="utf-8",
    )


def _summary_markdown(result: BenchmarkResult, trials: tuple[BenchmarkTrial, ...]) -> str:
    lines = [
        "# G2 Benchmark Summary",
        "",
        (
            "These synthetic symbolic benchmarks evaluate architecture and "
            "temporal-source handling. They are not evidence of consciousness and "
            "are not yet a comparison against state-of-the-art LLM agents."
        ),
        "",
        f"- Seed: {result.seed}",
        f"- Trial count: {result.trial_count}",
        f"- Families represented: {len({trial.family_id for trial in trials})}",
        "",
        "| System | Overall | Current | Past | Future | Stale-as-current | False-memory | Prediction-as-fact |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for system_id, metrics in result.metrics.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    system_id,
                    f"{metrics['overall_query_accuracy']:.3f}",
                    f"{metrics['current_state_accuracy']:.3f}",
                    f"{metrics['past_state_accuracy']:.3f}",
                    f"{metrics['future_query_accuracy']:.3f}",
                    str(metrics["stale_memory_as_current_count"]),
                    str(metrics["false_memory_contamination_count"]),
                    str(metrics["prediction_as_fact_count"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Failures are preserved in `g2_failure_samples.json` for NowMind and both baselines.",
        ]
    )
    return "\n".join(lines) + "\n"


def _baseline_rules() -> str:
    return """# G2 Baseline Rules

## NaivePersistentState

This deliberately simple baseline keeps the latest matching symbolic record from
the incoming record stream as active belief, regardless of whether that record
came from current observation, reconstructed memory, or a future hypothesis. It
is included to stress stale state and source-confusion failures. It is not a
state-of-the-art baseline.

## ChronologicalRecordReasoner

This stronger symbolic control receives chronological records with explicit
source labels. For NOW queries it uses only current observed/inferred records and
detects multiple current containment targets as contradiction. For PAST queries
it uses reconstructed-memory records. For POSSIBLE_FUTURE queries it uses future
hypothesis records and preserves multiple possibilities.

If this control matches or beats NowMind, the result should be reported as such.
"""


def _failure_sample(trial: BenchmarkTrial, output: SystemOutput) -> dict[str, Any]:
    return {
        "trial": trial.to_public_dict(),
        "actual": output.to_dict(),
        "reason": "Output did not match expected status/source/proposition set.",
    }


def _proposition_keys(propositions: tuple[Proposition, ...]) -> set[tuple[str, str, str]]:
    return {
        (item.source_id, item.relation_type.value, item.target_id)
        for item in propositions
    }


def _stable_uuid(*parts: str) -> UUID:
    return uuid5(NAMESPACE_URL, ":".join(parts))


def _pass_fail(name: str, passed: bool) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if passed else "FAIL"}


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

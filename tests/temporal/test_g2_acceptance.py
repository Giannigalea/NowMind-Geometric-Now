from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import pytest

from nowmind.core.cycle import CognitiveCycleRunner
from nowmind.evaluation.g2_distortion import make_false_memory_trace, seeded_distortion
from nowmind.evaluation.recorder import ExperimentRecorder
from nowmind.geometry.relation import RelationType
from nowmind.reasoning.query import TruthStatus
from nowmind.temporal import (
    FutureHypothesis,
    MemoryReconstructor,
    MemoryStore,
    MemoryTrace,
    Proposition,
    RetrievalCue,
    TemporalCycleRunner,
    TemporalIntent,
    TemporalNowState,
    TemporalQuery,
    TemporalSource,
    answer_temporal,
)
from nowmind.temporal.memory import encode_present_geometry
from nowmind.world.events import AddEntity, RemoveRelation, SetRelation
from nowmind.world.model import WorldState


def _ball_world(target_id: str | None, confidence: float = 1.0) -> WorldState:
    world = WorldState()
    for entity_id, kind in (
        ("ball", "object"),
        ("box_a", "container"),
        ("box_b", "container"),
        ("box_c", "container"),
        ("box_d", "container"),
    ):
        world.apply(AddEntity(entity_id, kind, entity_id))
    if target_id is not None:
        world.apply(SetRelation("ball", target_id, RelationType.INSIDE, confidence))
    return world


def _trace(
    target_id: str,
    confidence: float = 0.95,
    source_cycle_id: int = 1,
    encoded_at_cycle_id: int = 1,
) -> MemoryTrace:
    return MemoryTrace.create(
        source_cycle_id=source_cycle_id,
        encoded_at_cycle_id=encoded_at_cycle_id,
        proposition=Proposition("ball", RelationType.INSIDE, target_id),
        original_source=TemporalSource.OBSERVED_NOW,
        encoded_confidence=confidence,
        trace_strength=1.0,
    )


def _memory_store(*targets: str) -> MemoryStore:
    store = MemoryStore()
    for index, target in enumerate(targets, start=1):
        store.add(_trace(target, source_cycle_id=index, encoded_at_cycle_id=index))
    return store


def _cue(target_id: str | None = None) -> RetrievalCue:
    return RetrievalCue.for_relation(
        "ball",
        RelationType.INSIDE,
        target_id=target_id,
        temporal_intent=TemporalIntent.PAST.value,
    )


def test_g2_now_state_is_fresh_immutable_and_has_no_previous_state_reference() -> None:
    runner = TemporalCycleRunner()
    world = _ball_world("box_a")

    first = runner.run(world)
    second = runner.run(world)

    assert first.now_id != second.now_id
    assert first.cycle_id != second.cycle_id
    with pytest.raises(FrozenInstanceError):
        first.cycle_id = 99  # type: ignore[misc]
    forbidden = {"previous_now", "previous_temporal_now", "history", "raw_history"}
    assert forbidden.isdisjoint({field.name for field in fields(TemporalNowState)})


def test_g2_present_geometry_is_rebuilt_from_current_observation() -> None:
    runner = TemporalCycleRunner()
    world = _ball_world("box_a")

    first = runner.run(world)
    world.apply(RemoveRelation("ball", "box_a", RelationType.INSIDE))
    world.apply(SetRelation("ball", "box_b", RelationType.INSIDE))
    second = runner.run(world)

    assert first.present_geometry.find_relation("ball", "box_a", RelationType.INSIDE)
    assert second.present_geometry.find_relation("ball", "box_b", RelationType.INSIDE)
    assert second.present_geometry.find_relation("ball", "box_a", RelationType.INSIDE) is None


def test_g2_memory_trace_and_store_firewall() -> None:
    g1_now = CognitiveCycleRunner().run(_ball_world("box_a"))

    with pytest.raises(ValueError):
        MemoryTrace.create(
            source_cycle_id=1,
            encoded_at_cycle_id=1,
            proposition=Proposition("ball", RelationType.INSIDE, "box_a"),
            original_source=TemporalSource.OBSERVED_NOW,
            encoded_confidence=1.0,
            metadata={"raw_now": g1_now},
        )

    store = MemoryStore()
    trace = _trace("box_a")
    store.add(trace)
    with pytest.raises(TypeError):
        store.add(g1_now)  # type: ignore[arg-type]
    assert store.traces == (trace,)


def test_g2_temporal_runtime_does_not_import_evaluation_history() -> None:
    root = Path(__file__).parents[2] / "nowmind" / "temporal"
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.module is None or not node.module.startswith("nowmind.evaluation")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("nowmind.evaluation")


def test_g2_researcher_history_deletion_does_not_delete_memory_traces() -> None:
    store = _memory_store("box_a")
    runner = TemporalCycleRunner(next_cycle_id=2, memory_store=store)
    recorder = ExperimentRecorder()
    recorder.delete_logs()

    first = runner.run(_ball_world("box_b"), memory_cue=_cue("box_a"))
    recorder.record(CognitiveCycleRunner().run(_ball_world("box_b")), None, None)  # type: ignore[arg-type]
    recorder.delete_logs()
    second = runner.run(_ball_world("box_b"), memory_cue=_cue("box_a"))

    assert first.reconstructed_memories
    assert second.reconstructed_memories
    assert store.traces
    assert not recorder.history


def test_g2_deleting_actual_memory_traces_removes_reconstruction() -> None:
    store = _memory_store("box_a")
    runner = TemporalCycleRunner(next_cycle_id=2, memory_store=store)
    with_memory = runner.run(_ball_world("box_b"), memory_cue=_cue("box_a"))

    store.clear()
    without_memory = runner.run(_ball_world("box_b"), memory_cue=_cue("box_a"))

    assert with_memory.reconstructed_memories
    assert without_memory.reconstructed_memories == ()


def test_g2_reconstruction_is_new_provenanced_bounded_and_distortable() -> None:
    store = _memory_store("box_a")
    reconstructor = MemoryReconstructor()
    retrieved = store.retrieve(_cue("box_a"))
    first = reconstructor.reconstruct(retrieved, current_cycle_id=4)
    second = reconstructor.reconstruct(retrieved, current_cycle_id=4)

    assert first[0].reconstruction_id != second[0].reconstruction_id
    assert first[0].provenance is TemporalSource.RECONSTRUCTED_MEMORY
    assert first[0].source_trace_ids == (store.traces[0].trace_id,)
    assert first[0].historical_source_cycles == (1,)
    assert 0.0 <= first[0].confidence <= 1.0
    assert 0.0 <= first[0].fidelity <= 1.0

    distortion = seeded_distortion(123)
    repeat = seeded_distortion(123)
    assert distortion == repeat
    distorted = reconstructor.reconstruct(retrieved, current_cycle_id=4, distortion=distortion)
    assert distorted == () or distorted[0].provenance is TemporalSource.RECONSTRUCTED_MEMORY


def test_g2_reconstructed_memory_is_not_promoted_to_observed_now() -> None:
    store = _memory_store("box_a")
    now = TemporalCycleRunner(next_cycle_id=2, memory_store=store).run(
        _ball_world(None),
        memory_cue=_cue("box_a"),
    )
    answer = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, "box_a", TemporalIntent.NOW),
    )

    assert now.reconstructed_memories[0].provenance is TemporalSource.RECONSTRUCTED_MEMORY
    assert now.present_geometry.find_relation("ball", "box_a", RelationType.INSIDE) is None
    assert answer.status is TruthStatus.UNKNOWN


def test_g2_future_hypothesis_source_firewalls_and_confirmation() -> None:
    hypothesis = FutureHypothesis.create(
        2,
        Proposition("ball", RelationType.INSIDE, "box_c"),
        confidence=0.7,
    )
    now = TemporalCycleRunner(next_cycle_id=2).run(
        _ball_world(None),
        future_hypotheses=(hypothesis,),
    )

    current = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, "box_c", TemporalIntent.NOW),
    )
    future = answer_temporal(
        now,
        TemporalQuery.relation(
            "ball",
            RelationType.INSIDE,
            "box_c",
            TemporalIntent.POSSIBLE_FUTURE,
        ),
    )
    traces = encode_present_geometry(now.present_geometry)

    assert hypothesis.provenance is TemporalSource.HYPOTHETICAL_FUTURE
    assert current.status is TruthStatus.UNKNOWN
    assert future.status is TruthStatus.TRUE
    assert future.source is TemporalSource.HYPOTHETICAL_FUTURE
    assert all(trace.proposition.target_id != "box_c" for trace in traces)

    confirmed = TemporalCycleRunner(next_cycle_id=3).run(_ball_world("box_c"))
    confirmed_answer = answer_temporal(
        confirmed,
        TemporalQuery.relation("ball", RelationType.INSIDE, "box_c", TemporalIntent.NOW),
    )
    assert confirmed_answer.source is TemporalSource.OBSERVED_NOW
    assert hypothesis.provenance is TemporalSource.HYPOTHETICAL_FUTURE

    falsified = TemporalCycleRunner(next_cycle_id=3).run(_ball_world("box_d"))
    falsified_answer = answer_temporal(
        falsified,
        TemporalQuery.relation("ball", RelationType.INSIDE, "box_d", TemporalIntent.NOW),
    )
    assert falsified_answer.source is TemporalSource.OBSERVED_NOW
    assert falsified_answer.propositions[0].target_id == "box_d"


def test_g2_temporal_reasoning_policies() -> None:
    store = _memory_store("box_a")
    future = FutureHypothesis.create(
        2,
        Proposition("ball", RelationType.INSIDE, "box_c"),
        confidence=0.6,
    )
    now = TemporalCycleRunner(next_cycle_id=2, memory_store=store).run(
        _ball_world("box_b", confidence=0.6),
        memory_cue=_cue(),
        future_hypotheses=(future,),
    )

    current = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, None, TemporalIntent.NOW),
    )
    past = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, "box_a", TemporalIntent.PAST),
    )
    future_answer = answer_temporal(
        now,
        TemporalQuery.relation(
            "ball",
            RelationType.INSIDE,
            "box_c",
            TemporalIntent.POSSIBLE_FUTURE,
        ),
    )

    assert current.status is TruthStatus.TRUE
    assert current.source is TemporalSource.OBSERVED_NOW
    assert current.propositions[0].target_id == "box_b"
    assert past.status is TruthStatus.TRUE
    assert past.source is TemporalSource.RECONSTRUCTED_MEMORY
    assert past.propositions[0].target_id == "box_a"
    assert future_answer.status is TruthStatus.TRUE
    assert future_answer.source is TemporalSource.HYPOTHETICAL_FUTURE


def test_g2_confidence_inversion_and_missing_current_observation() -> None:
    store = MemoryStore([_trace("box_a", confidence=0.99)])
    now = TemporalCycleRunner(next_cycle_id=2, memory_store=store).run(
        _ball_world("box_b", confidence=0.55),
        memory_cue=_cue(),
    )
    current = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, None, TemporalIntent.NOW),
    )
    assert current.status is TruthStatus.TRUE
    assert current.source is TemporalSource.OBSERVED_NOW
    assert current.propositions[0].target_id == "box_b"

    hidden = TemporalCycleRunner(next_cycle_id=2, memory_store=store).run(
        _ball_world(None),
        memory_cue=_cue(),
    )
    hidden_answer = answer_temporal(
        hidden,
        TemporalQuery.relation("ball", RelationType.INSIDE, None, TemporalIntent.NOW),
    )
    assert hidden_answer.status is TruthStatus.UNKNOWN
    assert hidden_answer.context[0].source is TemporalSource.RECONSTRUCTED_MEMORY


def test_g2_contradictory_present_evidence_is_structured_uncertainty() -> None:
    world = _ball_world("box_b")
    world.apply(SetRelation("ball", "box_c", RelationType.INSIDE))
    now = TemporalCycleRunner(next_cycle_id=2).run(world)
    answer = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, None, TemporalIntent.NOW),
    )

    assert answer.status is TruthStatus.CONTRADICTORY
    assert answer.contradictions
    assert answer.source is TemporalSource.OBSERVED_NOW


def test_g2_false_memory_injection_remains_memory_context() -> None:
    store = MemoryStore(
        [
            make_false_memory_trace(
                source_cycle_id=1,
                encoded_at_cycle_id=1,
                proposition=Proposition("ball", RelationType.INSIDE, "box_d"),
            )
        ]
    )
    now = TemporalCycleRunner(next_cycle_id=2, memory_store=store).run(
        _ball_world("box_b"),
        memory_cue=_cue(),
    )
    answer = answer_temporal(
        now,
        TemporalQuery.relation("ball", RelationType.INSIDE, None, TemporalIntent.NOW),
    )

    assert answer.status is TruthStatus.TRUE
    assert answer.propositions[0].target_id == "box_b"
    assert any(item.proposition.target_id == "box_d" for item in answer.context)

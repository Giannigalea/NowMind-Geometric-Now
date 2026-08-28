from __future__ import annotations

from dataclasses import dataclass

from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.reasoning.query import TruthStatus
from nowmind.temporal.future import FutureHypothesis
from nowmind.temporal.memory import MemoryReconstruction
from nowmind.temporal.now_state import TemporalNowState
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.query import (
    EvidenceReference,
    TemporalAnswer,
    TemporalIntent,
    TemporalQuery,
)
from nowmind.temporal.source import TemporalSource


def answer_temporal(
    now: TemporalNowState,
    query: TemporalQuery,
    reliability_threshold: float = 0.5,
) -> TemporalAnswer:
    return TemporalReasoner(reliability_threshold=reliability_threshold).answer(now, query)


class TemporalReasoner:
    """Source-safe deterministic reasoner for a single TemporalNowState."""

    def __init__(self, reliability_threshold: float = 0.5) -> None:
        if not 0.0 <= reliability_threshold <= 1.0:
            raise ValueError("reliability_threshold must be within [0, 1]")
        self.reliability_threshold = reliability_threshold

    def answer(self, now: TemporalNowState, query: TemporalQuery) -> TemporalAnswer:
        if query.intent is TemporalIntent.NOW:
            return self._answer_now(now, query)
        if query.intent is TemporalIntent.PAST:
            return self._answer_past(now, query)
        if query.intent is TemporalIntent.POSSIBLE_FUTURE:
            return self._answer_future(now, query)
        return self._answer_source(now, query)

    def _answer_now(self, now: TemporalNowState, query: TemporalQuery) -> TemporalAnswer:
        context = _context_for_query(now, query)
        validation = now.present_geometry.validation
        if validation.contradictions:
            return TemporalAnswer(
                status=TruthStatus.CONTRADICTORY,
                query=query,
                confidence=0.0,
                source=TemporalSource.OBSERVED_NOW,
                context=context,
                contradictions=tuple(issue.message for issue in validation.contradictions),
                explanation=(
                    "Current Present Geometry contains structured contradictions.",
                    "Reconstructed memories and future hypotheses were not used as present facts.",
                ),
            )

        current_conflicts = _current_target_conflicts(now, query)
        if current_conflicts:
            return TemporalAnswer(
                status=TruthStatus.CONTRADICTORY,
                query=query,
                confidence=0.0,
                source=TemporalSource.OBSERVED_NOW,
                context=context,
                contradictions=current_conflicts,
                explanation=(
                    "Multiple incompatible current observations match the query cue.",
                    "No memory or hypothesis was promoted to resolve the current conflict.",
                ),
            )

        candidates = _current_evidence(now, query)
        if query.target_id is not None:
            candidates = tuple(
                item for item in candidates if item.source.target_id == query.target_id
            )
        if not candidates:
            return TemporalAnswer(
                status=TruthStatus.UNKNOWN,
                query=query,
                confidence=0.0,
                source=None,
                context=context,
                uncertainty_notes=(
                    "No valid observed/inferred current evidence answers this NOW query.",
                    "Memory context is visible but cannot substitute for present observation.",
                ),
            )
        best = max(candidates, key=lambda item: item.source.confidence)
        if best.source.confidence < self.reliability_threshold:
            return TemporalAnswer(
                status=TruthStatus.UNKNOWN,
                query=query,
                confidence=0.0,
                source=None,
                context=context,
                uncertainty_notes=(
                    f"Best current evidence confidence {best.source.confidence:.2f} "
                    f"is below threshold {self.reliability_threshold:.2f}.",
                    "Higher-confidence memory is not promoted to present fact.",
                ),
            )
        source = _source_from_g1(best.source.provenance)
        proposition = Proposition.from_relation(best.source)
        return TemporalAnswer(
            status=TruthStatus.TRUE,
            query=query,
            confidence=best.source.confidence,
            source=source,
            propositions=(proposition,),
            evidence=(
                EvidenceReference(
                    evidence_id=best.source.relation_id,
                    source=source,
                    cycle_id=now.cycle_id,
                    proposition=proposition,
                    confidence=best.source.confidence,
                ),
            ),
            context=context,
            explanation=(
                "NOW query answered only from OBSERVED_NOW/INFERRED_NOW evidence.",
                "Temporal context was retained separately.",
            ),
        )

    def _answer_past(self, now: TemporalNowState, query: TemporalQuery) -> TemporalAnswer:
        candidates = tuple(
            memory
            for memory in now.reconstructed_memories
            if memory.proposition.matches(
                source_id=query.source_id,
                relation_type=query.relation_type,
                target_id=query.target_id,
            )
            and (
                query.target_cycle_id is None
                or query.target_cycle_id in memory.historical_source_cycles
            )
        )
        if not candidates:
            return TemporalAnswer(
                status=TruthStatus.UNKNOWN,
                query=query,
                confidence=0.0,
                source=None,
                context=_context_for_query(now, query),
                uncertainty_notes=("No reconstructed memory matches this PAST query.",),
            )
        best = max(candidates, key=lambda item: item.confidence)
        evidence = _memory_evidence(best)
        return TemporalAnswer(
            status=TruthStatus.TRUE,
            query=query,
            confidence=best.confidence,
            source=TemporalSource.RECONSTRUCTED_MEMORY,
            propositions=(best.proposition,),
            evidence=(evidence,),
            context=_context_for_query(now, query),
            explanation=(
                "PAST query answered from a reconstruction created in the current cycle.",
                "This is not an exact replay of a previous NowState.",
            ),
        )

    def _answer_future(self, now: TemporalNowState, query: TemporalQuery) -> TemporalAnswer:
        candidates = tuple(
            hypothesis
            for hypothesis in now.future_hypotheses
            if hypothesis.proposition.matches(
                source_id=query.source_id,
                relation_type=query.relation_type,
                target_id=query.target_id,
            )
        )
        if not candidates:
            return TemporalAnswer(
                status=TruthStatus.UNKNOWN,
                query=query,
                confidence=0.0,
                source=None,
                context=_context_for_query(now, query),
                uncertainty_notes=("No future hypothesis matches this POSSIBLE_FUTURE query.",),
            )
        confidence = max(item.confidence for item in candidates)
        return TemporalAnswer(
            status=TruthStatus.TRUE,
            query=query,
            confidence=confidence,
            source=TemporalSource.HYPOTHETICAL_FUTURE,
            propositions=tuple(item.proposition for item in candidates),
            evidence=tuple(_future_evidence(item) for item in candidates),
            context=_context_for_query(now, query),
            explanation=(
                "Future query answered only from HYPOTHETICAL_FUTURE content.",
                "A hypothesis is present content about a possible future, not observation.",
            ),
        )

    def _answer_source(self, now: TemporalNowState, query: TemporalQuery) -> TemporalAnswer:
        context = _context_for_query(now, query)
        if not context:
            return TemporalAnswer(TruthStatus.UNKNOWN, query, 0.0, None)
        best = max(context, key=lambda item: item.confidence)
        return TemporalAnswer(
            status=TruthStatus.TRUE,
            query=query,
            confidence=best.confidence,
            source=best.source,
            propositions=(best.proposition,),
            evidence=(best,),
            context=context,
            explanation=("SOURCE query reports the strongest matching temporal-source record.",),
        )


@dataclass(frozen=True, slots=True)
class _CurrentCandidate:
    source: Relation


def _current_evidence(now: TemporalNowState, query: TemporalQuery) -> tuple[_CurrentCandidate, ...]:
    candidates: list[_CurrentCandidate] = []
    for relation in now.present_geometry.relations:
        if relation.source_id != query.source_id:
            continue
        if relation.relation_type is not query.relation_type:
            continue
        if relation.provenance not in {Provenance.OBSERVED_NOW, Provenance.INFERRED_NOW}:
            continue
        candidates.append(_CurrentCandidate(relation))
    return tuple(candidates)


def _current_target_conflicts(
    now: TemporalNowState,
    query: TemporalQuery,
) -> tuple[str, ...]:
    singleton_relations = {RelationType.INSIDE, RelationType.ON, RelationType.UNDER}
    if query.relation_type not in singleton_relations:
        return ()
    observed = [
        relation
        for relation in now.present_geometry.relations
        if relation.source_id == query.source_id
        and relation.relation_type is query.relation_type
        and relation.provenance is Provenance.OBSERVED_NOW
    ]
    targets = sorted({relation.target_id for relation in observed})
    if len(targets) <= 1:
        return ()
    return (
        (
            f"Current observation has incompatible {query.relation_type.value} "
            f"targets for {query.source_id}: {', '.join(targets)}"
        ),
    )


def _context_for_query(
    now: TemporalNowState,
    query: TemporalQuery,
) -> tuple[EvidenceReference, ...]:
    context: list[EvidenceReference] = []
    for memory in now.reconstructed_memories:
        if memory.proposition.matches(
            source_id=query.source_id,
            relation_type=query.relation_type,
            target_id=query.target_id,
        ) or memory.proposition.matches(
            source_id=query.source_id,
            relation_type=query.relation_type,
        ):
            context.append(_memory_evidence(memory))
    for hypothesis in now.future_hypotheses:
        if hypothesis.proposition.matches(
            source_id=query.source_id,
            relation_type=query.relation_type,
            target_id=query.target_id,
        ) or hypothesis.proposition.matches(
            source_id=query.source_id,
            relation_type=query.relation_type,
        ):
            context.append(_future_evidence(hypothesis))
    return tuple(context)


def _memory_evidence(memory: MemoryReconstruction) -> EvidenceReference:
    return EvidenceReference(
        evidence_id=str(memory.reconstruction_id),
        source=TemporalSource.RECONSTRUCTED_MEMORY,
        cycle_id=memory.created_at_cycle_id,
        proposition=memory.proposition,
        confidence=memory.confidence,
    )


def _future_evidence(hypothesis: FutureHypothesis) -> EvidenceReference:
    return EvidenceReference(
        evidence_id=str(hypothesis.hypothesis_id),
        source=TemporalSource.HYPOTHETICAL_FUTURE,
        cycle_id=hypothesis.created_at_cycle_id,
        proposition=hypothesis.proposition,
        confidence=hypothesis.confidence,
    )


def _source_from_g1(provenance: Provenance) -> TemporalSource:
    if provenance is Provenance.OBSERVED_NOW:
        return TemporalSource.OBSERVED_NOW
    return TemporalSource.INFERRED_NOW

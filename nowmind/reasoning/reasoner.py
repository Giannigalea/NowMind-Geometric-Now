from __future__ import annotations

from nowmind.core.now_state import NowState
from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.reasoning.query import Answer, Query, QueryType, ReasoningStep, TruthStatus


def answer(now: NowState, query: Query) -> Answer:
    return DeterministicReasoner().answer(now, query)


class DeterministicReasoner:
    """Reason over one current NowState.

    The public API deliberately accepts only a NowState and a Query. There is no
    history, recorder, memory, or previous-Now argument.
    """

    def answer(self, now: NowState, query: Query) -> Answer:
        geometry = now.geometry
        if geometry.validation.contradictions:
            return Answer(
                status=TruthStatus.CONTRADICTORY,
                confidence=0.0,
                query=query,
                issues=geometry.validation.contradictions,
            )

        if query.query_type in {
            QueryType.RELATION,
            QueryType.EXPLAIN,
            QueryType.IS_INSIDE,
        }:
            relation_type = query.relation_type
            if relation_type is None or query.target_id is None:
                return Answer(TruthStatus.UNKNOWN, 0.0, query)
            relation = geometry.find_relation(
                source_id=query.source_id,
                target_id=query.target_id,
                relation_type=relation_type,
            )
            if relation is None:
                return Answer(TruthStatus.UNKNOWN, 0.0, query)
            supporting, steps = _explain_relation(relation, geometry.relation_by_id)
            return Answer(
                status=TruthStatus.TRUE,
                confidence=relation.confidence,
                query=query,
                supporting_relations=supporting,
                explanation=steps,
            )

        if query.query_type is QueryType.WHAT_CONTAINS:
            containers = geometry.find_relations(
                source_id=query.source_id,
                relation_type=RelationType.INSIDE,
            )
            if not containers:
                return Answer(TruthStatus.UNKNOWN, 0.0, query)
            supporting, steps = _explain_many(containers, geometry.relation_by_id)
            return Answer(
                status=TruthStatus.TRUE,
                confidence=min(relation.confidence for relation in containers),
                query=query,
                supporting_relations=supporting,
                explanation=steps,
            )

        if query.query_type is QueryType.WHERE_IS:
            relations = geometry.find_relations(source_id=query.source_id, target_id=query.target_id)
            if not relations:
                return Answer(TruthStatus.UNKNOWN, 0.0, query)
            supporting, steps = _explain_many(relations, geometry.relation_by_id)
            return Answer(
                status=TruthStatus.TRUE,
                confidence=min(relation.confidence for relation in relations),
                query=query,
                supporting_relations=supporting,
                explanation=steps,
            )

        return Answer(TruthStatus.UNKNOWN, 0.0, query)


def _explain_many(
    relations: tuple[Relation, ...],
    relation_by_id: dict[str, Relation],
) -> tuple[tuple[Relation, ...], tuple[ReasoningStep, ...]]:
    supporting: list[Relation] = []
    steps: list[ReasoningStep] = []
    seen_supports: set[str] = set()
    seen_steps: set[str] = set()
    for relation in relations:
        relation_supporting, relation_steps = _explain_relation(relation, relation_by_id)
        for support in relation_supporting:
            if support.relation_id not in seen_supports:
                supporting.append(support)
                seen_supports.add(support.relation_id)
        for step in relation_steps:
            if step.conclusion not in seen_steps:
                steps.append(step)
                seen_steps.add(step.conclusion)
    return tuple(supporting), tuple(steps)


def _explain_relation(
    relation: Relation,
    relation_by_id: dict[str, Relation],
) -> tuple[tuple[Relation, ...], tuple[ReasoningStep, ...]]:
    supporting: list[Relation] = []
    steps: list[ReasoningStep] = []
    seen_supports: set[str] = set()
    seen_steps: set[str] = set()

    def visit(current: Relation) -> None:
        for premise_id in current.premise_ids:
            premise = relation_by_id.get(premise_id)
            if premise is not None:
                visit(premise)
        if current.relation_id not in seen_supports:
            supporting.append(current)
            seen_supports.add(current.relation_id)
        if (
            current.provenance is Provenance.INFERRED_NOW
            and current.rule_id is not None
            and current.relation_id not in seen_steps
        ):
            steps.append(
                ReasoningStep(
                    rule_id=current.rule_id,
                    premises=current.premise_ids,
                    conclusion=current.relation_id,
                )
            )
            seen_steps.add(current.relation_id)

    visit(relation)
    return tuple(supporting), tuple(steps)


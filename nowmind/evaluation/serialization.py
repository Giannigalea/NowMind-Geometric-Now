from __future__ import annotations

from typing import Any

from nowmind.core.now_state import NowState
from nowmind.geometry.relation import Provenance, Relation
from nowmind.geometry.validation import ValidationIssue
from nowmind.reasoning.query import Answer, Query, ReasoningStep
from nowmind.world.model import WorldRelation, WorldState


def serialize_world(world: WorldState) -> dict[str, Any]:
    return {
        "world_version": world.world_version,
        "entities": [entity.to_dict() for entity in world.entities],
        "relations": [serialize_world_relation(relation) for relation in world.relations],
    }


def serialize_world_relation(relation: WorldRelation) -> dict[str, Any]:
    return {
        "source_id": relation.source_id,
        "target_id": relation.target_id,
        "relation_type": relation.relation_type.value,
        "confidence": relation.confidence,
        "value": relation.value,
        "unit": relation.unit,
    }


def serialize_now(now: NowState) -> dict[str, Any]:
    observed = [
        serialize_relation(relation)
        for relation in now.geometry.relations
        if relation.provenance is Provenance.OBSERVED_NOW
    ]
    inferred = [
        serialize_relation(relation)
        for relation in now.geometry.relations
        if relation.provenance is Provenance.INFERRED_NOW
    ]
    return {
        "cycle_id": now.cycle_id,
        "now_id": str(now.now_id),
        "created_at": now.created_at.isoformat(),
        "world_version": now.geometry.world_version,
        "entities": [entity.to_dict() for entity in now.geometry.entities],
        "observed_relations": observed,
        "inferred_relations": inferred,
        "validation": serialize_validation(now),
    }


def serialize_cycle(
    now: NowState,
    query: Query | None = None,
    answer: Answer | None = None,
) -> dict[str, Any]:
    data = serialize_now(now)
    data["query"] = serialize_query(query) if query is not None else None
    data["answer"] = serialize_answer(answer) if answer is not None else None
    return data


def serialize_relation(relation: Relation) -> dict[str, Any]:
    return {
        "relation_id": relation.relation_id,
        "source_id": relation.source_id,
        "target_id": relation.target_id,
        "relation_type": relation.relation_type.value,
        "confidence": relation.confidence,
        "provenance": relation.provenance.value,
        "rule_id": relation.rule_id,
        "premise_ids": list(relation.premise_ids),
        "value": relation.value,
        "unit": relation.unit,
    }


def serialize_query(query: Query) -> dict[str, Any]:
    return {
        "query_type": query.query_type.value,
        "source_id": query.source_id,
        "target_id": query.target_id,
        "relation_type": query.relation_type.value if query.relation_type else None,
        "display": query_display(query),
    }


def query_display(query: Query) -> str:
    relation = query.relation_type.name if query.relation_type is not None else "RELATION"
    if query.target_id is None:
        return f"{query.query_type.name}({query.source_id})"
    return f"{query.source_id} {relation} {query.target_id}?"


def serialize_answer(answer: Answer) -> dict[str, Any]:
    return {
        "status": answer.status.value,
        "confidence": answer.confidence,
        "supporting_relations": [
            serialize_relation(relation) for relation in answer.supporting_relations
        ],
        "explanation": [serialize_step(step) for step in answer.explanation],
        "issues": [serialize_issue(issue) for issue in answer.issues],
    }


def serialize_step(step: ReasoningStep) -> dict[str, Any]:
    return {
        "rule_id": step.rule_id,
        "premises": list(step.premises),
        "conclusion": step.conclusion,
    }


def serialize_issue(issue: ValidationIssue) -> dict[str, Any]:
    return {
        "issue_type": issue.issue_type.value,
        "message": issue.message,
        "relation_ids": list(issue.relation_ids),
        "source_id": issue.source_id,
        "target_id": issue.target_id,
        "relation_types": [relation_type.value for relation_type in issue.relation_types],
    }


def serialize_validation(now: NowState) -> dict[str, Any]:
    return {
        "is_valid": now.geometry.validation.is_valid,
        "issues": [serialize_issue(issue) for issue in now.geometry.validation.issues],
    }


def summarize_relations(now: NowState) -> list[str]:
    return [
        (
            f"{relation.relation_type.name}({relation.source_id}, {relation.target_id})"
            f" [{relation.provenance.value}]"
        )
        for relation in now.geometry.relations
    ]


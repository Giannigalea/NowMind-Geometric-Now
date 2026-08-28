from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from nowmind.geometry.relation import Relation, RelationType
from nowmind.geometry.validation import ValidationIssue


class QueryType(str, Enum):
    RELATION = "relation"
    WHERE_IS = "where_is"
    IS_INSIDE = "is_inside"
    WHAT_CONTAINS = "what_contains"
    EXPLAIN = "explain"


class TruthStatus(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"
    CONTRADICTORY = "contradictory"


@dataclass(frozen=True, slots=True)
class Query:
    query_type: QueryType
    source_id: str
    target_id: str | None = None
    relation_type: RelationType | None = None

    @classmethod
    def relation(
        cls,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
    ) -> Query:
        return cls(QueryType.RELATION, source_id, target_id, relation_type)

    @classmethod
    def explain(
        cls,
        source_id: str,
        relation_type: RelationType,
        target_id: str,
    ) -> Query:
        return cls(QueryType.EXPLAIN, source_id, target_id, relation_type)

    @classmethod
    def is_inside(cls, source_id: str, target_id: str) -> Query:
        return cls(QueryType.IS_INSIDE, source_id, target_id, RelationType.INSIDE)

    @classmethod
    def where_is(cls, source_id: str, relative_to: str | None = None) -> Query:
        return cls(QueryType.WHERE_IS, source_id, relative_to, None)

    @classmethod
    def what_contains(cls, source_id: str) -> Query:
        return cls(QueryType.WHAT_CONTAINS, source_id, None, RelationType.INSIDE)


@dataclass(frozen=True, slots=True)
class ReasoningStep:
    rule_id: str
    premises: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True, slots=True)
class Answer:
    status: TruthStatus
    confidence: float
    query: Query
    supporting_relations: tuple[Relation, ...] = field(default_factory=tuple)
    explanation: tuple[ReasoningStep, ...] = field(default_factory=tuple)
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "supporting_relations", tuple(self.supporting_relations))
        object.__setattr__(self, "explanation", tuple(self.explanation))
        object.__setattr__(self, "issues", tuple(self.issues))


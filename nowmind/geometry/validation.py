from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from nowmind.geometry.entity import Entity
from nowmind.geometry.relation import Relation, RelationType


class ValidationIssueType(str, Enum):
    MISSING_ENTITY = "missing_entity"
    CONTRADICTION = "contradiction"
    INVALID_SELF_RELATION = "invalid_self_relation"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    issue_type: ValidationIssueType
    message: str
    relation_ids: tuple[str, ...] = field(default_factory=tuple)
    source_id: str | None = None
    target_id: str | None = None
    relation_types: tuple[RelationType, ...] = field(default_factory=tuple)

    @property
    def is_contradiction(self) -> bool:
        return self.issue_type is ValidationIssueType.CONTRADICTION


@dataclass(frozen=True, slots=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "issues", tuple(self.issues))

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def contradictions(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.is_contradiction)


INCOMPATIBLE_SAME_DIRECTION: tuple[tuple[RelationType, RelationType], ...] = (
    (RelationType.LEFT_OF, RelationType.RIGHT_OF),
    (RelationType.ABOVE, RelationType.BELOW),
    (RelationType.INSIDE, RelationType.CONTAINS),
    (RelationType.ON, RelationType.UNDER),
)

SELF_INVALID_RELATIONS: frozenset[RelationType] = frozenset(RelationType)


def validate_relations(
    entities: tuple[Entity, ...],
    relations: tuple[Relation, ...],
) -> ValidationResult:
    entity_ids = {entity.entity_id for entity in entities}
    issues: list[ValidationIssue] = []

    for relation in relations:
        missing = [
            entity_id
            for entity_id in (relation.source_id, relation.target_id)
            if entity_id not in entity_ids
        ]
        if missing:
            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.MISSING_ENTITY,
                    message=(
                        f"Relation {relation.relation_id} references unknown "
                        f"entity id(s): {', '.join(sorted(set(missing)))}"
                    ),
                    relation_ids=(relation.relation_id,),
                    source_id=relation.source_id,
                    target_id=relation.target_id,
                    relation_types=(relation.relation_type,),
                )
            )
        if (
            relation.source_id == relation.target_id
            and relation.relation_type in SELF_INVALID_RELATIONS
        ):
            issues.append(
                ValidationIssue(
                    issue_type=ValidationIssueType.INVALID_SELF_RELATION,
                    message=(
                        f"Relation {relation.relation_id} uses invalid self relation "
                        f"{relation.relation_type.value}"
                    ),
                    relation_ids=(relation.relation_id,),
                    source_id=relation.source_id,
                    target_id=relation.target_id,
                    relation_types=(relation.relation_type,),
                )
            )

    by_pair: dict[tuple[str, str], dict[RelationType, list[Relation]]] = {}
    for relation in relations:
        pair = (relation.source_id, relation.target_id)
        by_pair.setdefault(pair, {}).setdefault(relation.relation_type, []).append(relation)

    for (source_id, target_id), relation_map in by_pair.items():
        for left, right in INCOMPATIBLE_SAME_DIRECTION:
            left_relations = relation_map.get(left, [])
            right_relations = relation_map.get(right, [])
            if left_relations and right_relations:
                relation_ids = tuple(
                    relation.relation_id for relation in [*left_relations, *right_relations]
                )
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationIssueType.CONTRADICTION,
                        message=(
                            f"Current geometry contains incompatible simultaneous facts: "
                            f"{left.value}({source_id}, {target_id}) and "
                            f"{right.value}({source_id}, {target_id})"
                        ),
                        relation_ids=relation_ids,
                        source_id=source_id,
                        target_id=target_id,
                        relation_types=(left, right),
                    )
                )

    return ValidationResult(tuple(issues))


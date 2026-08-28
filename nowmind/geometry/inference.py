from __future__ import annotations

from collections.abc import Iterable

from nowmind.geometry.relation import Provenance, Relation, RelationType


INVERSE_RULES: dict[RelationType, tuple[RelationType, str]] = {
    RelationType.LEFT_OF: (RelationType.RIGHT_OF, "INVERSE_LEFT_RIGHT"),
    RelationType.RIGHT_OF: (RelationType.LEFT_OF, "INVERSE_RIGHT_LEFT"),
    RelationType.ABOVE: (RelationType.BELOW, "INVERSE_ABOVE_BELOW"),
    RelationType.BELOW: (RelationType.ABOVE, "INVERSE_BELOW_ABOVE"),
    RelationType.INSIDE: (RelationType.CONTAINS, "INVERSE_INSIDE_CONTAINS"),
    RelationType.CONTAINS: (RelationType.INSIDE, "INVERSE_CONTAINS_INSIDE"),
    RelationType.ON: (RelationType.UNDER, "INVERSE_ON_UNDER"),
    RelationType.UNDER: (RelationType.ON, "INVERSE_UNDER_ON"),
}

SYMMETRIC_RULES: dict[RelationType, str] = {
    RelationType.TOUCHING: "TOUCHING_SYMMETRIC",
}

TRANSITIVE_RULES: dict[RelationType, str] = {
    RelationType.LEFT_OF: "LEFT_TRANSITIVE",
    RelationType.RIGHT_OF: "RIGHT_TRANSITIVE",
    RelationType.ABOVE: "ABOVE_TRANSITIVE",
    RelationType.BELOW: "BELOW_TRANSITIVE",
    RelationType.INSIDE: "INSIDE_TRANSITIVE",
    RelationType.CONTAINS: "CONTAINS_TRANSITIVE",
}


class _RelationFactory:
    def __init__(self, start_index: int) -> None:
        self._next_index = start_index

    def create(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        confidence: float,
        rule_id: str,
        premise_ids: Iterable[str],
    ) -> Relation:
        relation = Relation(
            relation_id=f"i{self._next_index:04d}",
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
            provenance=Provenance.INFERRED_NOW,
            rule_id=rule_id,
            premise_ids=tuple(premise_ids),
        )
        self._next_index += 1
        return relation


def infer_relations(observed_relations: tuple[Relation, ...]) -> tuple[Relation, ...]:
    """Return observed plus deterministic current-cycle inferred relations.

    Confidence policy: an inferred relation receives the minimum confidence of
    its premises. No probabilistic semantics beyond that are introduced in G1.
    """

    relations = list(observed_relations)
    relation_by_key = {relation.key: relation for relation in relations}
    factory = _RelationFactory(start_index=len(relations))

    changed = True
    while changed:
        changed = False
        snapshot = tuple(relations)

        for relation in snapshot:
            inverse = _infer_inverse_or_symmetric(relation, factory)
            if inverse is not None and inverse.key not in relation_by_key:
                relation_by_key[inverse.key] = inverse
                relations.append(inverse)
                changed = True

        snapshot = tuple(relations)
        for left in snapshot:
            rule_id = TRANSITIVE_RULES.get(left.relation_type)
            if rule_id is None:
                continue
            for right in snapshot:
                if left is right:
                    continue
                if right.relation_type is not left.relation_type:
                    continue
                if left.target_id != right.source_id:
                    continue
                if left.source_id == right.target_id:
                    continue
                confidence = min(left.confidence, right.confidence)
                inferred = factory.create(
                    source_id=left.source_id,
                    target_id=right.target_id,
                    relation_type=left.relation_type,
                    confidence=confidence,
                    rule_id=rule_id,
                    premise_ids=(left.relation_id, right.relation_id),
                )
                if inferred.key not in relation_by_key:
                    relation_by_key[inferred.key] = inferred
                    relations.append(inferred)
                    changed = True

    return tuple(relations)


def _infer_inverse_or_symmetric(
    relation: Relation,
    factory: _RelationFactory,
) -> Relation | None:
    inverse = INVERSE_RULES.get(relation.relation_type)
    if inverse is not None:
        relation_type, rule_id = inverse
        return factory.create(
            source_id=relation.target_id,
            target_id=relation.source_id,
            relation_type=relation_type,
            confidence=relation.confidence,
            rule_id=rule_id,
            premise_ids=(relation.relation_id,),
        )

    rule_id = SYMMETRIC_RULES.get(relation.relation_type)
    if rule_id is not None:
        return factory.create(
            source_id=relation.target_id,
            target_id=relation.source_id,
            relation_type=relation.relation_type,
            confidence=relation.confidence,
            rule_id=rule_id,
            premise_ids=(relation.relation_id,),
        )

    return None


from __future__ import annotations

import pytest

from nowmind.core.cycle import CognitiveCycleRunner
from nowmind.geometry.builder import PresentGeometryBuilder
from nowmind.geometry.entity import Entity
from nowmind.geometry.relation import Provenance, Relation, RelationType
from nowmind.perception.observation import Observation, ObservedRelation
from nowmind.reasoning.query import Query, TruthStatus
from nowmind.reasoning.reasoner import answer
from nowmind.world.events import AddEntity, SetRelation
from nowmind.world.model import WorldState


def _geometry(
    relations: tuple[ObservedRelation, ...],
    entity_ids: tuple[str, ...] = ("a", "b", "c"),
):
    observation = Observation(
        cycle_id=1,
        world_version=1,
        observed_entities=tuple(Entity(entity_id, "object") for entity_id in entity_ids),
        observed_relations=relations,
    )
    return PresentGeometryBuilder().build(observation)


def test_inverse_left_right_is_inferred() -> None:
    geometry = _geometry((ObservedRelation("a", "b", RelationType.LEFT_OF),))

    observed = geometry.find_relation("a", "b", RelationType.LEFT_OF)
    inverse = geometry.find_relation("b", "a", RelationType.RIGHT_OF)

    assert observed is not None
    assert observed.provenance is Provenance.OBSERVED_NOW
    assert inverse is not None
    assert inverse.provenance is Provenance.INFERRED_NOW
    assert inverse.rule_id == "INVERSE_LEFT_RIGHT"


def test_inverse_above_below_is_inferred() -> None:
    geometry = _geometry((ObservedRelation("a", "b", RelationType.ABOVE),))

    inverse = geometry.find_relation("b", "a", RelationType.BELOW)

    assert inverse is not None
    assert inverse.provenance is Provenance.INFERRED_NOW


def test_containment_inverse_is_inferred() -> None:
    geometry = _geometry((ObservedRelation("a", "b", RelationType.INSIDE),))

    inverse = geometry.find_relation("b", "a", RelationType.CONTAINS)

    assert inverse is not None
    assert inverse.provenance is Provenance.INFERRED_NOW


def test_touching_is_symmetric_but_not_transitive() -> None:
    geometry = _geometry(
        (
            ObservedRelation("a", "b", RelationType.TOUCHING),
            ObservedRelation("b", "c", RelationType.TOUCHING),
        )
    )

    assert geometry.find_relation("b", "a", RelationType.TOUCHING) is not None
    assert geometry.find_relation("a", "c", RelationType.TOUCHING) is None


def test_left_transitivity_has_explanation() -> None:
    world = WorldState()
    for entity_id in ("a", "b", "c"):
        world.apply(AddEntity(entity_id, "object"))
    world.apply(SetRelation("a", "b", RelationType.LEFT_OF, confidence=0.7))
    world.apply(SetRelation("b", "c", RelationType.LEFT_OF, confidence=0.9))
    now = CognitiveCycleRunner().run(world)

    result = answer(now, Query.relation("a", "c", RelationType.LEFT_OF))

    assert result.status is TruthStatus.TRUE
    assert result.confidence == pytest.approx(0.7)
    assert result.supporting_relations[-1].provenance is Provenance.INFERRED_NOW
    assert result.explanation[-1].rule_id == "LEFT_TRANSITIVE"


def test_above_transitivity() -> None:
    geometry = _geometry(
        (
            ObservedRelation("a", "b", RelationType.ABOVE),
            ObservedRelation("b", "c", RelationType.ABOVE),
        )
    )

    assert geometry.find_relation("a", "c", RelationType.ABOVE) is not None


def test_nested_containment_transitivity() -> None:
    geometry = _geometry(
        (
            ObservedRelation("a", "b", RelationType.INSIDE),
            ObservedRelation("b", "c", RelationType.INSIDE),
        )
    )

    assert geometry.find_relation("a", "c", RelationType.INSIDE) is not None
    assert geometry.find_relation("c", "a", RelationType.CONTAINS) is not None


def test_relation_confidence_range_is_enforced() -> None:
    with pytest.raises(ValueError, match="confidence"):
        Relation(
            relation_id="bad",
            source_id="a",
            target_id="b",
            relation_type=RelationType.LEFT_OF,
            confidence=1.5,
            provenance=Provenance.OBSERVED_NOW,
        )


def test_missing_entity_is_invalid() -> None:
    geometry = _geometry(
        (ObservedRelation("a", "missing", RelationType.LEFT_OF),),
        entity_ids=("a",),
    )

    assert not geometry.validation.is_valid
    assert any(issue.issue_type.value == "missing_entity" for issue in geometry.validation.issues)


def test_contradiction_is_structured_and_reasoner_refuses_guess() -> None:
    geometry = _geometry(
        (
            ObservedRelation("a", "b", RelationType.LEFT_OF),
            ObservedRelation("a", "b", RelationType.RIGHT_OF),
        )
    )
    now = CognitiveCycleRunner().run(WorldState())
    now = type(now).create(geometry)

    result = answer(now, Query.relation("a", "b", RelationType.LEFT_OF))

    assert geometry.validation.contradictions
    assert result.status is TruthStatus.CONTRADICTORY
    assert result.issues


def test_unknown_remains_unknown() -> None:
    geometry = _geometry((ObservedRelation("a", "b", RelationType.LEFT_OF),))
    now = CognitiveCycleRunner().run(WorldState())
    now = type(now).create(geometry)

    result = answer(now, Query.relation("a", "c", RelationType.LEFT_OF))

    assert result.status is TruthStatus.UNKNOWN


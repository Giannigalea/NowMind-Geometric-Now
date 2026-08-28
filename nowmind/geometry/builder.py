from __future__ import annotations

from nowmind.geometry.inference import infer_relations
from nowmind.geometry.present_geometry import PresentGeometry
from nowmind.geometry.relation import Provenance, Relation
from nowmind.geometry.validation import validate_relations
from nowmind.perception.observation import Observation


class PresentGeometryBuilder:
    """Builds Present Geometry from the current-cycle observation only."""

    def build(self, observation: Observation) -> PresentGeometry:
        observed_relations = tuple(
            Relation(
                relation_id=f"o{index:04d}",
                source_id=observed.source_id,
                target_id=observed.target_id,
                relation_type=observed.relation_type,
                confidence=observed.confidence,
                provenance=Provenance.OBSERVED_NOW,
                value=observed.value,
                unit=observed.unit,
            )
            for index, observed in enumerate(observation.observed_relations)
        )
        relations = infer_relations(observed_relations)
        entities = tuple(observation.observed_entities)
        validation = validate_relations(entities, relations)
        return PresentGeometry(
            cycle_id=observation.cycle_id,
            world_version=observation.world_version,
            entities=entities,
            relations=relations,
            validation=validation,
        )


def build_present_geometry(observation: Observation) -> PresentGeometry:
    return PresentGeometryBuilder().build(observation)


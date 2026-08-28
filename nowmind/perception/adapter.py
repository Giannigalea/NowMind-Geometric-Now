from __future__ import annotations

from nowmind.perception.observation import Observation, ObservedRelation
from nowmind.world.model import WorldState


class PerceptionAdapter:
    """Perfect L1 perception for G1.

    The adapter snapshots the current world version into an Observation. It does
    not accept or read a previous NowState.
    """

    def observe(self, world: WorldState, cycle_id: int) -> Observation:
        return Observation(
            cycle_id=cycle_id,
            world_version=world.world_version,
            observed_entities=world.entities,
            observed_relations=tuple(
                ObservedRelation(
                    source_id=relation.source_id,
                    target_id=relation.target_id,
                    relation_type=relation.relation_type,
                    confidence=relation.confidence,
                    value=relation.value,
                    unit=relation.unit,
                )
                for relation in world.relations
            ),
        )


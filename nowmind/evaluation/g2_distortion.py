from __future__ import annotations

import random
from typing import Mapping

from nowmind.geometry.relation import RelationType
from nowmind.temporal.memory import MemoryTrace, ReconstructionDistortion
from nowmind.temporal.proposition import Proposition
from nowmind.temporal.source import TemporalSource


def make_false_memory_trace(
    source_cycle_id: int,
    encoded_at_cycle_id: int,
    proposition: Proposition,
    encoded_confidence: float = 0.95,
    trace_strength: float = 1.0,
    metadata: Mapping[str, object] | None = None,
) -> MemoryTrace:
    """Create an explicitly injected false trace for evaluation only."""

    false_metadata = dict(metadata or {})
    false_metadata["injected_false_memory"] = True
    return MemoryTrace.create(
        source_cycle_id=source_cycle_id,
        encoded_at_cycle_id=encoded_at_cycle_id,
        proposition=proposition,
        original_source=TemporalSource.OBSERVED_NOW,
        encoded_confidence=encoded_confidence,
        trace_strength=trace_strength,
        metadata=false_metadata,
    )


def seeded_distortion(
    seed: int,
    relation_choices: tuple[RelationType, ...] = (
        RelationType.INSIDE,
        RelationType.LEFT_OF,
        RelationType.RIGHT_OF,
    ),
    target_choices: tuple[str, ...] = ("box_a", "box_b", "box_c", "box_d"),
) -> ReconstructionDistortion:
    """Deterministic distortion for reproducible adversarial experiments."""

    rng = random.Random(seed)
    mode = rng.choice(("omit", "target", "relation", "confidence"))
    if mode == "omit":
        return ReconstructionDistortion(omit=True, tags=("seeded_omission",))
    if mode == "target":
        return ReconstructionDistortion(
            substitute_target_id=rng.choice(target_choices),
            fidelity=0.72,
            tags=("seeded_object_substitution",),
        )
    if mode == "relation":
        return ReconstructionDistortion(
            substitute_relation_type=rng.choice(relation_choices),
            fidelity=0.68,
            tags=("seeded_relation_substitution",),
        )
    return ReconstructionDistortion(
        confidence_multiplier=0.55,
        fidelity=0.9,
        tags=("seeded_confidence_degradation",),
    )

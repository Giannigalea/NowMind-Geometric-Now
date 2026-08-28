from __future__ import annotations

from nowmind.core.now_state import NowState
from nowmind.geometry.relation import RelationType


def has_stale_relation(
    now: NowState,
    source_id: str,
    target_id: str,
    relation_type: RelationType,
) -> bool:
    """Evaluation helper for stale-state contamination checks."""

    return now.geometry.find_relation(source_id, target_id, relation_type) is not None


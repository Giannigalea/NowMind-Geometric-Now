from __future__ import annotations

from enum import Enum


class TemporalSource(str, Enum):
    OBSERVED_NOW = "observed_now"
    INFERRED_NOW = "inferred_now"
    RECONSTRUCTED_MEMORY = "reconstructed_memory"
    HYPOTHETICAL_FUTURE = "hypothetical_future"


def source_label(source: TemporalSource | None) -> str:
    if source is None:
        return "none"
    return source.value

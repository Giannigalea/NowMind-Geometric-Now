from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


def _freeze_mapping(values: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(values or {}))


@dataclass(frozen=True, slots=True)
class Entity:
    """An object represented in the current Present Geometry."""

    entity_id: str
    kind: str
    label: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id must be non-empty")
        if not self.kind:
            raise ValueError("kind must be non-empty")
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "kind": self.kind,
            "label": self.label,
            "attributes": dict(self.attributes),
        }


from __future__ import annotations

from collections.abc import Iterable

from nowmind.world.model import WorldEvent, WorldState


def world_from_events(events: Iterable[WorldEvent]) -> WorldState:
    world = WorldState()
    for event in events:
        world.apply(event)
    return world


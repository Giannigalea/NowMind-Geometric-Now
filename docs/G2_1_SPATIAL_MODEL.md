# G2.1 Spatial Model

G2.1 uses a deterministic integer 2D grid.

Core records:

- `Pose2D(x, y)`;
- `SpatialEntity(entity_id, kind, pose, blocks_movement)`;
- `CellOccupancy(pose, state)`;
- `SpatialGeometry(width, height, entities, occupancy, derived_relations)`;
- `SpatialWorldState`, the persistent external environment.

Bounds are:

```text
0 <= x < width
0 <= y < height
```

Occupancy states remain distinct:

- `FREE`;
- `OCCUPIED`;
- `UNKNOWN`.

Observed occupied cells are blocked. Observed free cells are traversable. Unknown
cells are not treated as free unless a plan explicitly records a memory-supported
assumption.

Current observed spatial geometry can derive left/right, above/below, distance,
near, collision, and reachability relations from coordinates. These relations
are coordinate-derived current content; memory and future overlays are not
written into observed occupancy.


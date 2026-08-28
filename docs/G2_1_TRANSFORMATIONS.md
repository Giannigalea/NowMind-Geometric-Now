# G2.1 Transformations

Implemented deterministic transformations:

- `MOVE_NORTH`;
- `MOVE_SOUTH`;
- `MOVE_EAST`;
- `MOVE_WEST`;
- `WAIT`.

A `Transformation` receives a current or hypothetical `SpatialGeometry` and
creates a new `HypotheticalGeometry` record. The transformation never mutates
`SpatialWorldState`.

Every hypothetical geometry carries:

- a hypothesis id;
- parent id when generated from a prior candidate;
- root/current cycle id;
- depth;
- the transformation that produced it;
- validity;
- structured physical violations;
- `HYPOTHETICAL_FUTURE` provenance.

Physical violations include:

- `OUT_OF_BOUNDS`;
- `COLLISION`;
- `BLOCKED`;
- `UNKNOWN_CELL`;
- `INVALID_TRANSFORMATION`.

These are geometry/physics constraints only. They are not an L3 Veto Gate.


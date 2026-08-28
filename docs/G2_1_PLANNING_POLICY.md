# G2.1 Planning Policy

The default G2.1 planner is transparent A* search.

Policy:

- heuristic: Manhattan distance;
- movement: four cardinal moves;
- base move cost: `1`;
- wait cost: `0`;
- tie-breaking: deterministic east, south, west, north order plus stable heap
  ordering;
- observed occupied cells: blocked;
- observed free cells: traversable;
- unknown cells: blocked unless explicitly supported by a
  `RECONSTRUCTED_MEMORY` planning assumption;
- memory-supported unknown cells add an explicit surcharge and mark the plan
  conditional;
- a fully observed route is preferred before a conditional memory route.

Future hypotheses can be rendered and inspected as candidate future content, but
they do not overwrite the current target or obstacles. Selecting a path does not
promote any future hypothesis to observation.

Closed-loop execution:

```text
plan from current observation
-> execute one action in SpatialWorldState
-> observe again
-> build fresh TemporalNowState
-> continue only if remaining plan still matches current observation, otherwise replan
```


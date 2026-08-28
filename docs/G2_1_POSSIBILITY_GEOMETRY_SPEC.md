# G2.1 Possibility Geometry — Technical Specification

## 1. Core idea

G2 represented future hypotheses as typed propositions. G2.1 extends this into **explicit geometric state transformations**.

At cycle `t`, current geometry is `G_t`. The planner may generate transformations `T_1 ... T_n` producing hypothetical geometries `H_i = T_i(G_t)`.

Every `H_i` is a **hypothetical geometry represented now**, not observed reality.

## 2. Spatial model

Use a 2D deterministic grid world.

Recommended:

```python
@dataclass(frozen=True)
class Pose2D:
    x: int
    y: int
```

Bounds:

```text
0 <= x < width
0 <= y < height
```

Minimum entity kinds:
- agent;
- target;
- obstacle;
- optional door/container.

## 3. Occupancy

```python
class OccupancyState(Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    UNKNOWN = "unknown"
```

Observed occupancy is current geometry.
Memory-derived occupancy must not be silently written into observed occupancy.
Future occupancy must not be silently written into observed occupancy.

## 4. Spatial geometry

Conceptual:

```python
@dataclass(frozen=True)
class SpatialGeometry:
    width: int
    height: int
    entities: tuple[SpatialEntity, ...]
    occupancy: tuple[...]
    derived_relations: tuple[Relation, ...]
    cycle_id: int
```

Where practical derive left/right, above/below, distance, near, collision, adjacency, and reachability.

## 5. Transformation

```python
class TransformationType(Enum):
    MOVE_NORTH = "move_north"
    MOVE_SOUTH = "move_south"
    MOVE_EAST = "move_east"
    MOVE_WEST = "move_west"
    WAIT = "wait"
```

A transformation records ID, type, actor, cost, source cycle, and generation reason. It never mutates the world.

## 6. Hypothetical geometry

Conceptual:

```python
@dataclass(frozen=True)
class HypotheticalGeometry:
    hypothesis_id: UUID
    parent_id: UUID | None
    created_at_cycle_id: int
    depth: int
    geometry: SpatialGeometry
    transformation: Transformation
    valid: bool
    violations: tuple[ConstraintViolation, ...]
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE
```

Requirements:
- immutable;
- separate from world state;
- separate from observed Present Geometry;
- may form a search tree/DAG;
- never promoted to observation automatically.

## 7. Physical constraints

At minimum:
- in bounds;
- no obstacle collision;
- no teleportation;
- one move changes position by one configured unit.

Return structured violations such as `OUT_OF_BOUNDS`, `COLLISION`, `BLOCKED`, and `INVALID_TRANSFORMATION`.

This is geometry/physics validation, not ethical veto.

## 8. Planning assumptions

Memory and future information may support candidate branches.

```python
@dataclass(frozen=True)
class PlanningAssumption:
    assumption_id: UUID
    proposition: Proposition
    source: TemporalSource
    confidence: float
    description: str
```

Assumptions must never be relabeled as observed.

## 9. Unknown cells

Recommended policy:
- observed occupied -> blocked;
- observed free -> traversable;
- unknown -> not definitely free;
- memory may support a conditional route through unknown space;
- such plans must be marked assumption-dependent;
- prefer fully observed routes when reasonable;
- if only conditional routes exist, report them as conditional rather than guaranteed.

Exact cost/risk policy must be documented and benchmark-configurable.

## 10. Planner

Use A* or Dijkstra.

Recommended A* heuristic for four-directional grid movement:

```text
Manhattan distance
|x1-x2| + |y1-y2|
```

Base cardinal move cost = 1.
Optional assumption/risk surcharge may be applied but must be explicit.
Tie-breaking must be deterministic.

## 11. Plan

Conceptual:

```python
@dataclass(frozen=True)
class Plan:
    plan_id: UUID
    created_at_cycle_id: int
    start: Pose2D
    goal: Pose2D
    steps: tuple[PlanStep, ...]
    total_cost: float
    valid: bool
    assumptions: tuple[PlanningAssumption, ...]
    conditional: bool
    explanation: tuple[str, ...]
```

A plan is a current representation of a possible action sequence. It is not the future.

## 12. Action execution

Only the executor may mutate the real world:

```text
ActionProposal
-> ActionExecutor
-> WorldState mutation
```

Then:

```text
WorldState
-> perception
-> fresh PresentGeometry
-> fresh TemporalNowState
```

The executor must apply the selected concrete action, not replace the world with a hypothetical snapshot.

## 13. Closed-loop replanning

After every action:
1. observe;
2. reconstruct current geometry;
3. compare current geometry with remaining plan/assumptions;
4. continue if valid;
5. otherwise replan.

Replan for new obstacles, door changes, moved target, falsified memory, or falsified hypothesis.

## 14. Prediction confirmation

A hypothetical state and a later matching observation remain separate records. The evaluator may mark confirmation, but only the later observation is `OBSERVED_NOW`.

## 15. Search-tree provenance

Every candidate hypothetical state should be traceable to parent, transformation, depth, current-cycle root, assumptions, and validation result.

## 16. No Veto Gate yet

Reject collisions/out-of-bounds as physical infeasibility. Do not call this L3 Veto.

# Geometric Now G1 — Technical Specification

## 1. Objective

Implement a local deterministic prototype demonstrating that a reasoning system can repeatedly reconstruct a complete current relational state from current observations and reason over that state without directly carrying previous cognitive states forward.

## 2. G1 architecture

```text
        SIMULATED WORLD
              |
          WorldState
              |
              v
       L1 PERCEPTION
              |
        Observation_t
              |
              v
    L1.5 PRESENT GEOMETRY
              |
      PresentGeometry_t
              |
              v
       immutable NowState_t
              |
              v
    L2 DETERMINISTIC REASONER
              |
          Answer_t

External-only path:
NowState_t -> ExperimentRecorder
                 |
                 v
        history/evaluation logs

The runtime reasoner MUST NOT read ExperimentRecorder history.
```

## 3. Required packages/modules

Suggested repository structure:

```text
nowmind/
  __init__.py

  world/
    __init__.py
    model.py
    events.py
    simulator.py

  perception/
    __init__.py
    observation.py
    adapter.py

  geometry/
    __init__.py
    entity.py
    relation.py
    present_geometry.py
    builder.py
    inference.py
    validation.py

  core/
    __init__.py
    now_state.py
    cycle.py

  reasoning/
    __init__.py
    query.py
    reasoner.py

  evaluation/
    __init__.py
    recorder.py
    metrics.py

  demo/
    __init__.py
    scenarios.py
    cli.py

tests/
  unit/
  architecture/
  scenarios/
```

Codex may adjust filenames if necessary, but conceptual boundaries must remain.

## 4. Domain objects

### `WorldState`

Purpose:
- persistent environment ground truth;
- mutable only through explicit world events;
- not accessible directly to the reasoner.

Minimum fields:
- `entities`
- physical/relational properties
- `cycle_index` or version

### `WorldEvent`

Examples:
- add entity;
- remove entity;
- move entity;
- set containment;
- set contact/support;
- alter attribute.

Events update the world, not the Now directly.

### `Observation`

A snapshot produced for the current cycle.

Minimum:
- cycle id;
- observed entities;
- observed spatial properties;
- confidence;
- source/provenance.

G1 may use perfect perception by default so reasoning errors are not confused with perception errors.

### `Entity`

Minimum:
- stable environment `entity_id`;
- `kind`;
- optional human-readable `label`;
- current attributes;
- confidence/provenance if appropriate.

Stable entity IDs represent external object identity, not cognitive continuity.

### `Relation`

Minimum:
- source entity id;
- target entity id;
- relation type;
- optional scalar/vector value;
- optional unit;
- confidence;
- provenance = `OBSERVED_NOW` or `INFERRED_NOW`;
- rule id if inferred.

### `PresentGeometry`

A read-only graph/constraint structure for the current cycle.

Requirements:
- cannot contain stale relations from a previous cycle unless they are independently observed again now;
- supports queries;
- keeps observed and inferred facts distinguishable;
- validates contradictions.

### `NowState`

Minimum:
- unique `now_id`;
- cycle id;
- creation timestamp;
- `PresentGeometry`;
- optional current attention/query context if needed.

Requirements:
- immutable;
- contains no link/reference to previous `NowState`;
- contains no history list;
- contains no memory store;
- contains no predicted future state.

## 5. Relation vocabulary for G1

Minimum directional:
- `LEFT_OF`
- `RIGHT_OF`
- `ABOVE`
- `BELOW`

Minimum topology/containment:
- `INSIDE`
- `CONTAINS`
- `TOUCHING`
- `ON`
- `UNDER`

Optional if coordinates are implemented:
- `NEAR`
- `FAR`
- `DISTANCE`
- `ORIENTATION`

## 6. Inference rules

At minimum implement:

### Inverse relations

`LEFT_OF(A,B) -> RIGHT_OF(B,A)`

`ABOVE(A,B) -> BELOW(B,A)`

`INSIDE(A,B) -> CONTAINS(B,A)`

`ON(A,B) -> UNDER(B,A)` where semantically appropriate.

### Symmetric relations

`TOUCHING(A,B) -> TOUCHING(B,A)`

### Transitive relations

Where safe:

`LEFT_OF(A,B) AND LEFT_OF(B,C) -> LEFT_OF(A,C)`

`ABOVE(A,B) AND ABOVE(B,C) -> ABOVE(A,C)`

Containment may support:

`INSIDE(A,B) AND INSIDE(B,C) -> INSIDE(A,C)`

Do not blindly make all relations transitive.

## 7. Confidence

G1 may begin with all perfect observations at confidence `1.0`.

However the data model must support 0..1 confidence.

For inferred relations, use an explicit deterministic policy documented in code. A conservative starting rule is:

`confidence(inference) = min(confidence(premises))`

Do not invent probabilistic semantics beyond what is specified.

## 8. Contradictions

The geometry validator must detect at least:
- `LEFT_OF(A,B)` and `RIGHT_OF(A,B)` when both are asserted as simultaneous incompatible facts under a strict 1D ordering model;
- `ABOVE(A,B)` and `BELOW(A,B)`;
- invalid self-relations where applicable;
- missing entity references.

Contradiction handling in G1:
- do not silently delete one side;
- expose a structured validation result;
- reasoner may return `UNKNOWN` or `CONTRADICTORY`.

## 9. Query API

Minimum queries:

- `relation(A, B, relation_type)`
- `where_is(A, relative_to=B)`
- `is_inside(A, B)`
- `what_contains(A)`
- `explain(A, relation, B)`

Results should include:
- answer (`TRUE`, `FALSE`, `UNKNOWN`, `CONTRADICTORY`);
- confidence;
- supporting observed/inferred relations;
- rule chain/explanation.

The explanation path is important for later research communication.

## 10. Cognitive cycle

Pseudo-code:

```python
def cognitive_cycle(world: WorldState, query: Query) -> Answer:
    observation = perception.observe(world)
    geometry = geometry_builder.build(observation)
    now = NowState.create(geometry=geometry)
    answer = reasoner.answer(now, query)
    experiment_recorder.record(now, query, answer)  # external only
    return answer
```

Forbidden:

```python
def cognitive_cycle(previous_now, ...):
    now = mutate(previous_now)
```

Also forbidden:

```python
reasoner.answer(now, history=recorder.history)
```

## 11. Demonstration scenarios

### Scenario A — Fresh reconstruction

Cycle 1:
- red cube left of blue cube.

Cycle 2 world event:
- red cube moves to right of blue cube.

Required:
- Cycle 2 Present Geometry says red cube is right of blue cube;
- no stale `LEFT_OF(red, blue)` remains;
- the new Now does not need the previous Now to know current geometry.

### Scenario B — Inference

Current observations:
- A left of B;
- B left of C.

Required inference:
- A left of C.

Explanation must identify the premises and transitivity rule.

### Scenario C — Containment

- key inside box;
- box inside cabinet.

Required:
- key inside cabinet;
- cabinet contains key.

### Scenario D — Contradiction

Inject incompatible relations in one current observation.

Required:
- validation detects contradiction;
- reasoner does not fabricate certainty.

### Scenario E — History firewall

Record several previous Nows.

Required:
- runtime reasoner has no API to retrieve old Nows;
- architecture test verifies cognitive modules do not import evaluation history.

## 12. G1 completion definition

G1 is complete only when:
- all invariant tests pass;
- all demonstration scenarios pass;
- project runs locally on Windows;
- no LLM/cloud/network is needed;
- the architecture can demonstrate through code/tests that previous NowStates are not cognitive inputs;
- a human-readable demo can show state, inferred relations, and explanations per cycle.

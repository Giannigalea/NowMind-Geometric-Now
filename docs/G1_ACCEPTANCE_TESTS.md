# G1 Acceptance Tests

Automated tests must cover these invariants.

## A. Now lifecycle

### G1-NOW-001 Fresh object
Two consecutive cycles produce different `now_id` values.

### G1-NOW-002 Immutable
Attempting to mutate a core `NowState` field fails.

### G1-NOW-003 No previous reference
`NowState` has no `previous_now`, `history`, or equivalent field.

### G1-NOW-004 Rebuild from observation
Changing the world and running the next cycle reconstructs the geometry from the new observation.

### G1-NOW-005 No stale relation
A relation true only in cycle 1 does not survive cycle 2 unless observed/inferred from cycle 2 information.

## B. History firewall

### G1-HIST-001 Recorder external
Experiment recorder can save historical Nows.

### G1-HIST-002 Reasoner isolation
Reasoning API accepts current `NowState` and query only; no history argument.

### G1-HIST-003 No history import
Runtime reasoning modules do not import or instantiate experiment-history retrieval.

### G1-HIST-004 History deletion equivalence
Running the current reasoning query after deleting external logs returns the same answer.

This is a critical test: G1 cognition must not depend on experimental history.

## C. Relations

### G1-REL-001 Inverse left/right
Observed `LEFT_OF(A,B)` yields inferred `RIGHT_OF(B,A)`.

### G1-REL-002 Inverse above/below
Observed `ABOVE(A,B)` yields inferred `BELOW(B,A)`.

### G1-REL-003 Containment inverse
Observed `INSIDE(A,B)` yields inferred `CONTAINS(B,A)`.

### G1-REL-004 Touching symmetric
Observed `TOUCHING(A,B)` yields `TOUCHING(B,A)`.

### G1-REL-005 Left transitivity
`LEFT_OF(A,B)` + `LEFT_OF(B,C)` yields `LEFT_OF(A,C)`.

### G1-REL-006 Above transitivity
`ABOVE(A,B)` + `ABOVE(B,C)` yields `ABOVE(A,C)`.

### G1-REL-007 Nested containment
`INSIDE(A,B)` + `INSIDE(B,C)` yields `INSIDE(A,C)`.

### G1-REL-008 Non-transitive protection
Do not infer `TOUCHING(A,C)` from `TOUCHING(A,B)` + `TOUCHING(B,C)`.

## D. Provenance

### G1-PROV-001 Observed label
Direct facts are marked `OBSERVED_NOW`.

### G1-PROV-002 Inferred label
Derived facts are marked `INFERRED_NOW`.

### G1-PROV-003 Explanation chain
An inferred answer can return the rule and premises that produced it.

## E. Confidence

### G1-CONF-001 Range
Confidence must be within [0,1].

### G1-CONF-002 Conservative inference
With the initial policy, inferred confidence is no greater than the least-confident premise.

## F. Contradiction / unknown

### G1-VAL-001 Missing entity
Relation referencing an unknown entity is invalid.

### G1-VAL-002 Contradiction surfaced
Incompatible current facts produce a structured contradiction.

### G1-VAL-003 Unknown remains unknown
If the geometry contains insufficient evidence, the reasoner returns `UNKNOWN` rather than guessing.

## G. End-to-end scenarios

### G1-E2E-001 Move object
Cycle 1: A left of B.
World event.
Cycle 2: A right of B.
Cycle 2 answer must reflect only the new state.

### G1-E2E-002 Three-object chain
A left B, B left C.
Query A left C -> TRUE with explanation.

### G1-E2E-003 Nested containers
key in box in cabinet.
Query key in cabinet -> TRUE with explanation.

### G1-E2E-004 Current contradiction
Conflicting current inputs -> CONTRADICTORY/invalid, not a fabricated answer.

## Required final command

The project should document a single command equivalent to:

```text
python -m pytest
```

and a demo command equivalent to:

```text
python -m nowmind.demo.cli
```

Exact packaging may vary.

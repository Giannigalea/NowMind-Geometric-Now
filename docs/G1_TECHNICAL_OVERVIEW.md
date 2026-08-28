# G1 Technical Overview

## 1. Problem

NowMind Geometric Now G1 is a small research prototype for testing one
architectural constraint: a reasoning system should answer from a freshly
constructed current state, rather than silently carrying a previous cognitive
state forward. The project is inspired by Present Consciousness Theory (PCT), but
G1 is deliberately modest. It tests representation boundaries, deterministic
reasoning, provenance, and stale-state resistance. It does not test phenomenal
consciousness.

The motivating failure mode is temporal contamination. A conventional agent can
easily blend current facts, prior conversation, retrieved records, predictions,
and inferred assumptions into one undifferentiated context. That can be useful in
many applications, but it is a poor test bed for PCT-inspired state separation.
G1 therefore asks a narrower engineering question: can the system reason
correctly over current relations after the world changes, without directly using
the previous `NowState` as input?

## 2. PCT-inspired computational constraint

The governing computational rule is:

```text
WorldState_t -> Observation_t -> PresentGeometry_t -> NowState_t -> Reasoner
```

At each cycle, the current `WorldState` is observed, the observation is converted
into a Present Geometry, and a new immutable `NowState` is created. The reasoner
receives that current `NowState` and a current query. It does not receive a
previous Now, experiment logs, memory store, future hypothesis, identity object,
or hidden history.

This is a software boundary, not a metaphysical claim. Passing the tests shows
that the implementation respects the boundary under the tested scenarios. It does
not prove PCT and does not establish machine consciousness.

## 3. Architecture

The runtime package is intentionally plain Python:

```text
world -> perception -> geometry -> core -> reasoning
```

The `world` package models persistent simulated environment ground truth. The
`perception` package snapshots the current world into an `Observation`. The
`geometry` package builds the current relational graph and applies deterministic
inference and validation. The `core` package creates immutable `NowState`
objects. The `reasoning` package answers queries from the current `NowState`.

The `evaluation` package is outside the runtime cognitive path. It may record
historical Nows for experiments, generate evidence artifacts, and compute
metrics. Runtime cognitive packages are tested to ensure they do not import
`nowmind.evaluation`.

## 4. Why `WorldState` and `NowState` are separated

G1 allows the world to persist. A cube can remain the same environmental object
as it moves. This is not treated as cognitive persistence. The `WorldState`
represents external ground truth and changes only through explicit world events
such as `AddEntity`, `SetRelation`, or `MoveRelation`.

`NowState` is different. It is the current cognitive representation created for
one cycle. It is frozen, has a unique `now_id`, and contains a current
`PresentGeometry`. It has no `previous_now`, `history`, `memory`, `future_states`,
or identity-history fields. The separation lets G1 model causal continuity in
the world without implementing continuity as a hidden mutable cognitive object.

## 5. Present Geometry

Present Geometry is the L1.5 representation: a typed relational graph built from
current observations. Entities are nodes. Relations are edges with a source,
target, relation type, confidence, and provenance.

G1 implements a compact relation vocabulary: `LEFT_OF`, `RIGHT_OF`, `ABOVE`,
`BELOW`, `INSIDE`, `CONTAINS`, `TOUCHING`, `ON`, and `UNDER`. Directly observed
facts are marked `OBSERVED_NOW`. Derived facts are marked `INFERRED_NOW` and
carry rule IDs and premise IDs. This distinction is essential for inspection:
reviewers can see whether an answer came from current observation or deterministic
current-cycle inference.

## 6. Deterministic inference

The inference engine is symbolic and deterministic. It implements inverse rules,
safe symmetric rules, and selected transitive rules. Examples:

```text
LEFT_OF(A, B) -> RIGHT_OF(B, A)
TOUCHING(A, B) -> TOUCHING(B, A)
LEFT_OF(A, B) + LEFT_OF(B, C) -> LEFT_OF(A, C)
INSIDE(A, B) + INSIDE(B, C) -> INSIDE(A, C)
```

It does not blindly make every relation transitive. For example, touching is
symmetric but not transitive. Confidence is also deterministic:

```text
confidence(inference) = min(confidence(premises))
```

This is deliberately conservative. G1 does not invent probabilistic semantics
beyond the acceptance tests.

## 7. History firewall

The most important invariant is the history firewall. A previous `NowState` may
be recorded externally for experiment analysis, but it must not become cognitive
input to the next cycle. This is enforced in several ways:

- `NowState` has no previous/history fields.
- `CognitiveCycleRunner` stores a cycle counter, perception adapter, and geometry
  builder, but not prior Nows.
- `PresentGeometryBuilder.build()` accepts only an `Observation`.
- `PerceptionAdapter.observe()` accepts only the current `WorldState` and cycle ID.
- `reasoning.answer()` accepts only `now` and `query`.
- Runtime packages do not import the evaluation recorder.
- Deleting external experiment history does not change current reasoning answers.

The G1.1 browser demo preserves this boundary. Its history panel is researcher
instrumentation. It is not routed into the reasoner.

## 8. Experiments

The canonical experiments are:

1. Fresh Now / stale-state test: cycle 1 observes `red_cube LEFT_OF blue_cube`;
   a world event moves the red cube; cycle 2 observes `red_cube RIGHT_OF
   blue_cube`; the active geometry has no stale `red_cube LEFT_OF blue_cube`.
2. Geometric inference: `A LEFT_OF B` and `B LEFT_OF C` imply `A LEFT_OF C`.
3. Nested containment: `key INSIDE box` and `box INSIDE cabinet` imply `key
   INSIDE cabinet`.
4. Contradiction: simultaneous incompatible current facts produce structured
   validation issues and a `CONTRADICTORY` answer.
5. History firewall: deleting external experiment history and rerunning the same
   current query leaves the answer unchanged.

The repeatable runner `python -m nowmind.evaluation.run_g1_suite` generates JSON
evidence for these scenarios under `artifacts/g1/`.

## 9. Results

The G1.1 suite computes:

- scenario count;
- query accuracy;
- inference accuracy;
- contradiction detection rate;
- stale-state contamination count and rate;
- unknown-guess count.

For the deterministic G1 implementation, the target stale-state contamination
rate is `0.0`. Evidence artifacts include the observed relations, inferred
relations, query, answer, explanation, validation state, cycle ID, and `now_id`
for every canonical cycle.

## 10. Limitations

G1 uses perfect simulated perception. It does not model noisy sensors, real
vision, uncertain object detection, coordinates, distances, rotations, language
understanding, or action selection. Its reasoner is intentionally small and
symbolic. The contradiction policy is conservative: any current geometry
contradiction causes a `CONTRADICTORY` answer rather than attempting local
conflict resolution per query.

The external recorder stores experiment summaries. It is not a memory system.
The browser demo is an inspector, not a cognitive UI.

## 11. What G1 does NOT claim

G1 does not claim that NowMind is conscious, sentient, self-aware, alive, or an
AGI. It does not prove PCT. It does not demonstrate subjective experience. It
does not implement quantum consciousness. It tests a computational architecture:
fresh state reconstruction, relation provenance, deterministic reasoning, and a
history firewall.

## 12. G2 research direction

G2 may introduce temporal-source channels such as reconstructed memory and
hypothetical future states. If that work begins, it must preserve source
separation. A remembered event should enter the current Now only as an explicitly
marked reconstruction, not as a replayed historical `NowState`. A predicted
future should enter only as an explicitly marked hypothesis, not as observation.

G1.1 stops before that. Its purpose is presentation, auditability,
reproducibility, and evidence generation for the G1 boundary.


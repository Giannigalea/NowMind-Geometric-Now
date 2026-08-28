# G2.1 Acceptance Tests

All G1 and G2 tests remain mandatory.

## A. Spatial geometry

- G2.1-SPAT-001: entities have valid in-bounds coordinates.
- G2.1-SPAT-002: occupied/free/unknown cells remain distinct.
- G2.1-SPAT-003: spatial relations derive from coordinates where applicable.
- G2.1-SPAT-004: collision/blocking derives from geometry.

## B. Hypothetical states

- G2.1-HYP-001: every transformation creates a new immutable hypothetical geometry.
- G2.1-HYP-002: generating hypothetical state does not mutate WorldState.
- G2.1-HYP-003: every hypothetical geometry has future provenance.
- G2.1-HYP-004: every branch records parent/transformation.
- G2.1-HYP-005: invalid transformations return structured violations.

## C. Transformations

- G2.1-TR-001: cardinal movement correct.
- G2.1-TR-002: out-of-bounds invalid.
- G2.1-TR-003: movement into observed obstacle invalid.
- G2.1-TR-004: no teleportation.

## D. Planner

- G2.1-PLAN-001: valid route found in simple map.
- G2.1-PLAN-002: no-route condition reported.
- G2.1-PLAN-003: deterministic planning.
- G2.1-PLAN-004: plan exposes steps/cost/assumptions.
- G2.1-PLAN-005: chronological control uses same pathfinding quality or equivalent.

## E. Memory assumptions

- G2.1-MEM-001: observed blocked overrides memory free.
- G2.1-MEM-002: observed free overrides stale memory blocked.
- G2.1-MEM-003: unknown not silently treated as known-free.
- G2.1-MEM-004: memory-supported unknown route marked conditional.
- G2.1-MEM-005: memory assumption retains `RECONSTRUCTED_MEMORY` provenance.

## F. Future hypotheses

- G2.1-FUT-001: future branch retains hypothetical provenance.
- G2.1-FUT-002: plan selection does not promote hypothesis to observation.
- G2.1-FUT-003: only later real observation creates `OBSERVED_NOW`.
- G2.1-FUT-004: false hypothesis does not remain current fact.

## G. Action execution

- G2.1-ACT-001: executor is only world-mutation path.
- G2.1-ACT-002: executor applies concrete action, not whole hypothetical snapshot.
- G2.1-ACT-003: every action followed by fresh observation before next planning decision.
- G2.1-ACT-004: post-action cognition creates a fresh TemporalNowState.

## H. Replanning

- G2.1-REP-001: new obstacle triggers invalidation/replan when relevant.
- G2.1-REP-002: moved target updates goal/replan.
- G2.1-REP-003: observation contradicting memory invalidates memory-dependent assumption.
- G2.1-REP-004: falsified hypothesis triggers reassessment.
- G2.1-REP-005: remaining stale route is not blindly executed after change.

## I. Benchmark integrity

- G2.1-BENCH-001: default runs at least 2,000 trials, target 3,000.
- G2.1-BENCH-002: D1-D5 represented.
- G2.1-BENCH-003: all required families represented.
- G2.1-BENCH-004: same seed/config reproduces trials/aggregate metrics.
- G2.1-BENCH-005: ground truth external.
- G2.1-BENCH-006: Oracle evaluator-only.
- G2.1-BENCH-007: failures saved.
- G2.1-BENCH-008: metrics derived, not hard-coded.

## J. Visual demonstrator

- G2.1-WEB-001: 2D world renders agent, target, obstacles.
- G2.1-WEB-002: selected and rejected candidate paths visualized.
- G2.1-WEB-003: current/memory/hypothesis overlays visually distinct.
- G2.1-WEB-004: dynamic obstacle/target change visibly triggers replanning.
- G2.1-WEB-005: hypothetical future visibly distinct from observed world.

## Completion definition

G2.1 is complete only when all G1/G2/G2.1 tests pass, explicit 2D geometry exists, hypothetical transformations never mutate real world, closed-loop action/re-observation works, dynamic replanning works, benchmark completes with preserved failures, and browser demo visibly communicates possibility geometry.

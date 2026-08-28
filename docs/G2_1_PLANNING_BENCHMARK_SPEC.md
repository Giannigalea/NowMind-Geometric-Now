# G2.1 Planning Benchmark Specification

## 1. Research purpose

Test whether explicit Possibility Geometry supports reliable planning and replanning under spatial complexity, stale/false memory, partial observation, dynamic environment changes, and future hypotheses.

Also determine whether a well-designed chronological geometric planner performs equivalently. Do not assume NowMind should win.

## 2. Systems

### N — NowMind Possibility Geometry Planner
Uses current observed geometry, memory as typed assumptions, future hypotheses as typed possibilities, explicit hypothetical transformations, and closed-loop re-observation.

### C — Chronological Geometric Planner
Fair control using the same spatial world, movement set, and pathfinding quality, but chronological record semantics rather than fresh TemporalNow representation. Decision rules must be documented.

### R — Reactive Current-Only Planner
Uses current observations only. No memory or future hypotheses. Restricted control, not state of the art.

### O — Oracle Planner
Evaluator-only upper bound with full ground-truth current world. Not a fair cognitive competitor.

## 3. Canonical benchmark

Default trial count: target 3,000; minimum 2,000 if runtime is excessive.

Difficulty bands D1-D5 should monotonically increase grid size, obstacle density, partial observation, path length, memory conflict, dynamic change, distractors, and replanning demands.

Suggested bands:
- D1: 8x8, low obstacles, static, fully observed.
- D2: 10x10, moderate obstacles, memory/distractors.
- D3: 12x12, partial observation, stale memory, alternate routes.
- D4: 16x16, dynamic obstacles/targets, false memory/hypothesis conflicts.
- D5: 20x20 or similar, multiple dynamic changes, partial visibility, stale/false memory, competing hypotheses, multiple replans.

Adjust for runtime while preserving monotonic difficulty.

## 4. Scenario families

At minimum:

P1 Static shortest path.
P2 Stale remembered obstacle: memory blocked, current free.
P3 Stale remembered free cell: memory free, current blocked.
P4 False remembered shortcut.
P5 Occluded remembered corridor, requiring conditional planning.
P6 Dynamic obstacle appears after execution begins.
P7 Dynamic obstacle disappears.
P8 Target moves.
P9 Future target hypothesis true.
P10 Future target hypothesis false.
P11 Multiple routes: short assumption-dependent vs longer fully observed.
P12 Dead end.
P13 Multiple dynamic changes.
P14 Contradictory current geometry.
P15 Nested/contained goal requiring approach to access cell.
P16 Long history with many prior traces.

## 5. Dynamic event scheduling

External evaluator may schedule changes after N actions, at trigger cells, or at fixed cycles. Runtime planner must not know future evaluator events unless represented as an allowed hypothesis.

## 6. Ground truth

External evaluator owns true occupancy, dynamic event schedule, target truth, optimal current path, and truth/falsity of memory/hypotheses. Cognitive systems cannot access it.

## 7. Metrics

Planning:
- planning_success_rate
- goal_reached_rate
- valid_plan_rate
- invalid_action_rate
- collision_count
- collision_rate

Efficiency:
- path_efficiency
- optimality_gap_vs_oracle
- mean_executed_steps
- mean_planned_steps
- mean_planning_time_ms

Replanning:
- mean_replans
- replan_success_rate
- dynamic_change_recovery_rate
- unnecessary_replan_rate

Temporal/source integrity:
- stale_memory_planning_error_count/rate
- false_memory_planning_error_count/rate
- prediction_as_fact_planning_error_count/rate
- unsupported_assumption_count
- conditional_plan_rate
- assumption_validation_success_rate
- hypothesis_confirmation_violations

Closed-loop integrity:
- observation_after_action_rate
- plan_revalidation_rate

## 8. Difficulty reporting

Report every major metric overall, by D1-D5, by scenario family, and by system. Do not hide ceiling effects.

## 9. Failure preservation

Save representative failures for every system with trial ID, seed, initial geometry, temporal information, generated plan, executed steps, world changes, replans, failure type, and expected/actual outcome.

## 10. Fairness rules

Do not let NowMind see privileged information, use weaker pathfinding for controls, hide baseline wins, retune difficulty without versioning, or present Oracle as a fair competitor.

## 11. Interpretation

Potentially meaningful:

> Explicit Possibility Geometry preserves temporal-source distinctions while supporting closed-loop replanning under dynamic spatial change.

Stronger claim requiring evidence:

> NowMind yields lower stale-memory-induced planning errors than a chronological geometric representation under specified partial-observation/dynamic conditions.

Invalid at this stage:

> NowMind is generally superior to modern AI planners.

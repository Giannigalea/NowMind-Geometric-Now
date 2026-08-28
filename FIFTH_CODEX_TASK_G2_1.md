# FIFTH CODEX TASK — NowMind G2.1 Possibility Geometry

## Mission

Implement **NowMind G2.1 — Possibility Geometry** on top of the completed G1 and G2 architecture.

G1 established fresh Present Geometry and no direct cognitive carry-forward of previous NowStates.

G2 established explicit `OBSERVED_NOW`, `INFERRED_NOW`, `RECONSTRUCTED_MEMORY`, and `HYPOTHETICAL_FUTURE`, with memory reconstruction rather than historical Now replay.

G2.1 introduces:

> explicit geometric transformations of the current state into candidate hypothetical states, plus closed-loop spatial planning and replanning.

The central rule remains:

```text
A candidate future geometry is a present hypothesis.
It is NOT an observed future.
```

and:

```text
Executing an action changes the external world.
Only a subsequent observation can create the next observed Now.
```

## 1. Read before coding

Read fully:

1. `AGENTS.md`
2. `docs/PCT_COMPUTATIONAL_RULES.md`
3. `docs/G2_TEMPORAL_GEOMETRY_SPEC.md`
4. `docs/G2_ARCHITECTURE.md`
5. `docs/G2_MEMORY_MODEL.md`
6. `docs/G2_TEMPORAL_REASONING_POLICY.md`
7. `docs/G2_BENCHMARK_METHOD.md`
8. `docs/G2_1_POSSIBILITY_GEOMETRY_SPEC.md`
9. `docs/G2_1_PLANNING_BENCHMARK_SPEC.md`
10. `docs/G2_1_ACCEPTANCE_TESTS.md`
11. `docs/G2_1_VISUAL_DEMO_SPEC.md`
12. current G1/G2 source and tests.

Preserve every G1/G2 invariant.

## 2. Preserve G1 and G2

- all existing G1 tests remain green;
- all existing G2 tests remain green;
- G1 `NowState` semantics do not change;
- G2 `TemporalNowState` semantics do not change;
- memory continues to store traces, not old Nows;
- hypotheses remain `HYPOTHETICAL_FUTURE`;
- no hypothesis may become `OBSERVED_NOW` merely because a planner selected it;
- researcher history remains external to cognition.

Prefer additive modules under a new spatial/possibility/planning layer.

## 3. Target architecture

```text
EXTERNAL WORLD
     |
     v
WorldState_t
     |
     v
Observation_t
     |
     v
PresentGeometry_t
     |
     v
TemporalNowState_t
     |
     +-----------------------------+
     |                             |
     v                             v
Current spatial geometry      Reconstructed memory
     |                             |
     +-------------+---------------+
                   |
                   v
          PossibilityGenerator
                   |
                   v
         Candidate Transformations
           /        |        \
          /         |         \
         v          v          v
   HypGeom H1   HypGeom H2   HypGeom H3
         |          |          |
         v          v          v
   constraint    constraint   constraint
   validation    validation   validation
          \         |         /
           \        |        /
            +-------+-------+
                    |
                    v
                 Planner
                    |
                    v
             ActionProposal
                    |
                    v
             ActionExecutor
        (changes WORLD only)
                    |
                    v
              WorldState_t+1
                    |
                    v
               Observation
                    |
                    v
               NEW NOW
```

There is no direct cognitive arrow:

```text
HypotheticalGeometry_t ----------------X----------------> OBSERVED_NOW_(t+1)
```

Instead:

```text
HypotheticalGeometry_t
-> selected action
-> external world change
-> new observation
-> new observed PresentGeometry
```

## 4. Implement actual 2D geometry

Use a deterministic local 2D grid world.

Minimum concepts:

- world width/height;
- integer `(x, y)` positions;
- obstacles;
- agent position;
- target position;
- optional containers/doors;
- occupied/free/unknown cells.

Relations such as `LEFT_OF`, `RIGHT_OF`, `ABOVE`, `BELOW`, `NEAR`, `DISTANCE`, `COLLIDES_WITH`, and `REACHABLE` should be derived from geometry where practical rather than manually declared.

## 5. Required new domain concepts

Implement at minimum:

- `Pose2D`
- `SpatialEntity`
- `SpatialGeometry`
- `OccupancyState`
- `Transformation`
- `TransformationType`
- `HypotheticalGeometry`
- `ConstraintViolation`
- `TransformationOutcome`
- `PlanStep`
- `Plan`
- `PlanningAssumption`
- `ActionProposal`
- `ActionExecutionResult`

Core hypothetical objects should be immutable and explicitly future/hypothetical.

## 6. Transformation semantics

Start with deterministic transformations:

- move north;
- move south;
- move east;
- move west;
- optionally wait.

A transformation:
1. receives the current or hypothetical geometry;
2. creates a **new hypothetical geometry**;
3. never mutates the actual world;
4. records the transformation that produced it;
5. records constraint violations if invalid.

Collision/bounds checks are physical constraints, not L3 ethical veto logic.

## 7. Planner

Use a transparent deterministic planner.

Preferred: A* with Manhattan distance for four-directional movement. Dijkstra is acceptable if clearer.

Document:
- heuristic;
- tie-breaking;
- movement cost;
- traversability;
- unknown-cell policy;
- memory-supported assumptions.

Do not hide planning in a black-box library if a small inspectable implementation is practical.

## 8. Closed-loop planning

Default execution model:

```text
plan from current TemporalNow
-> select next action
-> execute ONE action in external world
-> observe again
-> build fresh Now
-> validate remaining plan against new present geometry
-> continue or replan
```

Do not blindly execute an entire precomputed path without re-observation.

## 9. Memory and planning

Memory may influence planning only through explicit assumptions.

Example:

```text
Current observation:
door state UNKNOWN

Reconstructed memory:
door OPEN

Possible plan:
route through door

PlanningAssumption:
door_open_based_on_memory
source = RECONSTRUCTED_MEMORY
confidence = 0.78
```

The planner may prefer fully observed routes, generate conditional memory-supported routes, and revalidate after observation. It must not relabel memory as current observation.

## 10. Hypotheses and planning

Future hypotheses may generate candidate planning branches but may not overwrite current target/obstacle state.

Executing toward a hypothesis does not make it true. Later observation must confirm or falsify it.

## 11. Plan output

Plans must expose:
- plan ID;
- current cycle;
- start/goal;
- ordered steps;
- total cost;
- validity;
- assumptions;
- conditional status;
- rejected alternatives where practical;
- explanation.

Each step should expose transformation, from/to pose, cost, and validation result.

## 12. Visual demonstrations

Implement `docs/G2_1_VISUAL_DEMO_SPEC.md`.

The UI must visibly render:
- 2D world/grid;
- agent;
- target;
- obstacles;
- current observed geometry;
- remembered overlay;
- future overlay;
- candidate paths;
- selected path;
- rejected/invalid path;
- dynamic replanning.

## 13. Required benchmark

Implement `docs/G2_1_PLANNING_BENCHMARK_SPEC.md`.

Canonical command:

```text
python -m nowmind.evaluation.run_g2_1_benchmark
```

Default:
- fixed documented seed;
- target at least 3,000 trials;
- minimum 2,000 if 3,000 is impractical, with justification;
- multiple difficulty levels;
- multiple scenario families;
- external ground truth;
- reproducible output;
- preserved failures.

Do not tune the benchmark after seeing results merely to improve NowMind.

## 14. Comparison systems

### System N — NowMind Possibility Geometry Planner
Uses current observed geometry, memory as typed assumptions, future hypotheses as typed possibilities, explicit hypothetical transformations, and closed-loop re-observation.

### System C — Chronological Geometric Planner
Fair symbolic control using the same spatial world, movement rules, and pathfinding quality, but chronological temporal records instead of NowMind's fresh TemporalNow representation. Document record resolution. Do not intentionally cripple it.

### System R — Reactive Current-Only Planner
Uses current observation only. No memory or future hypotheses. Clearly label as restricted control.

### System O — Oracle Planner
Evaluator-only upper bound using full ground truth. Not a fair cognitive competitor.

## 15. Benchmark dimensions

Vary:
- grid size;
- obstacle density;
- path length;
- turns;
- dynamic changes;
- target movement;
- memory age;
- memory truth/falsity;
- observation confidence;
- partial visibility;
- hypothesis truth/falsity;
- distractors;
- route count;
- dead ends;
- replanning frequency.

Report by difficulty band, not only aggregate.

## 16. Required metrics

At minimum:

- `planning_success_rate`
- `goal_reached_rate`
- `valid_plan_rate`
- `invalid_action_rate`
- `collision_count`
- `collision_rate`
- `path_efficiency`
- `optimality_gap_vs_oracle`
- `mean_replans`
- `replan_success_rate`
- `dynamic_change_recovery_rate`
- `stale_memory_planning_error_count`
- `stale_memory_planning_error_rate`
- `false_memory_planning_error_count`
- `false_memory_planning_error_rate`
- `prediction_as_fact_planning_error_count`
- `prediction_as_fact_planning_error_rate`
- `unsupported_assumption_count`
- `conditional_plan_rate`
- `assumption_validation_success_rate`
- `hypothesis_confirmation_violations`
- `observation_after_action_rate`
- `mean_planning_time_ms`

Also report by difficulty and family.

## 17. No artificial NowMind win

A tie is acceptable. A baseline win is acceptable.

Do not weaken controls after seeing results.

If all competent systems hit a ceiling, preserve results and recommend a harder versioned benchmark.

## 18. Required artifacts

Generate under `artifacts/g2_1/`:

- `g2_1_metrics.json`
- `g2_1_metrics_by_difficulty.json`
- `g2_1_metrics_by_family.json`
- `g2_1_trial_results.jsonl`
- `g2_1_failure_samples.json`
- `g2_1_invariant_results.json`
- `g2_1_seed_and_config.json`
- `g2_1_baseline_rules.md`
- `g2_1_benchmark_summary.md`
- `g2_1_planning_examples.json`
- `g2_1_oracle_gap.json`

## 19. Acceptance tests

Implement all tests in `docs/G2_1_ACCEPTANCE_TESTS.md`.

All G1 and G2 tests must remain green.

## 20. Documentation

Create/update:

- `docs/G2_1_ARCHITECTURE.md`
- `docs/G2_1_SPATIAL_MODEL.md`
- `docs/G2_1_TRANSFORMATIONS.md`
- `docs/G2_1_PLANNING_POLICY.md`
- `docs/G2_1_BENCHMARK_METHOD.md`
- `docs/G2_1_LIMITATIONS.md`
- `docs/DECISIONS_LOG.md`
- `README.md`
- `STATUS.md`

## 21. Commands

At completion run:

```text
python -m pytest
python -m nowmind.evaluation.run_g1_suite
python -m nowmind.evaluation.run_g2_benchmark
python -m nowmind.evaluation.run_g2_1_benchmark
python -m nowmind.demo.web
```

Verify the browser demo manually.

## 22. Do not implement yet

Do not add:
- L3 ethical Veto Gate;
- identity;
- dreaming;
- LLM integration;
- OpenAI API;
- other external model APIs;
- camera/microphone;
- autonomous OS/web tools;
- self-modification;
- quantum mechanism.

Do not package or contact Julian yet.

## 23. Completion report

Return:

1. G1 regression result;
2. G2 regression result;
3. G2.1 architecture summary;
4. total tests and results;
5. benchmark seed and trial count;
6. complete metrics for N/C/R/O;
7. results by difficulty;
8. results by scenario family;
9. representative NowMind failures;
10. cases where Chronological Planner matched or beat NowMind;
11. collision/invalid action summary;
12. stale/false-memory planning error summary;
13. hypothesis-as-fact violation summary;
14. dynamic replanning result;
15. browser demo URL;
16. artifact paths;
17. confirmation G1/G2 semantics remained unchanged;
18. deviations;
19. recommendation for G2.2 Hard Geometric Benchmark.

Do not claim architectural superiority unless the benchmark genuinely supports it.

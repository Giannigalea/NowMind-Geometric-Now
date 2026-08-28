# SIXTH CODEX TASK — NowMind G2.2 Epistemic Geometry

## Mission

Implement **NowMind G2.2 — Epistemic Geometry**.

G2.1 demonstrated explicit 2D geometry, hypothetical transformations, A* planning, closed-loop re-observation/replanning, zero collision/invalid-action errors, and clean source separation. But the benchmark revealed a ceiling: NowMind, Chronological, and Reactive planners had nearly identical success, and the Chronological planner slightly beat NowMind on efficiency.

Therefore G2.2 must **not simply increase map size or obstacle density**.

The purpose of G2.2 is to create planning problems where:
1. the current observation is deliberately incomplete;
2. memory is genuinely useful but potentially stale or false;
3. future hypotheses are useful but explicitly uncertain;
4. information-gathering actions have value;
5. the system must choose whether to act, inspect, verify, or replan.

This is an epistemic planning benchmark, not merely pathfinding.

## 1. Preserve earlier architecture

All G1, G2, and G2.1 tests must remain green.

Do not change:
- fresh-Now semantics;
- MemoryTrace semantics;
- reconstruction provenance;
- future-hypothesis provenance;
- hypothetical-geometry semantics;
- ActionExecutor-only world mutation;
- closed-loop re-observation.

G2.2 is additive.

## 2. Read authoritative specs

Read all prior authoritative docs plus:
- `docs/G2_2_EPISTEMIC_GEOMETRY_SPEC.md`
- `docs/G2_2_BENCHMARK_SPEC.md`
- `docs/G2_2_ACCEPTANCE_TESTS.md`

## 3. Core research question

> Can NowMind plan safely and efficiently when the present is only partially observed, while using reconstructed memory and hypotheses as typed, fallible information rather than treating them as present fact?

Canonical choice problem:

```text
Current observation:
corridor state UNKNOWN

Reconstructed memory:
corridor was OPEN

Alternative:
longer route is currently observed clear

Possible choices:
A. trust memory and take shortcut
B. take longer known-safe route
C. move to a vantage point and inspect corridor
```

The architecture should be capable of choosing C when verification has expected value.

## 4. Add local/partial perception

Implement a bounded local sensor model:
- Manhattan or Euclidean visibility radius;
- line-of-sight blocked by walls;
- optional orientation/FOV if useful;
- cells outside current perception = UNKNOWN.

The runtime must not receive the complete world map. Only evaluator/Oracle may see full ground truth.

## 5. Add active information-gathering actions

Implement at least one explicit information action, for example:
- `SCAN`
- or an equivalent inspect/look action.

Preferred minimal model:
- movement always produces local observation;
- `SCAN` increases observation range at an explicit cost;
- planner may move to a vantage point to resolve unknown geometry.

Information actions change knowledge, not physical truth.

## 6. Add epistemic planning state

Represent:
- known-free cells;
- known-blocked cells;
- unknown cells;
- memory-supported assumptions;
- future hypotheses;
- confidence;
- provenance.

Memory-supported unknown cells must not become observed free cells.

## 7. Add transparent verification policy

Implement a deterministic policy comparing:
- known-safe route cost;
- conditional shortcut cost;
- verification cost;
- uncertainty/risk penalty.

A simple documented formula is preferred.

The planner should sometimes rationally choose:
- safe route;
- conditional shortcut;
- verify-first route.

## 8. Make memory necessary in some scenarios

Create cases where:
- target is outside current visibility;
- current observation alone cannot locate it;
- recent memory provides useful information;
- later observation confirms or falsifies that memory.

Reactive current-only should now be genuinely disadvantaged in some families because the task requires information it does not possess.

Do not sabotage it.

## 9. Long-history stress

Add cohorts:
- 0
- 10
- 50
- 100
- 500
- optionally 1,000+ records

Include stale states, irrelevant distractors, repeated moves, repeated hypotheses, false memories, and corrections.

Measure:
- planning accuracy;
- temporal contamination;
- evidence items inspected;
- retrieval size;
- planning time;
- scaling with history length.

Chronological control may use legitimate indexing/caching. Do not force naive linear scans.

## 10. Sensor uncertainty

Add configurable observation confidence/noise:
- obstacle confidence;
- target-detection confidence;
- occasional false positives/negatives under evaluator control.

Source type and confidence remain separate.

Weak current evidence may trigger verification; high-confidence memory must not become observation.

## 11. Contradictory evidence

Support cases such as:

```text
sensor A says blocked 0.58
sensor B says free 0.61
memory says free 0.92
```

Expected:
structured uncertainty and possibly verification, not silent certainty.

## 12. Dynamic hidden world

Allow external changes outside current visibility:
- obstacle moves unseen;
- door closes unseen;
- target moves unseen.

The system must not know until observation reveals it.

No evaluator truth leakage.

## 13. Benchmark systems

### N — NowMind Epistemic Geometry
Uses partial observation, reconstructed memory, future hypotheses, typed assumptions, verification/information actions, and closed-loop replanning.

### C — Chronological Epistemic Planner
Strong fair control with same admissible observations/history/hypotheses/confidences, chronological representation, equivalent planning/search capability, and legitimate indexing/caching.

### R — Reactive Current-Only Planner
Uses only current partial observation. No memory or hypotheses.

### O — Oracle
Full ground-truth upper bound only.

## 14. Required benchmark families

At minimum:
E1 hidden target, recent accurate memory
E2 hidden target, stale memory
E3 hidden obstacle, accurate memory
E4 hidden obstacle, stale/false memory
E5 known-safe long route vs remembered shortcut
E6 verify-first is optimal
E7 verification is wasteful; safe route better
E8 memory shortcut is worth taking
E9 unseen door remembered open
E10 unseen door remembered closed
E11 dynamic hidden obstacle changes
E12 dynamic hidden target moves
E13 no useful memory -> explore/unknown
E14 contradictory current sensors
E15 high-confidence memory vs weak current evidence
E16 long history with many stale states
E17 long history with temporal distractors
E18 prediction supports intercept route and later confirms
E19 prediction supports route and later falsifies
E20 multiple remembered candidate locations
E21 information-gathering action required to avoid trap
E22 partial observability + multiple replans
E23 false-positive obstacle observation
E24 false-negative obstacle observation

## 15. Difficulty axes

Vary:
- visibility radius;
- observation noise;
- history length;
- memory age;
- memory fidelity;
- map size;
- obstacle density;
- dynamic-change rate;
- target mobility;
- unknown-cell count;
- competing memories;
- hypotheses;
- scan cost.

Use D1-D6 or equivalent monotonic bands.

## 16. Metrics

Task:
- goal_reached_rate
- planning_success_rate
- collision_rate
- invalid_action_rate
- path_efficiency
- optimality_gap_vs_oracle

Information:
- verification_action_rate
- useful_verification_rate
- wasted_verification_rate
- verification_prevented_failure_count
- unknown_correctly_preserved_rate
- unsupported_certainty_rate

Memory/source:
- memory_use_rate
- memory_helped_success_count
- memory_harmed_success_count
- stale_memory_planning_error_rate
- false_memory_planning_error_rate
- memory_as_observation_violation_count
- prediction_as_fact_violation_count

Partial observation:
- hidden_change_recovery_rate
- target_reacquisition_rate
- exploration_success_rate

Scaling:
- mean_history_records_available
- mean_evidence_items_inspected
- mean_memory_traces_retrieved
- mean_planning_time_ms
- p95_planning_time_ms
- peak_runtime_memory_mb if practical/reliable

Report by difficulty, family, and history cohort.

## 17. Statistical reporting

For major proportions, report counts/rates and 95% confidence intervals if straightforward.

Use paired trial IDs for N/C/R/O.

Do not claim significance without an appropriate calculation.

## 18. Artifacts

Generate under `artifacts/g2_2/`:
- `g2_2_metrics.json`
- `g2_2_metrics_by_family.json`
- `g2_2_metrics_by_difficulty.json`
- `g2_2_history_scaling.json`
- `g2_2_trial_results.jsonl`
- `g2_2_failure_samples.json`
- `g2_2_invariant_results.json`
- `g2_2_seed_and_config.json`
- `g2_2_baseline_rules.md`
- `g2_2_benchmark_summary.md`
- `g2_2_pairwise_comparison.json`

## 19. Visual demo

Extend the browser demo with an **Epistemic Geometry** scenario.

Visually distinguish:
- visible cells;
- fog-of-war/unknown cells;
- remembered geometry ghost overlay;
- future-hypothesis overlay;
- candidate path;
- information-gathering/vantage path.

Hero scenario:
1. shortcut hidden by fog-of-war;
2. memory says shortcut was clear;
3. long route is observed clear;
4. NowMind chooses inspection/vantage;
5. shortcut is revealed blocked;
6. memory is visibly contradicted;
7. NowMind replans safely;
8. no collision;
9. new Now ID appears.

Also provide a memory-correct version where verification allows the shortcut.

## 20. Acceptance tests

Implement every test in `docs/G2_2_ACCEPTANCE_TESTS.md`.

All previous tests remain green.

## 21. Do not implement yet

Do not add:
- LLM integration;
- embeddings;
- identity;
- dreaming;
- L3 ethical Veto Gate;
- camera/microphone;
- external APIs;
- autonomous OS tools;
- self-modification;
- quantum mechanism.

## 22. Completion report

Return:
1. G1/G2/G2.1 regression status;
2. G2.2 architecture summary;
3. total tests;
4. benchmark seed/trial count;
5. aggregate N/C/R/O metrics;
6. metrics by difficulty;
7. metrics by family;
8. history-length scaling;
9. cases where memory helped NowMind;
10. cases where memory harmed NowMind;
11. cases where Chronological matched/beat NowMind;
12. cases where Reactive beat NowMind;
13. verification-action analysis;
14. hidden-change recovery analysis;
15. representative NowMind failures;
16. source/invariant violations;
17. browser URL;
18. artifact paths;
19. deviations;
20. recommendation whether next step should be further symbolic work or G2.3 model/LLM integration.

Do not recommend further symbolic work merely to force a NowMind advantage.

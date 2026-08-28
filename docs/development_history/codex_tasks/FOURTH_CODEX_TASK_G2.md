# FOURTH CODEX TASK — NowMind G2 Temporal Geometry

## Mission

Implement **NowMind G2 — Temporal Geometry** on top of the frozen G1 foundation.

G1 established a strict fresh-Now boundary:

```text
WorldState_t
-> Observation_t
-> PresentGeometry_t
-> NowState_t
-> Reasoner
```

with no direct cognitive path from `NowState_(t-1)` to `NowState_t`.

G2 introduces the first deliberately difficult PCT-inspired problem:

> How can information about the past and possible future appear in the current Now without being confused with present observation?

G2 must implement:
- memory traces;
- current memory reconstruction;
- explicit temporal provenance;
- simple future hypotheses represented now;
- temporal reasoning;
- adversarial synthetic experiments;
- comparison baselines;
- a visual Temporal Geometry demonstrator.

Do **not** implement full trajectory planning, L3 Veto Gate, identity, dreaming, camera/microphone, or LLM integration yet. Those belong to later stages.

## 1. Read before coding

Read fully:

1. `AGENTS.md`
2. `docs/PCT_COMPUTATIONAL_RULES.md`
3. `docs/GEOMETRIC_NOW_G1_SPEC.md`
4. `docs/G1_ARCHITECTURE_AUDIT.md`
5. `docs/G1_TECHNICAL_OVERVIEW.md`
6. `docs/G2_TEMPORAL_GEOMETRY_SPEC.md`
7. `docs/G2_BENCHMARK_SPEC.md`
8. `docs/G2_ACCEPTANCE_TESTS.md`
9. current G1 source and tests
10. `reference/PCT_Book_Latest.pdf` only as broader philosophical context if practical; do not repeatedly attempt heavy PDF extraction if the environment cannot handle it.

The G2 specification files in this pack are authoritative for G2 software behavior unless Jonathan explicitly changes them.

## 2. Preserve G1

G1 is now a frozen foundation.

Requirements:
- all existing G1 tests must continue to pass;
- do not weaken the history firewall;
- do not add previous-Now references to G1 `NowState`;
- do not turn `ExperimentRecorder` into cognition;
- do not make the G1 reasoner read memory;
- avoid rewriting G1 core merely for convenience.

Prefer additive G2 modules.

If a genuine G1 bug is discovered:
1. document it;
2. make the smallest correction;
3. add a regression test;
4. update the Decisions Log.

## 3. Implement the G2 temporal pipeline

Target architecture:

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
                               | current evidence
                               |
           +-------------------+-------------------+
           |                                       |
           |                                       |
           v                                       v
      Memory cue                            Future hypotheses
           |                              generated/received NOW
           v                                       |
       MemoryStore                                 |
     (traces only)                                 |
           |                                       |
           v                                       |
  MemoryReconstructor                              |
           |                                       |
           v                                       v
 RECONSTRUCTED_MEMORY                    HYPOTHETICAL_FUTURE
           \                                       /
            \                                     /
             +---------------+-------------------+
                             v
                     TemporalNowState_t
                             |
                             v
                     TemporalReasoner
                             |
                             v
                           Answer
```

External evaluator/experiment logs remain outside cognition.

There must still be no direct cognitive path:

```text
Previous NowState ----------------X----------------> TemporalNowState_t
```

Memory can carry information forward only through:

```text
observed/inferred fact
-> MemoryTrace
-> retrieval
-> MemoryReconstruction created NOW
```

## 4. Implement the data model and runtime described in the spec

Follow `docs/G2_TEMPORAL_GEOMETRY_SPEC.md`.

At minimum implement:
- `TemporalSource`
- immutable `MemoryTrace`
- `MemoryStore`
- deterministic cue-based retrieval
- `MemoryReconstruction`
- reconstruction confidence / fidelity metadata
- `FutureHypothesis`
- immutable `TemporalNowState`
- `TemporalQuery`
- `TemporalAnswer`
- evidence references/explanations
- source-safe answer policies
- experiment-only false-memory/noise injection

The current Now must be able to contain simultaneously:

```text
OBSERVED_NOW:
ball INSIDE box_b

RECONSTRUCTED_MEMORY:
ball INSIDE box_a

HYPOTHETICAL_FUTURE:
ball INSIDE box_c
```

without collapsing those into one truth category.

## 5. Required core epistemic behavior

### Current-state question

If current observation says `ball INSIDE box_b` and reconstructed memory says `ball INSIDE box_a`, a current-state query must answer from `OBSERVED_NOW` / `INFERRED_NOW`, not from memory.

Memory may be shown as context but must not be promoted to present fact.

### Missing current observation

If no valid current evidence exists, return:

```text
Current state: UNKNOWN
Last reconstructed memory: ...
```

Do not silently use memory as present reality.

### Past-state question

Use reconstructed memory when appropriate and label it explicitly. Do not present reconstruction as exact historical replay.

### Future question

Use only `HYPOTHETICAL_FUTURE`.

Never answer a future hypothesis as current fact.

### High-confidence memory vs lower-confidence current perception

Source type matters.

A 0.95 reconstructed memory must not become a present observation just because a current observation is 0.55.

For a current-state query, report the current observation with uncertainty, or `UNKNOWN` if it falls below the configured validity threshold. Document the policy.

## 6. Memory lifecycle

By default, eligible memory encoding should derive from:
- `OBSERVED_NOW`;
- optionally selected `INFERRED_NOW` if explicitly configured and provenance retained.

Do not encode:
- `HYPOTHETICAL_FUTURE`;
- raw previous `NowState`;
- raw `TemporalNowState`;
- `ExperimentRecorder` snapshots as memories.

A `MemoryTrace` may contain a compact proposition/event representation:
- entity IDs;
- relation;
- source cycle;
- encoded confidence;
- source provenance;
- trace strength;
- metadata.

Encoding should normally occur after the current cycle has been evaluated so a later cycle can retrieve it.

## 7. Reconstruction, not replay

Retrieval returns traces. The system then creates a **new current reconstruction**.

Every `MemoryReconstruction` must include:
- reconstruction ID;
- current cycle association;
- proposition/content;
- source trace IDs;
- historical source cycles;
- reconstruction confidence;
- fidelity/distortion metadata;
- provenance = `RECONSTRUCTED_MEMORY`.

Support deterministic experiment-controlled distortions:
- omission;
- relation substitution;
- object substitution;
- confidence degradation.

Keep normal runtime behavior conservative.

False-memory injection belongs under evaluation/testing infrastructure.

Use seeded randomness where stochastic behavior exists.

## 8. Simple future hypotheses in G2

G2 represents future possibilities but does **not yet** perform full geometric trajectory search.

Implement immutable `FutureHypothesis` records with:
- hypothesis ID;
- created-for cycle;
- proposition/relations;
- confidence;
- generator/source metadata;
- provenance = `HYPOTHETICAL_FUTURE`.

Critical invariant:

> A hypothesis is present content about a possible future, not a future observation.

Never encode a hypothesis as an observed memory trace unless a later real observation confirms the event.

G2.1 will implement richer possibility geometry and transformations.

## 9. Build the adversarial benchmark from day one

Implement `docs/G2_BENCHMARK_SPEC.md`.

Required command:

```text
python -m nowmind.evaluation.run_g2_benchmark
```

Default benchmark:
- deterministic seed;
- at least 1,000 generated trials;
- multiple scenario families;
- reproducible output;
- non-zero exit on invariant failure.

Do not tune scenarios after seeing results merely to improve NowMind's score.

If NowMind performs poorly, preserve the failures and report them.

## 10. Comparison baselines

Implement both:

### Baseline A — NaivePersistentState

A simple persistent-belief/state approach where previously accepted facts remain active until explicitly overwritten.

Purpose:
stress reference for stale-state contamination.

Label clearly that it is deliberately simple, not state-of-the-art.

### Baseline B — ChronologicalRecordReasoner

A stronger symbolic control.

It receives the same underlying temporal records allowed by the benchmark and reasons from a chronological record representation rather than separated Temporal Geometry channels.

Document its decision rules fully.

Do not intentionally cripple it.

If it matches or beats NowMind, report that.

The eventual LLM comparison belongs to G2.3.

## 11. Required benchmark families

At minimum generate trials for:

1. stale memory after world update;
2. deliberately false memory;
3. high-confidence false/stale memory vs lower-confidence current observation;
4. current observation missing;
5. future hypothesis contradicting current observation;
6. multiple future hypotheses;
7. multiple historical memories;
8. distractor entities/relations;
9. contradictory current observations;
10. nested containment over time;
11. left/right spatial changes over time;
12. memory confidence degradation with age;
13. hypothesis accidentally matching a past state;
14. object moved multiple times across several cycles;
15. inferred current relation vs reconstructed historical relation;
16. current fact removed from visibility;
17. prediction later confirmed by a real event;
18. prediction later falsified.

Use ground truth external to cognition.

## 12. Required metrics

Calculate separately for NowMind and each baseline:

- `current_state_accuracy`
- `past_state_accuracy`
- `future_query_accuracy`
- `temporal_source_classification_accuracy`
- `stale_memory_as_current_count`
- `stale_memory_as_current_rate`
- `false_memory_contamination_count`
- `false_memory_contamination_rate`
- `prediction_as_fact_count`
- `prediction_as_fact_rate`
- `unsupported_current_claim_count`
- `unsupported_current_claim_rate`
- `correct_unknown_rate`
- `contradiction_detection_rate`
- `overall_query_accuracy`

Also output a temporal source confusion matrix.

Do not hide cases where a baseline performs as well as or better than NowMind.

## 13. Benchmark artifacts

Generate:

```text
artifacts/g2/
```

At minimum:
- `g2_metrics.json`
- `g2_benchmark_summary.md`
- `g2_trial_results.jsonl`
- `g2_source_confusion_matrix.json`
- `g2_failure_samples.json`
- `g2_invariant_results.json`
- `g2_seed_and_config.json`
- `g2_baseline_rules.md`

## 14. Build the Temporal Geometry browser demo

Extend the current polished G1 visual interface rather than replacing it with a developer dashboard.

Preserve the current visual design language where possible.

The main G2 scene should include:
- a ball/object;
- Box A;
- Box B;
- Box C;
- optionally a hidden/occluded state.

Cycle 1:
ball in Box A.

Cycle 2:
world moves ball to Box B.

Current Temporal Geometry should visibly show three separate lanes:

### PRESENT — green
`ball -> Box B`
`OBSERVED_NOW`

### RECONSTRUCTED PAST — amber
`ball -> Box A`
`RECONSTRUCTED_MEMORY`

### POSSIBLE FUTURE — purple/blue
`ball -> Box C`
`HYPOTHETICAL_FUTURE`

The viewer must not be able to mistake these three channels for equivalent facts.

## 15. Required visual demos

### G2-A — Memory vs present
Ball was in A, now in B.

Current query -> B.
Past query -> A as reconstructed memory.

### G2-B — Inject false memory
Current: B.
Injected reconstructed memory: D.

Current answer remains B.

Show:
`CONFLICTING MEMORY DID NOT REPLACE PRESENT`

### G2-C — Future hypothesis
Current: B.
Hypothesis: C.

Current query -> B.
Future query -> C as hypothetical.

### G2-D — Confidence conflict
Current observation B at moderate confidence.
Memory A at high confidence.

Show source-type preservation rather than highest-number selection.

### G2-E — No current visibility
No current observation.
Memory reconstructs A.

Current query -> UNKNOWN.
Display last reconstructed memory separately.

### G2-F — Contradictory current perception
Conflicting present observations -> structured contradiction/uncertainty.

## 16. Visual "what the reasoner sees now"

Show a `CURRENT TEMPORAL NOW` panel containing:
- present evidence;
- reconstructed memories;
- future hypotheses;
- their source types;
- confidence;
- current query.

Show separately under `NOT DIRECTLY AVAILABLE`:
- raw previous NowStates;
- researcher event log;
- ExperimentRecorder history.

## 17. Benchmark dashboard

Add a local browser view/tab showing:
- benchmark seed;
- trial count;
- current-state accuracy;
- stale-memory contamination;
- false-memory contamination;
- prediction-as-fact rate;
- source confusion matrix;
- comparison with both baselines.

Use local HTML/CSS/SVG only.

Visible disclaimer:

> These synthetic symbolic benchmarks evaluate architecture and temporal-source handling. They are not evidence of consciousness and are not yet a comparison against state-of-the-art LLM agents.

## 18. Tests

Implement every acceptance test in `docs/G2_ACCEPTANCE_TESTS.md`.

All G1 tests must remain green.

## 19. Documentation

Create/update:
- `docs/G2_ARCHITECTURE.md`
- `docs/G2_MEMORY_MODEL.md`
- `docs/G2_TEMPORAL_REASONING_POLICY.md`
- `docs/G2_BENCHMARK_METHOD.md`
- `docs/G2_LIMITATIONS.md`
- `docs/DECISIONS_LOG.md`
- `README.md`
- `STATUS.md`

## 20. Commands

At completion run:

```text
python -m pytest
python -m nowmind.demo.cli
python -m nowmind.evaluation.run_g1_suite
python -m nowmind.evaluation.run_g2_benchmark
python -m nowmind.demo.web
```

## 21. Do not implement yet

Do not add:
- full trajectory/path planning;
- geometric action transformations;
- L3 Veto Gate;
- identity;
- dreaming;
- LLM integration;
- OpenAI API;
- external model APIs;
- camera/microphone;
- autonomous tools;
- self-modification;
- quantum mechanism.

## 22. Completion report

Return:

1. G1 regression result;
2. G2 architecture summary;
3. files created/changed;
4. total tests and results;
5. benchmark seed and trial count;
6. full metric table for NowMind and both baselines;
7. temporal-source confusion matrix summary;
8. failure cases where NowMind performed incorrectly;
9. cases where either baseline matched or beat NowMind;
10. confirmation memory stores traces rather than old NowStates;
11. confirmation future hypotheses cannot become observations automatically;
12. browser demo URL;
13. benchmark artifact paths;
14. whether G1 cognitive semantics changed;
15. deviations;
16. recommendation for G2.1 Possibility Geometry.

Do not report "NowMind is superior" unless the benchmark actually demonstrates a meaningful advantage under the documented conditions.

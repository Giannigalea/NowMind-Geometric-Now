# G2 Benchmark Specification

## 1. Purpose

The G2 benchmark tests whether the Temporal Geometry architecture preserves source distinctions under adversarial temporal conflicts.

It is not a consciousness test.

It is not yet a state-of-the-art LLM comparison.

It must be reproducible and designed before examining final results.

## 2. Systems compared

### System N — NowMind Temporal Geometry

Uses explicit channels:
- `OBSERVED_NOW`
- `INFERRED_NOW`
- `RECONSTRUCTED_MEMORY`
- `HYPOTHETICAL_FUTURE`

inside the current `TemporalNowState`.

### System P — NaivePersistentState

A deliberately simple stateful reference.

Previously accepted state remains active until explicitly overwritten.

Purpose:
show what stale carry-forward errors look like.

Do not call this a state-of-the-art baseline.

### System C — ChronologicalRecordReasoner

A stronger symbolic control.

It receives chronological records representing the same underlying information available in each benchmark scenario.

Its decision rules must be documented before final benchmark execution.

Do not intentionally cripple it.

## 3. Ground truth

Ground truth belongs only to the external benchmark evaluator.

It includes:
- actual current world;
- true event sequence;
- whether injected memories are true/false;
- expected temporal source;
- expected query answer.

The cognitive systems may only receive their specified inputs.

## 4. Reproducibility

Default:
- deterministic fixed seed committed in config;
- minimum 1,000 trials;
- preferably 2,000–5,000 if runtime remains fast;
- exact configuration written to artifact.

Allow command-line override of:
- seed;
- trial count;
- difficulty.

Never overwrite default benchmark results silently.

## 5. Scenario families

Each family should contain many randomized variants.

### F1 — Stale memory after update

Historical:
ball in A.

Current:
ball in B.

Memory:
A.

Current query expects B.

### F2 — False memory

Current:
ball in B.

Injected memory:
D.

Current query expects B.

For a memory query, the system may report D as the current reconstruction if that is what was injected. Only the external evaluator knows that the injected trace is false unless current evidence exposes a conflict.

### F3 — Confidence inversion

Current:
B confidence 0.55–0.75.

Memory:
A confidence 0.85–0.99.

Current query must not select A merely because memory confidence is numerically higher.

### F4 — No current visibility

No valid current observation.

Memory:
A.

Current query expects UNKNOWN.

A past/recollection query may return A.

### F5 — Future conflict

Current:
B.

Hypothesis:
C.

Current query expects B.

Future query expects C as hypothetical.

### F6 — Multiple future hypotheses

Current:
B.

Hypotheses:
C 0.6
D 0.4

Future query should preserve multiple possibilities.

### F7 — Multiple old memories

Object moves:
A -> B -> C.

Current:
C.

Memory retrieval may include A and B.

Current query expects C.

Past-query behavior depends on requested cycle/recency.

### F8 — Distractors

Add irrelevant entities and relations.

Measure source confusion and reasoning robustness.

### F9 — Contradictory current evidence

Inject incompatible current observations.

Expected:
CONTRADICTORY/uncertain, not a guessed current fact.

### F10 — Nested containment over time

key in box A;
later box A inside cabinet;
later key moved to box B.

Ask current and past containment questions.

### F11 — Spatial direction changes

A left B;
later A right B;
memory retains left.

Current query expects right.

### F12 — Memory age

Older traces receive lower strength under configured decay.

Test retrieval/reconstruction behavior.

### F13 — Hypothesis matches past

A future hypothesis happens to match an older memory but not current reality.

Ensure source category remains future.

### F14 — Multiple moves

Object moves 3–8 times.

Stress current-state isolation from many historical traces.

### F15 — Inferred present vs remembered historical fact

Current direct observation supports an inference.
Old memory directly contradicts the inferred current relation.

Measure source-safe reasoning.

### F16 — Occlusion

Object currently unobserved.

Do not turn the latest memory into current fact.

### F17 — Prediction later confirmed

At t:
hypothesis says C.

At t+1:
world really moves object to C and observation confirms it.

The new observed fact is `OBSERVED_NOW`.
The old hypothesis remains a historical hypothesis.

### F18 — Prediction later falsified

Hypothesis says C.
Actual next observation is D.

Ensure the prediction does not persist as fact.

## 6. Difficulty dimensions

Randomize:
- entity count;
- distractor count;
- sequence length;
- memory age;
- memory confidence;
- observation confidence;
- number of memories;
- number of hypotheses;
- relation type;
- containment depth;
- contradiction presence;
- current visibility.

Write distribution settings to the config artifact.

## 7. Metrics

For each system calculate:

### Accuracy
- `current_state_accuracy`
- `past_state_accuracy`
- `future_query_accuracy`
- `overall_query_accuracy`

### Source integrity
- `temporal_source_classification_accuracy`
- `stale_memory_as_current_count`
- `stale_memory_as_current_rate`
- `false_memory_contamination_count`
- `false_memory_contamination_rate`
- `prediction_as_fact_count`
- `prediction_as_fact_rate`

### Epistemic behavior
- `unsupported_current_claim_count`
- `unsupported_current_claim_rate`
- `correct_unknown_rate`
- `contradiction_detection_rate`

### Confusion matrix
True required evidence source vs source actually used/reported.

## 8. Failure artifacts

Preserve representative failures.

For each failure store:
- seed/trial ID;
- generated world/event sequence;
- current observation;
- memory reconstructions;
- future hypotheses;
- expected answer;
- actual answer;
- evidence source used;
- reason/explanation.

Do not only save NowMind failures.
Save baseline failures too.

## 9. Fairness rules

Do not:
- tune trial generation after seeing a disappointing NowMind result;
- remove scenario families where NowMind performs badly;
- choose weaker baseline rules solely to create an advantage;
- hide ties;
- report deterministic synthetic scores as general AI superiority.

If a design change is made after benchmark review:
- version the benchmark;
- preserve previous results;
- explain why the design changed.

## 10. Interpretation

A potentially valid conclusion:

> Under the documented synthetic temporal-source benchmark, the Temporal Geometry architecture reduced specific source-confusion errors relative to one or more symbolic controls.

An invalid conclusion without much stronger evidence:

> NowMind reasons better than modern AI.

The model-level comparison comes later.

# G2 Temporal Geometry — Architecture Specification

## 1. Research objective

G1 established that a fresh current relational state can be constructed without directly carrying forward an earlier cognitive Now.

G2 asks:

> Can information about past and possible future states be made cognitively available in the current Now while remaining explicitly distinguishable from what is observed now?

The computational challenge is not simply memory storage. It is **source separation**.

A current cognitive state may contain:
- what is observed now;
- what is inferred now;
- what is reconstructed now about the past;
- what is hypothesized now about the future.

These are all current computational contents but have different epistemic roles.

## 2. Core temporal-source vocabulary

Implement:

```python
class TemporalSource(Enum):
    OBSERVED_NOW = "observed_now"
    INFERRED_NOW = "inferred_now"
    RECONSTRUCTED_MEMORY = "reconstructed_memory"
    HYPOTHETICAL_FUTURE = "hypothetical_future"
```

Reserve for later:
- `IDENTITY_CONSTRAINT`
- `EXTERNAL_FEEDBACK`

Do not reuse one value to mean another.

## 3. G2 cognitive state

Introduce a fresh immutable `TemporalNowState`.

Conceptual form:

```python
@dataclass(frozen=True)
class TemporalNowState:
    now_id: UUID
    cycle_id: int
    created_at: datetime
    present_geometry: PresentGeometry
    reconstructed_memories: tuple[MemoryReconstruction, ...]
    future_hypotheses: tuple[FutureHypothesis, ...]
```

Possible additional current-only fields:
- query context;
- attention/current cue;
- validation summary.

Forbidden:
- `previous_now`
- `previous_temporal_now`
- raw ExperimentRecorder history
- mutable references to historical cognitive states

Every cycle constructs a fresh `TemporalNowState`.

## 4. Memory trace

A `MemoryTrace` is stored information, not a stored conscious/cognitive Now.

Conceptual form:

```python
@dataclass(frozen=True)
class MemoryTrace:
    trace_id: UUID
    source_cycle_id: int
    encoded_at_cycle_id: int
    proposition: Proposition
    original_source: TemporalSource
    encoded_confidence: float
    trace_strength: float
    metadata: Mapping[str, object]
```

Rules:
- no `NowState` object field;
- no `TemporalNowState` object field;
- no full historical PresentGeometry snapshot by default;
- retain provenance;
- immutable where practical.

A proposition may identify:
- entity;
- relation;
- target;
- relevant attributes.

## 5. Memory store

Implement an explicit `MemoryStore`.

Properties:
- persists across cognitive cycles;
- stores `MemoryTrace` only;
- queryable only through an explicit retrieval interface;
- cannot read ExperimentRecorder;
- is not itself the current cognitive state.

G2 may use an in-memory store.

Persistent disk/database storage is not required.

No embeddings or vector database are required.

## 6. Memory encoding

Default eligible sources:
- selected `OBSERVED_NOW`;
- optionally `INFERRED_NOW` if explicitly enabled and provenance retained.

Not eligible:
- `RECONSTRUCTED_MEMORY` re-encoded as newly observed;
- `HYPOTHETICAL_FUTURE`;
- previous Now objects;
- evaluator ground truth.

Avoid recursive memory amplification.

## 7. Retrieval

Use deterministic current cues.

Possible cue fields:
- subject/entity ID;
- target/entity ID;
- relation type;
- query temporal intent;
- current attention.

Return candidate traces with explicit scores.

No hidden global-history retrieval.

Retrieval is a tool invoked in the current cycle.

## 8. Reconstruction

Retrieved traces must become new current objects.

Conceptual form:

```python
@dataclass(frozen=True)
class MemoryReconstruction:
    reconstruction_id: UUID
    created_at_cycle_id: int
    proposition: Proposition
    source_trace_ids: tuple[UUID, ...]
    historical_source_cycles: tuple[int, ...]
    confidence: float
    fidelity: float
    distortion_tags: tuple[str, ...]
    provenance: TemporalSource = TemporalSource.RECONSTRUCTED_MEMORY
```

Every reconstruction exists now.

It is not the historical Now.

## 9. Reconstruction confidence

Use a documented experimental confidence policy.

A simple starting model may combine:
- original encoded confidence;
- trace strength;
- age/decay;
- reconstruction fidelity.

Conceptually:

```text
reconstruction_confidence
= encoded_confidence
  * trace_strength
  * fidelity
```

Clamp to [0,1].

Do not present this as a neuroscience model.

## 10. Memory aging

Support configurable deterministic age decay.

Example:

```text
trace_strength(age) =
max(min_strength, initial_strength * decay_factor**age)
```

The exact formula is an engineering choice. Document it and keep benchmark parameters fixed/reproducible.

## 11. False memory and distortion

Core NowMind should not randomly hallucinate memories by default.

Evaluation infrastructure may inject controlled corruption:
- omit relation;
- swap target object;
- swap relation;
- reduce confidence;
- create explicitly false trace.

The injected false trace still reconstructs as `RECONSTRUCTED_MEMORY`, never `OBSERVED_NOW`.

## 12. Future hypothesis

Conceptual form:

```python
@dataclass(frozen=True)
class FutureHypothesis:
    hypothesis_id: UUID
    created_at_cycle_id: int
    proposition: Proposition
    confidence: float
    generator_id: str
    provenance: TemporalSource = TemporalSource.HYPOTHETICAL_FUTURE
```

A hypothesis is current content about a possible future.

It is not:
- current reality;
- memory;
- a guaranteed event.

## 13. Hypothesis confirmation

If a later real observation matches an earlier hypothesis:

The later observed fact is newly created as `OBSERVED_NOW`.

Do not mutate the old hypothesis into an observation.

The evaluator may link them for analysis, but they remain different records.

## 14. Temporal query model

Implement explicit temporal intent.

```python
class TemporalIntent(Enum):
    NOW = "now"
    PAST = "past"
    POSSIBLE_FUTURE = "possible_future"
    SOURCE = "source"
```

A `TemporalQuery` should include:
- query type;
- subject;
- relation/target as appropriate;
- temporal intent;
- optional target past cycle/range.

## 15. Temporal answer

A `TemporalAnswer` should include:
- status;
- answer proposition/value;
- confidence;
- source category;
- evidence references;
- explanation;
- uncertainty notes;
- contradiction information.

It should be possible to render:

```text
Current location: Box B
Source: OBSERVED_NOW
Confidence: 0.81

Context:
Reconstructed memory: Box A (0.94)
Future hypothesis: Box C (0.60)
```

without conflating context with the answer.

## 16. Source-safe current-state policy

For `NOW` queries:

1. valid current `OBSERVED_NOW` / `INFERRED_NOW` evidence answers current-state questions;
2. reconstructed memory can contextualize but cannot be silently promoted to current evidence;
3. future hypotheses cannot answer a current-state query;
4. if no valid current evidence exists, return `UNKNOWN`;
5. contradictory current evidence returns `CONTRADICTORY` or structured uncertainty;
6. current evidence below the configured reliability threshold produces uncertainty/unknown rather than substitution by memory.

The exact threshold must be documented and benchmark-configurable.

## 17. Past-state policy

For `PAST` queries:
- use `RECONSTRUCTED_MEMORY`;
- identify source trace cycles;
- provide confidence/fidelity;
- avoid wording that implies exact replay;
- return `UNKNOWN` if insufficient reconstruction exists.

## 18. Future policy

For `POSSIBLE_FUTURE` queries:
- use `HYPOTHETICAL_FUTURE`;
- return one or more possibilities;
- preserve confidence;
- never phrase a hypothesis as current observation.

Full transformation search belongs to G2.1.

## 19. External evaluator

The benchmark evaluator may retain:
- exact world ground truth;
- event history;
- every generated trace;
- injected corruption;
- expected answers.

This evaluator is not cognition.

Runtime temporal reasoning must not query evaluator ground truth.

Architecture tests must enforce the separation.

## 20. Core invariant summary

G2 must satisfy simultaneously:

```text
Past information can influence the current Now.
```

and:

```text
The old Now itself is not the current cognitive input.
```

and:

```text
A memory reconstruction is not current observation.
```

and:

```text
A future hypothesis is not current observation.
```

This is the central G2 experiment.

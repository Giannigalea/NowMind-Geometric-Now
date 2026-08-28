# G2 Architecture

G2 Temporal Geometry extends the frozen G1 fresh-Now foundation with explicit
temporal-source channels.

Runtime shape:

```text
WorldState_t
-> Observation_t
-> PresentGeometry_t
-> TemporalNowState_t
      |- present_geometry: OBSERVED_NOW / INFERRED_NOW
      |- reconstructed_memories: RECONSTRUCTED_MEMORY
      |- future_hypotheses: HYPOTHETICAL_FUTURE
-> TemporalReasoner
-> TemporalAnswer
```

The G1 `NowState` and G1 `reasoning.answer(now, query)` API were not changed.
G2 uses separate modules under `nowmind.temporal`.

## Runtime Modules

- `nowmind.temporal.source`: temporal provenance enum.
- `nowmind.temporal.proposition`: compact symbolic proposition content.
- `nowmind.temporal.memory`: traces, store, retrieval cues, reconstructions, and deterministic reconstruction confidence.
- `nowmind.temporal.future`: immutable future hypotheses.
- `nowmind.temporal.now_state`: immutable `TemporalNowState`.
- `nowmind.temporal.query`: temporal query/answer records.
- `nowmind.temporal.reasoner`: source-safe temporal reasoning policy.
- `nowmind.temporal.cycle`: temporal cycle runner.

## Firewall

`TemporalNowState` has no previous-Now or previous-TemporalNow field. Memory
enters through:

```text
observed/inferred relation -> MemoryTrace -> retrieval -> MemoryReconstruction
```

The temporal runtime does not import `nowmind.evaluation`. False-memory
injection and benchmarks live under evaluation/testing infrastructure only.

## Browser Demo

The local web demo includes G2-A through G2-F. In G2 mode the main panel shows
three lanes:

- `PRESENT`: current observed/inferred evidence.
- `RECONSTRUCTED PAST`: memory reconstructions.
- `POSSIBLE FUTURE`: hypotheses.

The browser receives serialized temporal runtime output. It does not calculate
temporal answers independently.

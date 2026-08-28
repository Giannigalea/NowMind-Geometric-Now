# G2 Memory Model

G2 implements memory as explicit traces and current reconstructions. It does not
store old `NowState` or `TemporalNowState` objects as cognition.

## Trace

`MemoryTrace` stores:

- trace id;
- historical source cycle;
- encoded-at cycle;
- compact `Proposition`;
- original source, limited to `OBSERVED_NOW` or explicitly configured `INFERRED_NOW`;
- encoded confidence;
- trace strength;
- metadata.

Trace metadata rejects raw `NowState` and `TemporalNowState` objects.

## Store

`MemoryStore` is an in-memory trace store. It accepts `MemoryTrace` only and is
queried through deterministic `RetrievalCue` fields: source id, relation type,
target id, and optional temporal intent.

The store does not import or read `ExperimentRecorder`.

## Reconstruction

`MemoryReconstructor` turns retrieved traces into new `MemoryReconstruction`
objects for the current cycle. Reconstruction confidence is:

```text
encoded_confidence * decayed_trace_strength * fidelity * confidence_multiplier
```

with clamping to `[0, 1]`.

Default decay parameters:

- decay factor: `0.94`;
- minimum strength: `0.20`.

This is an engineering policy for synthetic experiments, not a neuroscience
claim.

## Distortion

Normal runtime does not randomly hallucinate memories. Controlled distortion and
false-memory injection are provided under `nowmind.evaluation.g2_distortion` for
tests and benchmarks.

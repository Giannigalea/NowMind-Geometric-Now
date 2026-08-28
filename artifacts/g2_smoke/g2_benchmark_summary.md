# G2 Benchmark Summary

These synthetic symbolic benchmarks evaluate architecture and temporal-source handling. They are not evidence of consciousness and are not yet a comparison against state-of-the-art LLM agents.

- Seed: 20260823
- Trial count: 36
- Families represented: 18

| System | Overall | Current | Past | Future | Stale-as-current | False-memory | Prediction-as-fact |
|---|---:|---:|---:|---:|---:|---:|---:|
| NowMindTemporalGeometry | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| NaivePersistentState | 0.333 | 0.200 | 1.000 | 1.000 | 18 | 2 | 6 |
| ChronologicalRecordReasoner | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 |

Failures are preserved in `g2_failure_samples.json` for NowMind and both baselines.

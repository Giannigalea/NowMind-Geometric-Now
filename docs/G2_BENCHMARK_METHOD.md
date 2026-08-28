# G2 Benchmark Method

The G2 benchmark is implemented in `nowmind.evaluation.g2_benchmark` and runs
with:

```powershell
python -m nowmind.evaluation.run_g2_benchmark
```

Default configuration:

- seed: `20260823`;
- trial count: `1000`;
- scenario families: `18`;
- output directory: `artifacts/g2/`.

## Systems Compared

- `NowMindTemporalGeometry`: explicit temporal-source channels.
- `NaivePersistentState`: deliberately simple latest-record persistent belief.
- `ChronologicalRecordReasoner`: stronger symbolic chronological-record control.

The chronological control is source-safe and is not intentionally crippled. In
the default benchmark it matches NowMind on aggregate metrics.

## Scenario Families

The generator covers all required families: stale memory, false memory,
confidence inversion, missing current visibility, future conflict, multiple
future hypotheses, multiple old memories, distractors, contradictory current
evidence, nested containment over time, spatial direction changes, memory age,
hypothesis matching the past, multiple moves, inferred-present vs memory,
occlusion, prediction later confirmed, and prediction later falsified.

Ground truth and expected answers are external to cognition.

## Artifacts

The runner writes:

- `g2_metrics.json`;
- `g2_benchmark_summary.md`;
- `g2_trial_results.jsonl`;
- `g2_source_confusion_matrix.json`;
- `g2_failure_samples.json`;
- `g2_invariant_results.json`;
- `g2_seed_and_config.json`;
- `g2_baseline_rules.md`.

Failures are preserved for NowMind and both baselines.

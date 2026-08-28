# G2.1 Benchmark Method

The G2.1 benchmark runs with:

```powershell
python -m nowmind.evaluation.run_g2_1_benchmark
```

Default configuration:

- seed: `20260823`;
- trial count: `3000`;
- difficulty bands: D1-D5;
- scenario families: P1-P16;
- output directory: `artifacts/g2_1/`.

Systems:

- `N_NowMindPossibilityGeometry`: current observed geometry, explicit memory
  assumptions, future hypotheses as possibilities, closed-loop action and
  re-observation.
- `C_ChronologicalGeometricPlanner`: same pathfinding quality and executor, but
  chronological record-style resolution that may use memory-supported unknowns
  earlier.
- `R_ReactiveCurrentOnlyPlanner`: same pathfinding but no memory or future
  hypotheses.
- `O_OraclePlanner`: evaluator-only full ground-truth upper bound.

The evaluator owns ground truth, dynamic events, target truth, memory truth, and
oracle paths. Runtime planners see observations and allowed typed records only.

Artifacts:

- `g2_1_metrics.json`;
- `g2_1_metrics_by_difficulty.json`;
- `g2_1_metrics_by_family.json`;
- `g2_1_trial_results.jsonl`;
- `g2_1_failure_samples.json`;
- `g2_1_invariant_results.json`;
- `g2_1_seed_and_config.json`;
- `g2_1_baseline_rules.md`;
- `g2_1_benchmark_summary.md`;
- `g2_1_planning_examples.json`;
- `g2_1_oracle_gap.json`.


# G2.2 Benchmark Method

The G2.2 benchmark runs with:

```powershell
python -m nowmind.evaluation.run_g2_2_benchmark
```

Default configuration:

- seed: `20260823`;
- trial count: `3000`;
- difficulty bands: D1-D6;
- scenario families: E1-E24;
- history cohorts: H0, H10, H50, H100, H500, H1000;
- output directory: `artifacts/g2_2/`.

Systems:

- `N_NowMindEpistemicGeometry`: partial current observation, typed memory and
  future assumptions, verification actions, and closed-loop re-observation.
- `C_ChronologicalEpistemicPlanner`: same search, sensors, assumptions, and
  verification policy, with legitimate indexed chronological evidence access.
- `R_ReactiveCurrentOnlyPlanner`: same current observation and scan action, but
  no memory reconstructions or future hypotheses.
- `O_OraclePlanner`: evaluator-only ground-truth upper bound.

The benchmark is paired: every N/C/R/O system is evaluated against the same
trial ID, seed, initial world, sensor settings, hidden events, and oracle truth.
Only the oracle sees complete world truth.

Metrics are reported overall, by difficulty, by family, and by history cohort.
Major proportions include counts, rates, and simple 95% confidence intervals.

Artifacts:

- `g2_2_metrics.json`;
- `g2_2_metrics_by_family.json`;
- `g2_2_metrics_by_difficulty.json`;
- `g2_2_history_scaling.json`;
- `g2_2_trial_results.jsonl`;
- `g2_2_failure_samples.json`;
- `g2_2_invariant_results.json`;
- `g2_2_seed_and_config.json`;
- `g2_2_baseline_rules.md`;
- `g2_2_benchmark_summary.md`;
- `g2_2_pairwise_comparison.json`.

The benchmark is synthetic and symbolic. If NowMind and the chronological
control match or the chronological control beats NowMind on a metric, report
that result directly.

# Artifact Manifest

This directory preserves the Full-G benchmark and reviewer artifacts. Raw result
files are intentionally retained; this manifest identifies the recommended
review order and which files are canonical for the current package.

## Recommended Review Order

1. `full_g/full_g_benchmark_table.md`
2. `g1/g1_metrics.json`
3. `g2/g2_benchmark_summary.md`
4. `g2_1/g2_1_benchmark_summary.md`
5. `g2_2/g2_2_benchmark_summary.md`
6. `g2_2_1/g2_2_1_summary.md`
7. `g2_3/g2_3_summary.md`
8. `g2_3_2/g2_3_2_summary.md`
9. `g2_3_2/g2_3_2_statistical_summary.md`
10. `g2_3_4/g2_3_4_summary.md`

## Canonical Full-G Files

| Stage | File | Status | Notes |
|---|---|---|---|
| Full-G | `full_g/full_g_benchmark_table.md` | canonical | Cross-stage reviewer table. |
| G1 | `g1/g1_metrics.json` | canonical | Fresh-now deterministic metrics. |
| G1 | `g1/g1_invariant_results.json` | canonical | Architecture/firewall invariant evidence. |
| G2 | `g2/g2_benchmark_summary.md` | canonical | Temporal source-separation benchmark summary. |
| G2 | `g2/g2_metrics.json` | canonical | NowMind and baseline metrics. |
| G2.1 | `g2_1/g2_1_benchmark_summary.md` | canonical | Possibility/planning benchmark summary. |
| G2.1 | `g2_1/g2_1_metrics.json` | canonical | Planning metrics. |
| G2.2 | `g2_2/g2_2_benchmark_summary.md` | canonical | Epistemic benchmark summary. |
| G2.2 | `g2_2/g2_2_metrics.json` | canonical | Epistemic planning metrics. |
| G2.2.1 | `g2_2_1/g2_2_1_summary.md` | canonical | Recovery/retrieval summary. |
| G2.2.1 | `g2_2_1/g2_2_1_metrics_holdout.json` | canonical | Holdout metrics. |
| G2.3 | `g2_3/g2_3_summary.md` | canonical mock evidence | Deterministic mock model benchmark summary. |
| G2.3 | `g2_3/g2_3_model_manifest.json` | canonical mock evidence | Model/backend manifest. |
| G2.3.1 | `g2_3_1/g2_3_1_summary.md` | historical/local evidence | Initial local-model work and diagnostics. |
| G2.3.2 | `g2_3_2/g2_3_2_summary.md` | canonical local model evidence | Corrected Regime-B rerun with `qwen3:0.6b`. |
| G2.3.2 | `g2_3_2/g2_3_2_statistical_summary.md` | canonical local model evidence | Statistical summary. |
| G2.3.4 | `g2_3_4/g2_3_4_summary.md` | canonical final model-replication status | Free-provider compatible replication status. |

## Raw Data

Large `.jsonl` files are raw benchmark outputs. They are retained so reviewers
can inspect trial-level evidence. Some frozen local-model artifacts contain
historical machine/runtime provenance such as local model paths. Those files are
not edited during public presentation cleanup because they are frozen evidence.

## Seeds

Seed/config files are stored with each benchmark stage where relevant, for
example `g2/g2_seed_and_config.json`, `g2_1/g2_1_seed_and_config.json`,
`g2_2/g2_2_seed_and_config.json`, `g2_2_1/g2_2_1_holdout_seed_and_config.json`,
and `g2_3/g2_3_seed_and_config.json`.

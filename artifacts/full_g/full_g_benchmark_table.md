# Full-G Benchmark Table

These rows are compatible headline metrics only. `N/A` means the stage uses a different metric or no valid comparison exists.

| Stage | Primary system | Comparator | Headline metric | NowMind result | Comparator result | Interpretation | Primary artifact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | NowMind Present Geometry | N/A | stale-state contamination | 0 | N/A | Fresh Now firewall passed | `artifacts/g1/g1_metrics.json` |
| G2 | NowMind Temporal Geometry | ChronologicalRecordReasoner | overall query accuracy | 1.000 | 1.000 | Source separation succeeds but chronology matches | `artifacts/g2/g2_metrics.json` |
| G2 | NowMind Temporal Geometry | NaivePersistentState | overall query accuracy | 1.000 | 0.332 | Naive persistent state fails stale-source discipline | `artifacts/g2/g2_metrics.json` |
| G2.1 | NowMind Possibility Geometry | ReactiveCurrentOnlyPlanner | goal reached rate | 0.867 | 0.867 | Planning works but reactive often matches | `artifacts/g2_1/g2_1_metrics.json` |
| G2.1 | NowMind Possibility Geometry | ChronologicalGeometricPlanner | goal reached rate | 0.867 | 0.867 | Chronological matches in this setup | `artifacts/g2_1/g2_1_metrics.json` |
| G2.2 baseline | NowMind Epistemic Geometry | ChronologicalEpistemicPlanner | goal reached rate | 0.500 | 0.500 | Partial observation exposed recovery and retrieval problems | `artifacts/g2_2/baseline_before_g2_2_1/g2_2_metrics.json` |
| G2.2.1 holdout | NowMind Epistemic Geometry | ReactiveCurrentOnlyPlanner | goal reached rate | 0.9455 | 0.7085 | Recovery improves; reactive remains weaker | `artifacts/g2_2_1/g2_2_1_metrics_holdout.json` |
| G2.2.1 holdout | NowMind Epistemic Geometry | ChronologicalEpistemicPlanner | goal reached rate | 0.9455 | 0.9455 | N and C tie after fair retrieval correction | `artifacts/g2_2_1/g2_2_1_metrics_holdout.json` |
| G2.3 mock | NowMind Structured | Chronological | validated N/C wins | 0/0/1000 | 0/0/1000 | Infrastructure validated; no real-model evidence | `artifacts/g2_3/g2_3_summary.md` |
| G2.3.2 local model | NowMind Structured | Chronological | Regime A validated wins | 0 wins | 8 wins | Local qwen3:0.6b favored chronology in discordant cases | `artifacts/g2_3_2/g2_3_2_summary.md` |
| G2.3.2 local model | NowMind Structured | Chronological | Regime B corrected validated wins | 0 wins / 250 ties | 0 wins / 250 ties | Corrected fixed-budget regime ties | `artifacts/g2_3_2/g2_3_2_summary.md` |
| G2.3.4 OpenRouter | Exact-free provider-compatible candidates | N/A | calibration-valid model | 0 | N/A | No exact-free model passed calibration under frozen constraints | `artifacts/g2_3_4/g2_3_4_summary.md` |

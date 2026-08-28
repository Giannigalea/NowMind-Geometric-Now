# G2.2.1 Baseline Snapshot

This snapshot records the frozen G2.2 benchmark v1 evidence before G2.2.1
runtime changes.

Baseline artifacts were copied to:

```text
artifacts/g2_2/baseline_before_g2_2_1/
```

## Configuration

- seed: `20260823`
- trial count: `3000`
- families: E1-E24
- difficulty bands: D1-D6
- systems: N, C, R, O
- invariant status: `10 passed, 0 failed`

## Aggregate Metrics

| System | Goal | Plan | Collision | Invalid | Efficiency | Oracle gap | Verify | Useful verify | Wasted verify | Memory use | Evidence inspected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| N_NowMindEpistemicGeometry | 0.5000 | 0.9890 | 0.0000 | 0.0000 | 0.9259 | 0.6667 | 0.2349 | 0.4481 | 0.5519 | 0.4473 | 669.2 |
| C_ChronologicalEpistemicPlanner | 0.5000 | 0.9890 | 0.0000 | 0.0000 | 0.9259 | 0.6667 | 0.2349 | 0.4481 | 0.5519 | 0.4473 | 15.2 |
| R_ReactiveCurrentOnlyPlanner | 0.3750 | 0.7917 | 0.0000 | 0.0000 | 0.8981 | 0.8889 | 0.3107 | 0.4062 | 0.5938 | 0.0000 | 625.4 |
| O_OraclePlanner | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.9646 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0 |

## Recovery and Memory

| System | Hidden-change recovery | Target reacquisition | Memory helped | Memory harmed |
|---|---:|---:|---:|---:|
| N_NowMindEpistemicGeometry | 0.0000 | 0.2500 | 500 | 125 |
| C_ChronologicalEpistemicPlanner | 0.0000 | 0.2500 | 500 | 125 |
| R_ReactiveCurrentOnlyPlanner | 0.0000 | 0.4444 | 0 | 0 |
| O_OraclePlanner | 1.0000 | 0.2083 | 0 | 0 |

## Pairwise Summary

- N vs C: N better goal `0`, C better goal `0`, tied goal `3000`.
- N vs O: O better goal `1500`, tied goal `1500`.
- N vs R: N better goal `500`, R better goal `125`, tied goal `2375`.

## Interpretation

G2.2 v1 preserves source invariants but exposes implementation weaknesses:

- NowMind and Chronological match on goal and path metrics.
- NowMind inspects far more historical evidence than Chronological.
- Hidden-change recovery is zero for all non-oracle systems.
- Stale target memory harms NowMind in paired E2 cases where Reactive can win.

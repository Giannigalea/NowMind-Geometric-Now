# G2.3.2 Frozen Baseline

Date: 2026-08-26

The G2.3.1 `qwen3:0.6b` artifacts are frozen evidence and are not overwritten by G2.3.2.

- Model: `qwen3:0.6b`
- Paired trials: `250`
- Frozen Regime A validated result: C `8`, N `0`, ties `242`
- Frozen Regime B is invalid for fairness interpretation
- Fixed-budget violations: `166` of `500` checked N/C pairs
- Snapshot copy: `artifacts/g2_3_2/frozen_g2_3_1_snapshot/`

G2.3.2 reruns only the same frozen 250 Regime-B paired trial IDs after repairing deterministic fixed-budget enforcement.

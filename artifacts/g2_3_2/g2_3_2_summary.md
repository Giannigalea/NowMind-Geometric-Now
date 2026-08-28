# G2.3.2 Summary

- Corrected Regime-B paired trials: `250`
- Fairness failures: `0` of `250` checked N/C pairs
- Invariants: `6` passed, `0` failed
- Frozen Regime-A C-win cases analyzed: `8`

## Corrected Regime B Pairwise

- `qwen3:0.6b|B_FIXED_BUDGET|proposal` N=0 C=0 tied=250
- `qwen3:0.6b|B_FIXED_BUDGET|validated` N=0 C=0 tied=250

## Corrected Regime B Validated Accuracy

- `qwen3:0.6b|B_FIXED_BUDGET|C_CHRONOLOGICAL|validated` accuracy=0.116 source=0.244 parse=1.000
- `qwen3:0.6b|B_FIXED_BUDGET|N_NOWMIND_STRUCTURED|validated` accuracy=0.116 source=0.152 parse=0.992
- `qwen3:0.6b|B_FIXED_BUDGET|R_CURRENT_ONLY|validated` accuracy=0.116 source=0.244 parse=1.000
- `symbolic-nowmind-g2.3-reference|B_FIXED_BUDGET|S_SYMBOLIC_NOWMIND|validated` accuracy=1.000 source=1.000 parse=1.000

## Token Ceiling

- `N_NOWMIND_STRUCTURED` budgeted mean=1320.356 median=1562.0 p95=1589 max=1592
- `C_CHRONOLOGICAL` budgeted mean=1337.048 median=1550.0 p95=1584 max=1589
- `R_CURRENT_ONLY` budgeted mean=344.248 median=310.0 p95=459 max=462

Conclusion: G2.3.2 repairs the fixed-budget enforcement and preserves the original Regime-A evidence. The corrected Regime-B result should be interpreted from these artifacts only.

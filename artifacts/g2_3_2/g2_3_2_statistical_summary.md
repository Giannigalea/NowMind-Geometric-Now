# G2.3.2 Statistical Summary

## Frozen Regime A
- N better: `0`
- C better: `8`
- Ties: `242`
- Discordant pairs: `8`
- Exact paired binomial p-value: `0.007812`
- Paired accuracy difference, N minus C: `-0.032`
- Approximate 95% CI for N minus C: `[-0.054, -0.010]`

## Corrected Regime B
- N better: `0`
- C better: `0`
- Ties: `250`
- Discordant pairs: `0`
- Exact paired binomial p-value: `1.000000`
- Paired accuracy difference, N minus C: `0.000`
- Approximate 95% CI for N minus C: `[0.000, 0.000]`

## Limitations

- One ultra-small `qwen3:0.6b` local model.
- `250` paired trials from one synthetic benchmark.
- Exact tokenizer access was unavailable; Regime B uses one deterministic final-input estimator with a conservative safety multiplier.
- Results should not be generalized to all LLMs or to later NowMind stages.

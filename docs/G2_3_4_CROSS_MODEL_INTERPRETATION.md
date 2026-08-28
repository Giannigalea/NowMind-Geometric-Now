# G2.3.4 Cross-Model Interpretation

Interpret only schema-valid, provider-compatible OpenRouter pairs. G2.3.3 remains preserved as the strict-privacy negative result.

G2.3.4 relaxes only OpenRouter provider privacy routing to `data_collection=allow` for synthetic benchmark prompts. It does not change NowMind, the frozen benchmark, prompts, schema, scoring, validator, model-selection price gate, provider pinning, or fallback policy.

## nvidia/nemotron-3-super-120b-a12b:free

No completed provider-compatible paired result yet.

This candidate is the strongest G2.3.4 signal so far: it passed all four smoke checks at recorded cost `0`, then failed calibration after six schema-valid rows because the seventh raw model proposal was malformed JSON. Under the frozen schema rule, that is a calibration failure, not a tunable prompt issue.

## liquid/lfm-2.5-2.6b:free

No completed provider-compatible paired result yet.

Liquid produced one schema-valid smoke row after the privacy route was relaxed, then repeatedly paused on upstream shared-pool HTTP `429` rate limits.

## nvidia/nemotron-3-ultra-550b-a55b:free

No completed provider-compatible paired result yet.

The first smoke row had no usable raw JSON and no effective-provider evidence, so it was rejected by the provider consistency gate.

## z-ai/glm-5.2:free

No completed provider-compatible paired result yet.

Z.AI repeatedly paused on upstream shared-pool HTTP `429` rate limits before a schema-valid smoke row was available.

## minimax/minimax-m3:free

No completed provider-compatible paired result yet.

The endpoint rejected the frozen required-parameter request with HTTP `404`.

## dots-studio/dots-3-note-preview:free

No completed provider-compatible paired result yet.

The endpoint rejected the frozen required-parameter request with HTTP `404`.

## google/gemma-4-26b-a4b-it:free

No completed provider-compatible paired result yet.

The endpoint rejected the frozen required-parameter request with HTTP `404`.

No G2.3.4 cross-model evidence is complete enough yet to say whether the Regime-A chronology advantage persists, disappears, or reverses.

Because no exact-free model passed calibration, no G2.3.4 final Regime A or Regime B N/C/tie counts, raw accuracy, validated accuracy, paired p-values, or confidence intervals exist. The preserved local comparison remains `qwen3:0.6b`: Regime A C=8/N=0/T=242 and corrected Regime B C=0/N=0/T=250.

Do not claim NowMind superiority unless paired evidence supports it. Do not infer a general capability threshold from one exact-free model.

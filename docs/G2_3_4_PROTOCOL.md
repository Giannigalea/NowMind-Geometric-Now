# G2.3.4 Protocol

G2.3.4 preserves G2.3.3 as an unchanged negative strict-privacy result and writes only under `artifacts/g2_3_4/`.

The only relaxed operational constraint is provider privacy routing: requests use `data_collection=allow` for synthetic benchmark prompts only.

Frozen local reference: `qwen3:0.6b`, Regime A C=8/N=0/T=242, Regime B C=0/N=0/T=250.

Frozen scientific controls: 250 G2.3.2 trial IDs, Regime A semantics, corrected Regime B budget, common instruction, representation builders, output schema, scoring, validator, expected answers, exact `$0/$0` model gate, provider consistency, and fallback disabled.

Rediscovered exact-free text models: `18`.

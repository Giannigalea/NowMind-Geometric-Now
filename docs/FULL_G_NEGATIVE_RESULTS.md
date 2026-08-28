# Full-G Negative Results

Negative results are part of the milestone, not an embarrassment to hide. They keep the project falsifiable.

## Chronological Controls Often Match NowMind

In G2, `ChronologicalRecordReasoner` matched `NowMindTemporalGeometry` with `1.0` overall/source accuracy. The naive persistent-state baseline failed badly, but a competent source-aware chronological control did not.

In G2.1, Reactive and Chronological controls often matched NowMind on the synthetic spatial planning benchmark. Temporal memory was not yet a major advantage.

In G2.2 and G2.2.1, NowMind and Chronological tied after retrieval and recovery corrections. The improved architecture helped repair recovery and measurement issues, but it did not separate N from C on final corrected metrics.

## Real Local Model Did Not Favor NowMind

The completed local `qwen3:0.6b` benchmark did not show a NowMind advantage.

Regime A:

```text
Chronological wins = 8
NowMind wins = 0
ties = 242
```

Corrected Regime B:

```text
Chronological wins = 0
NowMind wins = 0
ties = 250
```

The eight Regime-A Chronological wins appear concentrated in tiny-model action/source-format weakness, but this is a plausible diagnosis, not a positive NowMind result.

## Free OpenRouter Replication Did Not Produce Cross-Model Evidence

G2.3.3 found no calibration-capable exact-free model under strict privacy/schema constraints.

G2.3.4 relaxed only provider privacy routing for synthetic benchmark data. One model passed smoke but failed calibration on malformed JSON. Other candidates were rate-limited, provider/parameter incompatible, or lacked provider/schema evidence.

No cloud cross-model N/C result exists for this milestone.

## Why This Matters

- It prevents benchmark gaming.
- It narrows claims to what the evidence actually supports.
- It separates source-aware architectural benefits from representation-specific performance benefits.
- It defines the next falsifiable questions: stronger models, better representation compression, harder non-chronological tasks, and possible learned consumers of Present Geometry.

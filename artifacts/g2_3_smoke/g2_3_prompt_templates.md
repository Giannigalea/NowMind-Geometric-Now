# G2.3 Prompt Templates

## Common System Instruction

```text
Use only supplied evidence.
Distinguish current observation, memory, and hypothetical future.
Do not promote memory or predictions to current fact.
Return UNKNOWN when current evidence is insufficient.
For action tasks, propose only actions supported by supplied state.
Return strict JSON with status, answer, source_used, confidence, action, assumptions, and explanation.
```

## Representation Prompt

Each condition receives the same system instruction and a deterministic JSON
representation after the marker `REPRESENTATION_JSON:`.

## Regime A

No truncation. Context overflow is recorded instead of silently truncating.

## Regime B

Both N and C use the same fixed token budget: `1600` estimated
tokens. N uses explicit reconstruction selection; C uses current/relevant
chronological records first and then newest records within the same budget.

# G2.3 Representation Fairness Rules

## Same model

For paired N/C comparison:
- exact same model;
- same generation parameters;
- same trial;
- same admissible underlying information.

## Regime A

No truncation. Test organization/representation.

## Regime B

Same input budget. Test resource-constrained behavior.

## Chronological condition

Do not intentionally make chronology confusing.

Use consistent cycle IDs/timestamps and legitimate source metadata.

## NowMind condition

Do not add evaluator truth or answer hints.

## Instruction parity

Prefer one common system instruction.

## Prompt versioning

Hash/version prompt templates and freeze before final evaluation.

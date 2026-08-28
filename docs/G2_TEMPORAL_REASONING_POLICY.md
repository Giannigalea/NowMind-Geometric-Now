# G2 Temporal Reasoning Policy

The G2 reasoner answers `TemporalQuery` from a single `TemporalNowState`.

## Temporal Intents

- `NOW`: current-state query.
- `PAST`: reconstructed-memory query.
- `POSSIBLE_FUTURE`: future-hypothesis query.
- `SOURCE`: strongest matching source report.

## NOW Queries

Current-state answers may use only:

- `OBSERVED_NOW`;
- `INFERRED_NOW`.

Reconstructed memory and future hypotheses are exposed as context but cannot
answer a current-state query.

If no valid current evidence exists, the answer is `UNKNOWN`. If current
evidence conflicts, the answer is `CONTRADICTORY`. Current evidence below the
configured reliability threshold returns `UNKNOWN` rather than falling back to
memory.

Default reliability threshold: `0.50`.

## PAST Queries

Past queries use `RECONSTRUCTED_MEMORY`. The answer includes reconstruction
confidence, source trace references, and historical source cycles. It is not
worded or treated as an exact replay of an old Now.

## POSSIBLE_FUTURE Queries

Future queries use `HYPOTHETICAL_FUTURE`. Multiple matching hypotheses are
preserved. A hypothesis is never current observation and is never encoded as
observed memory unless a later real observation independently confirms the fact.

## Confidence Conflict

Source type outranks numeric confidence for source selection. A current
observation at confidence `0.60` remains the current-state answer even if a
memory reconstruction has confidence `0.97`, as long as the current observation
passes the reliability threshold.

# G2.2.1 Verification Policy Audit

## Purpose

G2.2 verification was useful in some cases and wasted in others. G2.2.1 keeps
verification deterministic and symbolic, but tightens the decision gate so SCAN
is selected only when it can materially change the selected decision enough to
justify its cost.

## Decision Gate

The planner chooses verification only when all of these are true:

- scanning is available and has not already been used for the current geometry;
- the selected conditional plan depends on typed memory or future assumptions;
- at least one assumption is within scan reach;
- the known-safe alternative does not already dominate the conditional route;
- expected decision value exceeds scan cost.

The implemented gate is:

```text
verification_value = min(detour, expected_failure_cost) - scan_cost
verify if risk >= threshold and verification_value > 0
```

Where:

- `risk = 1 - mean(assumption confidence)`;
- `detour` is the known-safe route penalty avoided by using the conditional
  route, or the failure penalty when no safe route exists;
- `expected_failure_cost = risk * failure_penalty`;
- `scan_cost` is the configured information-action cost.

This is a transparent decision-value heuristic. It is not claimed as a formal
value-of-information optimum.

## Evaluator-Side Classifications

`verification_prevented_likely_failure_count`

A SCAN revealed an assumption cell as occupied, preventing a likely collision or
blocked-route failure.

`verification_enabled_shorter_route_count`

A SCAN can be counted here when it reveals assumptions as usable and thereby
enables a shorter route than the available known-safe alternative.

`verification_confirmed_useful_memory_count`

A SCAN revealed an assumption cell as free, confirming a remembered or
hypothesized route as usable.

`verification_wasted_safe_dominated_count`

A verification action had no concrete assumption target or was selected when the
safe route should have dominated.

`verification_wasted_no_decision_change_count`

A SCAN did not reveal information that could change the subsequent decision.

## Runtime Boundary

Verification classification is evaluator-side. Runtime planning receives only
the current `EpistemicGeometry`, explicit memory reconstructions, explicit future
hypotheses, and current recovery exclusions. Runtime code must not inspect
benchmark family names, trial ids, expected answers, seeds, or oracle truth.

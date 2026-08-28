# G2.2 Planning Policy

The G2.2 planner is deterministic symbolic search over epistemic geometry.

Search:

- heuristic: Manhattan distance;
- movement: four cardinal moves;
- movement order: east, south, west, north;
- base movement cost: `SensorConfig.move_cost`;
- observed occupied cells: blocked;
- observed free cells: traversable;
- unknown cells: blocked unless supported by an explicit planning assumption;
- `SCAN`: information action with `SensorConfig.scan_cost`.

Assumption sources:

- memory-supported free cells use `RECONSTRUCTED_MEMORY`;
- memory-supported hidden target locations use `RECONSTRUCTED_MEMORY`;
- future-supported cells or target locations use `HYPOTHETICAL_FUTURE`;
- assumptions never become `OBSERVED_NOW`.

The planner compares:

```text
known_safe_cost = path cost through observed free cells only
conditional_cost = path cost using typed memory/future assumptions
assumption_penalty =
  sum((1 - confidence) * memory_risk_weight) for memory assumptions
  + sum((1 - confidence) * unknown_cell_penalty) for future assumptions
conditional_score = conditional_cost + assumption_penalty
risk = 1 - mean(assumption confidences)
detour = known_safe_cost - conditional_cost
expected_failure_cost = risk * failure_penalty
verification_value = min(detour, expected_failure_cost) - scan_cost
```

Decision order:

1. If no goal is known, remembered, or hypothesized, choose `EXPLORE` with
   `SCAN` when scanning is available.
2. If a route depends on contradictory current sensor evidence, choose
   `VERIFY_FIRST`.
3. If the route depends on fallible assumptions, scanning can reach at least one
   assumption, `risk >= verify_risk_threshold`, and `verification_value > 0`,
   choose `VERIFY_FIRST`.
4. If the target is current observed and a fully observed route is competitive,
   choose `KNOWN_SAFE`.
5. If a memory/future-supported route is available, choose
   `CONDITIONAL_SHORTCUT`.
6. Otherwise return `NO_ROUTE`.

Important boundary:

A route to a coordinate can be physically known-safe while the reason for using
that coordinate as the goal is still fallible. If the goal came only from memory
or a future hypothesis, the plan remains conditional.

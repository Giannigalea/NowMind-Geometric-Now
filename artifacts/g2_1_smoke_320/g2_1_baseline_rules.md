# G2.1 Baseline Rules

## N - NowMind Possibility Geometry Planner

Uses current observed spatial geometry. Reconstructed memory may support unknown
cells only through explicit `RECONSTRUCTED_MEMORY` assumptions. The planner first
tries a fully observed route. Future hypotheses remain possibilities and do not
overwrite the current target.

## C - Chronological Geometric Planner

Uses the same A* pathfinding, movement rules, costs, and executor. It resolves
records chronologically and may use memory-supported unknown cells in the first
search pass rather than preferring a fully observed route. This can help on true
shortcuts and hurt on false remembered shortcuts.

## R - Reactive Current-Only Planner

Uses the same A* pathfinding on current observation only. Unknown cells are not
treated as free. It receives no memory reconstructions or future hypotheses.

## O - Oracle Planner

Evaluator-only upper bound using full current ground-truth occupancy and target
position. It is not a fair cognitive competitor.

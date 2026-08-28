# G2.2 Architecture

G2.2 Epistemic Geometry is additive. It preserves G1 fresh-Now semantics, G2
temporal source separation, and G2.1 one-action execution.

Runtime shape:

```text
SpatialWorldState_t
-> bounded epistemic observation
-> EpistemicGeometry_t
      |- observed free / observed blocked / unknown cells
      |- memory candidates as RECONSTRUCTED_MEMORY
      |- future candidates as HYPOTHETICAL_FUTURE
-> TemporalNowState_t
-> EpistemicPlanner
-> EpistemicPlan
      |- known-safe route, conditional route, verify-first, or explore
-> EpistemicActionExecutor
      |- SCAN changes observation only
      |- movement mutates SpatialWorldState by one step only
-> fresh EpistemicGeometry_t+1 / fresh TemporalNowState_t+1
```

The evaluator and oracle may inspect world truth. Runtime planners receive only
the current `EpistemicGeometry` plus explicitly supplied memory reconstructions
and future hypotheses.

## Runtime Modules

- `nowmind.epistemic.model`: sensor configuration, sensor readings, epistemic
  cells, partial observation, line-of-sight/fog handling, and conversion to
  present geometry.
- `nowmind.epistemic.planning`: deterministic epistemic planner, typed
  assumptions, scan/verify decisions, and planning metrics.
- `nowmind.epistemic.execution`: one-step action executor for movement or
  information actions.
- `nowmind.epistemic.cycle`: fresh epistemic cycles and closed-loop helper.

`nowmind.epistemic` does not import `nowmind.evaluation`; benchmarks remain
external research infrastructure.

## Source Firewall

- Unknown cells are never represented as `OBSERVED_NOW`.
- Memory-supported cells remain unknown unless current observation sees them.
- Future hypotheses can supply possible goals or route support, but remain
  `HYPOTHETICAL_FUTURE`.
- A plan is a current hypothesis, not a current fact.
- `SCAN` may reveal hidden geometry in the next observation, but it does not
  mutate physical world truth.

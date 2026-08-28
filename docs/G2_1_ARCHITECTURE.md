# G2.1 Architecture

G2.1 Possibility Geometry is additive. It does not change G1 `NowState` or G2
`TemporalNowState` semantics.

Runtime shape:

```text
SpatialWorldState_t
-> observed SpatialGeometry_t
-> TemporalNowState_t
      |- present_geometry: coordinate-derived current relations
      |- reconstructed_memories: explicit planning assumptions only
      |- future_hypotheses: possible future content only
-> AStarPlanner
-> Plan / ActionProposal
-> ActionExecutor mutates SpatialWorldState only
-> fresh observation / fresh TemporalNowState
```

There is no direct arrow from a selected plan or `HypotheticalGeometry` to
`OBSERVED_NOW`. A later matching observation is a new present fact.

## Runtime Modules

- `nowmind.spatial.model`: grid world, poses, spatial entities, occupancy, and
  observed spatial geometry.
- `nowmind.spatial.transformations`: cardinal transformations, hypothetical
  geometries, and physical constraint violations.
- `nowmind.spatial.planning`: A* planner, plan steps, assumptions, rejected
  alternatives, and action proposals.
- `nowmind.spatial.execution`: one-step executor that mutates the external
  spatial world.
- `nowmind.spatial.cycle`: fresh spatial observation plus `TemporalNowState`
  construction and a closed-loop helper.

`nowmind.spatial` does not import `nowmind.evaluation`; benchmarks remain
external evaluator infrastructure.


# Full-G Architecture Diagram Specification

Use this conceptual structure for reviewer diagrams:

```text
Physical World
      |
      v
Observation_t
      |
      v
Present Geometry_t
      |
      +---------------------+
      |                     |
      v                     v
Memory Reconstruction   Current Epistemic State
      |                     |
      +----------+----------+
                 |
                 v
          Temporal NowState
                 |
                 v
       Possibility Geometry
                 |
                 v
        Planner / Reasoner
                 |
                 v
              Action
                 |
                 v
          Physical World
                 |
                 v
             New Now
```

## Visual Rules

- Draw no arrow from a previous `NowState` directly into a new `NowState`.
- Memory enters only through `Memory Reconstruction`.
- Hypothetical futures must be marked `HYPOTHETICAL_FUTURE`.
- External experiment history must remain outside the reasoning loop.
- Physical `WorldState` may persist; cognitive `NowState` is reconstructed fresh.
- Observed, inferred, reconstructed-memory, and hypothetical-future content should use distinct source labels.
- The model faculty in G2.3 should be drawn as a replaceable proposal generator, not as observation, memory, world truth, or identity.

## Suggested Color/Legend

| Element | Meaning |
| --- | --- |
| Solid green | Current observed present content |
| Blue outline | Inferred current relation |
| Dashed amber | Reconstructed memory |
| Dotted violet | Hypothetical future |
| Gray side rail | Researcher/evaluator history outside runtime cognition |
| Red warning | Contradiction, unsupported certainty, or failed gate |

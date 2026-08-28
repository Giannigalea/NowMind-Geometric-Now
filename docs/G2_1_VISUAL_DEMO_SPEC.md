# G2.1 Visual Demonstrator Specification

## Goal

The browser demo should make a first-time viewer understand:

> NowMind generates and evaluates geometric possibilities from the current Now, then acts in the real world one step at a time and rebuilds a fresh Now after each observation.

The page should look like a small research simulator, not a raw developer dashboard.

## 1. Main canvas

Render a visible 2D world with:
- agent;
- target;
- obstacles/walls;
- optional door/container;
- grid/coordinate background.

Observed world objects should have solid styling.

## 2. Temporal overlays

Use clearly different styles:

- observed current geometry: solid, high priority, green/blue family;
- reconstructed memory: dashed/ghosted, amber family, label `MEMORY RECONSTRUCTION`;
- hypothetical future/path: translucent/dotted, purple family, label `POSSIBLE FUTURE`.

Never render a hypothetical path as the actual agent trail.

## 3. Candidate paths

Show:
- selected candidate path;
- at least one rejected/invalid candidate when available;
- rejection reason such as collision, blocked, out-of-bounds, higher cost, or assumption-dependent.

## 4. Step execution controls

Provide:
- `Plan`
- `Execute one step`
- `Run closed loop`
- `Pause`
- `Reset scenario`
- `Move obstacle`
- `Move target`
- `Inject stale memory`
- `Inject false memory`
- `Add future hypothesis`
- `Hide/reveal region` if partial observation is implemented.

After one step:
1. world changes;
2. hypothetical path remains only planning/history evidence;
3. fresh observation occurs;
4. new TemporalNowState ID appears;
5. planner continues or replans.

## 5. Legend

Always show:

```text
SOLID   = observed now
DASHED  = reconstructed memory
DOTTED  = hypothetical future
```

and:

```text
Selected plan is NOT reality.
Only executed + observed states become current facts.
```

## 6. Hero replanning scenario

1. Agent plans around obstacles to target.
2. Selected path appears.
3. After one or two executed steps, a new obstacle appears on the remaining path.
4. World is re-observed.
5. Old path is marked invalid.
6. New plan is generated from the new current Now.
7. New path appears.
8. External timeline shows separate Now IDs.

This should be the main G2.1 demonstration.

## 7. Stale-memory planning demo

Memory says shortcut open/free; current observation says blocked.

Show remembered shortcut ghosted/dashed, current obstacle solid, and planner rejection.

Display:

```text
Observed geometry overrides stale memory for current planning.
```

## 8. Unknown + memory demo

Corridor currently unobserved; memory says it was open.

Show unknown current corridor separately from memory overlay. Any route through it must be marked `CONDITIONAL`. If a fully observed alternative exists, show both.

## 9. Future target demo

Current target B solid; predicted future target C translucent/dotted.

Label C:

```text
HYPOTHETICAL — not current target location
```

## 10. Research inspector

Below the canvas keep expandable technical panels for current Present Geometry, TemporalNow sources, candidate hypothetical geometries, selected plan, assumptions, rejected alternatives, reasoning, and external history.

## 11. Benchmark view

Show systems compared, difficulty bands, planning success curves, collision rates, stale-memory planning errors, dynamic recovery, and Oracle optimality gap using local SVG/canvas/CSS only.

## 12. Disclaimer

> This is a deterministic/synthetic research environment for testing state representation, planning, and temporal-source handling. It does not demonstrate consciousness and is not yet a comparison with state-of-the-art learned AI planners.

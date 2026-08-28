# PRE_G1_2_VISUAL_CLARITY_TASK — Make G1.1 Intuitive and Visual

## Purpose

Do this task **before** G1.2 reviewer packaging.

The G1.1 browser demonstrator works technically, but it is still too developer-like and not visually intuitive enough. The main idea is not immediately obvious from the current interface.

The goal of this task is to make the demonstration understandable in under one minute by a first-time viewer.

## Critical rule

**Do not change the G1 cognitive architecture.**

Do not modify the logic of:
- WorldState
- Observation
- PresentGeometry
- NowState
- Reasoner
- ExperimentRecorder boundaries

This is a **presentation and explanation pass only**.

---

# 1. Main problem to solve

The current UI still looks like:
- text-heavy;
- developer-facing;
- abstract rather than geometric;
- too dependent on reading tables.

The central idea must become visually obvious:

> The world persists, but the cognitive Now is rebuilt fresh every cycle.

And:

> Previous Nows may remain visible to the researcher in external history, but they are not available to the current reasoner.

If a first-time viewer cannot see this immediately, the demo is still underperforming.

---

# 2. New top-of-page structure

Redesign the top of the page so the first screen clearly communicates the experiment.

## 2.1 Title section

Use:

### Title
`NowMind — Geometric Now G1`

### Subtitle
`A PCT-inspired experiment in rebuilding a fresh cognitive state every cycle.`

### Research disclaimer
`This prototype tests representation and reasoning behavior. It does not demonstrate or claim phenomenal consciousness.`

## 2.2 “What this tests” box

Add a clear box near the top:

### What this tests
Can an AI system rebuild a **fresh current cognitive state** every cycle, instead of silently carrying its previous cognitive state forward?

### Plain-English summary
- The **world** persists.
- The **current Now** is rebuilt from the current observation.
- The **reasoner sees only the current Now**.
- Previous Nows may remain in external history, but the reasoner cannot read them.

This should be short, plain English, and visible without scrolling.

---

# 3. Replace the ASCII architecture with a visual diagram

The current ASCII diagram is too weak visually.

Replace it with a proper browser-rendered diagram using HTML/CSS/SVG.

## Required diagram

Create a horizontal or vertical flow diagram with colored boxes.

### Suggested color meaning
- Blue = external world / external environment
- Green = current cognitive state / Present Geometry / current Now
- Gray = external history / previous Nows
- Red = blocked boundary / no access

## Required nodes
- WorldState
- Observation
- PresentGeometry
- NowState
- Reasoner
- Answer
- ExperimentRecorder

## Required relationship
Show:

`NowState -> ExperimentRecorder`

But then clearly show:
- a barrier,
- a blocked arrow,
- or an `X`
from ExperimentRecorder back to the Reasoner.

Make it visually obvious there is **no path back**.

Do **not** visually imply:
`NowState_t -> NowState_t+1`

because that would misrepresent the architecture.

---

# 4. Make Demo A the hero visual

The stale-state / Fresh Now demonstration must become the central demo.

When “Demo A - Fresh Now” is selected, the page should present:

## Left: visual world scene
## Center: current cognitive state
## Right: external history

The viewer should immediately see the difference between:
- what currently exists,
- what the reasoner currently sees,
- and what remains only in researcher history.

---

# 5. Add a real visual scene renderer

This is the key improvement.

Render the entities visually instead of only listing them in text.

## 5.1 For cubes
Render actual shapes:
- blue cube / square block
- red cube / square block

At minimum use 2D colored square blocks labeled:
- `blue_cube`
- `red_cube`

If a light isometric cube style is easy, that is fine.
If not, simple 2D colored squares are perfectly acceptable.

## 5.2 For spatial layout
If relation is:

`LEFT_OF(red_cube, blue_cube)`

render red cube visibly to the left of blue cube.

If relation becomes:

`RIGHT_OF(red_cube, blue_cube)`

render red cube visibly to the right of blue cube.

This should update after the move event.

The whole point is for the viewer to **see** the change, not only read it.

## 5.3 For containment demos
For:
- key inside box
- box inside cabinet

Render:
- a small key icon/rectangle inside a box
- the box inside a larger cabinet

Simple stylized shapes are enough.

## 5.4 For contradiction demo
Use a visual warning state:
- red outline,
- warning icon,
- or conflict banner.

Do not just bury contradiction in text.

---

# 6. Add a “Before / After” comparison for Demo A

For Demo A, show two visual cards side by side or stacked:

## Card 1 — Previous cycle
- `Cycle 1`
- `Now ID: ...`
- visual scene: red cube left of blue cube
- clearly label:
  `External history only`

## Card 2 — Current cycle
- `Cycle 2`
- `Now ID: ...`
- visual scene: red cube right of blue cube
- clearly label:
  `Current active Now`

Then add a highlighted conclusion:

### PASS
The current Now contains only the new relation.  
The previous Now still exists in external researcher history, but it is not available to the reasoner.

This is probably the single most important visual in the entire project.

---

# 7. Add “Reasoner can see / cannot see” panels

Create two visually distinct panels.

## Panel A — What the reasoner can see right now
Include:
- current Now ID
- current Present Geometry
- current observed relations
- current inferred relations
- current query

## Panel B — What exists but the reasoner cannot see
Include:
- previous Nows
- external experiment history
- deleted history result
- any archived cycle summaries

This should make the firewall intuitive.

---

# 8. Make the Present Geometry look geometric

Right now the relations are still too table-like.

Add a simple relation graph view.

Examples:

For Demo A:
- `[red_cube] --RIGHT_OF--> [blue_cube]`

For inference:
- `[A] --LEFT_OF--> [B]`
- `[B] --LEFT_OF--> [C]`
- inferred: `[A] --LEFT_OF--> [C]`

For containment:
- `[key] --INSIDE--> [box]`
- `[box] --INSIDE--> [cabinet]`

This can be rendered as:
- node cards with arrows;
- a mini SVG graph;
- or clean styled relation badges connected visually.

Do not remove the tabular details entirely.  
Instead:
- show the visual graph first;
- keep the tables below as technical detail.

---

# 9. Add a step-by-step mode

Add a guided display of the processing stages.

For the selected scenario, show step cards such as:

1. World exists
2. Observation taken
3. Present Geometry built
4. Fresh Now created
5. Reasoner answers
6. Result archived externally

This can be a horizontal stepper or numbered cards.

For the currently selected cycle, highlight the active path.

This will help non-programmers understand that the system is not just “a table of facts”.

---

# 10. Improve wording everywhere

Reduce overly internal or developer-heavy phrasing.

Use plain labels like:
- `Persistent world`
- `Current Now`
- `Observed now`
- `Inferred now`
- `External history`
- `Reasoner answer`
- `Blocked from reasoner`

Avoid making the page look like raw logs.

---

# 11. Keep technical detail, but collapse it

The current details are useful, but they should not dominate the first impression.

Use:
- summary view visible by default;
- expandable “Technical details” sections for tables, raw relation lists, validator output, rule IDs, JSON-like details.

This way:
- a first-time viewer gets the idea quickly;
- a technical reviewer can still inspect the exact evidence.

---

# 12. Add explicit visual success indicators

For key scenarios show badges like:
- `Fresh Now: PASS`
- `Stale-state contamination: NONE`
- `History firewall: ENFORCED`
- `Contradiction detected: YES`

Use clear colors:
- green for pass
- red/orange for contradiction or blocked access
- blue/gray for neutral info

---

# 13. Suggested layout

A good page layout could be:

## Row 1
- title / explanation / controls

## Row 2
- visual architecture diagram

## Row 3
- left: persistent world visual
- center: current Now visual / Present Geometry visual
- right: external history visual

## Row 4
- reasoner can see / cannot see

## Row 5
- technical details accordion
- relation tables
- explanation chain
- validation output

---

# 14. Keep all G1.1 guarantees

After the UI rewrite, the following must still be true:
- architecture audit still passes;
- runtime reasoner still only receives current `NowState`;
- UI must not bypass runtime logic;
- deleting history must not change current answer;
- all tests still pass.

Add or update tests as needed for the revised web/demo behavior.

---

# 15. Commands to run

Run and verify:

```text
python -m pytest
python -m nowmind.demo.cli
python -m nowmind.evaluation.run_g1_suite
python -m nowmind.demo.web
```

Verify that the browser experience clearly shows the visual scene and Fresh Now concept.

---

# 16. Completion report

When finished, return:
1. files created/changed;
2. what visual renderer was implemented;
3. how Demo A was improved;
4. whether the world scene now renders the cubes visually;
5. whether containment is rendered visually;
6. total test result;
7. whether any cognitive logic changed;
8. whether history firewall remains enforced;
9. browser demo URL;
10. any deviations;
11. recommendation on whether the project is now visually clear enough for G1.2 packaging.

## Important

Do not start G2 in this task.
Do not package reviewer materials in this task.
Only improve visual clarity and intuitive understanding.

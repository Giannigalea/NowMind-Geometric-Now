# G2.2 Acceptance Tests

All earlier tests remain mandatory.

## Perception
- cells outside visibility are UNKNOWN;
- occluded cells are not leaked from world truth;
- Oracle-only truth cannot be imported by runtime;
- sensor observations carry confidence/provenance.

## Information actions
- SCAN/vantage action changes observation, not world truth;
- information action has explicit cost;
- new information creates a fresh Now;
- planner can replan after verification.

## Memory
- memory-supported unknown cell remains UNKNOWN in observed geometry;
- memory may create a conditional planning assumption;
- stale memory is invalidated/contextualized after contradictory current observation;
- memory confidence never changes provenance.

## Future hypotheses
- hypothesis may support conditional branch;
- hypothesis is not current truth;
- later confirmation creates new observed evidence;
- falsification triggers reassessment.

## Epistemic planning
- planner can choose known-safe route;
- planner can choose conditional shortcut when policy favors it;
- planner can choose verify-first route when expected cost favors it;
- planner does not always scan;
- planner does not always avoid unknowns;
- decision is deterministic for fixed state/config.

## Hidden dynamics
- unobserved obstacle move remains unknown until observed;
- unobserved target move remains unknown until observed;
- after observation, stale plan is revalidated;
- no omniscient replanning.

## Long history
- H0/H10/H50/H100/H500 cohorts generated;
- history length does not alter present source labels;
- benchmark records evidence inspected;
- same seed reproduces cohorts.

## Benchmark
- minimum 3,000 trials by default unless documented runtime exception;
- E1-E24 represented;
- N/C/R/O all evaluated;
- pairwise trial IDs preserved;
- failure samples generated;
- metrics are derived.

## Web
- fog-of-war visible;
- memory overlay visually distinct;
- verify-first hero demo works;
- memory-correct and memory-false versions exist;
- current Now ID changes after verification.

# SECOND CODEX TASK — NowMind Geometric Now G1.1 Research Demonstrator

## Role

Continue as lead software engineer for the NowMind Geometric Now research project.

G1 has been reported complete with:
- 24 passing tests;
- successful CLI demos;
- enforced history firewall;
- no memory, LLM, prediction, identity, Veto Gate, Docker, or cloud dependency.

G1.1 must **not change the cognitive architecture**. Its purpose is to make G1 inspectable, demonstrable, reproducible, and ready for technical review by an external AI researcher.

Before changing code, read:
1. `AGENTS.md`
2. `docs/PCT_COMPUTATIONAL_RULES.md`
3. `docs/GEOMETRIC_NOW_G1_SPEC.md`
4. `docs/G1_ACCEPTANCE_TESTS.md`
5. `STATUS.md`
6. current G1 source and tests

---

# 1. First: independently audit G1

Do not trust the previous completion summary without checking the code.

Perform an architecture audit and confirm:

1. `NowState` is immutable.
2. `NowState` has no previous/history/memory reference.
3. each cycle creates a new `now_id`.
4. `WorldState` is distinct from `NowState`.
5. perception reads the current world state.
6. Present Geometry is rebuilt from the current observation.
7. no stale relation can survive merely because it existed in the previous cycle.
8. the deterministic reasoner receives only the current `NowState` plus current query.
9. runtime cognitive packages do not import evaluation-history retrieval.
10. `ExperimentRecorder` remains external to cognition.
11. inferred and observed relations retain distinct provenance.
12. predictions, memories, identities and LLM state are still absent.

If any invariant has been accidentally weakened, fix it before proceeding and document the correction in `docs/DECISIONS_LOG.md`.

Create `docs/G1_ARCHITECTURE_AUDIT.md` with:
- audit date;
- inspected modules;
- result for each invariant;
- exact relevant tests;
- any weakness found;
- final PASS/FAIL assessment.

---

# 2. Build the G1.1 visual research demonstrator

Create a lightweight **local browser-based demonstrator**.

Constraints:
- local only;
- no cloud;
- no LLM;
- no external API;
- no database;
- no telemetry;
- no Docker requirement;
- keep dependencies minimal;
- the demonstrator must call the existing G1 runtime rather than reimplement reasoning in JavaScript/UI code.

A standard-library Python HTTP server is preferred if practical. A tiny local dependency is acceptable only if it materially improves clarity and is documented.

Suggested command:

```text
python -m nowmind.demo.web
```

It should serve locally, for example:

```text
http://127.0.0.1:8765
```

Do not bind publicly by default.

---

# 3. Required demonstrator layout

The UI should visually separate four concepts.

## Panel A — Simulated World

Show current external `WorldState`.

Label explicitly:

> SIMULATED WORLD — persistent environment, external to NowMind cognition

## Panel B — Current Present Geometry

Show:
- current cycle ID;
- current `now_id`;
- entities;
- current observed relations;
- inferred relations;
- confidence;
- provenance;
- validation state.

Observed and inferred relations must be visibly distinguishable.

Label explicitly:

> PRESENT GEOMETRY — reconstructed fresh for this cognitive cycle

## Panel C — Reasoning / Explanation

Allow predefined queries and display:
- query;
- TRUE / FALSE / UNKNOWN / CONTRADICTORY;
- confidence;
- reasoning steps;
- premises;
- inference-rule identifiers.

Never hide a contradiction by rendering a guessed TRUE/FALSE result.

## Panel D — External Experiment History

Show prior recorded cycles in a separate panel.

Label explicitly:

> EXTERNAL EXPERIMENT RECORD — available to the researcher, NOT available to the runtime reasoner

For each recorded cycle show:
- cycle ID;
- `now_id`;
- summary of relations.

The runtime reasoner must not gain any new route to this history because of the UI.

---

# 4. Required interactive demonstrations

## Demo A — Fresh Now / stale-state test

Initial world:

```text
red_cube LEFT_OF blue_cube
```

Run Cycle 1.

Then apply world event:

```text
move red_cube to RIGHT_OF blue_cube
```

Run Cycle 2.

Show:
- a different `now_id`;
- `red_cube RIGHT_OF blue_cube`;
- inferred inverse `blue_cube LEFT_OF red_cube`;
- no stale `red_cube LEFT_OF blue_cube` in the active Present Geometry.

The external experiment history may still show Cycle 1.

## Demo B — Geometric inference

```text
A LEFT_OF B
B LEFT_OF C
```

Query:

```text
A LEFT_OF C?
```

Display TRUE and the complete transitivity explanation.

## Demo C — Nested containment

```text
key INSIDE box
box INSIDE cabinet
```

Query:

```text
key INSIDE cabinet?
```

Display TRUE with the inference chain.

## Demo D — Contradiction

Inject simultaneous incompatible current facts.

Display:
- contradiction warning;
- conflicting facts;
- structured validator result;
- `CONTRADICTORY` or project equivalent.

## Demo E — History firewall

Provide an action:

```text
Delete external experiment history
```

Then re-run the exact same current query.

Show that the answer remains unchanged.

Display:

> Current reasoning is unchanged because external experiment history is not a cognitive input.

This must be backed by the real runtime architecture, not merely simulated in the UI.

---

# 5. Architecture visualization

Add a simple diagram:

```text
WorldState
   |
   v
Observation
   |
   v
PresentGeometry
   |
   v
NowState
   |
   v
Reasoner
   |
   v
Answer

NowState ---> ExperimentRecorder
                  |
                  X
             no path back
             to Reasoner
```

Do not depict a direct arrow `NowState_t -> NowState_t+1`.

---

# 6. Reproducible evidence artifacts

Create:

```text
artifacts/g1/
```

Generate:

### `g1_test_results.txt`
Exact pytest command and summary.

### `g1_demo_results.json`
Machine-readable results from all canonical scenarios.

For every cycle include:
- cycle_id;
- now_id;
- observed relations;
- inferred relations;
- query;
- answer;
- explanation;
- validation state.

### `g1_invariant_results.json`
Machine-readable PASS/FAIL results for core architecture invariants.

### `g1_stale_state_experiment.json`
A focused multi-cycle experiment showing:
- Cycle 1 relation;
- world event;
- Cycle 2 relation;
- whether stale state contamination occurred.

Required runtime-derived result:

```json
{
  "stale_state_contamination": false
}
```

Do not hard-code it.

---

# 7. Repeatable experiment runner

Create a command similar to:

```text
python -m nowmind.evaluation.run_g1_suite
```

It should:
1. execute predefined G1 scenarios;
2. produce machine-readable artifacts;
3. compute summary metrics;
4. exit non-zero if a required invariant fails.

Minimum metrics:

```text
scenario_count
query_accuracy
inference_accuracy
contradiction_detection_rate
stale_state_contamination_count
stale_state_contamination_rate
unknown_guess_count
```

Document exactly how each metric is calculated.

Target deterministic stale-state contamination rate:

```text
0.0
```

---

# 8. Scientific wording

Use restrained wording.

Acceptable:
- cognitive architecture;
- Present Geometry;
- NowState;
- functional model;
- deterministic reasoner;
- PCT-inspired architecture;
- experiment;
- state reconstruction.

Do not claim:
- NowMind is conscious;
- G1 proves consciousness;
- G1 proves PCT;
- subjective experience;
- sentience;
- geometric reasoning is inherently conscious.

Visible disclaimer:

> NowMind G1 is a computational research architecture inspired by Present Consciousness Theory. Its behavior tests representation and reasoning properties; it does not demonstrate or claim phenomenal consciousness.

---

# 9. Reference-folder cleanup check

The previous completion report mentioned:

> "the large PDF under `reference/missing_originals/`"

Check this carefully.

`reference/missing_originals/` was intended for placeholders describing unavailable originals.

If an actual PCT book PDF is there:

1. move it to:

```text
reference/PCT_Book_Latest.pdf
```

2. update `reference/SOURCE_INDEX.md`;
3. remove/update the missing-original placeholder;
4. do not modify the book.

If no actual book exists, leave the missing status intact.

The inability to text-extract a large reference PDF is **not a G1 blocker**. Do not repeatedly perform heavy PDF extraction if it causes memory errors.

---

# 10. External-review documentation

Create `docs/G1_TECHNICAL_OVERVIEW.md`.

Audience: an AI researcher seeing the project for the first time.

Target: approximately 1,200–2,000 words.

Sections:
1. Problem
2. PCT-inspired computational constraint
3. Architecture
4. Why `WorldState` and `NowState` are separated
5. Present Geometry
6. Deterministic inference
7. History firewall
8. Experiments
9. Results
10. Limitations
11. What G1 does NOT claim
12. G2 research direction

Technical and restrained, not marketing copy.

Also create `docs/G1_REPRODUCIBILITY.md` with:
- Windows setup;
- supported Python version;
- install commands;
- test command;
- CLI demo command;
- browser demo command;
- experiment-suite command;
- artifact locations.

---

# 11. Update README

Add:
- concise G1 explanation;
- architecture diagram;
- core invariant;
- test command;
- CLI command;
- browser demo command;
- experiment generation command.

Keep detailed theory in `docs/`.

---

# 12. Testing requirements

Retain all existing G1 tests.

Add tests for:
- web/demo controller does not bypass runtime reasoning;
- UI/history endpoints cannot inject previous `NowState` into reasoning;
- experiment runner derives metrics correctly;
- stale-state experiment genuinely uses two fresh Nows;
- external history deletion does not affect current answer;
- evidence JSON has stable/documented structure.

Run:

```text
python -m pytest
python -m nowmind.demo.cli
python -m nowmind.evaluation.run_g1_suite
```

Launch and verify the local browser demonstrator.

All old and new tests must pass.

---

# 13. Do NOT implement G2 yet

Do not add:
- memory;
- retrieval;
- embeddings;
- hypothetical future states;
- identity;
- Veto Gate;
- LLM integration;
- OpenAI API;
- dreaming;
- camera/microphone;
- autonomous tools;
- self-modification.

G1.1 is presentation, reproducibility, evidence, and audit only.

---

# 14. Completion report

When finished, return:

1. architecture-audit result;
2. files created/changed;
3. total tests and pass/fail result;
4. exact commands executed;
5. G1 experiment metrics;
6. paths to generated evidence artifacts;
7. browser demo command/URL;
8. confirmation no G2 feature was introduced;
9. confirmation history firewall remains enforced;
10. status of the PCT reference PDF;
11. deviations;
12. recommendation for the next task.

Do not recommend contacting an external researcher until:
- all G1.1 tests pass;
- evidence artifacts are generated;
- technical overview exists;
- demonstrator is reproducible.

# FIRST CODEX TASK — Build NowMind Geometric Now G1

## Role

Act as the lead software engineer for an experimental AI architecture derived from Present Consciousness Theory (PCT).

Do not reinterpret the project as a generic agent framework.

## Before writing code

Read in full:

1. `00_READ_ME_FIRST.md`
2. `AGENTS.md`
3. every file in `docs/`
4. `SOURCE_MATERIALS_CHECKLIST.md`
5. `reference/SOURCE_INDEX.md`

If source material such as the PCT book or legacy NowMind repository has been added, inspect it for context, but follow the documented authority order.

## Task

Implement **NowMind Geometric Now G1** according to `docs/GEOMETRIC_NOW_G1_SPEC.md`.

### G1 must provide

1. a persistent simulated `WorldState`;
2. explicit world events;
3. a perception adapter producing current-cycle observations;
4. a fresh Present Geometry built from those observations;
5. a new immutable `NowState` every cognitive cycle;
6. deterministic relation inference;
7. relation provenance;
8. relation confidence;
9. contradiction/validation handling;
10. a reasoner that receives only the current `NowState`;
11. explanation chains for inferred answers;
12. an external experiment recorder that may store historical Nows but is not readable by runtime reasoning;
13. all acceptance tests in `docs/G1_ACCEPTANCE_TESTS.md`;
14. a CLI demo implementing the scenarios in the specification;
15. a clear `README.md` containing Windows setup and run instructions;
16. a `STATUS.md` summarizing what is implemented, tests run, known limitations, and next recommended task.

## Technical constraints

- Python 3.12+.
- Must run locally on Windows.
- Do not require Docker.
- Do not use an LLM.
- Do not require internet access.
- Avoid unnecessary dependencies.
- `pytest` is acceptable and preferred for tests.
- Use type hints.
- Prefer immutable dataclasses or equivalent for core Now objects.
- Core logic should be inspectable rather than hidden behind a large framework.
- Keep evaluation/history infrastructure outside the runtime cognitive dependency path.

## Critical architecture invariant

This is the invariant most likely to be accidentally violated:

> A previous `NowState` must never become cognitive input to the next Now.

The world can persist.
The evaluator can retain history.
The current Now must be reconstructed from current observation.

Write architecture tests specifically designed to fail if a future developer accidentally introduces direct previous-Now access.

## Expected demo

The CLI should visibly demonstrate at least:

### Demo 1 — State change
Cycle 1:
`red_cube LEFT_OF blue_cube`

World event:
move `red_cube` to the other side.

Cycle 2:
`red_cube RIGHT_OF blue_cube`

Show:
- cycle id;
- `now_id`;
- current observed relation;
- inferred inverse relation;
- answer to a query;
- no stale relation from cycle 1.

### Demo 2 — Transitive reasoning
A left of B.
B left of C.
Query: A left of C?
Result: TRUE.
Show explanation rule/premises.

### Demo 3 — Nested containment
key inside box.
box inside cabinet.
Query: key inside cabinet?
Result: TRUE with explanation.

### Demo 4 — Contradiction
Inject incompatible simultaneous relations.
Show structured contradiction rather than guessed answer.

## Implementation sequence

Use this order unless a strong engineering reason requires a change:

1. initialize package/project metadata;
2. implement domain records;
3. implement world/events;
4. implement perception;
5. implement Present Geometry builder;
6. implement inference rules;
7. implement validation;
8. implement immutable `NowState`;
9. implement reasoner/query/explanations;
10. implement cognitive cycle orchestration;
11. implement external recorder;
12. implement architecture firewall tests;
13. implement scenario tests;
14. implement CLI;
15. run full test suite;
16. update README, STATUS, Decisions Log.

## Do not implement yet

Do not add:
- memory;
- retrieval;
- vector databases;
- embeddings;
- LLM prompts;
- OpenAI API calls;
- identity;
- goals;
- emotions;
- future-state simulation;
- Veto Gate;
- dreaming;
- camera/mic;
- self-modification;
- cloud services.

If tempted to add one because it would make implementation easier, do not. Preserve the experiment.

## Completion report

When finished, report:

1. files created/changed;
2. architecture implemented;
3. tests run and exact results;
4. demo commands;
5. any deviation from spec;
6. known limitations;
7. whether the history-firewall invariant is demonstrably enforced;
8. recommended G1.1 task.

Do not claim G1 is complete unless all required tests pass.

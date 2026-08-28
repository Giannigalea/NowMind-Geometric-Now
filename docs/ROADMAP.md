# NowMind Geometric Roadmap

## G1 — Geometric Now Core

Goal:
Create and reason over a fresh Present Geometry every cognitive cycle.

Includes:
- simulated WorldState;
- perception snapshot;
- entities/relations;
- immutable NowState;
- deterministic inference;
- contradiction handling;
- explanations;
- external experiment logs;
- architecture firewall against previous Nows.

Excludes:
- memory;
- predictions;
- identity;
- LLM;
- veto;
- dreaming;
- camera/mic.

## G1.1 — Demonstrator

After G1 tests are stable:
- add a clear human-facing demo;
- visualize entities and relations;
- step world events one cycle at a time;
- show observed vs inferred edges;
- show the `now_id`;
- show previous Nows only in a separate evaluator panel clearly labelled as external history;
- demonstrate that the cognitive reasoner cannot access that history.

Purpose:
make the idea easy to inspect and eventually show to researchers such as Julian Michels / Sophontic AI.

## G2 — Temporal Now

Add explicit temporal-source channels.

### Memory
- encoded traces;
- retrieval;
- fuzzy reconstruction;
- confidence;
- cue dependence;
- current reconstruction object.

### Possibility geometry
- candidate transformations;
- hypothetical future states;
- explicit `HYPOTHETICAL_FUTURE` provenance;
- strict prevention of predictions being logged as observations.

Core research question:
Can past and possible future influence action while remaining computationally distinguishable from present observation?

## G3 — Identity + Veto

### Identity
Implement identity as a present construction constrained by relatively stable anchors/invariants.

Do not equate identity with:
- memory storage;
- chat history;
- exact autobiographical replay.

Measure:
- continuity;
- drift;
- coherence.

### Veto Gate
Implement L3 action inhibition:
- candidate action;
- projected consequences;
- uncertainty;
- ethical/operational constraints;
- allowed/inhibited decision;
- explanation.

Prior NowMind work included action inhibition under cognitive uncertainty; recover relevant legacy logic only after the new G1/G2 state model is stable.

## G4 — Embodied NowMind

Connect real perception:
- camera;
- microphone;
- possibly desktop/environment events.

Pipeline:
raw sensor -> L1 substrate -> observation -> Present Geometry -> L2 reasoning -> L3 veto -> action.

Use confidence aggressively because perception is no longer perfect.

## G5 — Dreaming / Offline Internal Experience

Only after memory and temporal provenance are stable.

Constraints:
- no live external data during dreaming;
- use prior internal experience;
- do not replay historical Nows as if they are current reality;
- reconstruct/recombine;
- modes may include random, context-driven, or goal-driven transformations.

## G6 — Model-integrated Geometric Reasoning

Only after deterministic baselines exist.

Experiment with:
- an LLM proposing relations/hypotheses;
- symbolic geometry validating them;
- LLM as one cognitive faculty rather than the identity/state architecture;
- possible comparison with latent-geometric reasoning research.

## Quantum/PCT research track

Keep separate from implementation until a falsifiable computational mechanism is defined.

Permitted early use:
- mathematical analogy;
- hypothesis-space discussion;
- uncertainty representation.

Not permitted:
- presenting probabilistic hypothesis selection as evidence of quantum consciousness.

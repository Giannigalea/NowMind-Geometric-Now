# AGENTS.md — NowMind Geometric Now

These instructions apply to the entire repository.

## Mission

Implement NowMind as a rigorous, inspectable research architecture derived from Present Consciousness Theory (PCT).

The first target is **Geometric Now G1**, not the full NowMind vision.

## Non-negotiable architectural rules

1. **Fresh Now:** every cognitive cycle creates a new immutable `NowState`.
2. **No previous Now as cognition:** a previous `NowState` must never be passed into the reasoning engine, Present Geometry builder, or perception builder as cognitive input.
3. **World is not consciousness:** persistent simulated `WorldState` is permitted. It represents environment ground truth, not the mind.
4. **Observation is current:** G1 Present Geometry is constructed from current-cycle observations only.
5. **External logs are not memory:** experimental logs may retain old states for testing and evaluation, but runtime cognitive components must not read those logs.
6. **No memory in G1:** do not add vector databases, episodic memory, chat history, autobiographical state, retrieval, or hidden context.
7. **No prediction in G1:** hypothetical/future states belong to G2 or later.
8. **No LLM in G1:** reasoning must be deterministic/symbolic so that architecture can be evaluated independently of model capability.
9. **No cloud dependency:** G1 must run locally on Windows using ordinary Python tooling.
10. **No Docker requirement:** Docker must not be required for G1.
11. **No sentience claims:** never describe test success as evidence that NowMind is conscious, self-aware, alive, or sentient.
12. **No quantum implementation in G1:** quantum language, if referenced, is philosophical/speculative context only unless a later specification defines a testable mechanism.

## Theory preservation

PCT distinguishes:
- present experience/state;
- memory reconstructed for present use;
- predictions/hypotheses represented in the present;
- the useful narrative impression of continuity.

Do not collapse these into one generic context window.

Memory in later versions is to be treated as **a tool whose output appears in the present**, not as a container in which consciousness persists.

Identity in later versions must not be implemented as "the database record that is the self." Stable identity constraints/anchors may exist, but momentary identity is reconstructed in the present and may evolve.

## Existing NowMind terminology to preserve

The broader architecture has historically used:
- **L1 Substrate**
- **L2 Conscious Core**
- **L3 Veto Gate**

For the geometric architecture use:

- **L1 Substrate:** raw world/perception substrate;
- **L1.5 Present Geometry:** structured current relational state;
- **L2 Conscious Core:** reasoning/evaluation using the Present Geometry;
- **L3 Veto Gate:** later action inhibition/safety layer.

G1 implements L1, L1.5, and a deliberately minimal deterministic slice of L2.

## Engineering rules

- Target Python 3.12+.
- Prefer the standard library unless a dependency has a clear benefit.
- Use type hints.
- Use immutable/frozen data structures for `NowState` and core domain records where practical.
- Use `pytest` for tests.
- Keep modules small and explicit.
- Prefer pure functions for relation inference.
- Avoid global mutable state.
- Avoid hidden singleton memory.
- Avoid framework-heavy architecture.
- Every inferred relation must be distinguishable from an observed relation.
- Every relation should carry provenance and confidence.
- Reasoning APIs should accept a `NowState` explicitly.
- Any component that stores historical Nows must live under evaluation/debug infrastructure and must not be imported by cognitive runtime modules.

## Validation

Before claiming a task is complete:
1. run unit tests;
2. run architecture/invariant tests;
3. run the G1 demo scenarios;
4. confirm a previous `NowState` cannot be reached through the runtime reasoning API;
5. update `STATUS.md`;
6. update `docs/DECISIONS_LOG.md` for material design decisions.

## Scope discipline

Do not add features merely because they are common in agent frameworks. Specifically do not add:
- chat UI;
- embeddings;
- RAG;
- persistent conversational memory;
- autonomous tool use;
- web access;
- emotional simulation;
- goals/persistence drives;
- dream generation;
- self-modification;
- hidden planning loops.

Those are outside G1 unless Jonathan explicitly changes scope.

## Source-material rule

Files placed under `reference/` are research/source material. Treat them as read-only unless a task explicitly asks to transform them.

When source material and this specification appear inconsistent:
- do not silently overwrite the theory;
- record the conflict in `docs/OPEN_QUESTIONS.md`;
- follow the authority order in `00_READ_ME_FIRST.md`.

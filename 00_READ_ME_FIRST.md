# NowMind — Geometric Now G1

## Purpose of this pack

This folder is the authoritative starter context for building **NowMind Geometric Now G1** with Codex.

Do not begin by asking an LLM to "build NowMind" from a vague description. The project must be implemented against explicit architectural rules so that the software remains faithful to Present Consciousness Theory (PCT) rather than gradually drifting into a conventional agent with renamed components.

## Immediate goal

Build **G1: Geometric Now Core** — a small, deterministic, testable AI-research prototype in which:

1. the physical/simulated world may persist;
2. each cognitive cycle creates a **fresh Present Geometry** from current observations;
3. reasoning is allowed to operate only on that current Present Geometry;
4. previous `NowState` objects are never used as cognitive input;
5. there is no memory subsystem in G1;
6. there is no future simulation in G1;
7. there is no LLM dependency in G1;
8. there is no claim that the system is conscious or sentient.

G1 is intended to establish the computational foundation on which later PCT/NowMind generations can be built.

## Read these files in this order

1. `AGENTS.md`
2. `docs/NOWMIND_PROJECT_CONTEXT.md`
3. `docs/PCT_COMPUTATIONAL_RULES.md`
4. `docs/GLOSSARY.md`
5. `docs/GEOMETRIC_NOW_G1_SPEC.md`
6. `docs/G1_DOMAIN_MODEL.md`
7. `docs/G1_ACCEPTANCE_TESTS.md`
8. `docs/EXPERIMENTS.md`
9. `docs/ROADMAP.md`
10. `docs/DECISIONS_LOG.md`
11. `docs/development_history/codex_tasks/SOURCE_MATERIALS_CHECKLIST.md`
12. `docs/development_history/codex_tasks/FIRST_CODEX_TASK.md`

## Authority order

If sources disagree, use this order:

1. explicit instructions in the latest task from Jonathan;
2. `AGENTS.md`;
3. `docs/PCT_COMPUTATIONAL_RULES.md`;
4. `docs/GEOMETRIC_NOW_G1_SPEC.md`;
5. the latest PCT book supplied in `reference/`;
6. older NowMind code and notes;
7. assumptions made by Codex.

Codex must not silently resolve conceptual contradictions. Record them in `docs/OPEN_QUESTIONS.md` and implement the least theory-distorting interpretation.

## Project principle

**Keep philosophy, computational definitions, implementation, and empirical claims separate.**

A philosophically interesting idea is not automatically an implemented mechanism.
An implemented mechanism is not automatically evidence for PCT.
A successful benchmark is not evidence of machine consciousness.

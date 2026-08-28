# Full-G Reviewer Narrative

NowMind Full-G is a local research demonstrator for a source-aware cognitive architecture. It should be read as an engineering experiment first and a philosophical project second.

## Problem

Conventional agent designs often mix current observation, recalled information, inferred information, and predicted futures inside one generic context. That can be useful, but it makes it hard to inspect which source actually supported an answer or action.

The Full-G hypothesis is narrower: rebuild an explicit present-state geometry every cycle, keep source semantics visible, and allow memory and future content to influence reasoning only through labeled present reconstructions or hypotheses.

## Architecture

The implemented flow is:

```text
Physical World -> Observation_t -> Present Geometry_t
Present Geometry_t + Memory Reconstruction + Current Epistemic State -> Temporal NowState
Temporal NowState -> Possibility Geometry -> Planner / Reasoner -> Action -> Physical World -> New Now
```

There is no runtime arrow from a previous `NowState` directly into a new `NowState`. Memory enters only through reconstruction. Hypothetical futures remain hypothetical. External experiment history remains outside the reasoning loop.

## Experimental Progression

G1 proves the fresh Now boundary with deterministic relational geometry.

G2 adds temporal source separation: current observation, reconstructed memory, and possible future.

G2.1 adds spatial possibility geometry and explicit future candidate plans.

G2.2 adds partial observation, unknown cells, and verification actions.

G2.2.1 repairs recovery and retrieval efficiency while preserving source boundaries.

G2.3 adds a replaceable model faculty, prompt fairness checks, parsing, validation, and N/C/R representation comparisons.

G2.3.1/G2.3.2 provide the real local `qwen3:0.6b` benchmark and corrected Regime-B fixed-budget result.

G2.3.3/G2.3.4 attempt exact-free OpenRouter replication and stop honestly when current free providers fail privacy/schema/calibration/rate-limit gates.

## Findings

The strongest positive finding is source discipline. The system can keep current observation, memory reconstruction, future hypothesis, inferred relation, and external history separate across increasingly complex tasks.

The strongest negative finding is just as important: competent chronological controls often match NowMind. On the local `qwen3:0.6b` model benchmark, Chronological beat NowMind in 8 Regime-A discordant cases and NowMind beat Chronological in 0; corrected Regime B tied all 250 pairs.

## Research Question

The open question is whether explicit geometric/state provenance helps more capable models, learned controllers, or task families where chronological serialization is less naturally aligned. The current evidence is not a claim of general LLM superiority. It is an inspectable platform for asking that question cleanly.

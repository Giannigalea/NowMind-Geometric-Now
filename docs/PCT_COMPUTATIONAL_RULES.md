# PCT Computational Rules

These rules translate core PCT ideas into software constraints.

## PCT-01 — Present primacy

At cognitive cycle `t`, the agent's active reasoning state is `NowState_t`.

Only `NowState_t` may be treated as the present cognitive representation.

## PCT-02 — Fresh construction

`NowState_t` must be newly constructed for cycle `t`.

It may not be implemented as a mutable object that simply accumulates changes indefinitely.

## PCT-03 — Previous Now prohibition

`NowState_(t-1)` must not be passed directly into the cognitive reasoning path of cycle `t`.

This is one of the most important invariants in the project.

## PCT-04 — Persistent environment is separate

The external/simulated world may persist as `WorldState`.

`WorldState` is not the mind.

At each cycle:

`WorldState_t -> Observation_t -> PresentGeometry_t -> NowState_t`

## PCT-05 — Memory is reconstruction, not persistence of consciousness

From G2 onward:

`past event -> encoded trace -> storage -> retrieval -> reconstruction_t`

Only `reconstruction_t` enters the current Now.

The raw historical trace is not itself the present conscious state.

The system must preserve the difference between:
- an event that occurred;
- a stored trace;
- a reconstruction produced now.

## PCT-06 — No exact-replay assumption

Later memory systems should not assume that retrieval recreates the historical Now exactly.

Memory reconstruction may be:
- partial;
- noisy;
- cue-dependent;
- confidence-bearing;
- context-sensitive.

## PCT-07 — Prediction is present representation

From G2 onward, a predicted state must be explicitly marked hypothetical.

A predicted state is a representation existing now of a possible future.

It must never be confused with an observation.

## PCT-08 — Temporal provenance

Every piece of information entering a later Now should be classifiable, where relevant, as one of:

- `OBSERVED_NOW`
- `INFERRED_NOW`
- `RECONSTRUCTED_MEMORY`
- `HYPOTHETICAL_FUTURE`
- `IDENTITY_CONSTRAINT`
- `EXTERNAL_FEEDBACK`

G1 uses the first two only.

## PCT-09 — Continuity is constructed

Do not implement continuity as an invisible mutable "self object" that simply persists and contains all experience.

Later versions should make continuity an explicit computation across present reconstructions.

## PCT-10 — Identity is not memory

Later identity must not reduce to:
- chat history;
- vector memory;
- autobiographical database;
- model weights.

Stable constraints/anchors may contribute to identity continuity, but identity presented at cycle `t` is a current construction.

## PCT-11 — Action occurs in the present

Only the current cycle may authorize action.

Historical states may inform action only after being reconstructed into the current state under explicit rules.

## PCT-12 — External logs are epistemically separate

Test/evaluation infrastructure may retain exact historical states.

The cognitive runtime must not be able to retrieve them unless a future explicitly specified memory adapter reconstructs information from them.

An evaluator knowing the past is not the same as NowMind remembering the past.

## PCT-13 — Dreaming is internally generated present experience

For future versions only:
- dreaming runs when external perception is unavailable/disabled or under an explicit idle rule;
- it uses prior internal experience;
- it does not directly replay historical Nows;
- it may recombine/reconstruct material;
- it does not use external live data while dreaming.

## PCT-14 — Safety remains independent

The L3 Veto Gate must remain conceptually separable from ordinary reasoning.

A later reasoning system may propose actions; the veto layer may inhibit them.

## PCT-15 — No metaphysical inference from implementation

Passing these rules or benchmarks does not establish:
- phenomenal consciousness;
- subjective experience;
- moral status;
- quantum consciousness;
- human-equivalent identity.

Those are separate philosophical/scientific questions.

# Experimental Programme

## Purpose

NowMind should be developed as an experiment, not only as software.

Every generation should have:
- a hypothesis;
- a baseline;
- controlled inputs;
- measurable outputs;
- failure criteria.

## G1 hypothesis

A strictly reconstructed Present Geometry can maintain correct current relational reasoning without direct access to previous cognitive states.

This is primarily an architectural proof.

## G1 measurements

Track:
- current-state relation accuracy;
- inference accuracy;
- contradiction detection;
- stale-state contamination rate;
- explanation completeness;
- cycle construction time.

### Stale-state contamination rate

Create scenarios where a relation changes between cycles.

Example:
- t1: A left of B;
- t2: A right of B.

A stale-state error occurs if t2 reasoning incorrectly reports the t1 relation because of retained cognitive state.

Target for deterministic G1:
- 0 stale-state errors.

## Baseline for later comparison

G1 itself may not require an LLM baseline.

However preserve scenarios in machine-readable form so later versions can compare:

### Baseline A
Conventional conversational/LLM agent supplied with a textual event history.

### Experimental B
NowMind architecture supplied with current Present Geometry plus explicit memory reconstruction/hypothesis channels.

Compare:
- current state accuracy;
- temporal-source confusion;
- false memory contamination;
- explanation quality;
- action-selection errors.

## G2 experiments — Temporal Now

Test:
- remembered past vs current observation;
- false/stale memory vs current perception;
- present prediction vs observation;
- memory confidence;
- reconstruction distortion.

Example:

```text
t1 box = closed
t2 box = open
memory trace says box was closed
question: what is true now?
```

The architecture must preserve:
- current observation = open;
- reconstructed memory = formerly closed;
- no category collapse.

## G3 experiments — Identity and Veto

Test:
- identity continuity despite changing memories/context;
- identity drift;
- conflict between candidate action and stable ethical constraints;
- veto under uncertainty;
- whether action inhibition improves safety without globally disabling reasoning.

## G4 experiments — Embodied Present Geometry

Introduce camera/microphone or other sensors only after simulated-state invariants are reliable.

Measure:
- perception-to-geometry accuracy;
- object persistence vs hallucinated persistence;
- uncertainty propagation;
- latency;
- grounding errors.

## Scientific caution

Do not use performance results as evidence that the architecture is phenomenally conscious.

The experiments assess:
- representation;
- reasoning;
- continuity modeling;
- source separation;
- action governance.

They do not directly measure subjective experience.

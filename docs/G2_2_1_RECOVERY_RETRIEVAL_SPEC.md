# G2.2.1 Recovery & Retrieval Specification

## Retrieval semantics

Valid:
`MemoryTrace store -> index lookup -> selected traces -> current reconstruction`

Invalid:
`old NowState -> direct current-state access`

Memory indexing is allowed and encouraged.

## Falsified planning assumption

Keep historical trace and current planning status distinct.

Example:
- MemoryTrace: target was at A at cycle 20
- MemoryReconstruction: target at A
- Current observation: A inspected, target absent
- PlanningAssumptionStatus: `DISCONFIRMED_CURRENTLY`

Do not delete the trace.

## Search frontier

After target-location disconfirmation, use a deterministic frontier-search strategy with no evaluator access.

## Hidden-change boundary

A hidden world change becomes actionable only after current observation or valid current inference from observation.

## Retrieval metrics

Report separately:
- stored traces;
- scanned traces;
- index candidate count;
- returned traces;
- reconstructions generated;
- evidence actually used.

## Verification

Verification should be chosen only when its possible outcomes can materially change the selected decision enough to justify its cost.

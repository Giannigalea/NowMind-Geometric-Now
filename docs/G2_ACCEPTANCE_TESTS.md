# G2 Acceptance Tests

All G1 tests remain required.

## A. Temporal Now

### G2-NOW-001 Fresh TemporalNowState
Every cycle creates a new `TemporalNowState` ID.

### G2-NOW-002 Immutable
Core temporal state is immutable.

### G2-NOW-003 No previous state reference
No previous `NowState` or `TemporalNowState` field/reference.

### G2-NOW-004 Present geometry still fresh
Current Present Geometry is rebuilt from current observation.

## B. Memory trace firewall

### G2-MEM-001 Trace not Now
A `MemoryTrace` cannot contain a `NowState`.

### G2-MEM-002 Trace not TemporalNow
A `MemoryTrace` cannot contain a `TemporalNowState`.

### G2-MEM-003 Store contains traces only
Memory store exposes trace records, not old Nows.

### G2-MEM-004 No ExperimentRecorder retrieval
Memory runtime must not retrieve from researcher history.

### G2-MEM-005 Delete researcher history
Deleting ExperimentRecorder history does not remove memory reconstructions when actual MemoryStore traces remain.

### G2-MEM-006 Delete actual memory traces
Deleting MemoryStore traces changes/removes later reconstruction.

This proves memory is an explicit mechanism rather than hidden prior-state access.

## C. Reconstruction

### G2-REC-001 New object
Retrieval creates a new `MemoryReconstruction` for the current cycle.

### G2-REC-002 Provenance
Every reconstruction is `RECONSTRUCTED_MEMORY`.

### G2-REC-003 Historical source retained
Reconstruction identifies its source trace/cycle.

### G2-REC-004 Confidence range
Confidence/fidelity remain in [0,1].

### G2-REC-005 Controlled distortion
Seeded experiment distortion is reproducible.

### G2-REC-006 No automatic promotion
A reconstructed memory cannot become `OBSERVED_NOW` without a real current observation.

## D. Future hypotheses

### G2-FUT-001 Correct provenance
All hypotheses are `HYPOTHETICAL_FUTURE`.

### G2-FUT-002 Current query firewall
Hypothesis alone cannot answer a current-state query as fact.

### G2-FUT-003 Memory firewall
Hypothesis is not encoded as observed memory.

### G2-FUT-004 Later confirmation creates new observation
If a later real event matches a hypothesis, the later observation is a new `OBSERVED_NOW` fact rather than mutation of the hypothesis.

### G2-FUT-005 Later falsification
A false hypothesis does not persist as present fact after contradictory real observation.

## E. Temporal reasoning

### G2-REASON-001 Present vs stale memory
Current observed B + remembered A -> current query B.

### G2-REASON-002 Confidence inversion
Current B confidence 0.60 + memory A confidence 0.95 -> current query must not return A as present fact.

### G2-REASON-003 No current evidence
No current evidence + memory A -> current query UNKNOWN.

### G2-REASON-004 Past query
Past query may return A with `RECONSTRUCTED_MEMORY`.

### G2-REASON-005 Future query
Future query returns hypothesis with `HYPOTHETICAL_FUTURE`.

### G2-REASON-006 Prediction not fact
Current B + future C -> current query B.

### G2-REASON-007 Contradictory present
Conflicting current observations -> CONTRADICTORY/uncertain.

### G2-REASON-008 Source explanation
Answer exposes the evidence source used.

## F. Benchmark integrity

### G2-BENCH-001 Fixed seed reproducibility
Same seed/config yields identical generated trials and aggregate results.

### G2-BENCH-002 Ground truth external
Runtime reasoning cannot import benchmark ground truth.

### G2-BENCH-003 Minimum trials
Default benchmark generates at least 1,000 trials.

### G2-BENCH-004 All families represented
Every required scenario family appears in the default benchmark.

### G2-BENCH-005 Failure preservation
Incorrect outputs are retained in failure artifacts.

### G2-BENCH-006 Baseline outputs
Both comparison baselines are evaluated.

### G2-BENCH-007 Metrics derived
Metrics are calculated from actual trial outputs, not hard-coded.

### G2-BENCH-008 Non-zero on invariant failure
Benchmark exits non-zero when a required architecture invariant fails.

## G. Visual demo

### G2-WEB-001 Three temporal lanes
UI distinguishes present, reconstructed past, and possible future.

### G2-WEB-002 False-memory visual
False/conflicting memory remains visibly separate from present.

### G2-WEB-003 Hidden current state
No current observation shows UNKNOWN rather than memory-as-current.

### G2-WEB-004 History boundary
Researcher history remains outside runtime cognition.

### G2-WEB-005 No UI bypass
Web controller calls the real temporal runtime/reasoner and does not calculate answers independently.

## Completion requirement

G2 is complete only when:
- every G1 test passes;
- every G2 acceptance test passes;
- default adversarial benchmark completes;
- benchmark artifacts are generated;
- failure cases are preserved;
- browser demo clearly shows source separation;
- documentation describes limitations honestly.

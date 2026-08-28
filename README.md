# NowMind Geometric Now G2.3

NowMind Geometric Now G1 is a local deterministic research prototype derived from
Present Consciousness Theory computational rules.

G1.1 keeps the G1 cognitive architecture unchanged and adds audit,
reproducibility, evidence artifacts, and a local browser demonstrator.

G2 adds Temporal Geometry on top of that frozen G1 foundation: memory traces,
current memory reconstruction, future hypotheses, source-safe temporal
reasoning, adversarial benchmarks, comparison baselines, and a local visual
demonstrator.

G2.1 adds Possibility Geometry: explicit 2D spatial state, hypothetical
transformations, A* planning, one-action execution, fresh re-observation, dynamic
replanning, planning benchmarks, and browser visuals for selected, rejected,
memory-supported, and future-hypothetical paths.

G2.2 adds Epistemic Geometry: bounded partial observation, fog-of-war unknown
cells, sensor confidence, typed memory/future assumptions, explicit SCAN
information actions, deterministic verify-first policy, hidden dynamic changes,
long-history stress, and an epistemic planning benchmark.

G2.2.1 adds targeted epistemic recovery and retrieval-efficiency diagnostics:
indexed current-memory retrieval, stale target disconfirmation, deterministic
target reacquisition, hidden obstacle/target recovery, a tightened verification
decision gate, and a separate holdout benchmark.

G2.3 adds local-first model integration and a representation benchmark: the same
admissible task facts are rendered as NowMind structured, clean chronological,
current-only, and symbolic-reference conditions, then proposal-only and
validated results are reported separately. In this environment no Ollama runtime
is installed, so generated G2.3 artifacts use the deterministic mock backend and
record the missing local-model prerequisite.

Core architecture:

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

The world may persist. Each cognitive cycle creates a fresh immutable `NowState`.
Runtime reasoning does not receive a previous Now, experiment history, memory,
future state, LLM context, or cloud service.

G2 temporal runtime adds:

```text
PresentGeometry_t
   |
   v
TemporalNowState_t
   |- OBSERVED_NOW / INFERRED_NOW
   |- RECONSTRUCTED_MEMORY
   |- HYPOTHETICAL_FUTURE
   v
TemporalReasoner
```

Memory enters only as `MemoryTrace -> MemoryReconstruction`. Future hypotheses
remain present content about possible futures, not observations.

G2.1 possibility runtime adds:

```text
SpatialGeometry_t
   |
   v
HypotheticalGeometry candidates
   |
   v
Plan / ActionProposal
   |
   v
ActionExecutor -> SpatialWorldState_t+1
   |
   v
fresh observation -> fresh TemporalNowState_t+1
```

A selected plan is not reality. Only execution in the external world followed by
observation creates new current facts.

G2.2 epistemic runtime adds:

```text
SpatialWorldState_t
   |
   v
bounded observation / SCAN
   |
   v
EpistemicGeometry_t
   |- OBSERVED_NOW known-free / known-blocked cells
   |- UNKNOWN fog cells
   |- RECONSTRUCTED_MEMORY candidates
   |- HYPOTHETICAL_FUTURE candidates
   v
EpistemicPlan
   |
   v
EpistemicActionExecutor -> fresh EpistemicGeometry_t+1
```

Memory-supported unknown cells remain unknown. Future hypotheses remain
hypotheses. A verify-first plan is a current hypothetical decision, not observed
truth.

G2.3 model-comparison runtime adds:

```text
Geometry / admissible facts
   |
   v
Representation Builder
   |
   v
Replaceable local model backend
   |
   v
ModelProposal
   |              \
   v               v
raw metrics    symbolic validation
                    |
                    v
              validated result
```

The model is a replaceable faculty. It may propose answers, actions, and
explanations, but it may not become identity, memory, observation, action
execution, or world truth.

## What Is Implemented

- Persistent simulated `WorldState`.
- Explicit world events such as adding entities and setting or moving relations.
- Perfect G1 perception adapter producing current-cycle `Observation` objects.
- Present Geometry builder using only current observations.
- Immutable `NowState` records with unique `now_id` values.
- Deterministic inference for inverse, symmetric, and safe transitive relations.
- Relation provenance: `OBSERVED_NOW` vs `INFERRED_NOW`.
- Relation confidence with conservative inference policy: `min(premises)`.
- Structured validation issues for missing entities, invalid self-relations, and contradictions.
- Reasoning API that accepts only a current `NowState` and a `Query`.
- Explanation chains for inferred answers.
- External experiment recorder that can store historical Nows outside runtime cognition.
- CLI demo scenarios for state change, transitivity, containment, and contradiction.
- Local browser demonstrator for inspecting G1.
- Repeatable evidence suite under `artifacts/g1/`.
- Automated acceptance and architecture/firewall tests.
- G2 `TemporalNowState` with explicit temporal-source channels.
- Immutable memory traces, deterministic cue retrieval, and current-cycle memory
  reconstruction.
- Immutable future hypotheses with `HYPOTHETICAL_FUTURE` provenance.
- Source-safe temporal reasoner for current, past, and possible-future queries.
- G2 adversarial benchmark with NowMind plus two symbolic baselines.
- G2 browser demos A-F and benchmark dashboard.
- G2.1 `nowmind.spatial` runtime with explicit 2D grid geometry, occupancy,
  transformations, hypothetical geometries, assumptions, plans, and one-step
  action execution.
- G2.1 planning benchmark with D1-D5 difficulty bands, P1-P16 scenario families,
  NowMind/chronological/reactive/oracle systems, and required artifacts.
- G2.1 browser demos for dynamic replanning, stale-memory rejection, conditional
  memory routes, and future target hypotheses.
- G2.2 `nowmind.epistemic` runtime with bounded partial perception, line-of-sight
  and fog handling, sensor readings, epistemic cells, scan actions, typed
  assumptions, deterministic verify-first planning, and closed-loop fresh
  re-observation.
- G2.2 benchmark with D1-D6 difficulty bands, E1-E24 scenario families, H0-H1000
  history cohorts, NowMind/chronological/reactive/oracle systems, and required
  artifacts.
- G2.2 browser demos for memory-false and memory-correct verification paths with
  fog, memory ghost, future overlay, selected path, SCAN, and fresh Now IDs.
- G2.2.1 indexed retrieval, recovery bookkeeping, stale-target/frontier
  reacquisition, hidden-change recovery metrics, verification-policy audit, and
  holdout benchmark artifacts.
- G2.2.1 browser demos for stale target recovery and hidden obstacle recovery.
- G2.3 `nowmind.modeling` backends, strict JSON proposal parsing, local-only
  Ollama wrapper, deterministic mock backend, representation builders, symbolic
  validator, and no-LLM symbolic reference condition.
- G2.3 paired representation benchmark with calibration/evaluation splits,
  Regime A equal information, Regime B fixed budget, N/C/R/S conditions,
  proposal-only and validated metrics, prompt-fairness artifacts, model
  manifest, failure samples, and browser model-comparison demo.

## Not Implemented

G2.3 intentionally still excludes vector databases, embeddings as memory,
OpenAI/Gemini/Anthropic calls, cloud models, identity, goals, emotions, L3 Veto
Gate, dreaming, camera/microphone input, self-modification, Docker, and
automatic model downloads.

Passing the tests is evidence that the software invariants hold. It is not
evidence that the system is conscious, self-aware, sentient, or alive.

## Windows Setup

Use Python 3.12 or newer.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

If `py` or `python` is not on PATH, use the full path to your Python 3.12
interpreter to create the venv, then run:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

Docker is not required.

## Run Tests

```powershell
python -m pytest
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Run Demo

```powershell
python -m nowmind.demo.cli
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.cli
```

The demo prints cycle ids, fresh `now_id` values, observed relations, inferred
relations, query answers, explanation rules, and contradiction issues.

## Run Browser Demonstrator

```powershell
python -m nowmind.demo.web
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.web
```

Open:

```text
http://127.0.0.1:8765
```

The browser demonstrator is local only. It calls the Python G1/G2 runtimes; the
browser code only renders state and sends demo actions.

## Generate Evidence Artifacts

```powershell
python -m nowmind.evaluation.run_g1_suite
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g1_suite
```

Artifacts are written to:

```text
artifacts/g1/
```

Key files:

- `g1_test_results.txt`
- `g1_demo_results.json`
- `g1_invariant_results.json`
- `g1_stale_state_experiment.json`
- `g1_metrics.json`

Generate G2 benchmark artifacts:

```powershell
python -m nowmind.evaluation.run_g2_benchmark
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_benchmark
```

Artifacts are written to:

```text
artifacts/g2/
```

Key files:

- `g2_metrics.json`
- `g2_benchmark_summary.md`
- `g2_trial_results.jsonl`
- `g2_source_confusion_matrix.json`
- `g2_failure_samples.json`
- `g2_invariant_results.json`
- `g2_seed_and_config.json`
- `g2_baseline_rules.md`

Generate G2.1 planning benchmark artifacts:

```powershell
python -m nowmind.evaluation.run_g2_1_benchmark
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_1_benchmark
```

Artifacts are written to:

```text
artifacts/g2_1/
```

Key files:

- `g2_1_metrics.json`
- `g2_1_metrics_by_difficulty.json`
- `g2_1_metrics_by_family.json`
- `g2_1_trial_results.jsonl`
- `g2_1_failure_samples.json`
- `g2_1_invariant_results.json`
- `g2_1_seed_and_config.json`
- `g2_1_baseline_rules.md`
- `g2_1_benchmark_summary.md`
- `g2_1_planning_examples.json`
- `g2_1_oracle_gap.json`

Generate G2.2 epistemic benchmark artifacts:

```powershell
python -m nowmind.evaluation.run_g2_2_benchmark
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_2_benchmark
```

Artifacts are written to:

```text
artifacts/g2_2/
```

Key files:

- `g2_2_metrics.json`
- `g2_2_metrics_by_difficulty.json`
- `g2_2_metrics_by_family.json`
- `g2_2_history_scaling.json`
- `g2_2_trial_results.jsonl`
- `g2_2_failure_samples.json`
- `g2_2_invariant_results.json`
- `g2_2_seed_and_config.json`
- `g2_2_baseline_rules.md`
- `g2_2_benchmark_summary.md`
- `g2_2_pairwise_comparison.json`

Generate G2.2.1 recovery/retrieval benchmark artifacts:

```powershell
python -m nowmind.evaluation.run_g2_2_1_benchmark
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_2_1_benchmark
```

Artifacts are written to:

```text
artifacts/g2_2_1/
```

Key files:

- `g2_2_1_metrics_v1_regression.json`
- `g2_2_1_metrics_holdout.json`
- `g2_2_1_history_scaling.json`
- `g2_2_1_retrieval_metrics.json`
- `g2_2_1_recovery_metrics.json`
- `g2_2_1_verification_metrics.json`
- `g2_2_1_pairwise_comparison.json`
- `g2_2_1_failure_samples.json`
- `g2_2_1_invariant_results.json`
- `g2_2_1_holdout_seed_and_config.json`
- `g2_2_1_summary.md`

Generate G2.3 model-representation benchmark artifacts:

```powershell
python -m nowmind.evaluation.run_g2_3_benchmark
```

Equivalent venv-explicit command:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_3_benchmark
```

Artifacts are written to:

```text
artifacts/g2_3/
```

Key files:

- `g2_3_model_manifest.json`
- `g2_3_prompt_templates.md`
- `g2_3_calibration_results.json`
- `g2_3_metrics.json`
- `g2_3_metrics_by_family.json`
- `g2_3_metrics_by_history.json`
- `g2_3_pairwise_n_vs_c.json`
- `g2_3_proposal_vs_validated.json`
- `g2_3_trial_results.jsonl`
- `g2_3_failure_samples.json`
- `g2_3_prompt_fairness_results.json`
- `g2_3_seed_and_config.json`
- `g2_3_summary.md`

## Architecture Notes

Runtime modules follow this dependency direction:

```text
world -> perception -> geometry -> core -> reasoning
```

The `evaluation` package imports runtime outputs for experiment recording. Runtime
cognitive modules do not import `evaluation`, and tests inspect this firewall.

The state-change scenario is the central invariant check:

1. Cycle 1 observes `LEFT_OF(red_cube, blue_cube)`.
2. A world event moves the red cube.
3. Cycle 2 observes `RIGHT_OF(red_cube, blue_cube)`.
4. Cycle 2 has no stale `LEFT_OF(red_cube, blue_cube)` relation.

## Review Documents

- `docs/G1_ARCHITECTURE_AUDIT.md`
- `docs/G1_TECHNICAL_OVERVIEW.md`
- `docs/G1_REPRODUCIBILITY.md`
- `docs/G2_ARCHITECTURE.md`
- `docs/G2_MEMORY_MODEL.md`
- `docs/G2_TEMPORAL_REASONING_POLICY.md`
- `docs/G2_BENCHMARK_METHOD.md`
- `docs/G2_LIMITATIONS.md`
- `docs/G2_1_ARCHITECTURE.md`
- `docs/G2_1_SPATIAL_MODEL.md`
- `docs/G2_1_TRANSFORMATIONS.md`
- `docs/G2_1_PLANNING_POLICY.md`
- `docs/G2_1_BENCHMARK_METHOD.md`
- `docs/G2_1_LIMITATIONS.md`
- `docs/G2_2_ARCHITECTURE.md`
- `docs/G2_2_EPISTEMIC_GEOMETRY_SPEC.md`
- `docs/G2_2_PLANNING_POLICY.md`
- `docs/G2_2_BENCHMARK_SPEC.md`
- `docs/G2_2_BENCHMARK_METHOD.md`
- `docs/G2_2_ACCEPTANCE_TESTS.md`
- `docs/G2_2_LIMITATIONS.md`
- `docs/G2_2_1_BASELINE_SNAPSHOT.md`
- `docs/G2_2_1_RECOVERY_RETRIEVAL_SPEC.md`
- `docs/G2_2_1_HOLDOUT_RULES.md`
- `docs/G2_2_1_ACCEPTANCE_TESTS.md`
- `docs/G2_2_1_EVIDENCE_METRIC_AUDIT.md`
- `docs/G2_2_1_VERIFICATION_POLICY_AUDIT.md`
- `docs/G2_3_MODEL_INTEGRATION_SPEC.md`
- `docs/G2_3_REPRESENTATION_FAIRNESS.md`
- `docs/G2_3_ACCEPTANCE_TESTS.md`
- `docs/G2_3_PROMPT_FAIRNESS_AUDIT.md`
- `docs/G2_3_STATISTICAL_METHOD.md`
- `docs/G2_3_LOCALITY_AUDIT.md`

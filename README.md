# NowMind Geometric Now Full-G Research Package

NowMind Geometric Now is a local, inspectable research prototype derived from
Present Consciousness Theory (PCT). It tests whether explicit present-state
relational geometry can enforce clean separation between current observation,
reconstructed memory, hypothetical futures, uncertainty, planning, and model
proposals.

This repository is public for technical review, evaluation, discussion, and
citation. It is not an open-source release. See [COPYRIGHT.md](COPYRIGHT.md).

NowMind currently investigates **explicit present-state relational geometry**.
It does not claim to train or discover latent geometric structure inside a
neural model. Whether explicit state geometry and learned internal reasoning
geometry can operate as complementary representational levels remains an open
research question.

## Reviewer Path

Start here:

- [REPRODUCE_FULL_G.md](REPRODUCE_FULL_G.md) - local reproduction commands.
- [docs/FULL_G_RESULTS_SUMMARY.md](docs/FULL_G_RESULTS_SUMMARY.md) - compact
  stage-by-stage results.
- [docs/FULL_G_CLAIMS_AND_NONCLAIMS.md](docs/FULL_G_CLAIMS_AND_NONCLAIMS.md) -
  what the evidence does and does not support.
- [docs/FULL_G_NEGATIVE_RESULTS.md](docs/FULL_G_NEGATIVE_RESULTS.md) - negative
  and null results, including local-model failures.
- [docs/EXTERNAL_TECHNICAL_BRIEF.md](docs/EXTERNAL_TECHNICAL_BRIEF.md) -
  neutral technical brief for external researchers.
- [artifacts/README.md](artifacts/README.md) - canonical artifact map.

## What This Does And Does Not Claim

The package claims only that the implemented software and frozen artifacts test
specific architectural invariants and benchmark conditions.

It does **not** establish:

- consciousness;
- sentience;
- phenomenal experience;
- quantum consciousness;
- general model superiority;
- a demonstrated NowMind-over-chronological-control advantage.

The strongest local real-model result used Ollama `qwen3:0.6b`:

| Regime | Chronological wins | NowMind wins | Ties |
|---|---:|---:|---:|
| Regime A, equal information | 8 | 0 | 242 |
| Corrected Regime B, fixed token budget | 0 | 0 | 250 |

The result supports an important negative conclusion: on this small local model,
the NowMind representation did not outperform the chronological control.

## Architecture Summary

G1 starts with a deterministic fresh-current-state architecture:

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

Later stages preserve that boundary while adding explicit representation layers:

- **G2 Temporal Geometry:** current observation, reconstructed memory, and
  hypothetical future are separate provenance channels.
- **G2.1 Possibility Geometry:** explicit 2D spatial state, hypothetical
  transformations, A* planning, one-action execution, and fresh re-observation.
- **G2.2 Epistemic Geometry:** bounded partial observation, fog-of-war unknowns,
  confidence, typed assumptions, SCAN actions, and verify-first planning.
- **G2.2.1 Epistemic Recovery:** indexed retrieval, stale-target
  disconfirmation, hidden obstacle/target recovery, and holdout metrics.
- **G2.3-G2.3.4 Model Comparison:** replaceable model backends, strict JSON
  proposals, representation builders, symbolic validation, local `qwen3:0.6b`
  results, and documented free-provider compatibility failures.

The model is a replaceable faculty. It may propose answers, actions, and
explanations, but it may not become identity, memory, observation, action
execution, or world truth.

## Implemented Scope

- Persistent simulated world state.
- Fresh observation and Present Geometry construction each cycle.
- Immutable Now records with unique IDs.
- Deterministic relation inference with provenance and confidence.
- Structured contradiction and validation reporting.
- Runtime reasoning APIs that accept the current Now explicitly.
- External experiment recording that cannot feed back into runtime cognition.
- G1 CLI and browser demos.
- G2 temporal-source benchmarks and baselines.
- G2.1 planning benchmarks and browser demos.
- G2.2 epistemic planning benchmarks and browser demos.
- G2.2.1 recovery/retrieval diagnostics and holdout benchmark.
- G2.3 representation benchmark, local/mock model backends, prompt fairness
  artifacts, symbolic validator, and proposal-vs-validated reporting.
- G2.3.1-G2.3.4 real/local/free-provider replication artifacts.

## Not Implemented

This milestone intentionally excludes vector databases, embeddings as memory,
identity, emotional simulation, L3 Veto Gate, dreaming, camera/microphone input,
self-modification, Docker requirements, paid cloud APIs, paid model calls, and
automatic model downloads.

Passing the tests is evidence that software invariants hold. It is not evidence
that the system is conscious, self-aware, sentient, or alive.

## Local Setup

Use Python 3.12 or newer.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

If `py` or `python` is not on PATH, use the full path to a Python 3.12
interpreter to create the virtual environment.

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

The demo prints cycle IDs, fresh `now_id` values, observed relations, inferred
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

Full-G reviewer mode:

```text
http://127.0.0.1:8765/?demo=full_g_reviewer
```

The browser demonstrator is local only. It calls the Python runtimes; browser
code only renders state and sends demo actions.

## Generate Evidence Artifacts

G1:

```powershell
python -m nowmind.evaluation.run_g1_suite
```

G2 through G2.3 local synthetic benchmarks:

```powershell
python -m nowmind.evaluation.run_g2_benchmark
python -m nowmind.evaluation.run_g2_1_benchmark
python -m nowmind.evaluation.run_g2_2_benchmark
python -m nowmind.evaluation.run_g2_2_1_benchmark
python -m nowmind.evaluation.run_g2_3_benchmark
```

The frozen Full-G package includes artifacts through G2.3.4. Paid APIs and paid
cloud model calls are not required for local review.

## Review Documents

Primary Full-G review documents:

- [REPRODUCE_FULL_G.md](REPRODUCE_FULL_G.md)
- [docs/FULL_G_RESULTS_SUMMARY.md](docs/FULL_G_RESULTS_SUMMARY.md)
- [docs/FULL_G_CLAIMS_AND_NONCLAIMS.md](docs/FULL_G_CLAIMS_AND_NONCLAIMS.md)
- [docs/FULL_G_NEGATIVE_RESULTS.md](docs/FULL_G_NEGATIVE_RESULTS.md)
- [docs/EXTERNAL_TECHNICAL_BRIEF.md](docs/EXTERNAL_TECHNICAL_BRIEF.md)
- [artifacts/README.md](artifacts/README.md)

Stage documents:

- [docs/G1_ARCHITECTURE_AUDIT.md](docs/G1_ARCHITECTURE_AUDIT.md)
- [docs/G1_TECHNICAL_OVERVIEW.md](docs/G1_TECHNICAL_OVERVIEW.md)
- [docs/G1_REPRODUCIBILITY.md](docs/G1_REPRODUCIBILITY.md)
- [docs/G2_ARCHITECTURE.md](docs/G2_ARCHITECTURE.md)
- [docs/G2_MEMORY_MODEL.md](docs/G2_MEMORY_MODEL.md)
- [docs/G2_TEMPORAL_REASONING_POLICY.md](docs/G2_TEMPORAL_REASONING_POLICY.md)
- [docs/G2_BENCHMARK_METHOD.md](docs/G2_BENCHMARK_METHOD.md)
- [docs/G2_LIMITATIONS.md](docs/G2_LIMITATIONS.md)
- [docs/G2_1_ARCHITECTURE.md](docs/G2_1_ARCHITECTURE.md)
- [docs/G2_1_SPATIAL_MODEL.md](docs/G2_1_SPATIAL_MODEL.md)
- [docs/G2_1_TRANSFORMATIONS.md](docs/G2_1_TRANSFORMATIONS.md)
- [docs/G2_1_PLANNING_POLICY.md](docs/G2_1_PLANNING_POLICY.md)
- [docs/G2_1_BENCHMARK_METHOD.md](docs/G2_1_BENCHMARK_METHOD.md)
- [docs/G2_1_LIMITATIONS.md](docs/G2_1_LIMITATIONS.md)
- [docs/G2_2_ARCHITECTURE.md](docs/G2_2_ARCHITECTURE.md)
- [docs/G2_2_EPISTEMIC_GEOMETRY_SPEC.md](docs/G2_2_EPISTEMIC_GEOMETRY_SPEC.md)
- [docs/G2_2_PLANNING_POLICY.md](docs/G2_2_PLANNING_POLICY.md)
- [docs/G2_2_BENCHMARK_SPEC.md](docs/G2_2_BENCHMARK_SPEC.md)
- [docs/G2_2_BENCHMARK_METHOD.md](docs/G2_2_BENCHMARK_METHOD.md)
- [docs/G2_2_ACCEPTANCE_TESTS.md](docs/G2_2_ACCEPTANCE_TESTS.md)
- [docs/G2_2_LIMITATIONS.md](docs/G2_2_LIMITATIONS.md)
- [docs/G2_2_1_BASELINE_SNAPSHOT.md](docs/G2_2_1_BASELINE_SNAPSHOT.md)
- [docs/G2_2_1_RECOVERY_RETRIEVAL_SPEC.md](docs/G2_2_1_RECOVERY_RETRIEVAL_SPEC.md)
- [docs/G2_2_1_HOLDOUT_RULES.md](docs/G2_2_1_HOLDOUT_RULES.md)
- [docs/G2_2_1_ACCEPTANCE_TESTS.md](docs/G2_2_1_ACCEPTANCE_TESTS.md)
- [docs/G2_2_1_EVIDENCE_METRIC_AUDIT.md](docs/G2_2_1_EVIDENCE_METRIC_AUDIT.md)
- [docs/G2_2_1_VERIFICATION_POLICY_AUDIT.md](docs/G2_2_1_VERIFICATION_POLICY_AUDIT.md)
- [docs/G2_3_MODEL_INTEGRATION_SPEC.md](docs/G2_3_MODEL_INTEGRATION_SPEC.md)
- [docs/G2_3_REPRESENTATION_FAIRNESS.md](docs/G2_3_REPRESENTATION_FAIRNESS.md)
- [docs/G2_3_ACCEPTANCE_TESTS.md](docs/G2_3_ACCEPTANCE_TESTS.md)
- [docs/G2_3_PROMPT_FAIRNESS_AUDIT.md](docs/G2_3_PROMPT_FAIRNESS_AUDIT.md)
- [docs/G2_3_STATISTICAL_METHOD.md](docs/G2_3_STATISTICAL_METHOD.md)
- [docs/G2_3_LOCALITY_AUDIT.md](docs/G2_3_LOCALITY_AUDIT.md)

## Copyright

Copyright (c) 2026 Jonathan Galea. All rights reserved. See
[COPYRIGHT.md](COPYRIGHT.md).

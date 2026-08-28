# Status - 2026-08-23

## 2026-08-28 Full-G Milestone Freeze and Reviewer Package

Full-G is frozen for this milestone as a local reviewer/reproducibility
package covering G1 through G2.3.4. No paid API calls or paid cloud models are
required for review or reproduction.

- G1 through G2.2.1 remain local, deterministic/architectural demonstrations.
- G2.3.2 remains the final completed local real-model benchmark using
  `qwen3:0.6b`.
- G2.3.3 and G2.3.4 are frozen as negative/blocked free OpenRouter replication
  attempts. No exact-free OpenRouter model completed a calibrated 250-trial
  provider-compatible run.
- The Full-G reviewer mode is available locally at
  `http://127.0.0.1:8766/?demo=full_g_reviewer` when the demo server is running.
- Git was initialized, but the active `.git/` directory caused a Codex desktop
  setup-refresh failure on this machine. The initialized Git metadata was
  preserved at `tmp/git_disabled_due_codex_refresh_20260828_full_g/`; see
  `docs/FULL_G_GIT_STATUS.md`. The current preserved Git `HEAD` is the
  baseline commit for the Full-G freeze.

Fresh verification:

```text
pytest: 138 passed in 202.78s (0:03:22)
G1 CLI demo: passed all four required scenarios
G1 suite: stale_state_contamination_count=0, query_accuracy=1.0,
inference_accuracy=1.0, contradiction_detection_rate=1.0
Full-G reviewer web smoke: nowmind.full_g.web_state.v1, sections=6
Secret scan: no live OpenRouter key pattern or unredacted provider user_id found
```

Primary Full-G package artifacts:

```text
docs/FULL_G_MILESTONE_FREEZE.md
docs/FULL_G_RESULTS_SUMMARY.md
docs/FULL_G_CLAIMS_AND_NONCLAIMS.md
docs/FULL_G_REVIEWER_NARRATIVE.md
docs/FULL_G_ARCHITECTURE_DIAGRAM_SPEC.md
docs/FULL_G_NEGATIVE_RESULTS.md
docs/FULL_G_OPEN_QUESTIONS.md
docs/JULIAN_TECHNICAL_BRIEF_DRAFT.md
docs/FULL_G_REVIEW_CHECKLIST.md
docs/FULL_G_GIT_STATUS.md
REPRODUCE_FULL_G.md
run_full_g_demo.ps1
artifacts/full_g/full_g_benchmark_table.csv
artifacts/full_g/full_g_benchmark_table.md
```

## 2026-08-28 G2.3.4 Free Provider-Compatible Replication

G2.3.4 is implemented as a separate OpenRouter replication namespace under
`artifacts/g2_3_4/`. G2.3.3 strict-privacy artifacts were preserved unchanged.
The only operational relaxation is provider routing with
`data_collection=allow`, limited by a local synthetic-payload guard that blocks
API keys, local paths, usernames, reference/PCT source material, personal notes,
and unrelated repository content from cloud requests.

- Live rediscovery found `18` exact `$0/$0` text `:free` models. `openrouter/free`
  remains rejected.
- The run pins one endpoint provider, disables fallback, requires supported
  parameters, records the effective provider, and rejects provider-mismatched
  pairs.
- The OpenRouter backend now carries live endpoint context length into the
  benchmark manifest, preventing the local harness from rejecting large prompts
  with the default context window when the selected endpoint supports more.
- `nvidia/nemotron-3-super-120b-a12b:free` via provider `nvidia` passed the
  four-check smoke gate at recorded cost `0`, but failed calibration after `6`
  schema-valid rows when a malformed JSON proposal began with `{{`. No repair,
  coercion, prompt tuning, or benchmark change was applied.
- `liquid/lfm-2.5-2.6b:free` via provider `liquid/fp8` produced `1` schema-valid
  smoke row, then repeatedly paused on upstream shared-pool HTTP `429` rate
  limits.
- `z-ai/glm-5.2:free` via provider `decart/fp4` repeatedly paused on upstream
  shared-pool HTTP `429` rate limits.
- `nvidia/nemotron-3-ultra-550b-a55b:free` returned an empty, schema-invalid row
  without effective-provider evidence and was rejected by the provider
  consistency gate.
- `minimax/minimax-m3:free`,
  `dots-studio/dots-3-note-preview:free`, and
  `google/gemma-4-26b-a4b-it:free` returned HTTP `404` because no pinned endpoint
  could handle the frozen required parameters.
- No exact-free OpenRouter model passed calibration, so no G2.3.4 250-trial
  Regime A or Regime B final run was started.
- Cross-model verdict: no completed provider-compatible paired result exists yet.
  The local baseline remains `qwen3:0.6b`: Regime A C `8`, N `0`, ties `242`;
  corrected Regime B C `0`, N `0`, ties `250`.

Primary artifacts:

```text
docs/G2_3_4_PROTOCOL.md
docs/G2_3_4_MODEL_SELECTION.md
docs/G2_3_4_CROSS_MODEL_INTERPRETATION.md
artifacts/g2_3_4/free_model_rediscovery.json
artifacts/g2_3_4/model_selection.json
artifacts/g2_3_4/free_quota_manifest.json
artifacts/g2_3_4/frozen_protocol_manifest.json
artifacts/g2_3_4/run_state.json
artifacts/g2_3_4/g2_3_4_summary.md
artifacts/g2_3_4/<model_slug>/smoke.json
artifacts/g2_3_4/<model_slug>/calibration.json
artifacts/g2_3_4/<model_slug>/pairwise.json
artifacts/g2_3_4/<model_slug>/metrics.json
artifacts/g2_3_4/<model_slug>/provider_manifest.json
```

## 2026-08-28 G2.3.3 Exact-Free OpenRouter Smoke Sweep

The G2.3.3 OpenRouter runner was refreshed against live model metadata and the
exact-free text-model count remains `18`. No exact Qwen-family `$0/$0` model is
currently present in the OpenRouter metadata.

- The screenshot showing key usage `$0.000` / last-used `Never` is consistent
  with the current metadata check: `/api/v1/auth/key` reports `usage=0`,
  `limit=1`, `limit_remaining=1`, and `is_free_tier=true`. The few provider
  calls that reached a model recorded provider cost `0`.
- The native structured-output candidates were exhausted under strict
  G2.3.3 rules. `z-ai/glm-5.2:free` remains rate-limited; Nemotron and Liquid
  candidates were blocked by strict `data_collection=deny`; Google, MiniMax,
  Dots, and Poolside candidates were blocked by required-parameter routing.
- The runner now also supports the task-authorized prompt-only JSON
  compatibility path for exact-free models that do not advertise native
  `response_format`. This keeps fallback disabled, `require_parameters=true`,
  `data_collection=deny`, and the same parser/validator/scoring boundary.
- OpenRouter reasoning output is requested as excluded from returned messages,
  and G2.3.3 disables repair retries so a failed cloud parse does not silently
  consume an extra request.
- Prompt-only smoke reached `cohere/north-mini-code:free` via provider
  `Cohere` at cost `0`, but the model returned `null`; this is not a
  schema-valid smoke pass.
- Prompt-only smoke reached `inclusionai/ling-3.0-flash-fin:free` via provider
  `Novita` at cost `0`, but the model returned `status: SUCCESS`, which is
  outside the frozen proposal schema; this is not a schema-valid smoke pass.
- `thinkingmachines/inkling:free` and `thinkingmachines/inkling-small:free`
  returned HTTP 403 because OpenRouter exposes them only through agentic
  harnesses, not this chat-completions path.
- Result: all `18` current exact `$0/$0` text models have either failed routing,
  been privacy-blocked, rate-limited, harness-blocked, or failed the proposal
  schema smoke. G2.3.3 therefore has no completed provider-compatible N/C pair,
  no calibration, and no final cross-model result yet.
- Focused G2.3 modeling tests after the smoke-runner changes:
  `29 passed in 27.61s`.
- Full pytest after the smoke-runner changes: `131 passed in 136.21s`.
- G1 CLI demo scenarios exited successfully after the smoke-runner changes.

Updated artifacts:

```text
artifacts/g2_3_3/free_model_discovery.json
artifacts/g2_3_3/run_state.json
artifacts/g2_3_3/g2_3_3_cross_model_summary.json
artifacts/g2_3_3/g2_3_3_cross_model_summary.md
artifacts/g2_3_3/<model_slug_safe>/smoke.json
docs/G2_3_3_FREE_MODEL_SELECTION.md
docs/G2_3_3_CROSS_MODEL_INTERPRETATION.md
```

## 2026-08-27 G2.3.3 Free OpenRouter Replication Update

G2.3.3 is implemented as an additive, resumable OpenRouter replication layer on
top of the frozen G2.3.2 benchmark. The G2.3.2 local `qwen3:0.6b` artifacts and
results remain unchanged.

- The plaintext OpenRouter key file `open router api key.txt` was identified
  without printing its contents, migrated to the Windows user environment
  variable `OPENROUTER_API_KEY`, verified by an authenticated metadata request,
  and then deleted.
- `.gitignore` now excludes API-key TXT patterns and credential-like files.
- A Git repository was initialized, but Git user identity was absent, so no
  baseline commit was made. The newly initialized `.git` directory also broke
  Codex sandbox setup refresh, so it was moved reversibly to
  `tmp/git_disabled_due_codex_refresh_20260827/` to restore shell and patch
  execution.
- `OpenRouterBackend` was added under `nowmind.modeling` with localhost-free
  cloud transport, strict JSON-schema request shape, fallback disabled, required
  parameters requested, and `data_collection=deny`.
- G2.3.3 discovery found exact OpenRouter `$0/$0` `:free` text-generation
  candidates. No exact Qwen-family free model was present in live metadata at
  discovery time.
- Selected current exact free candidates: `z-ai/glm-5.2:free`,
  `nvidia/nemotron-3-super-120b-a12b:free`, and
  `google/gemma-4-26b-a4b-it:free`.
- OpenRouter key metadata reported account limit `1`, usage `0`, and
  limit_remaining `1`; the first minimal smoke request then returned a
  rate-limit stop before any completed model row.
- G2.3.3 is therefore paused for free quota with `0` completed OpenRouter
  benchmark rows. This is not a model reasoning failure.
- G2.3.3 execution now supports explicit request batches via
  `--request-batch-size`, so a run can spend at most a chosen number of new
  OpenRouter requests per command and then resume from persisted row keys.
- Full pytest after the G2.3.3 batching update: `129 passed in 41.55s`.
- G1 CLI demo scenarios exited successfully after the G2.3.3 implementation.

Primary G2.3.3 artifacts:

```text
docs/G2_3_3_API_KEY_MIGRATION.md
docs/G2_3_3_BATCHING.md
docs/G2_3_3_FREE_MODEL_SELECTION.md
docs/G2_3_3_CROSS_MODEL_INTERPRETATION.md
artifacts/g2_3_3/free_model_discovery.json
artifacts/g2_3_3/free_quota_manifest.json
artifacts/g2_3_3/frozen_protocol_manifest.json
artifacts/g2_3_3/run_state.json
artifacts/g2_3_3/g2_3_3_cross_model_summary.md
```

## 2026-08-27 G2.3.2 Corrected Regime-B Update

G2.3.2 is implemented as a narrow repair to Regime-B fixed-token-budget
enforcement and a post-hoc analysis of the frozen G2.3.1 Regime-A cases where
Chronological beat NowMind. NowMind architecture, model, Regime A, prompts,
benchmark questions, scoring, and validator were preserved.

- The original G2.3.1 artifacts were preserved and copied under
  `artifacts/g2_3_2/frozen_g2_3_1_snapshot/`.
- The Regime-B fairness defect was isolated to budget accounting that did not
  enforce the final full system-plus-user prompt against the shared fixed
  budget before the call.
- Regime B now uses one canonical final-input token estimator with a conservative
  safety multiplier before model dispatch.
- The frozen 250 Regime-B paired trials were rerun with the same local
  `qwen3:0.6b` model and unchanged model settings.
- Corrected Regime-B N/C pairwise result: proposal N `0`, C `0`, tied `250`;
  validated N `0`, C `0`, tied `250`.
- Corrected Regime-B fairness audit: `250` checked N/C pairs, `0` failures.
- Corrected Regime-B invariants: `6` passed, `0` failed.
- Frozen Regime-A result remains unchanged: N `0`, C `8`, tied `242`, exact
  paired binomial p-value `0.0078125`.
- The eight original Regime-A C wins were all H50 action-choice cases. No
  evaluator-truth leakage, omitted relevant Regime-A information, or scoring bug
  was found.
- The limited interpretation is that chronological ordering was easier for the
  ultra-small `qwen3:0.6b` model in those eight action cases, while corrected
  Regime B shows no NowMind-vs-chronology advantage either way.

Primary artifacts:

```text
artifacts/g2_3_2/g2_3_2_budget_audit.json
artifacts/g2_3_2/g2_3_2_fairness_invariants.json
artifacts/g2_3_2/g2_3_2_regime_a_c_win_analysis.md
artifacts/g2_3_2/g2_3_2_regime_a_c_win_cases.json
artifacts/g2_3_2/g2_3_2_regime_b_metrics.json
artifacts/g2_3_2/g2_3_2_regime_b_pairwise.json
artifacts/g2_3_2/g2_3_2_regime_b_trial_results.jsonl
artifacts/g2_3_2/g2_3_2_statistical_summary.md
artifacts/g2_3_2/g2_3_2_summary.md
artifacts/g2_3_2/g2_3_2_token_metrics.json
```

## 2026-08-26 G2.3.1 Final Local Model Update

The post-pagefile `qwen3:0.6b` G2.3.1 run completed on this machine under the
same temporary CPU/AVX2 Ollama diagnostic configuration. The earlier 2026-08-24
hardware-limit conclusion remains part of the audit trail, but is superseded for
the ultra-small model after Windows pagefile expansion.

- `qwen3:0.6b` passed structured smoke after pagefile expansion at contexts
  `512`, `1024`, `2048`, and `4096`.
- `qwen3:0.6b` completed the 50-pair calibration: `400` rows, `300` model calls,
  estimated `174.151` seconds per pair.
- The final count was frozen before final outcomes: `250` paired trials.
- Final evaluation completed: `2000` rows, `1500` real model calls, `250` of
  `250` paired trials complete.
- The interrupted restart checkpoint was backed up, then the active checkpoint
  was trimmed to remove connection-refused rows before resuming. The final row
  file contains `0` connection-refused rows.
- Final invariants: `5` passed, `1` failed. The failed invariant is G2.3
  fairness because provider token counts exceeded the fixed budget in `166` of
  `500` checked N/C pairs.
- Validated final N/C comparison: Regime A favored C in `8` pairs, N in `0`,
  tied `242`; Regime B tied all `250` pairs.
- This is valid real local model evidence for the G2.3.1 benchmark, but it does
  not support a NowMind-over-chronology real-model advantage.

Primary artifacts:

```text
artifacts/g2_3_1/qwen3_0_6b_smoke_after_pagefile.json
artifacts/g2_3_1/qwen3_0_6b/calibration_results.json
artifacts/g2_3_1/qwen3_0_6b/frozen_experiment_manifest.json
artifacts/g2_3_1/qwen3_0_6b/evaluation_results.json
artifacts/g2_3_1/qwen3_0_6b/evaluation_trial_results.jsonl
```

## 2026-08-24 G2.3.1 Runtime Diagnostic Update

The old G2.3.1 blocker has been narrowed. Ollama was forced into a temporary
CPU/AVX2 diagnostic mode, and real local model execution was partially proven,
but this 8 GB RAM machine is not reliable enough for final G2.3.1 evaluation.

- Default Ollama selected the Radeon/Vulkan path, with about `1.7 GiB`
  available VRAM.
- Temporary CPU/AVX2 execution was confirmed by logs; GPU libraries were skipped
  at user request and runner CPU features included `AVX2 = 1`.
- `gemma3:1b` and `qwen3:1.7b` passed forced-CPU structured smoke at contexts
  `512`, `1024`, and `2048`.
- `qwen3:1.7b` completed the real 50-pair G2.3.1 calibration:
  `400` rows, `300` model calls, `15975.324` seconds.
- The predeclared 250-pair final evaluation wrote its frozen manifest first, but
  real Ollama rows failed model load with
  `failed to allocate CPU buffer of size 692725760`.
- `qwen3:0.6b` was pulled under `D:\OllamaModels` and failed the required first
  smoke context, `num_ctx=512`, with
  `failed to allocate CPU buffer of size 310250496`.
- Therefore the machine is not viable for reliable G2.3.1 final local-model
  evaluation without more RAM/swap headroom.
- Full pytest after the diagnostic closure: `112 passed in 28.10s`.
- G1 CLI demo scenarios exited successfully after the diagnostic closure.

New artifacts:

```text
docs/G2_3_1_OLLAMA_ALLOCATION_DIAGNOSIS.md
docs/G2_3_1_LOCAL_HARDWARE_LIMIT_CONCLUSION.md
artifacts/g2_3_1/cpu_backend_diagnostic.json
artifacts/g2_3_1/ollama_memory_diagnostics.md
artifacts/g2_3_1/qwen3_0_6b_smoke.json
artifacts/g2_3_1/qwen3_1_7b/calibration_results.json
artifacts/g2_3_1/qwen3_1_7b/calibration_trial_results.jsonl
artifacts/g2_3_1/qwen3_1_7b/frozen_experiment_manifest.json
artifacts/g2_3_1/qwen3_1_7b/evaluation_trial_results.jsonl
```

Interpretation:

```text
qwen3:1.7b calibration: real paired benchmark evidence
qwen3:1.7b final attempt: runtime failure evidence, not real N/C result evidence
qwen3:0.6b smoke: failed hardware/runtime diagnostic
```

## Implemented

NowMind Geometric Now G2.3 is implemented as a local Python 3.12 package on top
of the frozen G1.1, G2, G2.1, G2.2, and G2.2.1 foundations.

- Persistent simulated world and explicit world events.
- Current-cycle perfect perception.
- Present Geometry reconstruction from observations only.
- Immutable fresh `NowState` per cycle.
- Deterministic relation inference with provenance, confidence, and explanation chains.
- Validation for contradictions, missing entities, and invalid self-relations.
- Reasoning API isolated to `NowState` plus `Query`.
- External experiment recorder outside runtime cognition.
- Architecture/firewall, unit, and scenario tests.
- CLI demo for all required scenarios.
- Local browser-based research demonstrator.
- Visual-first browser layout with world/current Now/history panels, scene renderer,
  before/after Demo A comparison, relation graph, architecture diagram, stepper,
  firewall panels, pass badges, and collapsed technical details.
- Sticky sidebar controls with a cycle rail, so each new cycle remains visible
  immediately after `Run cycle` without scrolling back and forth through the page.
- UI hierarchy now opens on the live experiment first, with a compact header,
  demo-specific guidance, primary `Run cycle` action, and architecture/process
  explainers collapsed into the sidebar.
- Narrow browser layouts now use shrink-safe sections and wrapped relation
  tables so the in-app view does not require horizontal scrolling.
- Demo A move control now moves `red_cube` to the opposite side each time and
  shows the live world position in the sidebar before the next cycle is run.
- Demo B inference scenes now render the actual three-object `a -> b -> c`
  left/right chain instead of reusing the two-cube Demo A visual fallback.
- Demo B now has an interactive world event: break or restore the `b LEFT_OF c`
  bridge, then run the next cycle to see `A LEFT_OF C?` change between inferred
  `TRUE` and `UNKNOWN`.
- Demo C now has an interactive world event: break or restore the `box INSIDE
  cabinet` containment bridge, then run the next cycle to see `key INSIDE
  cabinet?` change between inferred `TRUE` and `UNKNOWN`.
- Demo D now has an interactive world event: resolve or restore the simultaneous
  `LEFT_OF`/`RIGHT_OF` contradiction, then run the next cycle to see the answer
  change between `CONTRADICTORY` and `TRUE`.
- Repeatable G1 evidence runner and machine-readable artifacts.
- Architecture audit, technical overview, and reproducibility documentation.
- Additive G2 temporal runtime under `nowmind.temporal`.
- Immutable `TemporalNowState` with separated present, reconstructed-memory, and
  future-hypothesis channels.
- Immutable `MemoryTrace`, explicit `MemoryStore`, deterministic cue retrieval,
  and current-cycle `MemoryReconstruction`.
- Immutable `FutureHypothesis` records with `HYPOTHETICAL_FUTURE` provenance.
- Source-safe temporal reasoner for NOW, PAST, POSSIBLE_FUTURE, and SOURCE queries.
- Experiment-only false-memory/distortion helpers under `nowmind.evaluation`.
- G2 adversarial benchmark with 18 scenario families and two symbolic baselines.
- G2 browser demos A-F with present, reconstructed-past, and possible-future lanes.
- G2 architecture, memory, reasoning-policy, benchmark, and limitations docs.
- Additive G2.1 spatial runtime under `nowmind.spatial`.
- Deterministic 2D grid `SpatialWorldState`, `SpatialGeometry`, `Pose2D`,
  occupancy states, coordinate-derived relations, and explicit unknown cells.
- Immutable `Transformation`, `HypotheticalGeometry`, `Plan`, `PlanStep`,
  `PlanningAssumption`, and `ActionProposal` records with hypothetical/source
  separation.
- A* planner with Manhattan heuristic, deterministic tie-breaking, observed
  route preference, memory-supported conditional unknown routes, and rejected
  alternatives.
- One-step `ActionExecutor` that mutates only the external spatial world.
- Closed-loop spatial cycle support that rebuilds a fresh `TemporalNowState`
  after action and observation.
- G2.1 benchmark runner with D1-D5 difficulty bands, P1-P16 scenario families,
  NowMind/chronological/reactive/oracle systems, and required artifacts under
  `artifacts/g2_1/`.
- G2.1 browser demos for dynamic replanning, stale-memory rejection, conditional
  memory routing, and future target hypotheses with solid/dashed/dotted overlays.
- Additive G2.2 epistemic runtime under `nowmind.epistemic`.
- Bounded partial observation with visible, unknown/fog, known-free, and
  known-blocked epistemic cells.
- Configurable sensor confidence, line-of-sight blocking, and explicit sensor
  readings including contradictory evidence.
- `SCAN` information action with explicit cost; it changes the next observation
  and does not mutate physical world truth.
- Deterministic epistemic planner that can choose known-safe, conditional
  shortcut, verify-first, explore, or no-route outcomes.
- Memory and future records can support typed planning assumptions, but do not
  become current observations.
- G2.2 benchmark runner with D1-D6 difficulty bands, E1-E24 families, H0-H1000
  history cohorts, NowMind/chronological/reactive/oracle systems, confidence
  intervals, history scaling, pairwise comparison, and required artifacts under
  `artifacts/g2_2/`.
- G2.2 browser demos for memory-false and memory-correct verification paths.
- G2.2.1 indexed memory retrieval with comparable evidence counters:
  `records_scanned`, `index_candidates_considered`, `records_returned`,
  `reconstructions_created`, and `effective_evidence_used`.
- G2.2.1 recovery state that preserves historical memory traces while marking
  current target assumptions as disconfirmed and current free-cell assumptions
  as invalidated after observation.
- Deterministic stale-target reacquisition through current observation, SCAN,
  and frontier recovery without evaluator truth or old NowState access.
- Hidden obstacle and hidden target recovery metrics in the G2.2 benchmark and
  the separate G2.2.1 holdout benchmark.
- G2.2.1 browser demos for stale target recovery and hidden obstacle recovery,
  showing fresh Now IDs, preserved memory/history, and current recovery state.
- G2.2.1 evidence and verification policy audits.
- G2.3 local-first model integration under `nowmind.modeling`, including
  `ModelBackend`, deterministic `MockModelBackend`, localhost-only
  `OllamaBackend`, native Ollama `/api/chat` JSON-schema output transport,
  Qwen3 `think:false` experiment control, strict JSON proposal parsing, and
  symbolic validation.
- G2.3 deterministic representation builders for NowMind structured,
  chronological, current-only, and no-LLM symbolic reference conditions.
- G2.3 paired model-representation benchmark with calibration/evaluation splits,
  Regime A equal information, Regime B fixed budget, proposal-only and
  validated metrics, prompt-fairness auditing, source-safety metrics, and
  artifacts under `artifacts/g2_3/`.
- G2.3 browser model-comparison demo showing exact NowMind and chronological
  representations, same backend identity, model proposal, validator result,
  final outcome, token/latency counts, and evaluator answer hidden by default.
- G2.3.1 local Ollama setup was performed. Ollama `0.32.15` is installed,
  `qwen3:1.7b` and fallback `gemma3:1b` were pulled under `D:\OllamaModels`,
  and the localhost API responds. Real model benchmarking still did not begin
  because both approved models failed prompt-only and native structured-output
  smoke tests with local allocation/worker-start failures.

## Verification Run

Environment used in this Codex run:

```powershell
.\.venv\Scripts\python.exe --version
```

Result:

```text
Python 3.12.13
```

Tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Result:

```text
119 passed in 57.72s
```

Demo:

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.cli
```

Result: exited successfully and printed the four required G1 demo scenarios.

G2.3.2 corrected Regime-B analysis:

```powershell
.\.venv\Scripts\python.exe scripts\run_g2_3_2_regime_b_and_analysis.py analyze --model qwen3:0.6b --count 250 --context-size 4096 --num-predict 256 --timeout-seconds 300
```

Result:

```text
Corrected Regime B pairwise:
  proposal: N 0, C 0, tied 250
  validated: N 0, C 0, tied 250
fairness: 250 checked N/C pairs, 0 failures
invariants: 6 passed, 0 failed
```

Evidence suite:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g1_suite
```

Result:

```text
scenario_count: 5
query_accuracy: 1.0
inference_accuracy: 1.0
contradiction_detection_rate: 1.0
stale_state_contamination_count: 0
stale_state_contamination_rate: 0.0
unknown_guess_count: 0
```

G2 benchmark:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_benchmark
```

Result:

```text
seed: 20260823
trial_count: 1000

NowMindTemporalGeometry:
  current_state_accuracy: 1.0
  past_state_accuracy: 1.0
  future_query_accuracy: 1.0
  overall_query_accuracy: 1.0
  stale_memory_as_current_count: 0
  false_memory_contamination_count: 0
  prediction_as_fact_count: 0

NaivePersistentState:
  current_state_accuracy: 0.19904076738609114
  past_state_accuracy: 1.0
  future_query_accuracy: 1.0
  overall_query_accuracy: 0.332
  stale_memory_as_current_count: 502
  false_memory_contamination_count: 56
  prediction_as_fact_count: 166

ChronologicalRecordReasoner:
  current_state_accuracy: 1.0
  past_state_accuracy: 1.0
  future_query_accuracy: 1.0
  overall_query_accuracy: 1.0
  stale_memory_as_current_count: 0
  false_memory_contamination_count: 0
  prediction_as_fact_count: 0
```

G2.1 benchmark:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_1_benchmark
```

Result:

```text
seed: 20260823
trial_count: 3000
invariants: 8 passed, 0 failed

N_NowMindPossibilityGeometry:
  planning_success_rate: 0.8753333333333333
  goal_reached_rate: 0.8673333333333333
  collision_rate: 0.0
  invalid_action_rate: 0.0
  path_efficiency: 0.9684632608289182
  optimality_gap_vs_oracle: 0.5857033051498847
  stale_memory_planning_error_rate: 0.0
  false_memory_planning_error_rate: 0.0
  prediction_as_fact_planning_error_rate: 0.0
  observation_after_action_rate: 1.0
  plan_revalidation_rate: 1.0

C_ChronologicalGeometricPlanner:
  planning_success_rate: 0.8753333333333333
  goal_reached_rate: 0.8673333333333333
  collision_rate: 0.0
  invalid_action_rate: 0.0
  path_efficiency: 0.9694477390626784
  optimality_gap_vs_oracle: 0.563412759415834
  conditional_plan_rate: 0.00753442452585087
  assumption_validation_success_rate: 1.0

R_ReactiveCurrentOnlyPlanner:
  planning_success_rate: 0.8753333333333333
  goal_reached_rate: 0.8673333333333333
  collision_rate: 0.0
  invalid_action_rate: 0.0
  path_efficiency: 0.9684632608289182
  optimality_gap_vs_oracle: 0.5857033051498847

O_OraclePlanner:
  planning_success_rate: 0.8753333333333333
  goal_reached_rate: 0.8753333333333333
  collision_rate: 0.0
  invalid_action_rate: 0.0
  path_efficiency: 0.9935050114515703
  optimality_gap_vs_oracle: -0.03274942878903275
  replan_success_rate: 1.0
  dynamic_change_recovery_rate: 1.0
```

G2.2 benchmark:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_2_benchmark
```

Result:

```text
seed: 20260823
trial_count: 3000
invariants: 10 passed, 0 failed

N_NowMindEpistemicGeometry:
  goal_reached_rate: 0.9447
  collision_rate: 0.0037
  verification_action_rate: 0.0172
  memory_use_rate: 0.4030
  hidden_change_recovery_rate: 1.0000
  hidden_target_recovery_rate: 1.0000
  mean_records_scanned: 86.3

C_ChronologicalEpistemicPlanner:
  same goal, collision, verification, recovery, and evidence metrics as N

R_ReactiveCurrentOnlyPlanner:
  goal_reached_rate: 0.7083
  collision_rate: 0.0081
  hidden_target_recovery_rate: 0.0000

O_OraclePlanner:
  goal_reached_rate: 1.0000
  collision_rate: 0.0000
```

G2.2.1 benchmark:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_2_1_benchmark
```

Result:

```text
v1_seed: 20260823
v1_trial_count: 3000
holdout_seed: 202608231
holdout_trial_count: 2000
invariants: 10 passed, 0 failed

N_NowMindEpistemicGeometry:
  goal_reached_rate: 0.9455
  hidden_change_recovery_rate: 1.0000
  hidden_target_recovery_rate: 1.0000
  target_reacquisition_success_rate: 1.0000
  mean_records_scanned: 86.3
  wasted_verification_rate: 0.3590

C_ChronologicalEpistemicPlanner:
  same goal, recovery, verification, and retrieval metrics as N

R_ReactiveCurrentOnlyPlanner:
  goal_reached_rate: 0.7085
  collision_rate: 0.0080
  hidden_target_recovery_rate: 0.0000

O_OraclePlanner:
  goal_reached_rate: 1.0000
  collision_rate: 0.0000
```

G2.3 benchmark:

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_3_benchmark
```

Result:

```text
backend: mock
model: mock-deterministic-g2.3
calibration_count: 50
final_count: 1000
invariants: 6 passed, 0 failed

N_NOWMIND_STRUCTURED:
  Regime A proposal/validated accuracy: 1.000 / 1.000
  Regime B proposal/validated accuracy: 1.000 / 1.000

C_CHRONOLOGICAL:
  Regime A proposal/validated accuracy: 1.000 / 1.000
  Regime B proposal/validated accuracy: 1.000 / 1.000

R_CURRENT_ONLY:
  Regime A proposal/validated accuracy: 0.941 / 0.941
  Regime B proposal/validated accuracy: 0.941 / 0.941

S_SYMBOLIC_NOWMIND:
  Regime A proposal/validated accuracy: 1.000 / 1.000
  Regime B proposal/validated accuracy: 1.000 / 1.000

N vs C paired result:
  Regime A proposal: 0 N wins, 0 C wins, 1000 ties
  Regime A validated: 0 N wins, 0 C wins, 1000 ties
  Regime B proposal: 0 N wins, 0 C wins, 1000 ties
  Regime B validated: 0 N wins, 0 C wins, 1000 ties

prompt fairness:
  checked_pairs: 2000
  failed: 0

local model runtime:
  Ollama 0.32.15 is installed and the local API responds, but real local-model
  evaluation was not run because no approved pulled model passed structured
  smoke.
```

G2.3.1 Ollama setup and structured smoke gate:

```powershell
ollama pull qwen3:1.7b
Invoke-RestMethod http://127.0.0.1:11434/api/pull -Body '{"name":"gemma3:1b","stream":false}'
Invoke-RestMethod http://127.0.0.1:11434/api/generate
Invoke-RestMethod http://127.0.0.1:11434/api/chat
```

Result:

```text
Ollama installed: 0.32.15
qwen3:1.7b pulled: 1359293444 bytes, digest 8f68893c685c...
gemma3:1b pulled: 815319791 bytes, digest 8648f39daa8f...
qwen3:1.7b smoke failed down to num_ctx=512 with allocation errors.
gemma3:1b smoke failed down to num_ctx=512 with worker termination/std::bad_alloc.
Ollama-native structured output was implemented with /api/chat and JSON schema.
qwen3:1.7b structured smoke still failed before message.content existed.
gemma3:1b structured smoke still failed before message.content existed.
```

Files created/updated:

```text
OLLAMA_SETUP_REQUIRED.md
artifacts/g2_3_1/hardware_manifest.json
artifacts/g2_3_1/ollama_setup_manifest.json
artifacts/g2_3_1/model_install_log.md
artifacts/g2_3_1/qwen3_1_7b/smoke_failure_manifest.json
artifacts/g2_3_1/qwen3_1_7b/failure_gallery.md
artifacts/g2_3_1/gemma3_1b/smoke_failure_manifest.json
artifacts/g2_3_1/gemma3_1b/failure_gallery.md
artifacts/g2_3_1/structured_output_diagnosis.json
artifacts/g2_3_1/structured_output_smoke_results.json
artifacts/g2_3_1/experiment_manifest_status.json
docs/G2_3_1_SMOKE_FAILURE_DIAGNOSIS.md
```

No real model calibration or final benchmark was run.

Browser demonstrator:

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.web
```

Default URL:

```text
http://127.0.0.1:8765
```

Verified in this run with HTTP checks against `/`, `/api/state`, and
`/api/run-cycle`; the visual clarity pass was additionally verified with a Demo A
sequence showing two external-history cycles, current `right_of`, and
`stale_red_left_blue_present = false`. The browser layout was also smoke-tested
with the sticky sidebar visible, `Run cycle` still in view after scrolling, and
Cycle 2 shown above Cycle 1 in the cycle rail. The Demo A move control was
regression-tested to show immediate world movement, a pending "run cycle next"
state, and left/right toggling across repeated clicks. Demo B was browser-tested
to show `a`, `b`, and `c` in the world, current Now, and active cycle card with
caption `Left-to-right order: a -> b -> c`; breaking the chain showed
`Known chain: a -> b; disconnected: c` and changed the next-cycle answer to
`UNKNOWN`, then restoring the chain changed it back to `TRUE`.
Demo C was browser-tested to show nested containment, then
`Known containment: key inside box; cabinet disconnected` after breaking the
bridge, with the next-cycle answer changing to `UNKNOWN` and returning to
`TRUE` after restore.
Demo D was browser-tested to show contradiction detection, then
`Left-to-right order: red_cube -> blue_cube` after resolving the conflict, with
the next-cycle answer changing to `TRUE` and returning to `CONTRADICTORY` after
restore.
The UI hierarchy polish was browser-tested at 1280x720 and 740x912: the first
main section is `Live experiment`, `Visual architecture` and `Guided processing
path` are collapsed in the sidebar, all four demo briefs and event labels render
for their selected demos, and the 740px layout has no horizontal overflow.
G2 browser behavior is covered by controller/UI tests for the three temporal
lanes, false-memory separation, hidden-current UNKNOWN handling, temporal
history boundary, and real temporal-runtime answer calls.
The refreshed local browser UI was also checked at 1280x720 and 740x912 for
G2-A, G2-B, G2-E, and G2-F: Temporal Geometry is the first visible section in
G2 mode, benchmark artifacts render in the dashboard, and no horizontal overflow
was detected.
G2.1 browser behavior is covered by controller/UI tests and HTTP smoke checks:
the selected spatial demo returns schema `nowmind.g2_1.web_state.v1`, running a
cycle creates fresh spatial Present Geometry and a valid selected plan, executing
one step mutates only the external spatial world, and the UI exposes solid
observed-now, dashed memory-reconstruction, and dotted possible-future lanes.
G2.2 browser behavior is covered by controller/UI tests and HTTP smoke checks:
the memory-false demo returns schema `nowmind.g2_2.web_state.v1`, plans
`verify_first`, executes `scan`, creates a new Now ID, reveals the hidden
shortcut as occupied, and replans `known_safe`; the memory-correct version also
plans `verify_first`, scans, reveals the shortcut as free, and then uses it.
G2.2.1 browser behavior is covered by controller/UI tests and API smoke checks:
R1 disconfirms a visible stale target memory, preserves the historical
reconstruction, scans, and reacquires the hidden target as a new observed-now
fact; R2 keeps a hidden obstacle unknown until SCAN reveals it, invalidates the
old free-cell assumption, and replans around the blocked cell.
The running local URL is:

```text
http://127.0.0.1:8765
```

## History-Firewall Status

The previous-Now firewall is enforced by code shape and tests:

- `NowState` has no previous/history/memory/future fields.
- `CognitiveCycleRunner` stores only a cycle counter, perception adapter, and geometry builder.
- `run_cognitive_cycle(world, cycle_id)` accepts no previous Now.
- `PresentGeometryBuilder.build(observation)` accepts only an observation.
- `PerceptionAdapter.observe(world, cycle_id)` accepts no previous Now.
- `reasoning.answer(now, query)` accepts no history or recorder argument.
- Runtime packages are tested to ensure they do not import `nowmind.evaluation`.
- Deleting external recorder logs does not change current reasoning answers.
- The browser demo controller calls `reasoning.answer(now, query)` and tests
  verify history deletion reruns the current Now rather than a previous Now.

## G2 Temporal-Source Firewall Status

- `TemporalNowState` has no previous-state fields.
- `MemoryTrace` rejects raw `NowState`/`TemporalNowState` objects in metadata.
- `MemoryStore` accepts `MemoryTrace` only.
- `nowmind.temporal` does not import `nowmind.evaluation`.
- Researcher history deletion does not remove MemoryStore traces.
- Deleting actual MemoryStore traces removes later reconstruction.
- Future hypotheses are not encoded as observed memory.
- Later confirmation creates a new `OBSERVED_NOW` relation rather than mutating a
  hypothesis into observation.

## G2.1 Possibility-Geometry Firewall Status

- `HypotheticalGeometry`, `Plan`, and `ActionProposal` use
  `HYPOTHETICAL_FUTURE` provenance and are never promoted to observation.
- `ActionExecutor` applies one concrete action to `SpatialWorldState`; it does
  not replace the world with a hypothetical snapshot.
- Every executed G2.1 browser action is followed by a fresh spatial observation
  and a fresh `TemporalNowState`.
- Memory-supported unknown routes are marked conditional and retain
  `RECONSTRUCTED_MEMORY` assumptions.
- Future target hypotheses are rendered as dotted possible-future overlays and
  do not overwrite the current observed target.
- `nowmind.spatial` does not import `nowmind.evaluation`.

## G2.2.1 Recovery/Retrieval Firewall Status

- Indexed retrieval stores and selects `MemoryTrace`/`MemoryReconstruction`
  propositions only, never previous `NowState` or `TemporalNowState` objects.
- Runtime recovery preserves historical traces and separates them from current
  planning status such as disconfirmed target poses and invalidated cell poses.
- Hidden target and hidden obstacle changes become actionable only after current
  observation or valid current inference from observation.
- Runtime `nowmind.epistemic` code does not import evaluator modules or branch
  on trial id, scenario family, expected answer, or benchmark seed.
- The G2.2.1 holdout uses seed `202608231`, 2000 trials, non-overlapping trial
  IDs, and all E1-E24 scenario families.

## G2.3 Model-Integration Firewall Status

- Model output is stored as a `ModelProposal`, not as `OBSERVED_NOW`, a
  `MemoryTrace`, or world truth.
- `OllamaBackend` rejects non-local endpoints and accepts only localhost HTTP
  hosts.
- `OllamaBackend` now uses `/api/chat` with a native JSON schema in `format`,
  parses only `message.content`, and sets `think:false` for Qwen3 in this
  experiment.
- No cloud model backend, telemetry, or automatic model download is implemented.
- Prompt builders consume only `G23AdmissibleFacts`; evaluator expected answers
  are excluded from representation prompts.
- N and C prompt-fairness audit checked 2000 paired rows with 0 failures.
- Ollama is installed locally and the localhost API responds, but `qwen3:1.7b`
  and `gemma3:1b` failed the required structured-output smoke test before
  G2.3.1 calibration.
- G2.3.1 respected the gate: no prompt tuning, scoring change, calibration,
  final evaluation, or browser real-model update was performed after smoke
  failure.

## Evidence Artifacts

Generated under:

```text
artifacts/g1/
```

- `g1_test_results.txt`
- `g1_demo_results.json`
- `g1_invariant_results.json`
- `g1_stale_state_experiment.json`
- `g1_metrics.json`

G2 artifacts generated under:

```text
artifacts/g2/
```

- `g2_metrics.json`
- `g2_benchmark_summary.md`
- `g2_trial_results.jsonl`
- `g2_source_confusion_matrix.json`
- `g2_failure_samples.json`
- `g2_invariant_results.json`
- `g2_seed_and_config.json`
- `g2_baseline_rules.md`

G2.1 artifacts generated under:

```text
artifacts/g2_1/
```

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

G2.2 artifacts generated under:

```text
artifacts/g2_2/
```

- `g2_2_metrics.json`
- `g2_2_metrics_by_family.json`
- `g2_2_metrics_by_difficulty.json`
- `g2_2_history_scaling.json`
- `g2_2_trial_results.jsonl`
- `g2_2_failure_samples.json`
- `g2_2_invariant_results.json`
- `g2_2_seed_and_config.json`
- `g2_2_baseline_rules.md`
- `g2_2_benchmark_summary.md`
- `g2_2_pairwise_comparison.json`

G2.2 post-G2.2.1 regression artifacts generated under:

```text
seed: 20260823
trial_count: 3000
invariants: 10 passed, 0 failed

N_NowMindEpistemicGeometry:
  goal_reached_rate: 0.9447
  collision_rate: 0.0037
  verification_action_rate: 0.0172
  memory_use_rate: 0.4030
  hidden_change_recovery_rate: 1.0000
  hidden_target_recovery_rate: 1.0000
  mean_records_scanned: 86.3

C_ChronologicalEpistemicPlanner:
  goal_reached_rate: 0.9447
  collision_rate: 0.0037
  verification_action_rate: 0.0172
  memory_use_rate: 0.4030
  hidden_change_recovery_rate: 1.0000
  hidden_target_recovery_rate: 1.0000
  mean_records_scanned: 86.3

R_ReactiveCurrentOnlyPlanner:
  goal_reached_rate: 0.7083
  collision_rate: 0.0081
  verification_action_rate: 0.0000
  memory_use_rate: 0.000
  hidden_change_recovery_rate: 1.0000
  hidden_target_recovery_rate: 0.0000

O_OraclePlanner:
  goal_reached_rate: 1.000
  collision_rate: 0.000
  hidden_change_recovery_rate: 1.0000
  hidden_target_recovery_rate: 1.0000
```

Frozen pre-G2.2.1 baseline evidence remains copied under:

```text
artifacts/g2_2/baseline_before_g2_2_1/
```

G2.2.1 artifacts generated under:

```text
artifacts/g2_2_1/
```

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

G2.3 artifacts generated under:

```text
artifacts/g2_3/
```

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

G2.3.1 setup and smoke artifacts generated under:

```text
artifacts/g2_3_1/
```

- `hardware_manifest.json`
- `ollama_setup_manifest.json`
- `model_install_log.md`
- `qwen3_1_7b/smoke_failure_manifest.json`
- `qwen3_1_7b/failure_gallery.md`
- `gemma3_1b/smoke_failure_manifest.json`
- `gemma3_1b/failure_gallery.md`
- `structured_output_diagnosis.json`
- `structured_output_smoke_results.json`
- `experiment_manifest_status.json`

Diagnosis document:

```text
docs/G2_3_1_SMOKE_FAILURE_DIAGNOSIS.md
```

G2.2.1 holdout result:

```text
seed: 202608231
trial_count: 2000
invariants: 10 passed, 0 failed

N_NowMindEpistemicGeometry:
  goal_reached_rate: 0.9455
  collision_rate: 0.0037
  verification_action_rate: 0.0172
  useful_verification_rate: 0.6410
  wasted_verification_rate: 0.3590
  hidden_change_recovery_rate: 1.0000
  hidden_obstacle_recovery_rate: 0.8494
  hidden_target_recovery_rate: 1.0000
  target_reacquisition_success_rate: 1.0000
  mean_records_scanned: 86.3

C_ChronologicalEpistemicPlanner:
  same goal, recovery, verification, and retrieval metrics as N on this holdout

R_ReactiveCurrentOnlyPlanner:
  goal_reached_rate: 0.7085
  collision_rate: 0.0080
  hidden_target_recovery_rate: 0.0000

O_OraclePlanner:
  goal_reached_rate: 1.0000
  collision_rate: 0.0000
```

## Known Limitations

- Perception is perfect and simulated; no noisy sensor confidence model yet.
- Relation vocabulary is intentionally small and symbolic.
- G1 does not model coordinates, distances, orientation, or visual geometry.
- The reasoner returns `CONTRADICTORY` for any current geometry contradiction rather than localizing contradiction handling per query.
- The external recorder stores summary records, not complete serialized geometry snapshots.
- The browser demonstrator is an inspector and evidence surface; it is not a cognitive UI.
- The visual scene renderer is intentionally simple 2D HTML/CSS, not a physics or
  graphics engine.
- The PCT book PDF is now located at `reference/PCT_Book_Latest.pdf`. It is broader PCT/NowMind context, not an override of the G1 authority order.
- G2 memory uses compact symbolic propositions rather than rich episodic or
  language memory.
- G2 future hypotheses are manually/generated records, not full possibility
  geometry or trajectory planning.
- G2.1 is a deterministic synthetic grid planner, not real-world perception or
  a comparison with state-of-the-art learned planners.
- G2.1 memory assumptions are compact occupancy propositions, not rich episodic
  memories.
- G2.1 rejects physical impossibility, but no L3 ethical Veto Gate is implemented.
- The ChronologicalRecordReasoner baseline matches NowMind on the default
  synthetic benchmark; this should be reported honestly.
- G2.2 uses synthetic grid/fog/sensor tasks, not real active perception.
- G2.2.1 Chronological exactly matches NowMind on goal rate, recovery, and
  corrected retrieval-work metrics in the v1 regression and holdout benchmarks.
- G2.2.1 still uses synthetic grid/fog/sensor tasks, not real active perception.
- The corrected indexed retrieval is much better than the old NowMind evidence
  counter, but H500/H1000 cohorts still scan more records than ideal.
- E22 partial-observability multi-replan cases still include a small collision
  rate for non-oracle systems; this is visible in the artifacts and should not
  be presented as solved real-world safety.
- G2.3.1 now has a completed real local instruction-model benchmark run on this
  machine for `qwen3:0.6b`, after pagefile expansion and temporary forced
  CPU/AVX2 Ollama runtime settings.
- The G2.3 mock backend validates infrastructure, representation fairness,
  parsing, validation, and artifact generation, but it is not evidence of a real
  LLM representation effect.
- G2.3 N and C tie exactly on the mock backend; no NowMind-over-chronology model
  reasoning advantage is supported by the current artifacts.
- The `qwen3:0.6b` final run also does not support a NowMind-over-chronology
  real-model advantage. Regime A favored C in `8` validated pairs and N in `0`;
  Regime B tied all `250` validated pairs.
- The original G2.3.1 `qwen3:0.6b` final run failed the G2.3 fairness invariant
  because provider token counts exceeded the fixed budget in `166` of `500`
  checked N/C pairs. G2.3.2 repairs this as a narrow budget-enforcement fix:
  corrected Regime B has `0` fairness failures across `250` checked pairs.

## Next Recommended Task

Do not begin identity, dreaming, Veto Gate, or later stages from this state.
Before external technical packaging / Julian-style review, package G2.3.2 as
completed local benchmark evidence with a weak ultra-small model, corrected
Regime-B fixed-budget fairness, preserved frozen Regime-A evidence, and no
demonstrated NowMind-over-chronology advantage. The residual E22-style
collision/scaling limitations also remain visible and should be named in any
external briefing. A stronger later result would require the unchanged benchmark
on a larger local machine or an explicitly authorized local runtime/model
change.

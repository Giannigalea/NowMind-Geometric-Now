# SIXTEENTH CODEX TASK — Freeze Model Work, Initialize Git, and Build the Full-G Research Package

## Mission

The project must remain **100% free** from this point onward.

Do not use:
- paid OpenRouter models
- paid APIs
- cloud services that may incur charges
- subscription-only inference services
- commercial credits

Do not make further OpenRouter model calls during this task.

Freeze model-integration work at the current state:

```text
G2.3.2:
Local qwen3:0.6b real-model benchmark completed.

Regime A:
  Chronological wins = 8
  NowMind wins = 0
  ties = 242

Regime B:
  Chronological wins = 0
  NowMind wins = 0
  ties = 250

G2.3.3:
Exact-free OpenRouter replication blocked under strict privacy/schema constraints.

G2.3.4:
Privacy routing relaxed for synthetic benchmark data only.
No current exact-free model passed calibration-valid replication.
```

Do not reinterpret these results.

Do not change NowMind to make the results look better.

This task has three goals:
1. initialize proper Git/version-control state;
2. freeze and consolidate the scientific evidence;
3. build a coherent Full-G research demonstrator/reviewer package from G1 through G2.3.4.

## 1. No more model experimentation in this task

Do not:
- call OpenRouter
- pull new Ollama models
- install alternate LLM runtimes
- tune prompts
- alter frozen trial results
- create new model-comparison claims

The current model-evidence status is final for this milestone.

## 2. Initialize Git safely

The project currently reports that no active `.git` repository exists.

Initialize Git in the true project root.

Before `git add`, create/update `.gitignore` to exclude at minimum:

```text
.env
*.env
*secret*
*api_key*
*apikey*
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
dist/
build/
*.log
.DS_Store
Thumbs.db
```

Also exclude:
- any local OpenRouter key file if a filename reference remains
- local model caches
- temporary Ollama/OpenRouter runtime files
- machine-specific temporary artifacts

Do NOT exclude scientific benchmark artifacts unless they contain secrets or are excessively large/generated transiently.

Run a secret scan before commit.

Confirm:
- no OpenRouter API key
- no API secret
- no personal credential
- no plaintext token
- no user/host serial identifiers

If Git `user.name` / `user.email` are already configured:
- create a baseline commit with message `Freeze Full-G baseline through G2.3.4`

If Git identity is not configured:
- do not invent identity
- initialize repository
- stage safely if appropriate
- report the exact commands Jonathan must run later

## 3. Freeze milestone

Create:

`docs/FULL_G_MILESTONE_FREEZE.md`

State that the Full-G milestone includes:

```text
G1       Present Geometry
G2       Temporal Geometry
G2.1     Possibility Geometry
G2.2     Epistemic Geometry
G2.2.1   Epistemic Recovery & Retrieval Efficiency
G2.3     Model Integration Infrastructure
G2.3.1   Real Local Model Evaluation
G2.3.2   Regime-B Fairness Repair
G2.3.3   Exact-Free OpenRouter Replication Attempt
G2.3.4   Free Provider-Compatible Replication Attempt
```

State explicitly that this milestone does NOT yet include:
- identity architecture
- dreaming
- phenomenology claims
- sentience claims
- survival drive
- quantum consciousness
- Geometric Veto unless already implemented elsewhere
- general LLM superiority

## 4. Build a single scientific results summary

Create:

`docs/FULL_G_RESULTS_SUMMARY.md`

Summarize each stage with:
- purpose
- experimental setup
- headline result
- limitations
- what changed in the next stage

Required results to preserve:

### G1
- stale-state contamination = 0
- deterministic architectural proof only
- no superiority claim

### G2
- source separation succeeds
- NaivePersistentState fails badly
- Chronological control matches NowMind
- source separation is necessary but not uniquely NowMind

### G2.1
- spatial possibility planning works
- Reactive and Chronological controls often match
- temporal memory mostly ornamental at this point

### G2.2
- partial observation exposes retrieval/recovery weaknesses
- N/C goal about 0.5 before fixes
- retrieval inefficiency and hidden-change recovery problems documented

### G2.2.1
- recovery/retrieval architecture substantially improved
- holdout N goal about 0.945
- N and C remain tied on corrected retrieval metrics
- Reactive weaker
- remaining residual failure documented

### G2.3
- model backend/fairness infrastructure validated
- mock model only
- no real-model evidence

### G2.3.1/G2.3.2
- qwen3:0.6b completed real benchmark
- Regime A: C 8 / N 0 / ties 242
- Regime B corrected: all 250 ties
- no NowMind-over-chronology advantage
- tiny-model formatting/action/source weakness appears plausible
- result limited to one very small model

### G2.3.3/G2.3.4
- free OpenRouter infrastructure explored honestly
- no calibration-valid exact-free model available under frozen constraints
- no cloud cross-model evidence produced
- stop condition reached

## 5. Create a research claims boundary

Create:

`docs/FULL_G_CLAIMS_AND_NONCLAIMS.md`

Allowed claims should be narrow, for example:
- NowMind can enforce fresh-state reconstruction without stale-state carryover.
- Temporal source separation can prevent stale memory or prediction from being treated as present fact.
- Geometric/epistemic planning can support explicit uncertainty, conditional assumptions, replanning, and recovery.
- The architecture is inspectable and source-aware.
- Symbolic controls demonstrate that many benefits are not unique to the NowMind representation.
- Real-model evidence from qwen3:0.6b does not show a NowMind reasoning advantage over chronology.

Forbidden claims:
- consciousness proved
- sentience
- phenomenal awareness
- identity continuity proved
- model superiority in general
- quantum consciousness
- NowMind is a person
- NowMind has rights/feelings
- NowMind outperforms conventional AI generally

## 6. Create the reviewer narrative

Create:

`docs/FULL_G_REVIEWER_NARRATIVE.md`

Target audience:
- technically literate AI researcher
- cognitive-architecture researcher
- geometric-reasoning researcher
- Sophontic/Julian-style technical reader

Tone:
- engineering/research first
- philosophy second
- no consciousness hype

Suggested narrative:
1. Problem: conventional agents often mix current observation, recalled information, inferred information, and predicted futures.
2. Hypothesis: reconstruct a fresh explicit present-state geometry every cycle and keep source semantics visible.
3. Architecture: World -> Observation -> Present Geometry -> Temporal/Epistemic Geometry -> Possibility Geometry -> Action -> World -> New Now.
4. Experiments: progressively harder baselines and partial-observability tasks.
5. Findings: source correctness, recovery, inspectability, but no demonstrated LLM accuracy advantage yet.
6. Negative results: competent chronology frequently matches NowMind; tiny real model slightly preferred chronology in Regime A.
7. Research question: whether explicit geometric/state provenance helps more capable models or different reasoning systems.

Do not lead with consciousness.

## 7. Build one clear architecture diagram specification

Create:

`docs/FULL_G_ARCHITECTURE_DIAGRAM_SPEC.md`

Use this conceptual structure:

```text
Physical World
      |
      v
Observation_t
      |
      v
Present Geometry_t
      |
      +---------------------+
      |                     |
      v                     v
Memory Reconstruction   Current Epistemic State
      |                     |
      +----------+----------+
                 |
                 v
          Temporal NowState
                 |
                 v
       Possibility Geometry
                 |
                 v
        Planner / Reasoner
                 |
                 v
              Action
                 |
                 v
          Physical World
                 |
                 v
             New Now
```

Important visual rule:
- no arrow from previous NowState directly into new NowState
- memory enters only through reconstruction
- hypothetical futures must be marked hypothetical
- external experiment history must remain outside the reasoning loop

## 8. Consolidate the browser demonstrator

Do not redesign the entire app.

Create a top-level reviewer mode/page with:
1. Present Geometry
2. Temporal Source Separation
3. Possibility Geometry
4. Epistemic Recovery
5. Real-Model Comparison
6. Full-G Results

Each section should show:
- one clear scenario
- current geometry/state
- source labels
- what changed
- answer/action
- why result matters
- relevant benchmark metric

No cloud calls.
Browser must work offline/local.

## 9. Add a "What the demo does NOT prove" panel

Show visibly:

```text
This demonstrator does not prove:
- consciousness
- sentience
- phenomenal experience
- general model superiority
- quantum consciousness
```

Also show:

```text
Real-model result to date:
qwen3:0.6b did not show a NowMind accuracy advantage over chronology.
```

## 10. Create reproducibility entry point

Create:

`REPRODUCE_FULL_G.md`

Include:
- Python version
- environment setup
- dependency install
- test command
- G1 demo command
- G2/G2.1/G2.2/G2.2.1 benchmark commands
- G2.3 mock command if useful
- local qwen3:0.6b reproduction only if the model is already installed
- no paid/cloud requirement
- browser reviewer demo start command

Do not require OpenRouter.

## 11. Create one-command local reviewer launcher

Create a Windows-friendly script such as:

`run_full_g_demo.ps1`

It should:
- verify Python environment
- start local browser app
- print local URL
- never call cloud services
- never require OpenRouter key
- fail clearly if dependencies are missing

## 12. Consolidate benchmark tables

Create:

```text
artifacts/full_g/full_g_benchmark_table.csv
artifacts/full_g/full_g_benchmark_table.md
```

Include compatible headline metrics only.

Use `N/A` where stages use different metrics.

Do not make misleading cross-stage comparisons.

## 13. Create negative-results section

Create:

`docs/FULL_G_NEGATIVE_RESULTS.md`

Include:
- G2 Chronological matched NowMind
- G2.1 Reactive/Chronological often matched
- G2.2/2.2.1 N and C tied after fair retrieval
- qwen3:0.6b Regime A favored C 8-0 among discordant cases
- corrected Regime B tied
- free OpenRouter models failed infrastructure/calibration gates

Explain why these matter:
- prevents benchmark gaming
- narrows claims
- separates architectural benefits from representation-specific benefits
- defines next falsifiable questions

## 14. Create open research questions

Create:

`docs/FULL_G_OPEN_QUESTIONS.md`

At minimum:
1. Does a larger/stronger model exploit NowMind representation better?
2. Does explicit geometry help tasks where chronology is less naturally aligned?
3. Which representation features create verbosity without benefit?
4. Are source labels best represented symbolically, graphically, or in latent embeddings?
5. Can a learned model consume Present Geometry directly rather than via text serialization?
6. Does a Geometric Veto layer provide measurable safety/uncertainty benefits?
7. Can geometry compression preserve provenance while reducing token burden?
8. What experiment could distinguish NowMind from a strong chronological state machine?

No speculative consciousness claims.

## 15. Julian/Sophontic preparation — draft only

Create:

`docs/JULIAN_TECHNICAL_BRIEF_DRAFT.md`

Do NOT send anything.

Keep it concise: about 1–2 pages.

Structure:
- What was built
- Why "geometry"
- How Present Geometry differs from latent geometry
- Experimental progression
- Strongest findings
- Negative results
- Real-model limitation
- Open question for Julian

Suggested final question:

```text
Do you see a meaningful connection between explicit present-state relational geometry like this
and the latent/internal geometry of reasoning you are studying, or do you see them as fundamentally separate levels?
```

Do not claim alignment with Sophontic beyond a possible research intersection.

## 16. Full-G reviewer checklist

Create:

`docs/FULL_G_REVIEW_CHECKLIST.md`

Checklist:
- tests pass
- stale-state invariant pass
- source invariants pass
- frozen results preserved
- no secret files
- browser reviewer mode works
- all links/docs resolve
- no cloud dependency
- no unsupported claims
- Git clean or explicitly documented
- negative results visible
- reproducibility instructions tested

## 17. Final test pass

Run full:

`python -m pytest`

Also run:
- G1 CLI demo
- G1 evidence suite
- representative G2 temporal demo
- G2.1 spatial demo
- G2.2.1 recovery demo
- local browser reviewer mode

Do not rerun cloud models.

## 18. Final completion report

Return:
1. Git initialization result
2. secret-scan result
3. baseline commit hash if created
4. full pytest result
5. G1 stale-state result
6. reviewer demo URL
7. Full-G stages included
8. benchmark summary path
9. claims/nonclaims path
10. negative-results path
11. reproducibility path
12. reviewer narrative path
13. Julian brief draft path
14. unresolved UI/documentation issues
15. confirmation no paid/cloud calls were made
16. whether Full-G is ready for internal review
17. whether it is ready to show Julian as an honest research demonstrator
18. recommended next research stage after Full-G

Do not add new architecture merely to make the package look more impressive.

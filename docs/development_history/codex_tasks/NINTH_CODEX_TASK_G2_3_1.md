# NINTH CODEX TASK — G2.3.1 Real Local Model Evaluation

## Mission

Do not change the NowMind architecture.

G2.3 infrastructure is complete, but the final 1000-pair evaluation used only:

`mock-deterministic-g2.3`

Therefore those results are **not model evidence**.

G2.3.1 exists only to run the already-defined G2.3 experiment against one or more real local instruction models through Ollama.

## 1. Preserve everything

All prior symbolic and G2.3 tests must remain green.

Do not modify prompts, benchmark rules, validators, representations, source semantics, or scoring merely to improve a real model's results.

If a genuine compatibility bug is found, version and document the fix before rerunning.

## 2. Check Ollama

Run:

```text
ollama --version
ollama list
```

If Ollama is unavailable:
- do not install it automatically;
- create `OLLAMA_SETUP_REQUIRED.md`;
- report that the evaluation cannot begin;
- stop before final model benchmarking.

If Ollama is available but no suitable local model exists:
- report installed models;
- do not auto-pull one;
- stop and ask Jonathan to choose/install a model.

## 3. Hardware audit

Before selecting a model, record:
- Windows version;
- CPU;
- total RAM;
- GPU model(s);
- available VRAM if detectable;
- free disk space.

Create:

`artifacts/g2_3_1/hardware_manifest.json`

Do not expose serial numbers, machine IDs, usernames, or unrelated personal data.

## 4. Model selection

Prefer at least two distinct local instruction models if already installed and practical.

Selection principles:
- enough context for Regime A histories where possible;
- structured JSON instruction-following;
- reasoning capability;
- feasible latency on the local machine.

Do not compare models by merging their scores.

Each model gets its own result set.

## 5. Record exact manifest

For every evaluated model record:
- Ollama model name/tag;
- digest if available;
- model size;
- context setting;
- generation parameters;
- temperature;
- top-p;
- seed if supported;
- thinking/reasoning mode settings if relevant.

Freeze this manifest before final evaluation.

## 6. Calibration only

Run the existing G2.3 calibration split first.

For each model:
- 50 paired trials;
- N/C/R conditions;
- verify JSON parsing;
- verify no context overflow;
- verify prompt fairness;
- measure latency.

Do not tune the model using final evaluation results.

Only make neutral compatibility changes needed for valid parsing, and version them.

## 7. Freeze prompts before final run

After calibration:
- hash prompt templates;
- freeze them;
- save hashes;
- freeze generation settings.

Create:

`artifacts/g2_3_1/<model_slug>/frozen_experiment_manifest.json`

## 8. Final paired evaluation

For each model run:

### Regime A
Equal information, no truncation.

Run only history cohorts that fit the configured context.

If H500/H1000 overflow:
- report them as unsupported under Regime A;
- do not silently truncate.

### Regime B
Fixed equal token/input budget for N and C.

Use the already-defined G2.3 fairness policy.

Target:
- minimum 1000 paired trials per evaluated model if runtime is practical.

If runtime makes 1000 unreasonable:
- run the largest justified predeclared count;
- report wall-clock duration;
- do not stop early because results look unfavorable.

## 9. Keep raw and validated results separate

For each trial preserve:

```text
raw model proposal
symbolic validation result
final validated result
```

Do not count a validator correction as raw model success.

## 10. Required primary comparison

For each model and regime report:

```text
N better than C
C better than N
tie
```

on identical paired trials.

Also report:
- McNemar test if applicable;
- confidence intervals;
- effect size/difference in accuracy;
- token difference;
- latency difference.

Do not call a tiny or statistically unsupported difference an advantage.

## 11. Source-confusion analysis

Report N vs C for:
- stale memory as current;
- false memory as current;
- prediction as fact;
- unsupported certainty;
- correct UNKNOWN;
- contradiction handling.

These are central G2.3 outcomes.

## 12. Long-history analysis

For H0/H10/H50/H100/H500/H1000, where supported:

Report:
- accuracy;
- source confusion;
- input tokens;
- latency;
- context overflow;
- N/C paired outcomes.

Regime A and B remain separate.

## 13. Action tasks

Report:
- invalid action proposals;
- collision proposals;
- unsafe/unsupported assumptions;
- validator rejection;
- validator-prevented errors.

Again distinguish raw from validated.

## 14. Real-model failure gallery

Create:

`artifacts/g2_3_1/<model_slug>/failure_gallery.md`

Include representative paired cases where:
- N succeeds and C fails;
- C succeeds and N fails;
- both fail differently;
- raw model fails but validator prevents an error;
- long history causes source confusion.

Include prompts only as needed and avoid enormous dumps.

## 15. Browser demo

Update the existing Model Comparison tab to use an evaluated real Ollama model.

Show:
- exact model;
- N input;
- C input;
- same settings;
- raw responses;
- parsed results;
- validation;
- token estimates/counts;
- latency.

Keep evaluator truth hidden by default.

## 16. No architecture changes

Do not add:
- identity;
- dreaming;
- Veto Gate;
- sensors;
- cloud model APIs;
- self-modification.

G2.3.1 is evaluation only.

## 17. Completion report

Return:

1. Ollama version;
2. hardware summary;
3. exact model(s) evaluated;
4. calibration results;
5. final paired trial count per model;
6. Regime A N/C/R results;
7. Regime B N/C/R results;
8. raw vs validated results;
9. N-win/C-win/tie;
10. statistical comparison;
11. source-confusion comparison;
12. history-scaling results;
13. token/context results;
14. latency results;
15. action safety results;
16. validator-prevented errors;
17. representative N wins;
18. representative C wins;
19. browser demo status;
20. artifact paths;
21. deviations;
22. whether results provide evidence of a representation effect;
23. whether the project is ready for Julian technical review.

Do not claim a NowMind advantage unless real paired model results support it.

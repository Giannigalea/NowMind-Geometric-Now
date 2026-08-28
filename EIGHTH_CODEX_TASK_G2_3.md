# EIGHTH CODEX TASK — NowMind G2.3 Model Integration

## Mission

Implement **NowMind G2.3 — Model Integration & Representation Benchmark**.

The new research question is:

> Given the same underlying task information and the same language model, does the representation architecture change reasoning quality?

G2.2.1 is now strong enough to make this comparison meaningful:
- symbolic N and C tie on paired holdout outcomes;
- retrieval work is comparable;
- stale-target recovery works;
- hidden target recovery works;
- hidden obstacle recovery is materially above zero;
- source violations remain zero.

Do not frame G2.3 as an "advantage stage". If N and C tie, report the tie. If C wins, report it.

## 1. Preserve all symbolic layers

All G1/G2/G2.1/G2.2/G2.2.1 tests and benchmarks remain required.

Do not alter symbolic semantics merely to improve model results.

Known residual symbolic limitations, including small E22-style collision/invalid rates, must remain documented unless a genuine regression bug is discovered.

## 2. Local-first model backend

Create a model-provider abstraction:

```python
class ModelBackend(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse:
        ...
```

Required:
- `MockModelBackend` for deterministic tests;
- `OllamaBackend` using localhost only.

Do not:
- call cloud APIs;
- add OpenAI/Anthropic/Gemini backends;
- upload benchmark data;
- auto-download a model.

Codex may run `ollama list`.

If one or more suitable local instruction models are already installed, use them. Otherwise implement infrastructure and report the missing runtime prerequisite.

Record:
- exact model name/tag;
- digest/hash if obtainable;
- context size if known;
- temperature/top-p/seed/etc.

## 3. Architectural role of the LLM

The LLM is a replaceable reasoning faculty.

It may propose:
- answers;
- actions;
- explanations.

It may not:
- become identity;
- become memory;
- write `OBSERVED_NOW`;
- bypass ActionExecutor;
- mutate WorldState directly;
- access evaluator ground truth.

Architecture:

```text
Present / Temporal / Possibility Geometry
              |
              v
      Representation Builder
              |
              v
          SAME MODEL
              |
              v
        Model Proposal
          /       \
         v         v
 raw metrics    symbolic validation
                   |
                   v
             validated result
```

## 4. Experimental conditions

Every paired trial uses the same model and same admissible underlying information.

### N — NowMind Structured Representation

Include:
- observed now;
- inferred now;
- reconstructed memories explicitly labeled;
- future hypotheses explicitly labeled;
- uncertainties;
- current query/goal;
- planning assumptions.

Do not include raw previous NowStates.

### C — Chronological Representation

Include the same admissible information as a clean chronological record:
- observations;
- events;
- memory/reconstruction records;
- hypotheses;
- cycle IDs/timestamps;
- current query/goal.

Do not intentionally make C confusing.

### R — Current-Only Representation

Current observed state only.

### S — Symbolic NowMind

Existing no-LLM symbolic reference.

## 5. Two fairness regimes

Run and report separately.

### Regime A — Equal Information / No Truncation

N and C receive all benchmark-relevant admissible information, provided it fits model context.

Purpose:
test organization/representation.

If a history cohort does not fit model context, record context limitation and do not silently truncate.

### Regime B — Fixed Token Budget

N and C receive the same maximum representation budget.

N uses explicit retrieval/reconstruction.
C uses a documented chronological selection/indexing/truncation policy.

Purpose:
test resource-constrained scaling.

Do not mix A/B results.

## 6. Shared instruction

Use one common neutral system instruction across N/C/R wherever possible.

Intent:

```text
Use only supplied evidence.
Distinguish current observation, memory, and hypothetical future.
Do not promote memory or predictions to current fact.
Return UNKNOWN when current evidence is insufficient.
For action tasks, propose only actions supported by supplied state.
Return strict JSON.
```

Do not add NowMind-only answer hints.

Create `docs/G2_3_PROMPT_FAIRNESS_AUDIT.md`.

## 7. Structured output schema

Require machine-parseable JSON similar to:

```json
{
  "status": "TRUE|FALSE|UNKNOWN|CONTRADICTORY|ANSWER|ACTION",
  "answer": "...",
  "source_used": "observed_now|inferred_now|reconstructed_memory|hypothetical_future|mixed|none",
  "confidence": 0.0,
  "action": null,
  "assumptions": [],
  "explanation": []
}
```

For invalid JSON:
- record parse failure;
- optionally allow one neutral schema-repair retry;
- use the same repair instruction for every condition;
- record retry count.

## 8. Proposal-only vs validated mode

### P — Proposal Only
Score raw model output.

### V — Validated
Pass proposal through existing symbolic validators.

Validator may reject:
- unsupported current claims;
- collision/out-of-bounds action;
- temporal-source violations.

Do not silently rewrite arbitrary wrong model answers into correct ones.

Report raw and validated metrics separately.

## 9. Paired task families

Reuse existing generators where practical.

Include at minimum:

### Temporal QA
- present vs stale memory;
- current UNKNOWN + memory;
- future hypothesis vs current;
- false memory;
- contradictory present evidence;
- long-history source confusion.

### Spatial QA
- relative position;
- containment;
- reachability;
- obstacle state.

### Action choice
- choose next move;
- safe vs conditional route;
- verify/scan vs act;
- respond after hidden change becomes observed.

### Explanation/source
- identify evidence source;
- explain why memory was not treated as current fact;
- identify assumptions behind a conditional action.

## 10. History scaling

Explicit cohorts:

```text
H0 H10 H50 H100 H500 H1000
```

Regime A only runs cohorts that fit model context without truncation.
Regime B runs under fixed budget.

## 11. Scale

First run a calibration set:
- 50 paired trials per condition.

After prompts/schema are frozen:
- target >=1000 paired model trials if local runtime is practical;
- prefer 2000+ if practical.

If local inference makes that unrealistic, run the largest justified paired set and report wall-clock cost. Do not fake scale.

## 12. Multiple local models

Preferred: use at least two materially different installed local instruction models if already available.

Do not auto-download.

If only one is installed, run one and document the limitation.

Never aggregate different models into one score.

## 13. Metrics

Report by:
- model;
- N/C/R;
- Regime A/B;
- Proposal/Validated;
- family;
- history cohort.

Minimum metrics:

### Reasoning
- overall_accuracy
- current_state_accuracy
- past_query_accuracy
- future_query_accuracy
- spatial_reasoning_accuracy
- action_choice_accuracy
- contradiction_detection_rate
- correct_unknown_rate

### Source integrity
- source_classification_accuracy
- stale_memory_as_current_rate
- false_memory_as_current_rate
- prediction_as_fact_rate
- unsupported_certainty_rate

### Action safety
- invalid_action_rate
- collision_proposal_rate
- validator_rejection_rate
- validator_prevented_error_count

### Output quality
- json_parse_success_rate
- repair_retry_rate
- explanation_grounding_rate

### Resource
- input tokens or best available estimate
- output tokens
- mean latency
- p95 latency
- model call count
- context-overflow count

## 14. Prompt/resource fairness

For each paired N/C trial record:
- same trial ID;
- same admissible fact set hash;
- condition;
- prompt hash;
- token count/estimate;
- model config;
- raw output;
- parsed output.

No hidden evaluator truth in prompts.

Add an automated fairness audit proving N/C derive from the same admissible trial information.

## 15. Statistics

Use paired comparisons.

For major binary outcomes report:
- counts/rates;
- 95% confidence intervals;
- N-win/C-win/tie counts.

If practical, use McNemar's test for paired correctness.

For latency/token metrics report mean/median/p95.

Create `docs/G2_3_STATISTICAL_METHOD.md`.

## 16. Avoid prompt overfitting

Create:
- calibration/development split;
- frozen evaluation split.

Prompt changes after final evaluation starts must version the experiment and preserve previous results.

Do not add family-specific answer hints.

## 17. Artifacts

Generate under `artifacts/g2_3/`:

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

## 18. Browser Model Comparison tab

For one scenario show side-by-side:

### NOWMIND REPRESENTATION
Exact structured input representation.

### CHRONOLOGICAL REPRESENTATION
Exact chronological input representation.

Below each:
- same model identity;
- model proposal;
- source used;
- raw correctness;
- validator result;
- final outcome;
- token count;
- latency.

Hide evaluator truth by default behind a "Reveal evaluator answer" control.

## 19. Hero demo

Use a long-history scenario with:
- repeated target moves;
- stale memory;
- one future hypothesis;
- partial current observation;
- current query/action choice.

Run the same model on N and C.

Show:
- both exact representations;
- proposals;
- source used;
- stale-memory contamination or absence;
- symbolic validation.

## 20. Testing

Using `MockModelBackend`, test:
- N/C receive same admissible fact set;
- model cannot mutate runtime;
- model output cannot become OBSERVED_NOW;
- model output cannot become MemoryTrace;
- proposed action cannot bypass validator/ActionExecutor;
- invalid JSON handling is identical;
- validator cannot inspect representation condition to favor N;
- prompt builders cannot see evaluator truth;
- fixed-budget logic deterministic;
- paired trial IDs preserved.

All previous tests remain green.

## 21. Locality audit

Ollama must use localhost only.

No cloud telemetry or external model calls.

Create `docs/G2_3_LOCALITY_AUDIT.md`.

## 22. Do not add yet

Do not add:
- identity;
- dreaming;
- ethical L3 Veto Gate;
- camera/microphone;
- cloud models;
- self-modification;
- quantum mechanism.

## 23. Completion report

Return:
1. all symbolic regression results;
2. exact local model manifest;
3. calibration size;
4. final paired trial count;
5. N/C/R Regime A metrics;
6. N/C/R Regime B metrics;
7. proposal-only metrics;
8. validated metrics;
9. N/C paired win-loss-tie;
10. history scaling;
11. source-confusion metrics;
12. action-safety metrics;
13. token/latency results;
14. prompt fairness audit;
15. N-beats-C cases;
16. C-beats-N cases;
17. representative failures;
18. validator-prevented errors;
19. browser URL;
20. artifact paths;
21. source/invariant violations;
22. deviations;
23. recommendation whether the project is ready for external technical packaging / Julian, or precisely what evidence remains missing.

Do not claim NowMind improves model reasoning unless paired results support that conclusion.

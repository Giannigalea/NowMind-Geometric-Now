# THIRTEENTH CODEX TASK — G2.3.2 Fix Regime B Fairness and Analyze Chronological Wins

## Mission
Do not change the NowMind architecture, benchmark, model, prompts, validator, or scoring to improve results.

G2.3.1 produced the first real-model result with `qwen3:0.6b` over 250 paired trials.

Frozen Regime A result:
- Chronological wins: 8
- NowMind wins: 0
- Ties: 242

Regime B is not valid evidence because 166/500 checked N/C pairs exceeded the fixed token budget.

G2.3.2 has exactly two goals:
1. repair Regime B fixed-budget enforcement;
2. analyze the 8 Regime-A cases where Chronological beat NowMind.

## 1. Freeze existing evidence
Preserve all G2.3.1 artifacts exactly.

Create:
`artifacts/g2_3_2/frozen_g2_3_1_snapshot/`

Create `docs/G2_3_2_FROZEN_BASELINE.md` recording:
- model `qwen3:0.6b`
- paired trials `250`
- Regime A = C 8 / N 0 / ties 242
- Regime B invalid for fairness interpretation
- fixed-budget violations = 166/500

Do not overwrite or reinterpret these results.

## 2. Preserve Regime A
Do not rerun Regime A as the primary result.
The existing run is frozen evidence.
Individual replays are allowed only for debugging and must never replace original outputs.

## 3. Audit the token-budget bug
Create `docs/G2_3_2_TOKEN_BUDGET_AUDIT.md`.

Identify why 166/500 N/C checks exceeded budget. Classify causes such as:
- tokenizer/estimator mismatch
- wrapper/system text added after truncation
- inconsistent schema accounting
- N/C different counting paths
- history selection overflow
- off-by-one logic
- template overhead
- another cause

Do not fix by simply increasing the budget.

## 4. Canonical accounting
Create one shared canonical final-input counting method for N/C/R and the fairness audit.

Count the FINAL prompt actually sent to the model.

If exact tokenizer access is unavailable:
- use one deterministic estimator
- apply the same method and safety margin to N and C
- document limitations

## 5. Hard pre-send budget gate
Pipeline:

build admissible representation
-> deterministic trimming/selection
-> build final prompt
-> count final input tokens
-> if over budget, reduce deterministically
-> assert <= budget
-> send request

No over-budget prompt may be sent.

## 6. Fair N policy
If trimming is required, preserve:
- current observation
- current query/goal
- source labels
- highest-relevance reconstructed memories/hypotheses according to existing retrieval

Drop lower-priority material deterministically.
No evaluator truth or answer-aware selection.

## 7. Fair C policy
Chronological remains a strong control.

If trimming is required:
- preserve current records
- retain query-relevant historical records using legitimate indexing/selection
- preserve chronological order among retained records
- preserve temporal/source metadata
- use deterministic selection

Do not intentionally waste its budget with irrelevant history.

## 8. Equal ceiling, not equal length
Regime B requires:
- N final prompt <= B
- C final prompt <= B

They need not use identical token counts.
Record actual tokens, unused budget, evidence retained, evidence dropped.
Do not pad shorter prompts.

## 9. Fairness invariant
All 250 paired Regime B trials must have:
- N tokens <= budget
- C tokens <= budget
- same underlying admissible trial information
- same model
- same parameters
- same trial ID
- same scoring
- same validator

Target: 0 budget violations.

If any remain, Regime B remains invalid.

## 10. Rerun ONLY Regime B
Use the exact same:
- qwen3:0.6b model
- 250 trial IDs
- benchmark seed
- generation settings
- scoring
- validator

Do not generate new trials.
Do not change questions or expected answers.

## 11. Preserve raw and validated results
Store separately:
- raw model proposal
- parsed output
- raw correctness
- validator decision
- validated result

## 12. Analyze the 8 Regime-A C wins
Create `docs/G2_3_2_REGIME_A_C_WIN_ANALYSIS.md`.

For each case inspect:
- trial ID
- family
- history length
- N/C prompt tokens
- N/C representation structure
- N/C answers
- evaluator answer
- source used
- omitted relevant information?
- chronology preserving useful sequence?
- NowMind fragmenting causal sequence?
- verbosity?
- tiny-model source-label misunderstanding?
- semantic/parsing/action-choice failure?

Diagnosis only. Do not modify prompts in this task.

## 13. Categorize the 8 cases
Assign one or more:
A chronology preserves useful temporal sequence
B NowMind too verbose
C NowMind fragments causal context
D model follows chronology more naturally
E relevant info missing from N
F source-label misunderstanding
G token/context pressure
H parsing/schema issue
I evaluator/scoring issue
J unclear/other

If E or I reveals a genuine bug, document it and recommend a versioned future experiment. Do not rewrite frozen Regime A evidence.

## 14. Statistical analysis
For original Regime A 8/0/242:
- paired exact binomial or McNemar as appropriate
- p-value
- paired accuracy difference
- 95% CI where appropriate

State limitations:
- one 0.6B model
- 250 trials
- one benchmark
- not generalizable to all LLMs

Do the same for corrected Regime B.

## 15. Token analysis
For corrected Regime B report:
- declared budget
- mean/median/p95/max N tokens
- mean/median/p95/max C tokens
- unused budget
- evidence retained/dropped

Break down by H0/H10/H50/H100/H500/H1000 where present.

## 16. No prompt tuning
Do not alter:
- common system instruction
- source labels
- output schema
- task definitions
- wording to favor either condition

Only deterministic fixed-budget enforcement may change prompt length/content.

If any other prompt text changes, version it separately and do not treat it as the same frozen experiment.

## 17. Regression tests
Add tests proving:
- final N/C prompts never exceed budget
- count occurs after final prompt construction
- same counter used for N/C
- trimming deterministic
- no evaluator truth used
- current observation/query preserved
- exact 250 frozen trial IDs reused
- validator unchanged
- Regime A frozen result unchanged

All prior tests must remain green.

## 18. Artifacts
Generate under `artifacts/g2_3_2/`:
- `g2_3_2_budget_audit.json`
- `g2_3_2_regime_b_metrics.json`
- `g2_3_2_regime_b_pairwise.json`
- `g2_3_2_regime_b_trial_results.jsonl`
- `g2_3_2_token_metrics.json`
- `g2_3_2_fairness_invariants.json`
- `g2_3_2_regime_a_c_win_cases.json`
- `g2_3_2_regime_a_c_win_analysis.md`
- `g2_3_2_statistical_summary.md`
- `g2_3_2_summary.md`

Preserve all G2.3.1 artifacts.

## 19. Browser demo
If helpful, show:
- declared budget
- actual N tokens
- actual C tokens
- PASS/FAIL
- evidence retained/dropped

Do not alter representation semantics.

## 20. Completion report
Return:
1. exact cause of 166/500 violations
2. corrected accounting method
3. full pytest result
4. confirmation Regime A remains C8/N0/tie242
5. statistical interpretation of Regime A
6. corrected Regime B fairness result
7. corrected Regime B N-win/C-win/tie
8. raw Regime B N/C/R accuracy
9. validated Regime B N/C/R accuracy
10. Regime B token metrics
11. results by history cohort
12. category for all 8 Regime-A C wins
13. whether any of the 8 expose a fairness/implementation bug
14. whether chronology appears genuinely easier for qwen3:0.6b
15. validator-prevented errors
16. browser status
17. artifact paths
18. deviations
19. exact research conclusion supported by qwen3:0.6b
20. recommended next experiment

Do not claim a NowMind advantage unless corrected paired evidence supports it.
Do not change NowMind merely because Chronological performed better.

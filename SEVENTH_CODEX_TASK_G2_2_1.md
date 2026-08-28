# SEVENTH CODEX TASK — NowMind G2.2.1 Epistemic Recovery & Retrieval Efficiency

## Mission

Do **not** add an LLM yet.

G2.2 exposed three genuine weaknesses:
1. NowMind and Chronological matched on goal rate, but NowMind inspected far more evidence (~669.2 vs ~15.2).
2. Hidden-change recovery was 0.0 for all non-oracle systems.
3. Stale memory harmed NowMind in E2; Reactive beat NowMind in 125 paired trials.

G2.2.1 is a targeted correction and diagnostic phase.

Goals:
- make memory retrieval efficient without weakening G1/G2 semantics;
- add principled stale-target recovery;
- implement hidden-change recovery;
- reduce unnecessary verification;
- preserve benchmark integrity;
- determine whether remaining weaknesses are architectural or implementation-specific.

## 1. Freeze current evidence

Before changing runtime behavior, copy current G2.2 artifacts into:

`artifacts/g2_2/baseline_before_g2_2_1/`

Create `docs/G2_2_1_BASELINE_SNAPSHOT.md` recording exact pre-change metrics.

Do not overwrite original evidence.

## 2. Freeze benchmark v1

Preserve the existing G2.2 benchmark exactly:
- seed `20260823`
- trials `3000`
- E1-E24
- D1-D6

Call it **G2.2 benchmark v1**. Do not alter scenarios or expected outcomes to improve NowMind.

## 3. Add a holdout benchmark

Create a separate G2.2.1 holdout:
- different seed;
- at least 2000 trials;
- same scenario grammar, independently generated maps/events/noise;
- no overlapping trial IDs;
- config written before final evaluation.

Workflow:
1. write holdout seed/config;
2. implement using unit tests + benchmark v1;
3. freeze code;
4. run holdout for final assessment.

Do not repeatedly tune from holdout results.

## 4. Audit evidence-inspection metrics

Create `docs/G2_2_1_EVIDENCE_METRIC_AUDIT.md`.

Determine whether N and C currently count inspected evidence comparably.

Required metrics:
- `records_scanned`
- `index_candidates_considered`
- `records_returned`
- `reconstructions_created`
- `effective_evidence_used`

If the current 669 vs 15 comparison is not apples-to-apples, preserve old numbers and add corrected comparable metrics.

## 5. Implement fair indexed retrieval

Memory indexing is allowed.

Allowed indices:
- subject/entity;
- relation type;
- target;
- source cycle;
- recency;
- provenance;
- useful composites such as `(entity_id, relation_type)`.

Requirements:
- MemoryStore still stores MemoryTrace, never old NowState/TemporalNowState;
- retrieval remains explicit;
- returned traces are reconstructed into current memories;
- no ExperimentRecorder or evaluator access;
- no answer precomputation.

Measure retrieval scaling at H0/H10/H50/H100/H500/H1000.

## 6. Stale-target disconfirmation

When memory says target is at A and current observation later verifies A is empty:

1. preserve the historical MemoryTrace;
2. mark the current planning assumption as disconfirmed;
3. do not repeatedly route back to A;
4. reduce current reliance on that reconstruction;
5. enter target reacquisition/search.

Historical memory remains; current planning confidence changes.

## 7. Target reacquisition

Implement a transparent deterministic search policy when:
- target is not currently observed;
- remembered location has been checked and falsified.

Possible policy:
- nearest frontier search;
- deterministic frontier ordering;
- last-seen neighborhood expansion;
- memory-weighted search with falsified regions excluded.

No evaluator truth.

Measure:
- reacquisition attempts;
- success rate;
- cells explored;
- steps to reacquire.

## 8. Hidden obstacle recovery

Canonical behavior:
1. route planned;
2. obstacle changes outside FOV;
3. agent does not know immediately;
4. later observation reveals conflict;
5. plan invalidates;
6. stale assumption is contradicted;
7. replan from fresh Now;
8. continue safely if possible.

No advance knowledge of hidden change.

## 9. Hidden target recovery

Canonical behavior:
1. target known/remembered at A;
2. target moves unseen to B;
3. NowMind does not know;
4. A later observed empty;
5. assumption A is disconfirmed;
6. reacquisition begins;
7. B later observed;
8. B becomes new `OBSERVED_NOW`.

Never rewrite old memory as if it had always said B.

## 10. Verification-policy audit

Current:
- verification rate ~0.2349
- useful ~0.4481
- wasted ~0.5519

Create `docs/G2_2_1_VERIFICATION_POLICY_AUDIT.md`.

Classify verify-first decisions:
- prevented likely failure;
- enabled shorter route;
- confirmed useful memory;
- wasted because safe alternative dominated;
- wasted because outcome could not change decision.

Implement a transparent decision-value gate:

`verify if ExpectedDecisionValue > VerificationCost`

Do not claim formal value-of-information optimality unless actually derived.

## 11. Anti-overfitting

Runtime code must not branch on:
- scenario family names such as E2/E11;
- trial IDs;
- benchmark seed;
- expected answer.

Benchmark metadata stays evaluator-side.

## 12. Targets, not hard-coded gates

Aim to:
- substantially reduce evidence inspection at long histories;
- reduce E2 stale-memory harm;
- raise hidden-change recovery materially above 0;
- reduce wasted verification without destroying useful verification.

Report honestly if tradeoffs prevent these.

## 13. Preserve epistemic integrity

Required:
- memory-as-observation violations = 0;
- prediction-as-fact violations = 0;
- hidden changes unknown until perceived;
- falsified planning assumptions do not delete historical traces;
- unknown remains explicit when unsupported.

## 14. Continue evaluating N/C/R/O

If C still matches or beats N, report it.
If R beats N in some families, report it.

Do not weaken controls.

## 15. Artifacts

Generate `artifacts/g2_2_1/` with:
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

## 16. Web demos

Add:
### R1 — Stale target recovery
Memory target A -> inspect A -> absent -> mark assumption falsified -> frontier search -> find B.

### R2 — Hidden obstacle recovery
Obstacle moves under fog -> no omniscient reaction -> later observation reveals it -> old path invalid -> replan.

Show fresh Now IDs and preserve old memory/history separately.

## 17. Tests

Add tests proving:
- indexed retrieval returns the same semantically valid trace set as reference retrieval;
- no evaluator/history access;
- falsified location is not reused indefinitely;
- target reacquisition can find moved target;
- hidden obstacle triggers replan only after observation;
- hidden target movement does not leak;
- verification depends on possible decision change;
- runtime is independent of trial/family labels;
- v1 stays reproducible;
- holdout seed/config differs.

All previous tests remain green.

## 18. Completion report

Return:
1. all regression results;
2. v1 before/after comparison;
3. holdout results;
4. exact evidence metric definitions;
5. H0/H10/H50/H100/H500/H1000 scaling;
6. NowMind vs Chronological retrieval work;
7. E2 stale-target results;
8. hidden obstacle recovery;
9. hidden target recovery;
10. target reacquisition rate;
11. verification useful/wasted rates;
12. memory-help/memory-harm counts;
13. N/C/R/O pairwise results;
14. regressions;
15. source/invariant violations;
16. browser demo status;
17. artifact paths;
18. deviations;
19. recommendation: G2.3 LLM integration or one final symbolic correction only if a fundamental bug remains.

Do not continue symbolic benchmarking indefinitely to manufacture a NowMind advantage.

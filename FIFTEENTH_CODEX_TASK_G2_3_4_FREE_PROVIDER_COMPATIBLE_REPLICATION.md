# FIFTEENTH CODEX TASK — G2.3.4 Free Provider-Compatible Replication

## Mission

G2.3.3 is complete as a negative infrastructure result. No current exact-free OpenRouter model produced a schema-valid smoke pass under the strict privacy-routing rule.

G2.3.4 changes exactly ONE operational constraint:

OLD:
provider data collection must be denied / ZDR-compatible

NEW:
provider data collection may be allowed, but only synthetic benchmark data may ever be sent.

Everything scientific remains frozen.

Do NOT change:
- NowMind architecture
- frozen 250 trial IDs
- Regime A semantics
- corrected Regime B semantics
- common instructions
- N/C/R representation semantics
- response schema
- scoring
- validator
- expected answers
- free-only requirement
- provider pinning requirement
- no-fallback requirement

## 1. Preserve G2.3.3 exactly

Do not overwrite G2.3.3 artifacts.

Create:
- `artifacts/g2_3_4/`
- `docs/G2_3_4_PROTOCOL.md`

Record the frozen local reference:

```text
qwen3:0.6b local Ollama

Regime A:
  C wins = 8
  N wins = 0
  ties = 242

Regime B:
  C wins = 0
  N wins = 0
  ties = 250
```

## 2. Privacy relaxation boundary

Only synthetic benchmark prompt/response data may be sent to OpenRouter/providers.

Still forbidden:
- PCT book content
- personal information
- private notes
- arbitrary source files
- API keys
- local paths
- usernames
- machine identifiers
- unrelated logs
- unpublished prose outside the synthetic benchmark

Add a payload guard that fails locally if unexpected private/repository content is present.

## 3. Free-only is still a hard rule

Every selected model must have live OpenRouter pricing:

```text
input price = $0
output price = $0
```

Reject:
- nonzero-price models
- paid fallback
- `openrouter/free`
- random or automatic model routing

Do not spend money.

## 4. Re-discover exact-free models

Query live OpenRouter metadata.

Create:
- `artifacts/g2_3_4/free_model_rediscovery.json`
- `docs/G2_3_4_MODEL_SELECTION.md`

Record per candidate:
- exact slug
- family
- context length
- structured-output support
- provider endpoints
- current price
- whether provider requires data collection
- whether required parameters are supported
- whether provider pinning is possible

Prioritize candidates that failed G2.3.3 only because of strict `data_collection=deny`, especially current Nemotron/Liquid-style candidates if still free and compatible.

Do not blindly retry structurally incompatible candidates unless live metadata changed.

## 5. Provider consistency

For every run:
- pin one exact provider where possible
- same provider for N and C
- disable fallback
- require parameters where supported

If exact pinning is impossible:
- record provider for every response
- reject N/C pairs served by different providers
- never include mismatched-provider pairs in paired statistics

## 6. Schema remains frozen

Use the exact existing G2.3 response schema.

Do NOT:
- add enum values
- coerce invalid values into valid ones
- map `SUCCESS` into `TRUE`
- accept null where forbidden
- introduce per-model semantic repair

Prompt-only JSON compatibility may remain only as already implemented in G2.3.3.

## 7. Model selection priority

Use a deterministic order:
1. exact-free candidate previously blocked only by privacy routing
2. strongest practical candidate with adequate context
3. different family from qwen3 where possible
4. stable endpoint/provider
5. schema compatibility

Do not select based on N-vs-C outcomes.

## 8. Smoke stage

Use the minimum number of calls required.

Test:
- basic JSON
- current-vs-memory
- hypothetical-vs-current
- action output

Success:
- provider reached
- cost remains zero
- schema-valid output
- no fallback
- no sensitive payload
- provider/model recorded

Do not require perfect semantic accuracy.

## 9. Calibration

For the first schema-valid candidate, run 5–10 paired frozen trials.

Purpose:
- schema stability
- provider stability
- latency
- token compatibility
- quota/rate-limit behavior
- zero-cost confirmation

Do not tune prompts from outcomes.

Freeze model/provider/parameters/hashes after calibration.

## 10. Resumable execution

Persist every completed request immediately.

Stable identity:
- model_slug
- provider
- regime
- trial_id
- condition
- prompt_hash

Before issuing a call, reuse any valid completed row.

On rate limit:
- save state
- stop cleanly
- report progress
- provide a resume command

HTTP 429 is not a model reasoning failure.

## 11. Final target

For every candidate that passes calibration:

```text
250 frozen paired trials
Regime A
Regime B
```

Do not reduce the target merely to finish quickly.

Multi-day completion is allowed only if model/provider/parameters/hashes remain unchanged.

If they change materially, version the run and do not merge silently.

## 12. Regime A

Use frozen G2.3.2 Regime A unchanged.

No artificial common budget.
No silent truncation.

If context is insufficient, mark unsupported and prefer another model.

## 13. Regime B

Use corrected G2.3.2 fixed-budget logic unchanged.

Required:
- N <= B
- C <= B
- fairness failures = 0

Do not change B.

## 14. Raw vs validated results

Store separately:
- raw response
- parsed response
- schema-valid flag
- raw correctness
- validator decision
- validated correctness

## 15. Scientific comparison

Per completed model report:

Regime A:
- N wins
- C wins
- ties
- raw N/C accuracy
- validated N/C accuracy
- paired exact/McNemar result
- 95% CI where meaningful

Regime B:
same.

Compare independently against:

```text
Local qwen3:0.6b
A = C8 / N0 / T242
B = C0 / N0 / T250
```

Do not pool models into one pseudo-sample.

## 16. Cross-model interpretation

Create:
`docs/G2_3_4_CROSS_MODEL_INTERPRETATION.md`

Evaluate:
- C>N persists?
- disappears?
- reverses?
- only in Regime A?
- only under fixed budget?
- source/action errors decline?
- validator changes direction?
- family/capability appears relevant?

Do not claim a capability threshold from one additional model.

## 17. Avoid wasting requests

Retry first those blocked only by privacy routing.

Skip known structural failures unless live metadata materially changed.

Document why each candidate is retried, skipped, accepted, or rejected.

## 18. API key handling

Continue reading only:
`OPENROUTER_API_KEY`

Never print or persist it.

Verify:
- no secret file recreated
- `.gitignore` remains safe
- no key enters Git/artifacts/logs

## 19. Tests

Maintain/add tests for:
- synthetic-only payload guard
- free-price hard gate
- rejection of nonzero price
- exact model selection
- provider consistency
- no fallback
- schema strictness
- no semantic coercion
- resumable state
- duplicate prevention
- frozen trial hashes
- unchanged Regime B budget
- API-key redaction
- all prior tests

Run:
`python -m pytest`

## 20. Required artifacts

At minimum:
- `artifacts/g2_3_4/free_model_rediscovery.json`
- `artifacts/g2_3_4/model_selection.json`
- `artifacts/g2_3_4/run_state.json`
- `artifacts/g2_3_4/<model_safe>/smoke.json`
- `artifacts/g2_3_4/<model_safe>/calibration.json`
- `artifacts/g2_3_4/<model_safe>/regime_a_results.jsonl`
- `artifacts/g2_3_4/<model_safe>/regime_b_results.jsonl`
- `artifacts/g2_3_4/<model_safe>/pairwise.json`
- `artifacts/g2_3_4/<model_safe>/metrics.json`
- `artifacts/g2_3_4/<model_safe>/provider_manifest.json`
- `artifacts/g2_3_4/<model_safe>/statistical_summary.md`
- `artifacts/g2_3_4/g2_3_4_summary.md`

No secrets.

## 21. Stop conditions

Stop instead of improvising if:
- no exact-free candidate passes smoke
- any selected endpoint becomes nonzero-price
- provider pinning cannot be maintained
- provider changes within an N/C pair
- Regime B fairness fails
- prompt/schema hashes differ
- sensitive data would be sent
- quota exhausted

Quota exhaustion is a normal resumable stop.

## 22. Completion/progress report

Return:
1. confirmation G2.3.3 preserved unchanged
2. exact privacy rule relaxed
3. confirmation only synthetic data was sent
4. exact-free candidates rediscovered
5. candidates retried and why
6. selected model slugs
7. pinned providers
8. live $0/$0 verification
9. smoke results
10. calibration results
11. quota/rate-limit state
12. full pytest result
13. frozen trial-hash verification
14. progress count per model
15. complete or paused state
16. resume command if paused
17. Regime A N/C/tie
18. Regime B N/C/tie
19. raw vs validated accuracy
20. paired statistics
21. comparison to local qwen3:0.6b
22. whether C>N persists, disappears, or reverses
23. whether any NowMind advantage is supported
24. whether another exact-free model should be tested
25. whether evidence is strong enough yet for Julian technical review

Never claim consciousness, sentience, phenomenal awareness, identity transfer, or general AI superiority.

# FOURTEENTH CODEX TASK — G2.3.3 Free OpenRouter Cross-Model Replication

## Mission

G2.3.2 is complete and frozen.

This stage must:
1. migrate the OpenRouter API key safely from the plaintext TXT file Jonathan placed in the project root;
2. use only current OpenRouter models whose usage price is exactly $0 for input and output;
3. preserve the frozen G2.3.2 benchmark and architecture;
4. run resumable cross-model replication without spending money.

Do not change:
- NowMind architecture;
- benchmark questions;
- frozen 250 trial IDs;
- Regime A semantics;
- corrected Regime B semantics;
- scoring;
- validator;
- expected answers;
- task families.

Existing frozen local result:

```text
Model: qwen3:0.6b local Ollama

Regime A:
  Chronological wins = 8
  NowMind wins = 0
  ties = 242

Regime B:
  Chronological wins = 0
  NowMind wins = 0
  ties = 250

Regime B fairness failures = 0
```

Preserve this result exactly.

---

# 1. Safely migrate the OpenRouter API key

Jonathan has placed the OpenRouter API key in a TXT file in the project root.

Do NOT print the key.

Do NOT copy the key into:
- source code;
- JSON;
- markdown;
- logs;
- Git;
- test fixtures;
- shell-history documentation;
- browser output.

Find the root-level TXT file containing the OpenRouter key.

Safe identification:
- inspect root-level `.txt` files programmatically without printing contents;
- identify a plausible OpenRouter key by expected format/prefix/length;
- if more than one plausible secret file exists, STOP and ask Jonathan which filename contains the key;
- never echo candidate values.

Once identified:

1. read the key into memory only;
2. set it as the Windows USER environment variable:

```text
OPENROUTER_API_KEY
```

Use a safe PowerShell/.NET or `setx` method.

3. make the current process/session able to use it;
4. verify it by making a harmless authenticated OpenRouter metadata/models request;
5. verify only success/failure — never print the key;
6. add the plaintext key filename to `.gitignore` BEFORE any Git add/commit;
7. after successful environment-variable verification, delete the plaintext key file from the project root;
8. confirm the deleted file is not tracked by Git.

If migration fails:
- leave the source TXT file untouched;
- do not delete it;
- report the failure without revealing the key.

Create:

```text
docs/G2_3_3_API_KEY_MIGRATION.md
```

Record only:
- source filename;
- migration success/failure;
- destination variable name;
- verification status;
- deletion status;
- Git-ignore status.

Never record the secret value.

---

# 2. Git baseline

Before implementation changes:

Check whether the project is already a Git repository.

If not:
- initialize Git in the project root;
- create/update `.gitignore`;
- exclude:
  - `.env`
  - API-key TXT filename
  - credential files
  - Python caches
  - temporary logs
  - model caches
  - other obvious transient files

Do not exclude scientific benchmark artifacts unless they contain secrets or are unreasonably large.

If Git user identity is configured:
- make a baseline commit of the completed G2.3.2 state BEFORE G2.3.3 code changes.

If Git user identity is absent:
- do not invent name/email;
- initialize/stage safely;
- continue the experiment;
- report that commit identity remains to be configured.

Never commit the API key.

---

# 3. OpenRouter backend

Add:

```text
OpenRouterBackend
```

conforming to the existing `ModelBackend` protocol.

Endpoint:

```text
https://openrouter.ai/api/v1/chat/completions
```

Read authorization only from:

```text
OPENROUTER_API_KEY
```

Keep existing:
- MockModelBackend;
- OllamaBackend.

Use:
- non-streaming calls;
- structured JSON output where supported;
- same benchmark schema for N/C/R;
- same generation settings within a model.

---

# 4. FREE MODELS ONLY — hard rule

This task is explicitly restricted to models whose current OpenRouter pricing is:

```text
input price  = $0
output price = $0
```

Do not use:
- paid models;
- promotional models with nonzero fallback pricing;
- `openrouter/free` random router;
- auto-routing across different model IDs.

Before any experiment:
1. query current OpenRouter model metadata/API;
2. discover exact model IDs currently marked free;
3. verify exact current input/output price = 0;
4. verify text generation;
5. verify sufficient context for the benchmark;
6. verify structured-output support, or at minimum stable JSON output compatibility.

Create:

```text
artifacts/g2_3_3/free_model_discovery.json
docs/G2_3_3_FREE_MODEL_SELECTION.md
```

Record:
- model slug;
- model family;
- context length;
- structured-output support;
- current price;
- provider choices;
- free-tier limitations.

Do not rely on stale hard-coded model availability.

---

# 5. Select exact models, not the random free router

Never use:

```text
openrouter/free
```

because it may route different requests to different models.

For experimental validity, use exact current `:free` model slugs or exact free model IDs.

Target a cross-family set.

Preferred selection strategy:
- first: strongest practical current free Qwen-family instruction model;
- second: strongest practical current free non-Qwen model;
- third: another independent strong free model if request limits/time permit.

Examples to investigate, not blindly assume:
- current Qwen free instruction models;
- current GPT-OSS free models;
- current Nemotron free models;
- current other strong free instruction models.

Verify exact live availability before selecting.

---

# 6. Provider consistency

Within one model run:
- pin a single provider where possible;
- use the same provider for N and C;
- disable provider fallback;
- require requested parameters if OpenRouter supports it.

If the free model does not allow stable provider pinning:
- document the limitation;
- record provider metadata for every response;
- do NOT compare N/C pairs if the two members were served by different providers;
- rerun mismatched pairs later if possible under the same provider.

Never silently mix providers within a paired comparison.

---

# 7. Privacy

Send only synthetic benchmark content.

Do NOT send:
- PCT book;
- personal documents;
- arbitrary repository source;
- private notes;
- personal identifiers.

Use the strictest available no-data-collection / ZDR provider setting compatible with the selected free model where possible.

If privacy routing makes a candidate unavailable:
- prefer another free model;
- do not relax privacy settings silently.

---

# 8. Freeze protocol

Create:

```text
artifacts/g2_3_3/frozen_protocol_manifest.json
```

Hash and freeze:
- 250 trial IDs;
- common system instruction;
- N builder;
- C builder;
- R builder if used;
- Regime A template;
- Regime B template;
- output schema;
- validator;
- scoring;
- corrected budget implementation.

All 250 trial IDs must exactly match G2.3.2.

---

# 9. Free-tier quota discovery

Before running experiments, determine current account/model request limits.

Record:
- apparent daily request limit;
- per-minute/request throttles;
- model/provider rate limits if exposed;
- whether limits differ by free model.

Do not attempt to bypass quotas.

Do not create extra accounts.

Do not rotate keys.

Create:

```text
artifacts/g2_3_3/free_quota_manifest.json
```

---

# 10. Resumable execution — mandatory

Because free models may have strict request limits, all cloud evaluation must be resumable.

Each completed request must be persisted immediately.

Use stable identifiers such as:

```text
model_slug
provider
regime
trial_id
condition
```

Before issuing a request:
- check whether a valid completed row already exists;
- never pay/reconsume a free request for already completed work unless that row is invalid.

On rate-limit exhaustion:
- save all state;
- stop cleanly;
- report exact progress;
- provide a resume command;
- next run must continue exactly where it stopped.

Never treat HTTP 429/rate limit as a model reasoning failure.

---

# 11. Smoke test per model

For each selected free model, run a minimal smoke stage first.

Keep request usage small.

Test:
- basic structured JSON;
- temporal current vs memory;
- hypothetical vs current;
- spatial relation;
- action choice.

If current quota is extremely low, reduce smoke calls to the minimum needed to establish transport compatibility.

Do not require semantic perfection.

---

# 12. Calibration policy

Do not waste a large proportion of the daily free quota on calibration.

Use a small fixed calibration subset adequate to verify:
- stable schema;
- latency;
- provider consistency;
- context compatibility;
- no transport errors.

Suggested:
- 5–10 paired trials per model,
unless quota is comfortably higher.

Do not tune prompts based on N/C outcomes.

Once compatibility is established, freeze settings.

---

# 13. Final evaluation

Goal per model:

```text
same frozen 250 paired trials
Regime A
Regime B
```

However, because free quotas may make this take several days:
- run in resumable batches;
- do not fabricate completion;
- do not reduce the final target simply to finish in one day.

The completed dataset may be accumulated across multiple days as long as:
- model slug remains unchanged;
- provider remains controlled;
- parameters remain unchanged;
- prompt hashes remain unchanged;
- model version/provider metadata are recorded.

If the underlying free model/version materially changes during the multi-day experiment:
- stop;
- version the dataset;
- do not silently merge incompatible runs.

---

# 14. Regime A

Use the frozen G2.3.2 Regime-A representation rules.

No common artificial token ceiling.

No silent truncation.

If a free model's context window is insufficient for specific trials:
- mark those trials unsupported;
- do not silently truncate;
- prefer a different free model with adequate context for the main replication.

---

# 15. Regime B

Use the corrected G2.3.2 fixed-budget implementation unchanged.

Required:
- N <= B
- C <= B
- fairness failures = 0

Do not increase B because cloud models have larger context windows.

---

# 16. Raw vs validated scoring

Store separately:
- raw model output;
- parsed response;
- raw correctness;
- validator decision;
- validated result.

Do not let validation hide model errors.

---

# 17. Cross-model results

For every completed model report:

## Regime A
- N wins;
- C wins;
- ties;
- raw N/C accuracy;
- validated N/C accuracy;
- paired exact/McNemar result;
- token use;
- latency.

## Regime B
same.

Compare against frozen local result:

```text
Local qwen3:0.6b:
A = C8 / N0 / T242
B = C0 / N0 / T250
```

Do not pool models into one sample.

---

# 18. Interpretation

Create:

```text
docs/G2_3_3_CROSS_MODEL_INTERPRETATION.md
```

Evaluate:
- whether chronology advantage persists;
- disappears;
- reverses;
- only appears in Regime A;
- only appears under fixed budgets;
- correlates with model capability/family;
- stems from source/action formatting;
- validator changes outcome.

Do not claim a general "capability threshold" unless replicated across multiple model sizes/families.

Do not claim NowMind superiority unless paired evidence supports it.

---

# 19. Tests

Add tests for:
- API key redaction;
- plaintext key never enters Git;
- OpenRouterBackend request shape;
- exact model selection;
- free-model price hard gate;
- rejection of nonzero-price models;
- rejection of `openrouter/free`;
- resumable state;
- duplicate-request prevention;
- provider matching within N/C pairs;
- provider fallback disabled where supported;
- frozen trial hashes;
- unchanged Regime B budget;
- synthetic-only payload guard;
- all prior tests.

Run:

```text
python -m pytest
```

---

# 20. Artifacts

Create at minimum:

```text
artifacts/g2_3_3/free_model_discovery.json
artifacts/g2_3_3/free_quota_manifest.json
artifacts/g2_3_3/frozen_protocol_manifest.json
artifacts/g2_3_3/run_state.json
artifacts/g2_3_3/<model_slug_safe>/smoke.json
artifacts/g2_3_3/<model_slug_safe>/calibration.json
artifacts/g2_3_3/<model_slug_safe>/regime_a_results.jsonl
artifacts/g2_3_3/<model_slug_safe>/regime_b_results.jsonl
artifacts/g2_3_3/<model_slug_safe>/pairwise.json
artifacts/g2_3_3/<model_slug_safe>/metrics.json
artifacts/g2_3_3/<model_slug_safe>/provider_manifest.json
artifacts/g2_3_3/<model_slug_safe>/statistical_summary.md
artifacts/g2_3_3/g2_3_3_cross_model_summary.md
```

No API keys in artifacts.

---

# 21. Stop conditions

Stop and report instead of improvising if:
- API key migration fails;
- no suitable free exact model exists;
- candidate price is nonzero;
- selected model requires paid fallback;
- provider matching cannot be maintained;
- Regime B fairness fails;
- trial hashes differ;
- context truncation would be required;
- account free quota is exhausted.

Quota exhaustion is a normal resumable stop, not failure.

---

# 22. Completion / progress report

Return:

1. API-key migration status;
2. confirmation plaintext key file deleted after successful migration;
3. Git/security status;
4. full pytest result;
5. current exact free models discovered;
6. selected model(s) and why;
7. exact current price verification ($0/$0);
8. provider/privacy settings;
9. quota/rate-limit findings;
10. smoke results;
11. calibration results;
12. frozen trial-hash verification;
13. progress count per model;
14. whether run completed or paused for free quota;
15. resume command if paused;
16. Regime A results for any completed model;
17. Regime B results for any completed model;
18. paired statistics;
19. comparison to qwen3:0.6b;
20. whether C>N persists, disappears, or reverses;
21. whether any NowMind advantage is supported;
22. next free model recommended;
23. whether enough cross-model evidence exists for Julian technical review.

Never claim consciousness, sentience, identity, phenomenal awareness, or general AI superiority.

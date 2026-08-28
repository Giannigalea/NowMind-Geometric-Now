# ELEVENTH CODEX TASK — Fix Ollama Structured Output Compatibility and Resume G2.3.1

## Purpose

Do not change NowMind architecture or the benchmark.

Ollama is installed and the approved local models are present:

- `qwen3:1.7b`
- `gemma3:1b`

The previous G2.3.1 continuation stopped because both models failed a prompt-only JSON smoke test.

Before concluding that the models are unsuitable, use Ollama's native structured-output API correctly.

This is a neutral backend compatibility fix, not prompt tuning.

---

# 1. Preserve everything

Do not change:
- G1-G2.3 cognitive semantics;
- benchmark ground truth;
- N/C/R representation content;
- scoring rules;
- validator rules;
- final evaluation trial set.

All existing 109+ tests must remain green.

Do not pull another model yet.

---

# 2. Diagnose the existing smoke failures first

Read:

```text
artifacts/g2_3_1/qwen3_1_7b/smoke_failure_manifest.json
artifacts/g2_3_1/gemma3_1b/smoke_failure_manifest.json
artifacts/g2_3_1/model_install_log.md
```

Create:

```text
docs/G2_3_1_SMOKE_FAILURE_DIAGNOSIS.md
```

For each model determine exactly what failed:

- HTTP/API error?
- process/model load failure?
- timeout?
- out of memory?
- empty `message.content`?
- content placed in `message.thinking`?
- malformed JSON?
- valid JSON but wrong schema?
- correct schema but wrong answer?
- context allocation failure?
- parser bug?

Preserve raw API response metadata where safe.

Do not infer "model cannot do JSON" unless the failure actually supports that conclusion.

---

# 3. Use Ollama's native structured outputs

For G2.3 model calls, use:

```text
POST http://127.0.0.1:11434/api/chat
```

with:

```json
{
  "stream": false,
  "format": <JSON_SCHEMA>
}
```

Prefer the exact JSON schema already defined for `ModelResponse`.

Do not rely only on natural-language instructions like:

```text
Return JSON only
```

The prompt may still describe the schema, but the API `format` field must enforce it.

---

# 4. Define one canonical G2.3 response schema

Use a JSON schema matching the existing benchmark output contract.

Conceptually:

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": [
        "TRUE",
        "FALSE",
        "UNKNOWN",
        "CONTRADICTORY",
        "ANSWER",
        "ACTION"
      ]
    },
    "answer": {
      "type": ["string", "null"]
    },
    "source_used": {
      "type": "string",
      "enum": [
        "observed_now",
        "inferred_now",
        "reconstructed_memory",
        "hypothetical_future",
        "mixed",
        "none"
      ]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "action": {
      "type": ["string", "null"]
    },
    "assumptions": {
      "type": "array",
      "items": {"type": "string"}
    },
    "explanation": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": [
    "status",
    "answer",
    "source_used",
    "confidence",
    "action",
    "assumptions",
    "explanation"
  ]
}
```

If the current G2.3 schema differs, use the existing authoritative schema rather than silently replacing it.

Use one schema for N/C/R.

---

# 5. Qwen3 thinking behavior

Qwen3 supports a separate thinking channel.

For this G2.3 benchmark, set:

```json
"think": false
```

for `qwen3:1.7b`.

Reason:
- G2.3 is comparing representation conditions, not chain-of-thought behavior;
- structured final output should appear in `message.content`;
- disabling thinking reduces unnecessary context/runtime pressure;
- the setting must be identical for N/C/R using Qwen.

Record this in the model manifest.

Do not store or expose hidden reasoning traces as benchmark evidence.

For a non-thinking model, omit unsupported thinking settings rather than inventing behavior.

---

# 6. Parse the correct response field

For `/api/chat`, parse:

```text
message.content
```

as the final structured result.

Do not concatenate:

```text
message.thinking
```

with:

```text
message.content
```

for JSON validation.

If `message.thinking` exists, treat it as separate model metadata and do not use it for scoring.

---

# 7. Deterministic generation

Use:

```text
temperature = 0
stream = false
```

and preserve all other fixed generation parameters.

If Ollama/model supports a seed used by the existing experiment, record it.

Apply equivalent generation settings to N/C/R.

---

# 8. Structured-output smoke test

Run a minimal test against `qwen3:1.7b` first.

Use an explicit small schema, for example:

```json
{
  "type": "object",
  "properties": {
    "answer": {"type": "string"}
  },
  "required": ["answer"]
}
```

Ask:

```text
What is the capital of France?
```

Success criteria:

1. HTTP request succeeds;
2. model completes;
3. `message.content` parses as JSON;
4. schema validates;
5. answer semantically equals Paris.

Do not require byte-for-byte output formatting.

Record:
- total duration;
- load duration;
- prompt eval count;
- eval count;
- context setting;
- response content;
- parse result.

---

# 9. If explicit JSON schema fails

Try, in this order:

## A
Explicit JSON schema in `format`.

## B
`format: "json"` with the same neutral JSON instruction.

Do not immediately switch models.

If both fail, classify the actual failure.

---

# 10. Context settings

The previous smoke attempt reduced `num_ctx` as far as 512.

Do not assume smaller context fixes JSON formatting.

For smoke testing, use a modest context such as:

```text
2048
```

if the machine can load it.

Then calibration should progressively determine practical context limits.

Do not allocate 40K context immediately on this 8 GB machine.

Suggested context feasibility sequence for Qwen 1.7B:

```text
2048
4096
8192
16384
```

Stop increasing when resource pressure becomes unacceptable.

Regime A must later mark unsupported history cohorts rather than silently truncating.

---

# 11. Test Gemma after Qwen

If Qwen passes structured smoke:
- keep it as primary;
- then optionally verify `gemma3:1b` with the same structured-output mechanism.

If Qwen still fails for a genuine runtime/resource reason:
- test Gemma using the same schema mechanism.

Do not pull another model during this task unless both fail for genuine model/runtime incompatibility and Jonathan later authorizes another model.

---

# 12. Backend implementation

Update `OllamaBackend` so it can send:

- `format` JSON schema;
- `stream: false`;
- model-specific `think` option;
- deterministic options;
- configurable context.

The backend must preserve:
- raw API response;
- final `message.content`;
- token/eval counters where Ollama provides them;
- latency;
- model identity.

Add tests with mocked HTTP responses.

This compatibility layer must apply equally to N/C/R.

---

# 13. No benchmark tuning

Do not modify:
- N structured representation;
- C chronological representation;
- task questions;
- expected answers;
- benchmark families;

to get a model through smoke testing.

Only output transport/schema compatibility may change.

Update prompt/version hashes if the schema description in the prompt genuinely changes, and document why.

---

# 14. Resume G2.3.1 after smoke success

As soon as at least one approved model passes the structured smoke test:

1. resume `NINTH_CODEX_TASK_G2_3_1.md`;
2. run its 50-pair calibration;
3. freeze the prompts/schema/settings;
4. estimate runtime;
5. select the predeclared final pair count;
6. run Regime A where context fits;
7. run Regime B under the fixed equal budget.

Do not stop again merely because a small local model has imperfect benchmark accuracy. Imperfect reasoning is exactly what we need to measure.

---

# 15. Calibration sanity threshold

JSON does not need to be correct semantically on every calibration trial.

Calibration is successful if:
- the API is stable;
- structured response parse rate is high enough for meaningful evaluation;
- no repeated crashes/OOM;
- N/C/R fairness remains intact.

Do not demand 100% model accuracy before final evaluation.

---

# 16. Resource safety

This machine has about 8 GB RAM.

Do not:
- disable system protections;
- change pagefile automatically;
- pull larger models;
- allocate extreme context;
- run multiple models concurrently.

Run one model at a time.

Monitor for severe memory pressure.

---

# 17. New artifacts

Create:

```text
artifacts/g2_3_1/structured_output_diagnosis.json
artifacts/g2_3_1/structured_output_smoke_results.json
```

Update:
- model manifest;
- setup log;
- experiment manifest;
- STATUS.

Preserve the old failure manifests.

Do not overwrite history as though the first smoke attempt never happened.

---

# 18. Final completion report

Return:

1. exact original smoke failure cause for Qwen;
2. exact original smoke failure cause for Gemma;
3. whether `format: <schema>` was implemented;
4. whether Qwen `think:false` was implemented;
5. structured smoke result for Qwen;
6. structured smoke result for Gemma if tested;
7. practical context setting reached;
8. G2.3.1 calibration result;
9. final real-model trial count;
10. Regime A N/C/R metrics;
11. Regime B N/C/R metrics;
12. N-win/C-win/tie;
13. raw vs validated accuracy;
14. source-confusion metrics;
15. context/token/latency results;
16. validator-prevented errors;
17. full pytest result;
18. browser demo URL;
19. artifact paths;
20. deviations;
21. whether there is now genuine real-model evidence;
22. whether the project is ready for Julian technical review.

Do not claim a representation advantage unless paired real-model results support it.

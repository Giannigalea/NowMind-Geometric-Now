# G2.3.1 Smoke Failure Diagnosis

Date: 2026-08-23

## Summary

The original G2.3.1 smoke failures were not JSON-formatting failures and not
parser failures. They occurred before the models produced any final content.

The structured-output follow-up implemented the requested Ollama-native
transport path:

- endpoint: `POST http://127.0.0.1:11434/api/chat`
- `stream: false`
- `format: <JSON_SCHEMA>`
- Qwen3 `think: false`
- parse only `message.content`

The follow-up smoke tests still failed before `message.content` existed. The
current blocker is local model initialization/resource failure on this machine,
not evidence that either model cannot follow JSON.

## Original Prompt-Only Smoke Diagnosis

| Model | Failure class | Evidence | Content produced |
| --- | --- | --- | --- |
| `qwen3:1.7b` | Context allocation / model-load failure | KV-cache and CPU buffer allocation errors from `num_ctx=40960` down to `1024`; `std::bad_alloc` at `512` | none |
| `gemma3:1b` | Model worker initialization failure | worker terminated with `0xe06d7363`; `std::bad_alloc` at `1024` | none |

Original failures were not:

- empty `message.content`;
- content only in `message.thinking`;
- malformed JSON;
- valid JSON with wrong schema;
- correct schema with wrong answer;
- parser bugs.

They were HTTP 500/runtime failures before scoring could begin.

## Structured-Output Follow-Up

### qwen3:1.7b

The structured schema request at `num_ctx=2048` failed with HTTP 500:

```text
llama-server reported out-of-memory during startup:
failed to allocate CPU buffer of size 159383552
failed to allocate buffer for kv cache
```

The same schema request at `num_ctx=512` failed with:

```text
llama-server process has terminated: exit status 0xe06d7363
```

The `format: "json"` fallback at `num_ctx=512` also failed with the same worker
termination pattern.

Conclusion: Qwen did not reach structured output generation. Disabling thinking
and using `/api/chat` did not remove the local resource/runtime failure.

### gemma3:1b

The structured schema request at `num_ctx=2048` failed with:

```text
llama-server process has terminated: exit status 0xe06d7363
```

The same schema request at `num_ctx=512` failed with the same worker termination
pattern.

The `format: "json"` fallback at `num_ctx=512` also failed with the same worker
termination pattern.

Conclusion: Gemma did not reach structured output generation. The failure is a
local model worker/runtime failure, not a JSON/schema failure.

## Benchmark Resume Decision

G2.3.1 calibration was not started because no approved local model passed the
required structured-output smoke test.

No G1-G2.3 cognitive semantics, benchmark ground truth, N/C/R representation
content, scoring rules, validator rules, or final evaluation trial set were
changed.

# G2.3.3 Free Model Selection

Date: 2026-08-28T09:53:29.411239+00:00

Only exact OpenRouter models with current input price `0` and output price `0` are eligible. `openrouter/free` is rejected because it is a random router.

Discovered exact free text models: `18`

## Selected Models

- `z-ai/glm-5.2:free` family=z-ai context=256000 price=input `0` output `0` structured=True
- `nvidia/nemotron-3-super-120b-a12b:free` family=nvidia context=262144 price=input `0` output `0` structured=True
- `google/gemma-4-26b-a4b-it:free` family=google context=262144 price=input `0` output `0` structured=True

No exact Qwen-family `$0/$0` model was present in the live metadata at discovery time.

Provider settings for all model calls request fallback disabled, required parameters enabled, and data collection denied. If a model cannot run under those settings, it is stopped rather than silently relaxed.

## Smoke Sweep Note

After the selected native structured-output candidates failed to produce a usable
smoke row, the remaining exact `$0/$0` text models were tested through the
task-authorized prompt-only JSON compatibility path when they did not advertise
native `response_format`. This did not relax the price gate, provider fallback
rule, required-parameter request, or `data_collection=deny`.

Current result: no exact-free model has produced a schema-valid G2.3.3 smoke row
yet. `cohere/north-mini-code:free` and
`inclusionai/ling-3.0-flash-fin:free` reached providers at provider cost `0`,
but their outputs failed the frozen proposal schema. Other candidates were
rate-limited, privacy-blocked, required-parameter blocked, or harness-blocked.

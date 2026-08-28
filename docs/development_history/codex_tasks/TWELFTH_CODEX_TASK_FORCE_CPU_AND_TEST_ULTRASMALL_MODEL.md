# TWELFTH CODEX TASK — Force CPU/AVX2, Diagnose Ollama Allocation Failure, and Test Qwen3 0.6B

## Purpose

Do not change NowMind or the G2.3 benchmark.

Current state:
- Ollama 0.32.15 is installed.
- `qwen3:1.7b` and `gemma3:1b` are installed.
- Both fail before producing `message.content`.
- Qwen fails during model/context allocation.
- Gemma fails with worker termination / `std::bad_alloc`.
- Both fail even at `num_ctx=512`.
- Structured-output transport is already implemented correctly.

This task is the final controlled local-runtime diagnostic before deciding this machine is unsuitable for real-model G2.3.1 evaluation.

The machine has:
- Intel i5-8265U
- 7.88 GB RAM
- Intel UHD Graphics 620
- models stored on D:

The i5-8265U supports AVX2.

## 1. Preserve project state

Do not modify:
- G1-G2.3 architecture
- benchmark prompts
- representations
- scoring
- validators
- trial generators

All current tests must remain green.

Do not delete existing failure artifacts.

## 2. Inspect the actual Ollama server log

Before changing anything, collect the relevant portion of:

`%LOCALAPPDATA%\Ollama\server.log`

and, if needed, the immediately previous rotated server log.

Create:

`docs/G2_3_1_OLLAMA_ALLOCATION_DIAGNOSIS.md`

Record:
- which LLM library Ollama selected
- whether Intel/Vulkan/GPU discovery occurred
- total/available system memory reported
- memory.required/full/kv/graph values if present
- exact allocation error
- whether failure occurs before runner startup or after model load begins

Do not include username, hostname, or serial identifiers.

## 3. Stop Ollama cleanly

Ensure no duplicate Ollama server or loaded model is consuming memory.

Use `ollama ps` and stop loaded models if necessary.

Quit the tray/server cleanly before launching the diagnostic server.

Do not kill unrelated processes.

## 4. Force CPU AVX2

Launch a diagnostic Ollama server from PowerShell with temporary process-local environment variables:

```powershell
$env:OLLAMA_LLM_LIBRARY="cpu_avx2"
$env:OLLAMA_DEBUG="1"
$env:OLLAMA_MODELS="D:\OllamaModels"
```

Then start the Ollama server using:

```powershell
ollama serve
```

or the correct absolute executable path if PATH is stale.

Keep the server bound to localhost.

Do not make the CPU override permanent yet.

## 5. Confirm CPU library selection

Inspect the server log/stdout.

The diagnostic is valid only if the log confirms CPU/AVX2 is actually selected or used.

If `cpu_avx2` is unavailable:
- record available LLM libraries
- try `cpu_avx` if available
- then `cpu` only as a last compatibility test

Do not call this a CPU-only test if logs show GPU/Vulkan execution.

## 6. Re-test Gemma 1B first

With forced CPU/AVX2, test:

`gemma3:1b`

Use:
- `num_ctx=512`
- `stream=false`
- existing structured JSON schema
- temperature 0
- one request only
- no other model loaded concurrently
- keep-alive 0 after request if supported

If it succeeds, repeat at:
- 1024
- 2048

Stop increasing if memory pressure becomes unacceptable.

If it fails, preserve exact memory diagnostics.

## 7. Re-test Qwen 1.7B only if useful

If Gemma succeeds, optionally test `qwen3:1.7b` at 512/1024 if memory headroom looks sufficient.

If Gemma still fails with a clear allocation error, do not waste time repeatedly loading Qwen 1.7B.

Proceed to the ultra-small model.

## 8. Pull the authorized ultra-small model

You are explicitly authorized to pull:

`qwen3:0.6b`

from the official Ollama registry.

Expected model size is about 523 MB.

Run:

```powershell
ollama pull qwen3:0.6b
```

Keep it under:

`D:\OllamaModels`

Do not pull any larger or additional models during this task.

## 9. Test Qwen3 0.6B under forced CPU

Use:
- `think:false`
- native JSON schema in `format`
- `stream:false`
- temperature 0
- one request at a time

Context sequence:

```text
512
1024
2048
4096
```

Start at 512 only to prove allocation.

If successful, increase sequentially until 4096 succeeds or resource failure occurs.

Record:
- model load time
- total duration
- prompt eval count
- output eval count
- selected compute library
- Ollama memory diagnostics
- response content

## 10. Smoke task

Question:

`What is the capital of France?`

Schema:

```json
{
  "type": "object",
  "properties": {
    "answer": {"type": "string"}
  },
  "required": ["answer"]
}
```

Success means:
- model loads
- HTTP succeeds
- `message.content` exists
- JSON parses
- schema validates
- answer is semantically Paris

## 11. If qwen3:0.6b succeeds

Do not immediately run the full 1000-trial benchmark.

First:
1. update the real-model manifest
2. run the existing 50-pair G2.3.1 calibration
3. measure parse rate, accuracy, latency, memory pressure, practical context, and estimated time for 250/500/1000 paired trials

Because this model is very small, its reasoning may be weak. That is acceptable.

Do not reject it simply because calibration accuracy is imperfect.

If infrastructure is stable, select a fixed final count before examining final outcomes:
- minimum useful diagnostic: 250 paired trials
- preferred: 500 if runtime is reasonable
- 1000 only if practical

Then resume the existing G2.3.1 evaluation unchanged.

## 12. If qwen3:0.6b also fails under confirmed CPU/AVX2

Stop local-model experimentation on this machine.

Do not:
- pull more models
- change pagefile
- disable security
- install alternate GPU runtimes
- alter Windows memory settings
- cycle through more quantizations

Create:

`docs/G2_3_1_LOCAL_HARDWARE_LIMIT_CONCLUSION.md`

Recommend one of:
1. run the existing benchmark on another local machine with at least 16 GB RAM
2. upgrade RAM if practical
3. run the same local Ollama benchmark on another LAN/offline workstation
4. only with explicit later authorization, test an alternate local runtime such as llama.cpp

Do not change the benchmark to accommodate hardware failure.

## 13. Evidence artifacts

Create/update:

```text
artifacts/g2_3_1/cpu_backend_diagnostic.json
artifacts/g2_3_1/qwen3_0_6b_smoke.json
artifacts/g2_3_1/ollama_memory_diagnostics.md
```

If calibration succeeds:

```text
artifacts/g2_3_1/qwen3_0_6b/calibration_results.json
artifacts/g2_3_1/qwen3_0_6b/frozen_experiment_manifest.json
```

Preserve all earlier failure artifacts.

## 14. Final tests

Run:

`python -m pytest`

All previous tests must remain green.

## 15. Completion report

Return:
1. Ollama selected library before override
2. whether forced `cpu_avx2` was available
3. whether logs confirmed CPU/AVX2 use
4. relevant memory requirement/availability diagnostics
5. Gemma 1B forced-CPU result
6. Qwen 1.7B forced-CPU result if attempted
7. Qwen3 0.6B pull result
8. Qwen3 0.6B smoke results by context size
9. whether structured JSON output succeeded
10. if smoke succeeded, 50-pair calibration result
11. estimated benchmark runtime
12. selected final pair count if evaluation resumed
13. any real N/C results produced
14. full pytest result
15. artifact paths
16. whether the blocker was GPU/autodetection, RAM/allocation, or another runtime issue
17. whether this machine is viable for G2.3.1
18. recommended next action if not viable

Do not claim real-model evidence unless a real model actually completed paired benchmark trials.

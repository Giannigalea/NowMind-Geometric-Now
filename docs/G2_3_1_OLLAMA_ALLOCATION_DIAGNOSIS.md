# G2.3.1 Ollama Allocation Diagnosis

Date: 2026-08-24

## Summary

The original failures were caused by Ollama runtime allocation behavior on this
machine, not by the NowMind G2.3 benchmark prompts, parser, validator, or JSON
schema transport.

The default Ollama server selected Vulkan on the discrete Radeon 520 GPU. A
temporary diagnostic server forced `OLLAMA_LLM_LIBRARY=cpu_avx2`, used
`OLLAMA_MODELS=D:\OllamaModels`, and remained bound to `127.0.0.1:11434`.
Logs confirmed GPU libraries were skipped at user request and that model
runners reported CPU AVX2 support.

## Before CPU Override

Observed default server behavior:

- `OLLAMA_LLM_LIBRARY` was empty.
- `OLLAMA_VULKAN` was true.
- Intel UHD Graphics 620 was discovered and dropped by default.
- Radeon 520 Vulkan was selected.
- Reported Radeon memory: total `2.0 GiB`, available `1.7 GiB`.
- Default context from VRAM: `4096`.

The earlier model failures occurred before useful `message.content` was
available.

## Forced CPU/AVX2 Diagnostic

Temporary process environment:

```text
OLLAMA_LLM_LIBRARY=cpu_avx2
OLLAMA_DEBUG=1
OLLAMA_MODELS=D:\OllamaModels
OLLAMA_HOST=127.0.0.1:11434
```

Server evidence:

- `OLLAMA_LLM_LIBRARY:cpu_avx2` appeared in server config.
- CUDA, ROCm, and Vulkan libraries were skipped at user request.
- Inference compute was CPU-only.
- Runner CPU feature log included `AVX2 = 1`.
- Runner `vram` was `0 B`.
- Model mmap was disabled because the runner was CPU.

## Successful Forced-CPU Smoke Observations

Under a cleaner memory state, forced CPU/AVX2 smoke tests succeeded for:

- `gemma3:1b` at contexts `512`, `1024`, and `2048`.
- `qwen3:1.7b` at contexts `512`, `1024`, and `2048`.

All successful smoke tests used native Ollama JSON schema transport, returned
`message.content`, parsed as JSON, matched the minimal schema, and answered
Paris.

## Calibration Result

`qwen3:1.7b` completed the 50-pair G2.3.1 calibration:

- Paired trials: `50`
- Rows: `400`
- Model calls: `300`
- Wall clock: `15975.324` seconds
- Estimated seconds per pair: `319.506`
- Calibration artifact:
  `artifacts/g2_3_1/qwen3_1_7b/calibration_results.json`

This proves the model could load and run real paired benchmark trials under
some CPU memory conditions.

## Final Evaluation Failure

The selected 250-pair final run wrote the frozen manifest first, then attempted
evaluation. The model calls failed at load with CPU allocation errors, while the
symbolic rows completed. The resulting final files are failure evidence, not
valid real-model N/C evidence.

Representative error:

```text
ggml_backend_cpu_buffer_type_alloc_buffer: failed to allocate buffer of size 692725760
alloc_tensor_range: failed to allocate CPU buffer of size 692725760
error loading model: unable to allocate CPU buffer
```

Final row file:

```text
artifacts/g2_3_1/qwen3_1_7b/evaluation_trial_results.jsonl
```

The row count is complete (`2000` rows for `250 x 8`), but all real Ollama rows
are runtime failures. Therefore the final evaluation does not support any
real-model representation-effect claim.

## Ultra-Small Model Failure

`qwen3:0.6b` was pulled under `D:\OllamaModels` and tested at `num_ctx=512`.
It also failed before `message.content`.

Server memory/load evidence:

```text
system memory: total 7.9 GiB, free 1.3 GiB, free_swap 180.9 MiB
CPU: 8064 MiB, 1406 MiB free
Host projected: 378 MiB = model 295 + context 56 + compute 26
CPU_REPACK projected: 196 MiB
failed to allocate CPU buffer of size 310250496
```

Smoke artifact:

```text
artifacts/g2_3_1/qwen3_0_6b_smoke.json
```

## Diagnosis

The blocker is local runtime memory allocation on this 8 GB RAM machine. The
initial failure path was worsened by Vulkan/GPU autodetection, but forced
CPU/AVX2 does not make the machine reliably viable. The key limiting condition
is low free RAM and very low free swap during model load.

No benchmark, prompt, scoring, validator, or NowMind architecture change was
made to improve results.

## 2026-08-26 Pagefile Workaround Update

The low-swap conclusion above was superseded after Windows pagefile headroom was
increased and the machine was restarted. Under the same temporary CPU/AVX2
diagnostic configuration, `qwen3:0.6b` loaded successfully and completed the
real local G2.3.1 final evaluation.

Post-pagefile smoke:

- Model: `qwen3:0.6b`
- Contexts passed: `512`, `1024`, `2048`, `4096`
- Artifact: `artifacts/g2_3_1/qwen3_0_6b_smoke_after_pagefile.json`

Post-pagefile calibration:

- Paired trials: `50`
- Rows: `400`
- Model calls: `300`
- Artifact: `artifacts/g2_3_1/qwen3_0_6b/calibration_results.json`

Post-pagefile final evaluation:

- Frozen manifest written before final rows:
  `artifacts/g2_3_1/qwen3_0_6b/frozen_experiment_manifest.json`
- Paired trials: `250`
- Rows: `2000`
- Model calls: `1500`
- Context overflows: `248`
- Connection-refused rows after checkpoint cleanup: `0`
- Artifact: `artifacts/g2_3_1/qwen3_0_6b/evaluation_results.json`

The final result is valid real local model evidence for `qwen3:0.6b`, but it
does not support a NowMind-over-chronology advantage. Validated N/C comparison:

- Regime A: C better `8`, N better `0`, tied `242`
- Regime B: C better `0`, N better `0`, tied `250`

The G2.3 fairness invariant still failed because provider token counts exceeded
the fixed budget in `166` of `500` checked N/C pairs.

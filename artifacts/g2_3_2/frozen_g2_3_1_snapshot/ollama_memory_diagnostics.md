# Ollama Memory Diagnostics

Date: 2026-08-24

## Default Server

- Selected library: Vulkan.
- Selected device: Radeon 520.
- Reported VRAM: total `2.0 GiB`, available `1.7 GiB`.
- Intel UHD Graphics 620 was discovered and dropped.
- Default context from VRAM: `4096`.

## Forced CPU/AVX2 Server

- Temporary `OLLAMA_LLM_LIBRARY=cpu_avx2`.
- CUDA, ROCm, and Vulkan libraries skipped at user request.
- Compute selected: CPU.
- Runner CPU feature line included `AVX2 = 1`.
- Runner VRAM: `0 B`.

## Successful Forced-CPU Smoke

- `gemma3:1b`: passed at `512`, `1024`, `2048`.
- `qwen3:1.7b`: passed at `512`, `1024`, `2048`.
- Native `/api/chat` JSON schema returned valid `message.content`.

## G2.3.1 Calibration

- Model: `qwen3:1.7b`.
- Paired trials: `50`.
- Rows: `400`.
- Wall clock: `15975.324` seconds.
- Model calls: `300`.
- Artifact: `artifacts/g2_3_1/qwen3_1_7b/calibration_results.json`.

## Final Evaluation Failure

- Selected final count: `250` paired trials.
- Frozen manifest was written before final rows.
- Real model calls failed at load with:

```text
failed to allocate CPU buffer of size 692725760
```

- The final row file is complete as failure evidence (`2000` rows), but the
  real Ollama rows have empty output and parse failures.

## Qwen3 0.6B Failure

- Pull succeeded under `D:\OllamaModels`.
- Smoke attempted first required context: `512`.
- HTTP result: `500`.
- Server load diagnostics:

```text
system memory total: 7.9 GiB
system memory free: 1.3 GiB
free swap: 180.9 MiB
projected Host memory: 378 MiB
projected CPU_REPACK memory: 196 MiB
failed allocation: 310250496 bytes
```

## Interpretation

The machine is not reliably viable for G2.3.1 real local model evaluation. The
initial GPU/Vulkan path was a blocker, and forced CPU/AVX2 solved that part, but
the remaining RAM/swap headroom is too low for reliable model allocation.

## 2026-08-26 Pagefile Follow-Up

After Windows pagefile headroom was increased and the machine restarted, the
ultra-small diagnostic path became viable under the same temporary CPU/AVX2
Ollama configuration.

- `qwen3:0.6b` passed smoke at contexts `512`, `1024`, `2048`, and `4096`.
- Smoke artifact:
  `artifacts/g2_3_1/qwen3_0_6b_smoke_after_pagefile.json`
- `qwen3:0.6b` completed 50-pair calibration:
  `artifacts/g2_3_1/qwen3_0_6b/calibration_results.json`
- `qwen3:0.6b` completed the predeclared 250-pair final evaluation:
  `artifacts/g2_3_1/qwen3_0_6b/evaluation_results.json`
- Final row file: `2000` rows, `250` paired trials, `0` connection-refused rows
  after the interrupted restart checkpoint was cleaned.
- Final invariants: `5` passed, `1` failed. The failed invariant is G2.3
  fairness: `166` of `500` checked N/C pairs exceeded the fixed token budget.

The final result is valid real local model evidence for `qwen3:0.6b`, but it
does not support a NowMind-over-chronology advantage.

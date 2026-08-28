# G2.3.1 Ollama Install And Model Log

## Install Result

- Ollama install status: installed.
- Install method: official Windows installer downloaded from `https://ollama.com/download/OllamaSetup.exe`.
- `winget` status: unavailable on this machine.
- Executable: `C:\Users\jonat\AppData\Local\Programs\Ollama\ollama.exe`.
- Ollama version: `0.32.15`.
- Local API verified at `http://127.0.0.1:11434/api/version`.

## Storage

- Desired model storage: `D:\OllamaModels`.
- Pulled model files are present under `D:\OllamaModels`.
- Total model-storage file bytes after both pulls: `2174614949`.
- Persistent user environment variable verification remains incomplete: later sandbox access to `HKCU:\Environment` did not show `OLLAMA_MODELS`, and `setx OLLAMA_MODELS D:\OllamaModels` failed with registry access denied.

## Commands Used

```powershell
winget --version
ollama --version
New-Item -ItemType Directory -Force 'D:\OllamaModels'
[Environment]::SetEnvironmentVariable('OLLAMA_MODELS', 'D:\OllamaModels', 'User')
Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'tmp\OllamaSetup.exe' -UseBasicParsing
Start-Process -FilePath 'tmp\OllamaSetup.exe' -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART' -Wait -PassThru -WindowStyle Hidden
$env:OLLAMA_MODELS = 'D:\OllamaModels'
Start-Process -FilePath 'C:\Users\jonat\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -PassThru -WindowStyle Hidden
ollama pull qwen3:1.7b
Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/pull' -Method Post -Body '{"name":"gemma3:1b","stream":false}' -ContentType 'application/json'
Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags'
Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/generate'
setx OLLAMA_MODELS D:\OllamaModels
```

## Model Pulls

| Model | Role | Digest | Size bytes | Result |
| --- | --- | --- | ---: | --- |
| `qwen3:1.7b` | primary | `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7` | `1359293444` | Pulled, smoke failed |
| `gemma3:1b` | fallback | `8648f39daa8fbf5b18c7b4e6a8fb4990c692751d49917417b8842ca5758e7ffc` | `815319791` | Pulled, smoke failed |

## Smoke Tests

Smoke prompt intent:

```text
Return valid JSON only:
{"answer":"Paris"}
Question: What is the capital of France?
```

No model produced a usable response.

### qwen3:1.7b

| Context | Approx elapsed | Outcome |
| ---: | ---: | --- |
| `40960` | `20.9s` | OOM, failed to allocate `4697620480` bytes |
| `4096` | `24.0s` | OOM, failed to allocate `335544320` bytes |
| `2048` | `26.9s` | OOM, failed to allocate `159383552` bytes |
| `1024` | `55.1s` | OOM, failed to allocate `75497472` bytes |
| `512` | `45.3s` | `std::bad_alloc` during context initialization |

### gemma3:1b

| Context | Approx elapsed | Outcome |
| ---: | ---: | --- |
| `4096` | `53.8s` | model worker terminated with `0xe06d7363` |
| `1024` | `41.0s` | `std::bad_alloc` during context initialization |
| `512` | `52.7s` | model worker terminated with `0xe06d7363` |

## Benchmark Resume Status

The existing G2.3.1 benchmark was not resumed because no approved local model passed the required JSON smoke test.

No G2.3 prompt, representation, validator, scoring rule, benchmark family, or NowMind cognitive architecture was changed to improve results.

## Structured-Output Follow-Up

The later compatibility pass changed the Ollama transport layer, not the
benchmark:

- endpoint changed to `POST http://127.0.0.1:11434/api/chat`;
- `format` now carries a native JSON schema;
- Qwen3 uses `think:false`;
- only `message.content` is parsed for scoring;
- `message.thinking`, if present, is metadata and is not concatenated into JSON.

Structured-output smoke tests still failed before any response content was
created:

| Model | Mode | Context | Outcome |
| --- | --- | ---: | --- |
| `qwen3:1.7b` | schema | `2048` | HTTP 500, KV-cache/CPU buffer allocation failure |
| `qwen3:1.7b` | schema | `512` | HTTP 500, worker terminated `0xe06d7363` |
| `qwen3:1.7b` | `format:"json"` fallback | `512` | HTTP 500, worker terminated `0xe06d7363` |
| `gemma3:1b` | schema | `2048` | HTTP 500, worker terminated `0xe06d7363` |
| `gemma3:1b` | schema | `512` | HTTP 500, worker terminated `0xe06d7363` |
| `gemma3:1b` | `format:"json"` fallback | `512` | HTTP 500, worker terminated `0xe06d7363` |

See:

```text
docs/G2_3_1_SMOKE_FAILURE_DIAGNOSIS.md
artifacts/g2_3_1/structured_output_diagnosis.json
artifacts/g2_3_1/structured_output_smoke_results.json
```

## Forced CPU/AVX2 Follow-Up

Temporary diagnostic environment:

```powershell
$env:OLLAMA_LLM_LIBRARY = 'cpu_avx2'
$env:OLLAMA_DEBUG = '1'
$env:OLLAMA_MODELS = 'D:\OllamaModels'
$env:OLLAMA_HOST = '127.0.0.1:11434'
ollama serve
```

Logs confirmed:

- CUDA/ROCm/Vulkan libraries skipped at user request.
- CPU inference selected.
- Runner CPU features included `AVX2 = 1`.
- Runner VRAM was `0 B`.

Forced CPU/AVX2 smoke:

| Model | Contexts | Outcome |
| --- | --- | --- |
| `gemma3:1b` | `512`, `1024`, `2048` | Passed native JSON-schema smoke |
| `qwen3:1.7b` | `512`, `1024`, `2048` | Passed native JSON-schema smoke |

Real G2.3.1 calibration:

| Model | Pairs | Rows | Outcome |
| --- | ---: | ---: | --- |
| `qwen3:1.7b` | `50` | `400` | Completed in `15975.324` seconds |

Predeclared final attempt:

| Model | Pairs | Rows | Outcome |
| --- | ---: | ---: | --- |
| `qwen3:1.7b` | `250` | `2000` | Frozen manifest written, but all real model rows failed model load |

Final failure:

```text
failed to allocate CPU buffer of size 692725760
```

Ultra-small diagnostic:

| Model | Digest | Size | Context | Outcome |
| --- | --- | ---: | ---: | --- |
| `qwen3:0.6b` | `7df6b6e09427` | `522 MB` | `512` | Failed model load |

Ultra-small failure:

```text
failed to allocate CPU buffer of size 310250496
```

Conclusion: this machine is not reliably viable for G2.3.1 final local-model
evaluation. The completed 50-pair calibration is real-model evidence; the
250-pair final attempt is runtime-failure evidence only.

## 2026-08-26 Pagefile Workaround and Final qwen3:0.6b Run

After Windows pagefile headroom was increased and the machine restarted,
`qwen3:0.6b` loaded under the same temporary CPU/AVX2 Ollama diagnostic
configuration.

Smoke after pagefile:

| Model | Contexts | Outcome |
| --- | --- | --- |
| `qwen3:0.6b` | `512`, `1024`, `2048`, `4096` | Passed native JSON-schema smoke |

Real G2.3.1 calibration after pagefile:

| Model | Pairs | Rows | Outcome |
| --- | ---: | ---: | --- |
| `qwen3:0.6b` | `50` | `400` | Completed in `8707.57` seconds |

Predeclared final evaluation after pagefile:

| Model | Pairs | Rows | Outcome |
| --- | ---: | ---: | --- |
| `qwen3:0.6b` | `250` | `2000` | Completed as real local model evidence |

Final validated N/C result:

| Regime | C better | N better | Tied |
| --- | ---: | ---: | ---: |
| A equal information | `8` | `0` | `242` |
| B fixed budget | `0` | `0` | `250` |

The final run failed the G2.3 fairness invariant because `166` of `500` checked
N/C pairs exceeded the fixed token budget. The result does not support a
NowMind-over-chronology real-model advantage.

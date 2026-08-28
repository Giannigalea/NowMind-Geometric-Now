# G2.3.1 Local Model Runtime Still Blocked

This file originally recorded that G2.3.1 could not begin because `ollama` was
not available on `PATH`.

That setup blocker is now superseded: Ollama was installed locally, the local
API is available at `http://127.0.0.1:11434`, and model files were pulled under
`D:\OllamaModels`.

G2.3.1 is still blocked, but for a different reason: the approved local models
failed the required smoke test on this low-memory machine before calibration
could begin.

A later compatibility pass implemented Ollama-native structured output via
`/api/chat`, native JSON-schema `format`, and Qwen3 `think:false`. The smoke
tests still failed before `message.content` existed.

## Commands Attempted

```powershell
ollama --version
ollama list
ollama pull qwen3:1.7b
Invoke-RestMethod http://127.0.0.1:11434/api/pull -Body '{"name":"gemma3:1b","stream":false}'
Invoke-RestMethod http://127.0.0.1:11434/api/generate
Invoke-RestMethod http://127.0.0.1:11434/api/chat
```

Initial PATH checks failed with:

```text
The term 'ollama' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

After installation, the local API reported:

```text
Ollama 0.32.15
qwen3:1.7b
gemma3:1b
```

Smoke testing then failed:

```text
qwen3:1.7b: local allocation / KV-cache failures down to num_ctx=512
gemma3:1b: worker termination or std::bad_alloc down to num_ctx=512
qwen3:1.7b structured-output smoke: HTTP 500 before message.content
gemma3:1b structured-output smoke: HTTP 500 before message.content
```

## Required Before Rerun

Free enough RAM for one of the installed local models to pass a small structured
JSON smoke test, or explicitly authorize a smaller model/runtime alternative.

Then rerun:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/generate
```

Then rerun the existing G2.3 experiment through the local Ollama backend without
changing prompts, validators, representations, scoring, or benchmark rules to
improve results.

## Status

Real local model benchmarking was not run. Existing G2.3 mock artifacts remain
infrastructure validation only, not real model evidence. See:

```text
artifacts/g2_3_1/ollama_setup_manifest.json
artifacts/g2_3_1/model_install_log.md
artifacts/g2_3_1/structured_output_diagnosis.json
artifacts/g2_3_1/structured_output_smoke_results.json
artifacts/g2_3_1/qwen3_1_7b/smoke_failure_manifest.json
artifacts/g2_3_1/gemma3_1b/smoke_failure_manifest.json
docs/G2_3_1_SMOKE_FAILURE_DIAGNOSIS.md
```

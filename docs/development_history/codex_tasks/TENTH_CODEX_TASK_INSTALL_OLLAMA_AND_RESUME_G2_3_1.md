# TENTH CODEX TASK — Install Ollama, Configure Local Models, and Resume G2.3.1

## User authorization

Jonathan has explicitly authorized you to perform the local installation and setup required for G2.3.1.

You are now allowed to:
- install Ollama locally on this Windows machine;
- configure Ollama model storage on drive D:;
- download/pull a suitable local instruction model;
- verify it;
- resume the existing G2.3.1 real-model benchmark.

Do not install unrelated software.

Do not use cloud model APIs.

---

# 1. Hardware constraints already known

Current machine:

```text
Windows 10 Home 25H2 build 26200
Intel Core i5-8265U
7.88 GB RAM
Intel UHD Graphics 620
C: approximately 18 GB free
D: approximately 498 GB free
```

Treat this as a CPU-first / low-memory machine.

Do not start with an 8B+ model.

---

# 2. Preserve project state

Before installation:

1. do not modify NowMind cognitive architecture;
2. do not modify the G2.3 benchmark or prompts;
3. keep all existing results/artifacts intact;
4. update `STATUS.md` only as needed.

This task is environment setup + continuation of G2.3.1.

---

# 3. Configure Ollama model location on D:

Use:

```text
D:\OllamaModels
```

as the desired model storage location.

Create the directory if needed.

Set the **user-level** environment variable:

```text
OLLAMA_MODELS=D:\OllamaModels
```

Use a safe Windows mechanism such as PowerShell/.NET or `setx`.

Do not overwrite unrelated environment variables.

After setting it, ensure the Ollama process launched later receives the new variable.

Document the exact command used.

---

# 4. Install Ollama

First check:

```powershell
ollama --version
```

If already installed, do not reinstall.

If not installed, prefer installation in this order:

## Option A — winget

Check:

```powershell
winget --version
```

If available, search/confirm the official Ollama package and install the official package.

Use a non-interactive/silent option where supported.

## Option B — official installer

If winget is unavailable or fails, download and run the official Ollama Windows installer from the official Ollama source.

Do not use third-party mirrors.

Do not install through an unofficial package manager.

If installation requires elevation/UAC that Codex cannot approve itself:
- launch the installer;
- clearly tell Jonathan what approval dialog to accept;
- continue automatically afterward if possible.

Do not weaken Windows security settings.

---

# 5. Refresh PATH / locate executable

After installation:

1. find `ollama.exe`;
2. make the current Codex shell/session aware of its path;
3. do not require a full reboot unless truly necessary.

If the executable is installed but PATH in the current shell is stale:
- invoke it by absolute path;
- or refresh the environment safely.

Verify:

```powershell
ollama --version
ollama list
```

Record the version.

---

# 6. Verify storage configuration

Confirm Ollama is using:

```text
D:\OllamaModels
```

for newly pulled models.

Do not place the large model data on C: if avoidable.

If Ollama was already running before the environment variable was set:
- stop/restart the Ollama application/service safely;
- verify the new process inherited `OLLAMA_MODELS`.

Do not delete any pre-existing models.

---

# 7. Select and pull the first model

Primary model:

```text
qwen3:1.7b
```

This is the preferred first model for the known hardware.

Run:

```powershell
ollama pull qwen3:1.7b
```

Do not pull a larger model first.

If `qwen3:1.7b` is not available from the installed Ollama registry for any reason, use the fallback:

```text
gemma3:1b
```

and document the reason.

Do not pull both initially unless the first model is demonstrated to work acceptably.

---

# 8. Smoke test the model

Run a short deterministic/local test.

Example intent:

```text
Return valid JSON only:
{"answer":"Paris"}
Question: What is the capital of France?
```

Verify:
- the model actually responds;
- output is local;
- JSON instruction following is at least usable;
- no crash/out-of-memory condition occurs.

Record approximate first-response latency.

If the model causes severe memory pressure or repeated failure:
- stop it;
- fall back to `gemma3:1b`;
- document the failure.

Do not change Windows pagefile/security settings automatically.

---

# 9. Verify Ollama locality

Confirm the model backend is local only.

Expected endpoint:

```text
http://127.0.0.1:11434
```

or equivalent localhost binding.

Do not expose Ollama to LAN/public interfaces.

Do not change `OLLAMA_HOST` to a public binding.

---

# 10. Resume G2.3.1 automatically

Once the model works, resume the existing:

```text
NINTH_CODEX_TASK_G2_3_1.md
```

Do not ask Jonathan to reissue that task.

Continue from the previous blocked state.

Use the real model through the existing `OllamaBackend`.

---

# 11. Calibration

Run the required 50-pair calibration first.

Check:
- N/C/R all execute;
- JSON parse rate;
- repair path if needed;
- latency;
- context usage;
- prompt fairness;
- no architecture/source violations.

Do not tune against final results.

Neutral schema-format compatibility fixes are allowed only if:
- applied equally to all representation conditions;
- versioned/documented;
- prompts are then frozen again before final evaluation.

---

# 12. Runtime feasibility decision

This machine is relatively modest.

After calibration, calculate an estimated duration for 1,000 paired trials.

If 1,000 paired trials are practical:
- run the full 1,000.

If the estimated runtime is excessive (for example many hours):
- select a scientifically reasonable fixed count before looking at final outcome;
- minimum preferred real-model sample: 250 paired trials;
- stronger target: 500;
- ideal: 1000.

Document:
- selected count;
- reason;
- estimated and actual runtime.

Do not reduce sample size because early results favor or disfavor NowMind.

---

# 13. Regime A context protection

For Regime A:

- never silently truncate;
- if H500/H1000 exceed model context, mark those cohorts unsupported;
- continue with cohorts that fit.

Record context overflow explicitly.

---

# 14. Regime B

Run the existing equal fixed-budget comparison unchanged.

N and C must use the same configured budget.

---

# 15. Do not install additional models yet unless justified

After completing the first real-model benchmark:

If `qwen3:1.7b` ran reliably and system resources remain comfortable, you may **recommend** a second model.

Do not automatically pull a second larger model as part of this task unless:
- the G2.3.1 specification explicitly requires it;
- runtime/storage clearly permit it;
- the first benchmark is already safely complete.

Preferred second candidates for later:
- `gemma3:1b` for a different small model family;
- `qwen3:4b` only if memory/runtime testing suggests it is practical.

Do not use 8B+ on this machine without separate authorization.

---

# 16. Safety / machine hygiene

Do not:
- disable Windows Defender;
- disable firewall;
- change BitLocker;
- modify boot settings;
- install Docker;
- alter pagefile automatically;
- delete unrelated files;
- remove existing models/data;
- expose Ollama publicly.

If UAC requires manual confirmation, pause only for that confirmation and give Jonathan a precise instruction.

---

# 17. Artifacts

In addition to existing G2.3.1 artifacts, record:

```text
artifacts/g2_3_1/ollama_setup_manifest.json
artifacts/g2_3_1/model_install_log.md
```

Include:
- Ollama version;
- install method;
- executable path;
- model storage path;
- model name;
- model digest if available;
- model file size;
- smoke-test result;
- benchmark runtime.

Do not store usernames, hostnames, serial numbers, or unrelated system identifiers.

---

# 18. Final verification

At completion run:

```powershell
ollama --version
ollama list
```

Then run:

```text
python -m pytest
```

and the full applicable G2.3.1 real-model commands.

Verify browser Model Comparison view against the real model.

---

# 19. Completion report

Return:

1. Ollama installation result;
2. exact installation method;
3. Ollama version;
4. model storage path;
5. exact real model installed;
6. model digest/size if available;
7. smoke-test result;
8. calibration results;
9. selected final paired trial count and why;
10. Regime A metrics;
11. Regime B metrics;
12. N/C/R raw proposal results;
13. validated results;
14. N-win/C-win/tie counts;
15. source-confusion metrics;
16. history scaling and context limits;
17. token/input size metrics;
18. latency and total benchmark runtime;
19. validator-prevented errors;
20. representative N wins;
21. representative C wins;
22. full regression test result;
23. browser demo URL;
24. artifact paths;
25. any manual action Jonathan had to approve;
26. whether real-model results support any representation effect;
27. whether NowMind is ready for Julian technical review.

Do not claim a NowMind advantage unless real-model paired results support it.

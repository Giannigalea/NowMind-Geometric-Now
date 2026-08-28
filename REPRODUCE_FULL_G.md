# Reproduce Full-G Locally

This milestone is designed to run locally without paid APIs or cloud model calls.

## Python

Required: Python 3.12+.

Check:

```powershell
.\.venv\Scripts\python.exe --version
```

Known local version during freeze:

```text
Python 3.12.13
```

## Environment Setup

If the existing `.venv` is present, use it. If you need a fresh environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pip install pytest
```

No OpenRouter key is required. Do not run the G2.3.3/G2.3.4 cloud runners as part of local reproduction.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## G1 Demo and Evidence

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.cli
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g1_suite
```

## Benchmarks

These commands regenerate local synthetic benchmark artifacts. They do not call cloud services.

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_benchmark
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_1_benchmark
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_2_benchmark
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_2_1_benchmark
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g2_3_benchmark
```

## Local Real-Model Reproduction

The completed G2.3.1/G2.3.2 local model result used Ollama `qwen3:0.6b` after local pagefile/runtime setup. Reproduce it only if the model is already installed locally and the machine can load it. Do not pull new models or use paid services for this Full-G review package.

The frozen result to compare against is:

```text
Regime A: Chronological 8, NowMind 0, ties 242
Corrected Regime B: Chronological 0, NowMind 0, ties 250
```

## Browser Reviewer Demo

Start the local browser demonstrator:

```powershell
.\run_full_g_demo.ps1
```

Then open:

```text
http://127.0.0.1:8765/?demo=full_g_reviewer
```

The reviewer mode is local/offline and does not require OpenRouter.

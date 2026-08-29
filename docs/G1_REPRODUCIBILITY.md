# G1 Reproducibility

## Supported Environment

- Windows PowerShell
- Python 3.12 or newer
- No Docker
- No database
- No cloud account
- No LLM/API key

## Setup

From PowerShell:

```powershell
cd path\to\NowMind-Geometric-Now
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

If `py` is not on PATH, create the virtual environment with the full path to a
Python 3.12 interpreter.

## Unit And Architecture Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Equivalent generic command:

```powershell
python -m pytest
```

## CLI Demo

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.cli
```

Equivalent generic command:

```powershell
python -m nowmind.demo.cli
```

## Browser Demonstrator

```powershell
.\.venv\Scripts\python.exe -m nowmind.demo.web
```

Default URL:

```text
http://127.0.0.1:8765
```

The server binds to `127.0.0.1` by default. It does not expose a public network
service unless a different host is explicitly supplied.

## Evidence Suite

```powershell
.\.venv\Scripts\python.exe -m nowmind.evaluation.run_g1_suite
```

Equivalent generic command:

```powershell
python -m nowmind.evaluation.run_g1_suite
```

The command executes the canonical G1 scenarios, runs pytest, computes metrics,
and exits non-zero if required invariants fail.

## Evidence Artifacts

Generated artifacts are written to:

```text
artifacts/g1/
```

Files:

- `g1_test_results.txt`
- `g1_demo_results.json`
- `g1_invariant_results.json`
- `g1_stale_state_experiment.json`
- `g1_metrics.json`

## Metric Definitions

- `scenario_count`: number of canonical G1.1 scenarios executed.
- `query_accuracy`: expected query statuses matched divided by expected query count.
- `inference_accuracy`: expected inference-rule/evidence checks passed divided by inference expectation count.
- `contradiction_detection_rate`: contradiction scenarios returning structured contradiction divided by contradiction expectation count.
- `stale_state_contamination_count`: count of focused stale-state experiments where a cycle-1-only relation survived in cycle 2.
- `stale_state_contamination_rate`: stale-state contamination count divided by one focused stale-state experiment.
- `unknown_guess_count`: expected `UNKNOWN` or `CONTRADICTORY` queries incorrectly returned as `TRUE` or `FALSE`.

The deterministic G1 target for stale-state contamination rate is `0.0`.

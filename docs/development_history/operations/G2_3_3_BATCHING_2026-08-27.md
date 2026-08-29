# G2.3.3 Batching

G2.3.3 OpenRouter execution is request-batched and resumable.

Use `--request-batch-size N` to spend at most `N` new OpenRouter requests in one
command. Completed rows are skipped on the next run using stable row keys:

```text
model | regime | trial_id | condition
```

Recommended low-quota sequence:

```powershell
$env:OPENROUTER_API_KEY = [Environment]::GetEnvironmentVariable('OPENROUTER_API_KEY','User')
.\.venv\Scripts\python.exe scripts\run_g2_3_3_openrouter_replication.py smoke --models z-ai/glm-5.2:free --smoke-count 1 --request-batch-size 1 --num-predict 128 --timeout-seconds 180
.\.venv\Scripts\python.exe scripts\run_g2_3_3_openrouter_replication.py calibrate --models z-ai/glm-5.2:free --calibration-count 5 --request-batch-size 2 --num-predict 128 --timeout-seconds 180
.\.venv\Scripts\python.exe scripts\run_g2_3_3_openrouter_replication.py run --models z-ai/glm-5.2:free --final-count 250 --request-batch-size 2 --num-predict 128 --timeout-seconds 180
.\.venv\Scripts\python.exe scripts\run_g2_3_3_openrouter_replication.py analyze --models z-ai/glm-5.2:free
```

A planned batch stop exits successfully after writing artifacts and updating
`artifacts/g2_3_3/run_state.json`. A real quota/rate-limit stop is still treated
as a pause condition and exits with the resumable quota-stop code.

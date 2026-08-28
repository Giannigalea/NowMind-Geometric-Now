# G2.3 Statistical Method

## Unit Of Comparison

The unit is a paired trial id. For each paired trial, N and C are run with the
same admissible facts, model config, regime, and output schema.

## Splits

G2.3 writes separate calibration and frozen evaluation artifacts:

- calibration default: 50 paired trials;
- evaluation default: 1000 paired trials.

Prompt or schema changes after evaluation should create a new versioned artifact
set rather than overwriting prior conclusions.

## Metrics

Metrics are reported by model, regime, condition, and mode:

- proposal-only;
- validated.

Reported metric families include reasoning accuracy, source integrity, action
safety, output quality, and resource usage. Aggregate accuracy includes a normal
approximation 95 percent confidence interval. Latency and token metrics include
mean, median where applicable, and p95 latency.

## Paired N/C Outcomes

`g2_3_pairwise_n_vs_c.json` reports N-win, C-win, and tie counts for proposal and
validated modes in each regime.

A win means one condition was correct and the other was incorrect for the same
trial id. A tie means both were correct or both were incorrect. The report must
not claim an architectural advantage when ties dominate.

## McNemar Readiness

The row-level JSONL artifact preserves paired correctness, so McNemar's test can
be applied externally without rerunning the benchmark. The current internal
artifact records the paired contingency as win/loss/tie counts; it does not yet
write a p-value field.

## Local Runtime Limitation

The current run uses the deterministic mock backend because no installed Ollama
runtime was available. These statistics validate benchmark mechanics and
invariants, not real LLM representation effects.

# G2.3 Acceptance Tests

All earlier tests remain mandatory.

## Backend
- mock backend deterministic;
- Ollama local-only;
- no automatic model download;
- backend cannot mutate cognitive state.

## Representation fairness
- N/C use same trial/admissible fact set;
- evaluator truth absent;
- builders deterministic;
- Regime A does not silently truncate;
- Regime B enforces documented budget.

## Output
- structured parse works;
- invalid JSON handling consistent;
- retry count recorded;
- raw output preserved.

## Source safety
- model output cannot become OBSERVED_NOW;
- model output cannot become MemoryTrace;
- proposed action must pass validator/ActionExecutor;
- model cannot bypass symbolic source rules.

## Pairing
- N/C/R share paired trial IDs;
- same model config used;
- pairwise stats derive from real outputs.

## Browser
- side-by-side representations;
- same model identity visible;
- raw proposal and validator outcome visible;
- hidden evaluator answer not shown by default.

## Locality
- no non-local model endpoint;
- no cloud API dependency;
- no telemetry.

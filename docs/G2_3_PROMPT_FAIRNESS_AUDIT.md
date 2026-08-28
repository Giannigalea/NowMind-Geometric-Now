# G2.3 Prompt Fairness Audit

## Scope

G2.3 compares representation format, not model identity. The active model
conditions are:

- `N_NOWMIND_STRUCTURED`
- `C_CHRONOLOGICAL`
- `R_CURRENT_ONLY`

`S_SYMBOLIC_NOWMIND` is a no-LLM symbolic reference row. It is reported beside
the model conditions but is not part of the N/C prompt-fairness claim.

## Shared Instruction

N, C, and R receive the same neutral system instruction:

```text
Use only supplied evidence.
Distinguish current observation, memory, and hypothetical future.
Do not promote memory or predictions to current fact.
Return UNKNOWN when current evidence is insufficient.
For action tasks, propose only actions supported by supplied state.
Return strict JSON with status, answer, source_used, confidence, action, assumptions, and explanation.
```

The instruction does not contain expected answers, benchmark family solutions,
or NowMind-only hints.

## Same Admissible Facts

Each paired trial starts from one `G23AdmissibleFacts` object. Both N and C store
the same `fact_set_hash` in trial results. The benchmark audit checks every N/C
pair for:

- same trial id;
- same admissible fact-set hash;
- same model configuration;
- no fixed-budget overflow in Regime B.

The generated audit is written to:

```text
artifacts/g2_3/g2_3_prompt_fairness_results.json
```

## Regime A

Regime A is equal information with no truncation. If a representation exceeds
context, the row records `context_overflow` instead of silently truncating.

## Regime B

Regime B uses a fixed representation budget of 1600 estimated tokens for N and
C. N uses explicit reconstruction/future/assumption selection. C uses current
and relevant records first, then newest chronological records that fit.

## Evaluator Leakage

Prompt builders consume only `G23AdmissibleFacts`. They do not receive
`G23Expected`, correctness labels, or evaluator ground truth. The test suite
asserts that generated prompts do not include forbidden evaluator terms such as
`expected_answer`, `oracle`, or `ground_truth`.

## Current Limitation

On this machine no Ollama executable was found on `PATH`, so final G2.3 artifacts
use the deterministic `MockModelBackend`. The fairness machinery is complete,
but real local-model prompt behavior still needs to be measured once a suitable
local instruction model is installed.

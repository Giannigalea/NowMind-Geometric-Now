# G2.3.2 Token Budget Audit

Date: 2026-08-26

## Cause

The 166/500 G2.3.1 Regime-B fairness failures came from accounting mismatch, not from NowMind cognition or benchmark scoring.

- The old trimming helper measured only `estimate_tokens(_prompt(representation))`.
- The final model request also included the common system instruction.
- The old fairness audit then subtracted an estimated system length from provider token counts after sending.
- Ollama provider token counts used the model tokenizer and were higher than the local estimator.

Classified causes:

- tokenizer/estimator mismatch: yes
- wrapper/system text added after truncation: yes
- inconsistent schema accounting: no evidence
- N/C different counting paths: no
- history selection overflow: no
- off-by-one logic: no
- template overhead: yes

## Corrected Method

G2.3.2 uses one canonical deterministic final-input counter for N/C/R:

`estimate_tokens(system_instruction + newline + final_prompt)`

Exact qwen tokenizer access was not available before sending, so the hard gate applies a shared conservative safety multiplier of `1.25`. A Regime-B model prompt is sent only if `budgeted_input_tokens <= 1600`.

Repair prompts use the same gate. If a repair prompt would exceed budget, the repair is skipped and the original parse failure remains visible to scoring and validation.

## Corrected Status

- Checked N/C pairs: `250`
- Failed N/C pairs: `0`

# G2.3.4 Summary

Local baseline: `qwen3:0.6b`, Regime A C=8/N=0/T=242, Regime B C=0/N=0/T=250.

G2.3.4 changed only provider privacy routing to `data_collection=allow` for synthetic benchmark prompts. All models below were live exact `$0/$0` `:free` candidates, with fallback disabled and a pinned provider requested.

## nvidia/nemotron-3-super-120b-a12b:free
- Smoke: `complete`, schema `4/4`
- Calibration rows: `7`, schema `6`
- Stop reason: failed frozen raw schema during calibration with malformed JSON beginning `{{`; no repair or coercion was applied.
- No completed provider-compatible N/C pairwise result yet.

## liquid/lfm-2.5-2.6b:free
- Smoke: `paused_rate_limit`, schema `1/4`
- Calibration rows: `0`, schema `0`
- Stop reason: upstream shared-pool HTTP `429` after one schema-valid smoke row.
- No completed provider-compatible N/C pairwise result yet.

## nvidia/nemotron-3-ultra-550b-a55b:free
- Smoke: `stopped_error`, schema `0/1`
- Calibration rows: `0`, schema `0`
- Stop reason: empty schema-invalid response with no effective-provider evidence; rejected by provider consistency gate.
- No completed provider-compatible N/C pairwise result yet.

## z-ai/glm-5.2:free
- Smoke: `paused_rate_limit`, schema `0/1`
- Calibration rows: `0`, schema `0`
- Stop reason: repeated upstream shared-pool HTTP `429`.
- No completed provider-compatible N/C pairwise result yet.

## minimax/minimax-m3:free
- Smoke: `stopped_error`, schema `0/1`
- Calibration rows: `0`, schema `0`
- Stop reason: HTTP `404`; no pinned endpoint could handle the frozen required parameters.
- No completed provider-compatible N/C pairwise result yet.

## dots-studio/dots-3-note-preview:free
- Smoke: `stopped_error`, schema `0/1`
- Calibration rows: `0`, schema `0`
- Stop reason: HTTP `404`; no pinned endpoint could handle the frozen required parameters.
- No completed provider-compatible N/C pairwise result yet.

## google/gemma-4-26b-a4b-it:free
- Smoke: `stopped_error`, schema `0/1`
- Calibration rows: `0`, schema `0`
- Stop reason: HTTP `404`; no pinned endpoint could handle the frozen required parameters.
- No completed provider-compatible N/C pairwise result yet.

No model passed calibration. Therefore no G2.3.4 250-trial Regime A or corrected Regime B final run was started.

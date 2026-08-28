# G2.3.1 Local Hardware Limit Conclusion

Date: 2026-08-24
Superseded: 2026-08-26

## Conclusion

The 2026-08-24 stop conclusion was accurate for the pre-pagefile machine state,
but it is now superseded by the 2026-08-26 pagefile workaround result.

After increasing Windows pagefile headroom and restarting, this machine could
load and run `qwen3:0.6b` under the same temporary CPU/AVX2 Ollama diagnostic
configuration. The 250-pair final G2.3.1 evaluation completed with real local
model calls.

This does not change the NowMind architecture or benchmark, and it does not
support a NowMind-over-chronology model-result claim.

## Evidence

- Default Ollama selected Vulkan/Radeon with about `1.7 GiB` available VRAM.
- Forced CPU/AVX2 was confirmed by logs.
- `qwen3:1.7b` calibration completed:
  `artifacts/g2_3_1/qwen3_1_7b/calibration_results.json`
- `qwen3:1.7b` final evaluation model calls failed with:
  `failed to allocate CPU buffer of size 692725760`
- `qwen3:0.6b` smoke at `num_ctx=512` failed with:
  `failed to allocate CPU buffer of size 310250496`
- After pagefile expansion and restart, `qwen3:0.6b` passed smoke at contexts
  `512`, `1024`, `2048`, and `4096`:
  `artifacts/g2_3_1/qwen3_0_6b_smoke_after_pagefile.json`
- `qwen3:0.6b` completed the 50-pair calibration:
  `artifacts/g2_3_1/qwen3_0_6b/calibration_results.json`
- `qwen3:0.6b` completed the predeclared 250-pair final evaluation:
  `artifacts/g2_3_1/qwen3_0_6b/evaluation_results.json`
- The final row file has `2000` rows, `250` complete paired trials, and no
  connection-refused rows after the interrupted restart checkpoint was trimmed.

## Final Result Summary

- Final model: `qwen3:0.6b`
- Final paired trials: `250`
- Final rows: `2000`
- Real model calls: `1500`
- Context overflows: `248`
- Invariants: `5` passed, `1` failed
- Failed invariant: G2.3 fairness, because provider token counts exceeded the
  fixed budget in `166` of `500` checked N/C pairs.
- Regime A validated N/C comparison: C better `8`, N better `0`, tied `242`.
- Regime B validated N/C comparison: C better `0`, N better `0`, tied `250`.

## Recommended Next Actions

1. Treat `qwen3:0.6b` as the completed real local G2.3.1 final run for this
   machine.
2. Report the failed fairness invariant and weak model accuracy honestly.
3. Do not claim a NowMind-over-chronology real-model advantage from these
   artifacts.
4. For stronger evidence later, rerun the unchanged benchmark on a larger local
   machine or with explicitly authorized local runtime/model changes.

Do not change NowMind or the benchmark to accommodate this hardware failure.

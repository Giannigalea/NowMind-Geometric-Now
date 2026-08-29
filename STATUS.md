# NowMind Geometric Now Public Status

Date: 2026-08-29

This repository is a Full-G research-review package covering G1 through G2.3.4.
It preserves the frozen scientific artifacts and benchmark results while keeping
the public entry points focused on research, evidence, and reproduction.

## Current Scope

- G1: fresh current-state Present Geometry and deterministic symbolic reasoning.
- G2: temporal source separation between observed now, reconstructed memory, and
  hypothetical future.
- G2.1: possibility geometry and closed-loop planning.
- G2.2: epistemic geometry, unknown cells, SCAN actions, and verify-first
  planning.
- G2.2.1: targeted epistemic recovery and retrieval-efficiency diagnostics.
- G2.3-G2.3.4: model-representation comparisons with mock, local, and free
  provider compatibility evidence.

## Current Model Result

The frozen local real-model result used Ollama `qwen3:0.6b`.

| Regime | Chronological wins | NowMind wins | Ties |
|---|---:|---:|---:|
| Regime A, equal information | 8 | 0 | 242 |
| Corrected Regime B, fixed token budget | 0 | 0 | 250 |

The result does not show a NowMind-over-chronological-control advantage for this
small local model.

## Review Entry Points

- [REPRODUCE_FULL_G.md](REPRODUCE_FULL_G.md)
- [README.md](README.md)
- [docs/FULL_G_RESULTS_SUMMARY.md](docs/FULL_G_RESULTS_SUMMARY.md)
- [docs/FULL_G_CLAIMS_AND_NONCLAIMS.md](docs/FULL_G_CLAIMS_AND_NONCLAIMS.md)
- [docs/FULL_G_NEGATIVE_RESULTS.md](docs/FULL_G_NEGATIVE_RESULTS.md)
- [docs/EXTERNAL_TECHNICAL_BRIEF.md](docs/EXTERNAL_TECHNICAL_BRIEF.md)
- [artifacts/README.md](artifacts/README.md)

## Preserved History

Historical build notes, task specifications, operational troubleshooting, and
public-review audits are archived under `docs/development_history/`. They are
kept for provenance but are not the normal reviewer path.

## Legal Status

This repository is public for technical review and citation. It is not released
under an open-source license. See [COPYRIGHT.md](COPYRIGHT.md) and
[CITATION.cff](CITATION.cff).

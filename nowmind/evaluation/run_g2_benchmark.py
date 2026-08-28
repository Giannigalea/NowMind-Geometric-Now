from __future__ import annotations

import argparse
from pathlib import Path

from nowmind.evaluation.g2_benchmark import (
    DEFAULT_ARTIFACT_DIR,
    DEFAULT_SEED,
    DEFAULT_TRIAL_COUNT,
    run_benchmark,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NowMind G2 temporal benchmark.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    args = parser.parse_args()

    result = run_benchmark(
        artifacts_dir=args.artifacts_dir,
        seed=args.seed,
        trial_count=args.trial_count,
    )
    print(f"Artifacts: {result.artifacts_dir}")
    print(f"seed: {result.seed}")
    print(f"trial_count: {result.trial_count}")
    for system_id, metrics in result.metrics.items():
        print(f"[{system_id}]")
        for name, value in metrics.items():
            print(f"{name}: {value}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

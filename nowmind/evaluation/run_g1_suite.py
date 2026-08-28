from __future__ import annotations

import argparse
from pathlib import Path

from nowmind.evaluation.g1_suite import DEFAULT_ARTIFACT_DIR, run_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NowMind G1 evidence suite.")
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory for generated G1 evidence artifacts.",
    )
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Generate runtime artifacts without invoking pytest.",
    )
    args = parser.parse_args()

    result = run_suite(args.artifacts_dir, run_pytest=not args.skip_pytest)
    print(f"Artifacts: {result.artifacts_dir}")
    for name, value in result.metrics.items():
        if name in {"schema", "definitions"}:
            continue
        print(f"{name}: {value}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())


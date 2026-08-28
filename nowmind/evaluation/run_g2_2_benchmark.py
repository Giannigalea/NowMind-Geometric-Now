from __future__ import annotations

from nowmind.evaluation.g2_2_benchmark import run_benchmark


def main() -> None:
    result = run_benchmark()
    print(f"artifacts: {result.artifacts_dir}")
    print(f"seed: {result.seed}")
    print(f"trial_count: {result.trial_count}")
    print(
        "invariants: "
        f"{result.invariant_results['summary']['passed']} passed, "
        f"{result.invariant_results['summary']['failed']} failed"
    )
    for system_id, metrics in result.metrics.items():
        print(
            f"{system_id}: "
            f"goal={metrics['goal_reached_rate']:.3f} "
            f"verify={metrics['verification_action_rate']:.3f} "
            f"memory={metrics['memory_use_rate']:.3f} "
            f"collision={metrics['collision_rate']:.3f} "
            f"evidence={metrics['mean_evidence_items_inspected']:.1f}"
        )


if __name__ == "__main__":
    main()

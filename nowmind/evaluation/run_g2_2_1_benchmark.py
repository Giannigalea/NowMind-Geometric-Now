from __future__ import annotations

from nowmind.evaluation.g2_2_1_benchmark import run_g2_2_1_benchmark


def main() -> None:
    result = run_g2_2_1_benchmark()
    v1 = result["v1"]
    holdout = result["holdout"]
    invariants = result["invariants"]
    print(f"artifacts: {holdout.artifacts_dir.parent}")
    print(f"v1_seed: {v1.seed}")
    print(f"v1_trial_count: {v1.trial_count}")
    print(f"holdout_seed: {holdout.seed}")
    print(f"holdout_trial_count: {holdout.trial_count}")
    print(
        "invariants: "
        f"{invariants['summary']['passed']} passed, {invariants['summary']['failed']} failed"
    )
    for system_id, metrics in holdout.metrics.items():
        print(
            f"{system_id}: "
            f"goal={metrics['goal_reached_rate']:.3f} "
            f"records={metrics.get('mean_records_scanned', 0.0):.1f} "
            f"hidden={metrics.get('hidden_change_recovery_rate', 0.0):.3f} "
            f"reacquire={metrics.get('target_reacquisition_rate', 0.0):.3f} "
            f"wasted_verify={metrics.get('wasted_verification_rate', 0.0):.3f}"
        )


if __name__ == "__main__":
    main()

from nowmind.evaluation.g2_3_benchmark import run_g2_3_benchmark


def main() -> int:
    result = run_g2_3_benchmark()
    selected = result.model_manifest["selected"]
    print(f"artifacts: {result.artifacts_dir}")
    print(f"backend: {selected['backend']}")
    print(f"model: {selected['model']}")
    print(f"calibration_count: {result.calibration_count}")
    print(f"final_count: {result.final_count}")
    print(f"invariants: {result.invariants['summary']['passed']} passed, {result.invariants['summary']['failed']} failed")
    for key, values in result.metrics.items():
        if "|validated" in key:
            print(f"{key}: accuracy={values['overall_accuracy']:.3f} source={values['source_classification_accuracy']:.3f} parse={values['json_parse_success_rate']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

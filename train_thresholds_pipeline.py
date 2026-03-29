import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def run_step(command: List[str]) -> None:
    print(f"\n>> Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.strip())
        raise SystemExit(result.returncode)


def load_jsonl(path: Path) -> List[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def evaluate(dataset_path: Path, thresholds_path: Path) -> Dict[str, Dict[str, float]]:
    dataset = load_jsonl(dataset_path)
    with thresholds_path.open("r", encoding="utf-8") as f:
        thresholds = json.load(f)

    report: Dict[str, Dict[str, float]] = {}
    grouped: Dict[str, List[dict]] = {}
    for row in dataset:
        grouped.setdefault(row["environment"], []).append(row)

    for env, samples in grouped.items():
        env_thr = thresholds.get(env, thresholds.get("campus", {"medium": 45}))
        medium = float(env_thr["medium"])
        tp = fp = tn = fn = 0
        for s in samples:
            pred = 1 if float(s["score"]) >= medium else 0
            label = int(s["label"])
            if pred == 1 and label == 1:
                tp += 1
            elif pred == 1 and label == 0:
                fp += 1
            elif pred == 0 and label == 0:
                tn += 1
            else:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        accuracy = (tp + tn) / len(samples) if samples else 0.0
        report[env] = {
            "samples": len(samples),
            "threshold_medium": medium,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-command calibration pipeline (build + calibrate + report).")
    parser.add_argument("--samples", default="calibration_samples.jsonl", help="Raw samples JSONL")
    parser.add_argument("--labels", help="CSV labels file (event_id,label)")
    parser.add_argument("--dataset", default="calibration_dataset.jsonl", help="Output labeled dataset JSONL")
    parser.add_argument("--review", default="review_queue.csv", help="Output review queue CSV")
    parser.add_argument("--thresholds", default="calibrated_thresholds.json", help="Output thresholds JSON")
    parser.add_argument("--report", default="calibration_report.json", help="Output metrics report JSON")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    build_script = root / "build_calibration_dataset.py"
    calibrate_script = root / "calibrate_thresholds.py"

    build_cmd = [
        sys.executable,
        str(build_script),
        "--samples",
        args.samples,
        "--output",
        args.dataset,
        "--review-output",
        args.review,
    ]
    if args.labels:
        build_cmd.extend(["--labels", args.labels])
    run_step(build_cmd)

    dataset_path = root / args.dataset
    if not dataset_path.exists() or dataset_path.stat().st_size == 0:
        print("\nNo labeled dataset produced yet. Fill labels in review queue and re-run with --labels.")
        return

    calibrate_cmd = [
        sys.executable,
        str(calibrate_script),
        "--input",
        args.dataset,
        "--output",
        args.thresholds,
    ]
    run_step(calibrate_cmd)

    report = evaluate(root / args.dataset, root / args.thresholds)
    report_path = root / args.report
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\nCalibration quality report:")
    for env, metrics in report.items():
        print(
            f"- {env}: accuracy={metrics['accuracy']:.3f}, "
            f"precision={metrics['precision']:.3f}, recall={metrics['recall']:.3f}, f1={metrics['f1']:.3f}"
        )
    print(f"\nSaved report to: {args.report}")


if __name__ == "__main__":
    main()

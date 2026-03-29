import argparse
import csv
import json
from typing import Dict, List


def read_jsonl(path: str) -> List[dict]:
    rows: List[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def read_labels_csv(path: str) -> Dict[str, int]:
    """
    CSV format:
      event_id,label
    where label is 0 (non-threat) or 1 (threat)
    """
    labels: Dict[str, int] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event_id = str(row["event_id"]).strip()
            label = int(row["label"])
            labels[event_id] = label
    return labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Build clean calibration dataset from raw logged samples.")
    parser.add_argument("--samples", default="calibration_samples.jsonl", help="Raw JSONL samples from live inference")
    parser.add_argument("--labels", required=False, help="Optional CSV with manual labels: event_id,label")
    parser.add_argument("--output", default="calibration_dataset.jsonl", help="Output JSONL for calibration")
    parser.add_argument("--review-output", default="review_queue.csv", help="CSV of unlabeled events to review")
    args = parser.parse_args()

    samples = read_jsonl(args.samples)
    labels = read_labels_csv(args.labels) if args.labels else {}

    labeled_count = 0
    unlabeled_rows: List[dict] = []
    output_rows: List[dict] = []

    for row in samples:
        event_id = str(row.get("event_id", "")).strip()
        if not event_id:
            continue

        label = row.get("label")
        if label is None and event_id in labels:
            label = labels[event_id]

        if label is None:
            unlabeled_rows.append(
                {
                    "event_id": event_id,
                    "timestamp": row.get("timestamp", ""),
                    "environment": row.get("environment", "campus"),
                    "score": row.get("score", 0),
                    "threat_level": row.get("threat_level", "LOW"),
                    "persons_count": row.get("persons_count", 0),
                    "threats_count": row.get("threats_count", 0),
                    "distress_score": row.get("distress_score", 0),
                    "reason_codes": "|".join(row.get("reason_codes", [])),
                }
            )
            continue

        label = int(label)
        if label not in (0, 1):
            continue

        output_rows.append(
            {
                "event_id": event_id,
                "environment": str(row.get("environment", "campus")).lower(),
                "score": float(row.get("score", 0.0)),
                "label": label,
            }
        )
        labeled_count += 1

    with open(args.output, "w", encoding="utf-8") as f:
        for r in output_rows:
            f.write(json.dumps(r) + "\n")

    with open(args.review_output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "event_id",
                "timestamp",
                "environment",
                "score",
                "threat_level",
                "persons_count",
                "threats_count",
                "distress_score",
                "reason_codes",
                "label",
            ],
        )
        writer.writeheader()
        for row in unlabeled_rows:
            row["label"] = ""
            writer.writerow(row)

    print(f"Total raw samples: {len(samples)}")
    print(f"Labeled samples written: {labeled_count} -> {args.output}")
    print(f"Unlabeled review queue: {len(unlabeled_rows)} -> {args.review_output}")


if __name__ == "__main__":
    main()

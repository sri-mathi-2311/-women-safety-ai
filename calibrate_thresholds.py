import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Sample:
    environment: str
    score: float
    label: int  # 1 = threat, 0 = non-threat


def load_samples(path: str) -> List[Sample]:
    """
    Supports JSON array or JSONL.
    Each record should include:
      - environment: campus/workspace/public
      - score: fused or confidence score (0-100)
      - label: 1 for threat, 0 for non-threat
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    rows: List[dict]
    if raw.startswith("["):
        rows = json.loads(raw)
    else:
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]

    samples: List[Sample] = []
    for row in rows:
        env = str(row.get("environment", "campus")).lower()
        score = float(row["score"])
        label = int(row["label"])
        samples.append(Sample(environment=env, score=score, label=label))
    return samples


def metrics(samples: List[Sample], medium: float) -> Tuple[float, float, float]:
    tp = fp = fn = 0
    for s in samples:
        pred = 1 if s.score >= medium else 0
        if pred == 1 and s.label == 1:
            tp += 1
        elif pred == 1 and s.label == 0:
            fp += 1
        elif pred == 0 and s.label == 1:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0:
        return precision, recall, 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def find_best_medium_threshold(samples: List[Sample]) -> float:
    best_thr = 45.0
    best_f1 = -1.0
    for thr in range(20, 86):
        _, _, f1 = metrics(samples, float(thr))
        if f1 > best_f1:
            best_f1 = f1
            best_thr = float(thr)
    return best_thr


def derive_full_thresholds(best_medium: float) -> Dict[str, float]:
    """
    Keep policy spacing consistent:
    MEDIUM -> logging boundary
    HIGH   -> human-alert boundary
    CRITICAL -> immediate escalation
    """
    high = min(95.0, best_medium + 18.0)
    critical = min(98.0, high + 15.0)
    return {
        "medium": round(best_medium, 2),
        "high": round(high, 2),
        "critical": round(critical, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate environment thresholds from labeled scores.")
    parser.add_argument("--input", required=True, help="Path to JSON or JSONL labeled samples")
    parser.add_argument("--output", default="calibrated_thresholds.json", help="Output thresholds file")
    args = parser.parse_args()

    samples = load_samples(args.input)
    if not samples:
        raise SystemExit("No samples found.")

    by_env: Dict[str, List[Sample]] = {}
    for s in samples:
        by_env.setdefault(s.environment, []).append(s)

    thresholds: Dict[str, Dict[str, float]] = {}
    for env, env_samples in by_env.items():
        best_medium = find_best_medium_threshold(env_samples)
        p, r, f1 = metrics(env_samples, best_medium)
        thresholds[env] = derive_full_thresholds(best_medium)
        print(
            f"[{env}] medium={best_medium:.1f} "
            f"precision={p:.3f} recall={r:.3f} f1={f1:.3f} "
            f"samples={len(env_samples)}"
        )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)
    print(f"\nSaved calibrated thresholds to: {args.output}")


if __name__ == "__main__":
    main()

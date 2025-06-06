import os
import json
import argparse
from typing import List
from sklearn.metrics import accuracy_score, f1_score


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate VLM rebus-puzzle results."
    )
    parser.add_argument(
        "--timestamp",
        required=True,
        help="Timestamp folder under logs/, e.g. 20250520_142530"
    )
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Root logs directory (default: logs/)"
    )
    parser.add_argument(
        "--use-f1",
        action="store_true",
        help="Also compute macro F1 over tokenized predictions"
    )
    return parser.parse_args()


def load_results(logs_dir: str, timestamp: str) -> List[dict]:
    """
    Reads logs/<timestamp>/results.json and returns the list of
    {image_id, ground_truth, prediction}.
    """
    path = os.path.join(logs_dir, timestamp, "results.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No results.json at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text: str) -> List[str]:
    """
    Simple whitespace tokenizer, lowercased.
    """
    return text.lower().split()


def evaluate(results: List[dict], use_f1: bool = False) -> dict:
    """
    Compute accuracy and optionally macro F1.
    Returns a metrics dict.
    """
    y_true = [r["ground_truth"] for r in results]
    y_pred = [r["prediction"]   for r in results]

    # Exact-match accuracy
    acc = accuracy_score(y_true, y_pred)

    metrics = {"exact_match_accuracy": acc}

    if use_f1:
        # For F1 we need sequence-level tokens; flatten all samples
        # Here we compute per-sample F1 and then macro-average
        token_f1s = []
        for gt, pred in zip(y_true, y_pred):
            gt_toks = tokenize(gt)
            pred_toks = tokenize(pred)
            # If either side is empty, skip F1 for that sample
            if gt_toks and pred_toks:
                token_f1s.append(
                    f1_score(gt_toks, pred_toks, average="macro")
                )
        # Macro-average across samples
        if token_f1s:
            metrics["macro_f1"] = sum(token_f1s) / len(token_f1s)
        else:
            metrics["macro_f1"] = 0.0

    return metrics


def main():
    args = parse_args()
    # 1. Load results
    results = load_results(args.logs_dir, args.timestamp)

    # 2. Evaluate
    metrics = evaluate(results, use_f1=args.use_f1)

    # 3. Write metrics.json
    out_dir = os.path.join(args.logs_dir, args.timestamp)
    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # 4. Print summary
    print(f"Results for run {args.timestamp}")
    print(f"  Exact-match accuracy: {metrics['exact_match_accuracy']:.4f}")
    if args.use_f1:
        print(f"  Macro F1 (token-level): {metrics.get('macro_f1',0):.4f}")
    print(f"Metrics written to {metrics_path}")


if __name__ == "__main__":
    main()

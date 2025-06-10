import os
import sys
import json
import argparse
import re
from typing import List

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def extract_idiom(prediction: str) -> str:
    """
    Extract the actual idiom from verbose model predictions.
    Handles various formats like quotes, bold text, keywords, etc.
    """
    if not prediction or not isinstance(prediction, str):
        return ""
    
    # Clean the text first
    text = prediction.strip()
    
    # Pattern 1: Text in bold quotes **"idiom"**
    patterns = [
        r'\*\*["\']([^"\']+)["\']?\*\*',  # **"jump the gun"**
        r'\*\*([^*]+)\*\*',               # **jump the gun**
        r'["\']([^"\']+)["\']',           # "jump the gun"
        r'answer is[:\s]*["\']?([^"\'.\n]+)["\']?',  # answer is: "jump the gun"
        r'idiom is[:\s]*["\']?([^"\'.\n]+)["\']?',   # idiom is: jump the gun
        r'represents[:\s]*["\']?([^"\'.\n]+)["\']?', # represents: jump the gun
        r'solution[:\s]*["\']?([^"\'.\n]+)["\']?',   # solution: jump the gun
        r'puzzle is[:\s]*["\']?([^"\'.\n]+)["\']?',  # puzzle is: jump the gun
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Take the longest match (most likely to be the full idiom)
            idiom = max(matches, key=len).strip()
            # Clean up the extracted idiom
            idiom = re.sub(r'^(the\s+)?', '', idiom.lower().strip())  # Remove leading "the"
            idiom = re.sub(r'[.,!?]*$', '', idiom)  # Remove trailing punctuation
            if len(idiom) > 3:  # Reasonable idiom length
                return idiom
    
    # Fallback: Look for the last quoted text or capitalized phrase
    fallback_patterns = [
        r'([A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+the\s+[a-z]+)*)',  # Capitalized phrases
        r'([a-z]+\s+the\s+[a-z]+)',  # "verb the noun" patterns
    ]
    
    for pattern in fallback_patterns:
        matches = re.findall(pattern, text)
        if matches:
            idiom = matches[-1].lower().strip()  # Take the last match
            if len(idiom) > 3:
                return idiom
    
    # Last resort: return the original prediction truncated
    return text[:50].lower().strip()

def normalize_idiom(idiom: str) -> str:
    """Normalize idioms for comparison (handle variations)"""
    if not idiom:
        return ""
    
    # Convert to lowercase and strip
    normalized = idiom.lower().strip()
    
    # Remove common variations
    normalized = re.sub(r'^(a\s+|an\s+|the\s+)', '', normalized)  # Remove articles
    normalized = re.sub(r'[.,!?;:]*$', '', normalized)  # Remove punctuation
    normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
    
    return normalized.strip()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate VLM rebus-puzzle results with idiom extraction."
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed extraction results for debugging"
    )
    return parser.parse_args()

def load_results(logs_dir: str, timestamp: str) -> List[dict]:
    """
    Reads logs/<timestamp>/results.json and returns the list of
    {image_id, ground_truth, prediction}.
    """
    # Handle both relative and absolute paths
    if not os.path.isabs(logs_dir):
        logs_dir = os.path.join(project_root, logs_dir)
    
    path = os.path.join(logs_dir, timestamp, "results.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No results.json at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def tokenize(text: str) -> List[str]:
    """Simple whitespace tokenizer, lowercased."""
    return text.lower().split()

def calculate_token_f1(ground_truth: str, prediction: str) -> float:
    """Calculate F1 score based on token overlap"""
    gt_tokens = set(tokenize(ground_truth))
    pred_tokens = set(tokenize(prediction))
    
    if not gt_tokens and not pred_tokens:
        return 1.0
    if not gt_tokens or not pred_tokens:
        return 0.0
    
    intersection = gt_tokens.intersection(pred_tokens)
    precision = len(intersection) / len(pred_tokens)
    recall = len(intersection) / len(gt_tokens)
    
    if precision + recall == 0:
        return 0.0
    
    return 2 * precision * recall / (precision + recall)

def evaluate(results: List[dict], use_f1: bool = False, debug: bool = False) -> dict:
    """
    Compute accuracy metrics with idiom extraction.
    Returns a metrics dict.
    """
    # Extract idioms from predictions
    extracted_results = []
    extraction_success = 0
    
    for result in results:
        ground_truth = normalize_idiom(result["ground_truth"])
        raw_prediction = result["prediction"]
        extracted_prediction = extract_idiom(raw_prediction)
        normalized_prediction = normalize_idiom(extracted_prediction)
        
        # Check if extraction seems successful
        if len(extracted_prediction) > 0 and len(extracted_prediction) < len(raw_prediction):
            extraction_success += 1
        
        extracted_results.append({
            "image_id": result["image_id"],
            "ground_truth": ground_truth,
            "prediction": normalized_prediction,
            "raw_prediction": raw_prediction,
            "extracted_prediction": extracted_prediction
        })
        
        if debug and len(extracted_results) <= 5:  # Show first 5 for debugging
            print(f"\n--- Debug Example {len(extracted_results)} ---")
            print(f"Image: {result['image_id']}")
            print(f"Ground Truth: '{ground_truth}'")
            print(f"Raw Prediction: '{raw_prediction[:100]}...'")
            print(f"Extracted: '{extracted_prediction}'")
            print(f"Normalized: '{normalized_prediction}'")
            print(f"Match: {'✅' if ground_truth == normalized_prediction else '❌'}")
    
    # Calculate exact match accuracy on extracted idioms
    y_true = [r["ground_truth"] for r in extracted_results]
    y_pred = [r["prediction"] for r in extracted_results]
    
    exact_matches = sum(1 for gt, pred in zip(y_true, y_pred) if gt == pred)
    exact_accuracy = exact_matches / len(y_true) if y_true else 0
    
    # Calculate partial match (ground truth appears in prediction)
    partial_matches = sum(1 for gt, pred in zip(y_true, y_pred) if gt in pred or pred in gt)
    partial_accuracy = partial_matches / len(y_true) if y_true else 0
    
    metrics = {
        "exact_match_accuracy": exact_accuracy,
        "partial_match_accuracy": partial_accuracy,
        "extraction_success_rate": extraction_success / len(results) if results else 0,
        "total_samples": len(results)
    }
    
    if use_f1:
        # Calculate F1 scores
        token_f1s = [calculate_token_f1(gt, pred) for gt, pred in zip(y_true, y_pred)]
        metrics["macro_f1"] = sum(token_f1s) / len(token_f1s) if token_f1s else 0.0
    
    return metrics

def main():
    args = parse_args()
    
    # Handle both relative and absolute paths
    logs_dir = args.logs_dir
    if not os.path.isabs(logs_dir):
        logs_dir = os.path.join(project_root, logs_dir)
    
    # 1. Load results
    print(f"Loading results from {args.timestamp}...")
    results = load_results(logs_dir, args.timestamp)
    
    # 2. Evaluate with idiom extraction
    print(f"Evaluating {len(results)} samples...")
    metrics = evaluate(results, use_f1=args.use_f1, debug=args.debug)
    
    # 3. Write metrics.json
    out_dir = os.path.join(logs_dir, args.timestamp)
    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    
    # 4. Print summary
    print(f"\n📊 Results for run {args.timestamp}")
    print("=" * 50)
    print(f"  📈 Exact-match accuracy: {metrics['exact_match_accuracy']:.4f} ({metrics['exact_match_accuracy']*100:.1f}%)")
    print(f"  📈 Partial-match accuracy: {metrics['partial_match_accuracy']:.4f} ({metrics['partial_match_accuracy']*100:.1f}%)")
    print(f"  🔧 Extraction success rate: {metrics['extraction_success_rate']:.4f} ({metrics['extraction_success_rate']*100:.1f}%)")
    
    if args.use_f1:
        print(f"  📈 Macro F1 (token-level): {metrics.get('macro_f1',0):.4f}")
    
    print(f"  📁 Total samples: {metrics['total_samples']}")
    print(f"\n💾 Metrics written to {metrics_path}")

if __name__ == "__main__":
    main()
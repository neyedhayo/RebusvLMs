import os
import sys
import json
import argparse
import re
from typing import List

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def clean_extracted_idiom(idiom: str) -> str:
    """Clean up extracted idiom text"""
    if not idiom:
        return ""
    
    cleaned = idiom.strip()
    cleaned = re.sub(r'^(the\s+)?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[.,!?;:]*$', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip().lower()

def is_description_text(text: str) -> bool:
    """Check if text looks like description rather than an idiom"""
    if not text:
        return True
    
    description_words = [
        'word', 'letter', 'image', 'puzzle', 'shows', 'written', 'drawn', 
        'depicts', 'represents', 'visual', 'graphic', 'picture', 'illustration',
        'stacked', 'positioned', 'placed', 'arranged', 'times', 'bottom', 'top',
        'left', 'right', 'corner', 'above', 'below', 'line', 'number'
    ]
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in description_words):
        return True
    
    if len(text.split()) == 1 and text.upper() == text:
        return True
    
    return False

def is_likely_idiom(text: str) -> bool:
    """Check if text looks like a real idiom"""
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    if len(text_lower) < 3 or len(text_lower) > 50:
        return False
    
    idiom_patterns = [
        r'\b\w+\s+the\s+\w+',
        r'\b\w+\s+(in|on|under|over|up|down|out|off)\s+',
        r'\b(break|cut|kick|jump|throw|catch|hit|run|get|put|take)\s+',
    ]
    
    for pattern in idiom_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return len(text.split()) >= 2

def select_best_idiom_candidate(candidates: List[str]) -> str:
    """Select the best idiom candidate from a list"""
    if not candidates:
        return ""
    
    if len(candidates) == 1:
        return candidates[0]
    
    scored_candidates = []
    
    for candidate in candidates:
        score = 0
        candidate_lower = candidate.lower()
        
        if re.search(r'\w+\s+the\s+\w+', candidate_lower):
            score += 10
        if any(word in candidate_lower for word in ['kick', 'jump', 'cut', 'break', 'throw']):
            score += 5
        if any(word in candidate_lower for word in ['under', 'over', 'in', 'on', 'out']):
            score += 3
        
        if any(word in candidate_lower for word in ['word', 'letter', 'shows', 'depicts']):
            score -= 10
        
        word_count = len(candidate.split())
        if 2 <= word_count <= 5:
            score += word_count
        
        scored_candidates.append((score, candidate))
    
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return scored_candidates[0][1]

def extract_idiom(prediction: str) -> str:
    """
    Extract the actual idiom from verbose model predictions.
    Uses context-aware patterns prioritizing answers over descriptions.
    """
    if not prediction or not isinstance(prediction, str):
        return ""
    
    text = prediction.strip()
    
    # Priority 1: Text after specific keywords (most reliable)
    context_patterns = [
        r'(?:idiom|answer|represents|solution|puzzle)\s*(?:is)?[:\s]+\*\*["\']?([^"\'*\n]+)["\']?\*\*',
        r'(?:idiom|answer|represents|solution|puzzle)\s*(?:is)?[:\s]+["\']([^"\'.\n]+)["\']',
        r'(?:idiom|answer|represents|solution|puzzle)\s*(?:is)?[:\s]+\*\*([^*\n]+)\*\*',
        r'(?:suggests|therefore)[^:]*[:\s]+\*\*["\']?([^"\'*\n]+)["\']?\*\*',
        r'(?:suggests|therefore)[^:]*[:\s]+["\']([^"\'.\n]+)["\']',
    ]
    
    for pattern in context_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            idiom = matches[0].strip()
            idiom = clean_extracted_idiom(idiom)
            if len(idiom) > 2:
                return idiom
    
    # Priority 2: Bold text (medium reliability)
    bold_patterns = [
        r'\*\*["\']([^"\']+)["\']?\*\*',
        r'\*\*([^*]+)\*\*',
    ]
    
    for pattern in bold_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            valid_matches = []
            for match in matches:
                cleaned = clean_extracted_idiom(match)
                if not is_description_text(cleaned):
                    valid_matches.append(cleaned)
            
            if valid_matches:
                idiom = select_best_idiom_candidate(valid_matches)
                if idiom:
                    return idiom
    
    # Priority 3: Regular quotes (lowest reliability, filter heavily)
    quote_patterns = [
        r'["\']([^"\']{4,30})["\']',
    ]
    
    for pattern in quote_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            valid_matches = []
            for match in matches:
                cleaned = clean_extracted_idiom(match)
                if is_likely_idiom(cleaned) and not is_description_text(cleaned):
                    valid_matches.append(cleaned)
            
            if valid_matches:
                idiom = select_best_idiom_candidate(valid_matches)
                if idiom:
                    return idiom
    
    # Fallback: Look for capitalized phrases that might be idioms
    fallback_patterns = [
        r'([A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+the\s+[a-z]+)*)',
    ]
    
    for pattern in fallback_patterns:
        matches = re.findall(pattern, text)
        if matches:
            idiom = matches[-1].lower().strip()
            if is_likely_idiom(idiom):
                return idiom
    
    # Last resort: return truncated original
    return text[:50].lower().strip()

def normalize_idiom(idiom: str) -> str:
    """Normalize idioms for comparison (handle variations)"""
    if not idiom:
        return ""
    
    normalized = idiom.lower().strip()
    normalized = re.sub(r'^(a\s+|an\s+|the\s+)', '', normalized)
    normalized = re.sub(r'[.,!?;:]*$', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()

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
    if not os.path.isabs(logs_dir):
        logs_dir = os.path.join(project_root, logs_dir)
    
    path = os.path.join(logs_dir, timestamp, "results.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No results.json at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate(results: List[dict], use_f1: bool = False, debug: bool = False) -> dict:
    """
    Compute accuracy metrics with idiom extraction.
    Returns a metrics dict.
    """
    extracted_results = []
    extraction_success = 0
    
    for result in results:
        ground_truth = normalize_idiom(result["ground_truth"])
        raw_prediction = result["prediction"]
        extracted_prediction = extract_idiom(raw_prediction)
        normalized_prediction = normalize_idiom(extracted_prediction)
        
        if len(extracted_prediction) > 0 and len(extracted_prediction) < len(raw_prediction):
            extraction_success += 1
        
        extracted_results.append({
            "image_id": result["image_id"],
            "ground_truth": ground_truth,
            "prediction": normalized_prediction,
            "raw_prediction": raw_prediction,
            "extracted_prediction": extracted_prediction
        })
        
        if debug and len(extracted_results) <= 5:
            print(f"\n--- Debug Example {len(extracted_results)} ---")
            print(f"Image: {result['image_id']}")
            print(f"Ground Truth: '{ground_truth}'")
            print(f"Raw Prediction: '{raw_prediction[:100]}...'")
            print(f"Extracted: '{extracted_prediction}'")
            print(f"Normalized: '{normalized_prediction}'")
            print(f"Match: {'✅' if ground_truth == normalized_prediction else '❌'}")
    
    y_true = [r["ground_truth"] for r in extracted_results]
    y_pred = [r["prediction"] for r in extracted_results]
    
    exact_matches = sum(1 for gt, pred in zip(y_true, y_pred) if gt == pred)
    exact_accuracy = exact_matches / len(y_true) if y_true else 0
    
    partial_matches = sum(1 for gt, pred in zip(y_true, y_pred) if gt in pred or pred in gt)
    partial_accuracy = partial_matches / len(y_true) if y_true else 0
    
    metrics = {
        "exact_match_accuracy": exact_accuracy,
        "partial_match_accuracy": partial_accuracy,
        "extraction_success_rate": extraction_success / len(results) if results else 0,
        "total_samples": len(results)
    }
    
    if use_f1:
        token_f1s = [calculate_token_f1(gt, pred) for gt, pred in zip(y_true, y_pred)]
        metrics["macro_f1"] = sum(token_f1s) / len(token_f1s) if token_f1s else 0.0
    
    return metrics

def main():
    args = parse_args()
    
    logs_dir = args.logs_dir
    if not os.path.isabs(logs_dir):
        logs_dir = os.path.join(project_root, logs_dir)
    
    print(f"Loading results from {args.timestamp}...")
    results = load_results(logs_dir, args.timestamp)
    
    print(f"Evaluating {len(results)} samples...")
    metrics = evaluate(results, use_f1=args.use_f1, debug=args.debug)
    
    out_dir = os.path.join(logs_dir, args.timestamp)
    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    
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
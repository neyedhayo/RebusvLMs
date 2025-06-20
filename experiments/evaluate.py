import os
import json
import argparse
import re
import yaml
from typing import List, Set, Dict, Tuple, Optional, Any
from sklearn.metrics import accuracy_score, f1_score


def extract_idiom(text: str) -> str:
    """
    Extract the most likely idiom from model response text.
    Handles various response formats and extracts clean idiom phrases.
    Prioritizes triple curly bracket format {{{answer}}}.
    """
    if not text or not text.strip():
        return ""
    
    text = text.strip()
    
    # Pattern 1: Look for triple curly brackets (highest priority)
    triple_brace_pattern = r'\{\{\{([^}]+?)\}\}\}'
    match = re.search(triple_brace_pattern, text, re.DOTALL)
    if match:
        extracted = match.group(1).strip()
        if extracted and len(extracted) > 0:
            cleaned = clean_extracted_idiom(extracted)
            if is_likely_idiom(cleaned):
                return cleaned
            # If cleaning made it invalid, return the raw extracted content
            elif len(extracted.split()) >= 2 and len(extracted.split()) <= 8:
                return extracted.strip()
    
    # Pattern 2: Look for quoted idioms
    quote_patterns = [
        r'"([^"]+)"',
        r"'([^']+)'",
        r'`([^`]+)`'
    ]
    
    for pattern in quote_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            cleaned = clean_extracted_idiom(match)
            if is_likely_idiom(cleaned):
                return cleaned
    
    # Pattern 3: Look for "The idiom is:" or similar
    idiom_intro_patterns = [
        r'(?:the idiom is|idiom is|answer is|solution is)[:.]?\s*(.+?)(?:\.|$)',
        r'(?:this idiom is|it is|this is)[:.]?\s*(.+?)(?:\.|$)',
        r'(?:represents|means)[:.]?\s*(.+?)(?:\.|$)'
    ]
    
    for pattern in idiom_intro_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            cleaned = clean_extracted_idiom(candidate)
            if is_likely_idiom(cleaned):
                return cleaned
    
    # Pattern 4: Look for standalone phrases on their own lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        if not is_description_text(line):
            cleaned = clean_extracted_idiom(line)
            if is_likely_idiom(cleaned):
                return cleaned
    
    # Pattern 5: Extract from the first sentence if it looks like an idiom
    sentences = re.split(r'[.!?]+', text)
    if sentences:
        first_sentence = sentences[0].strip()
        cleaned = clean_extracted_idiom(first_sentence)
        if is_likely_idiom(cleaned):
            return cleaned
    
    # Pattern 6: Look for common idiom patterns in the text
    idiom_candidates = []
    
    # Find phrases that look like idioms (3-8 words, common idiom words)
    words = text.split()
    for i in range(len(words)):
        for j in range(i + 3, min(i + 9, len(words) + 1)):
            phrase = ' '.join(words[i:j])
            cleaned = clean_extracted_idiom(phrase)
            if is_likely_idiom(cleaned):
                idiom_candidates.append(cleaned)
    
    if idiom_candidates:
        return select_best_idiom_candidate(idiom_candidates)
    
    # Fallback: return the whole text cleaned up
    return clean_extracted_idiom(text)


def normalize_idiom(idiom: str) -> str:
    """
    Normalize an idiom for comparison by standardizing format.
    """
    if not idiom:
        return ""
    
    # Convert to lowercase
    normalized = idiom.lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove common punctuation at start/end
    normalized = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', normalized)
    
    # Handle common variations
    replacements = {
        r'\band\b': '&',  # Convert 'and' to '&' for consistency
        r'\bu\b': 'you',   # Convert 'u' to 'you'
        r'\br\b': 'are',   # Convert 'r' to 'are'
        r'\s*-\s*': ' ',   # Convert dashes to spaces
        r'\s*_\s*': ' ',   # Convert underscores to spaces
    }
    
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    
    # Remove articles at the beginning for better matching
    normalized = re.sub(r'^(a|an|the)\s+', '', normalized)
    
    return normalized.strip()


def clean_extracted_idiom(text: str) -> str:
    """
    Clean extracted text to get just the idiom phrase.
    """
    if not text:
        return ""
    
    cleaned = text.strip()
    
    # Remove triple curly braces if they wrap the entire string
    # (This should not happen if extraction worked correctly, but just in case)
    if cleaned.startswith('{{{') and cleaned.endswith('}}}'):
        cleaned = cleaned[3:-3].strip()
    
    # Remove common prefixes/suffixes
    prefixes_to_remove = [
        r'^(?:the idiom is|idiom is|answer is|solution is|this is|it is)[:.]?\s*',
        r'^(?:i think|i believe|this looks like|this appears to be)[:.]?\s*',
        r'^(?:the answer is|the solution is)[:.]?\s*',
        r'^(?:this idiom|this rebus|this puzzle)[:.]?\s*(?:represents|means|shows|is)[:.]?\s*'
    ]
    
    for prefix in prefixes_to_remove:
        cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
    
    # Remove common suffixes
    suffixes_to_remove = [
        r'\s*(?:idiom|rebus|puzzle|phrase)$',
        r'\s*(?:is the answer|is the solution)$',
        r'\s*(?:\.|!|\?)$'
    ]
    
    for suffix in suffixes_to_remove:
        cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
    
    # Remove quotes if they wrap the entire string
    cleaned = cleaned.strip()
    if (cleaned.startswith('"') and cleaned.endswith('"')) or \
       (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1]
    
    return cleaned.strip()


def is_description_text(text: str) -> bool:
    """
    Check if text is likely a description rather than an idiom.
    """
    if not text:
        return True
    
    description_indicators = [
        'this idiom', 'this rebus', 'this puzzle', 'this image', 'this picture',
        'the idiom', 'the rebus', 'the puzzle', 'the image', 'the picture',
        'represents', 'means that', 'refers to', 'indicates', 'suggests',
        'thinking step by step', 'let me think', 'analyzing', 'looking at',
        'i can see', 'i notice', 'this shows', 'this depicts'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in description_indicators)


def is_likely_idiom(text: str) -> bool:
    """
    Check if text looks like a plausible idiom.
    """
    if not text or len(text.strip()) < 3:
        return False
    
    text = text.strip()
    
    # Too long to be an idiom
    if len(text) > 100:
        return False
    
    # Check word count (idioms are usually 2-10 words)
    word_count = len(text.split())
    if word_count < 1 or word_count > 10:  # Allow single words for some idioms
        return False
    
    # Check for description indicators
    if is_description_text(text):
        return False
    
    return True


def select_best_idiom_candidate(candidates: List[str]) -> str:
    """
    Select the best idiom candidate from a list.
    """
    if not candidates:
        return ""
    
    if len(candidates) == 1:
        return candidates[0]
    
    # Prefer shorter, more concise candidates
    scored_candidates = []
    for candidate in candidates:
        score = 0
        word_count = len(candidate.split())
        
        # Prefer 3-6 word idioms
        if 3 <= word_count <= 6:
            score += 10
        elif word_count <= 8:
            score += 5
        
        # Prefer candidates without description words
        if not is_description_text(candidate):
            score += 5
        
        # Prefer candidates with common idiom patterns
        if any(word in candidate.lower() for word in ['the', 'a', 'an']):
            score += 2
        
        scored_candidates.append((score, candidate))
    
    # Return the highest scoring candidate
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return scored_candidates[0][1]


def calculate_token_f1(ground_truth: str, prediction: str) -> float:
    """
    Calculate token-level F1 score between ground truth and prediction.
    """
    def tokenize_for_f1(text: str) -> Set[str]:
        # Normalize and tokenize
        text = normalize_idiom(text)
        return set(text.split())
    
    gt_tokens = tokenize_for_f1(ground_truth)
    pred_tokens = tokenize_for_f1(prediction)
    
    if not gt_tokens and not pred_tokens:
        return 1.0
    if not gt_tokens or not pred_tokens:
        return 0.0
    
    # Calculate precision, recall, F1
    intersection = gt_tokens.intersection(pred_tokens)
    precision = len(intersection) / len(pred_tokens) if pred_tokens else 0.0
    recall = len(intersection) / len(gt_tokens) if gt_tokens else 0.0
    
    if precision + recall == 0:
        return 0.0
    
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate VLM rebus-puzzle results with advanced idiom extraction."
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
        default=True,  # Changed: default to True
        help="Also compute macro F1 over tokenized predictions"
    )
    parser.add_argument(
        "--use-extraction",
        action="store_true",
        default=True,  # Changed: default to True since this is what they want
        help="Use advanced idiom extraction before evaluation"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed debug information"
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


def evaluate(results: List[dict], use_f1: bool = False, use_extraction: bool = False, debug: bool = False) -> dict:
    """
    Compute accuracy and optionally macro F1 with advanced idiom extraction.
    Returns a metrics dict.
    """
    y_true = []
    y_pred = []
    y_pred_extracted = []
    
    extraction_debug = []
    
    for i, r in enumerate(results):
        ground_truth = r["ground_truth"]
        prediction = r["prediction"]
        
        # Apply extraction if requested
        if use_extraction:
            extracted_prediction = extract_idiom(prediction)
            y_pred_extracted.append(extracted_prediction)
            
            if debug and i < 5:  # Show first 5 examples
                extraction_debug.append({
                    "image_id": r.get("image_id", f"sample_{i}"),
                    "ground_truth": ground_truth,
                    "raw_prediction": prediction[:200] + "..." if len(prediction) > 200 else prediction,
                    "extracted": extracted_prediction
                })
        else:
            extracted_prediction = prediction
        
        y_true.append(ground_truth)
        y_pred.append(prediction)
    
    # Use extracted predictions for evaluation if extraction is enabled
    eval_predictions = y_pred_extracted if use_extraction else y_pred
    
    # Exact-match accuracy (with normalization for fair comparison)
    normalized_true = [normalize_idiom(gt) for gt in y_true]
    normalized_pred = [normalize_idiom(pred) for pred in eval_predictions]
    
    exact_matches = sum(1 for gt, pred in zip(normalized_true, normalized_pred) 
                       if gt == pred)
    exact_match = exact_matches / len(normalized_true) if normalized_true else 0
    
    # Raw accuracy (without normalization)
    raw_accuracy = accuracy_score(y_true, eval_predictions)
    
    metrics = {
        "total_samples": len(results),
        "exact_matches": exact_matches,
        "exact_match_accuracy": exact_match,
        "raw_accuracy": raw_accuracy,
        "extraction_enabled": use_extraction,
        # Formatted versions with percentages
        "exact_match_accuracy_formatted": f"{exact_match:.4f} ({exact_match*100:.1f}%)",
        "raw_accuracy_formatted": f"{raw_accuracy:.4f} ({raw_accuracy*100:.1f}%)"
    }
    
    if use_extraction:
        # Also compute accuracy on raw predictions for comparison
        raw_normalized_pred = [normalize_idiom(p) for p in y_pred]
        raw_exact_matches = sum(1 for gt, pred in zip(normalized_true, raw_normalized_pred) 
                               if gt == pred)
        raw_exact_match = raw_exact_matches / len(normalized_true) if normalized_true else 0
        
        # Calculate extraction improvement
        extraction_improvement = exact_match - raw_exact_match
        
        metrics["raw_exact_matches"] = raw_exact_matches
        metrics["raw_exact_match_accuracy"] = raw_exact_match
        metrics["extraction_improvement"] = extraction_improvement
        
        # Formatted versions
        metrics["raw_exact_match_accuracy_formatted"] = f"{raw_exact_match:.4f} ({raw_exact_match*100:.1f}%)"
        metrics["extraction_improvement_formatted"] = f"+{extraction_improvement:.4f} (+{extraction_improvement*100:.1f}%)"
    
    if use_f1:
        # Token-level F1 scores
        token_f1s = []
        for gt, pred in zip(y_true, eval_predictions):
            f1_score = calculate_token_f1(gt, pred)
            token_f1s.append(f1_score)
        
        macro_f1 = sum(token_f1s) / len(token_f1s) if token_f1s else 0.0
        metrics["macro_f1"] = macro_f1
        metrics["macro_f1_formatted"] = f"{macro_f1:.4f} ({macro_f1*100:.1f}%)"
    
    if debug:
        metrics["extraction_debug"] = extraction_debug
    
    return metrics


def main():
    args = parse_args()
    
    print(f"🔍 Evaluating results from {args.timestamp}")
    print(f"📁 Looking in: {args.logs_dir}/{args.timestamp}/")
    print(f"🔧 Settings: extraction={args.use_extraction}, f1={args.use_f1}, debug={args.debug}")
    print("=" * 60)
    
    # 1. Load results
    try:
        results = load_results(args.logs_dir, args.timestamp)
        print(f"✅ Loaded {len(results)} results")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Evaluate
    metrics = evaluate(results, use_f1=args.use_f1, use_extraction=args.use_extraction, debug=args.debug)
    
    # 3. Write metrics.json
    out_dir = os.path.join(args.logs_dir, args.timestamp)
    metrics_path = os.path.join(out_dir, "metrics.json")
    
    # Remove debug info before saving
    save_metrics = {k: v for k, v in metrics.items() if k != "extraction_debug"}
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(save_metrics, f, indent=2)
    
    # 4. Print summary
    print(f"\n📊 EVALUATION RESULTS")
    print("=" * 40)
    print(f"Total samples:           {metrics['total_samples']}")
    print(f"Exact matches:           {metrics['exact_matches']}")
    print(f"Exact match accuracy:    {metrics['exact_match_accuracy_formatted']}")
    print(f"Raw accuracy:            {metrics['raw_accuracy_formatted']}")
    
    if args.use_extraction:
        print(f"Raw exact matches:       {metrics.get('raw_exact_matches', 0)}")
        print(f"Raw exact match accuracy: {metrics.get('raw_exact_match_accuracy_formatted', 'N/A')}")
        print(f"Extraction improvement:  {metrics.get('extraction_improvement_formatted', 'N/A')}")
    
    if args.use_f1:
        print(f"Macro F1 (token-level):  {metrics.get('macro_f1_formatted', 'N/A')}")
    
    print(f"\n💾 Metrics saved to: {metrics_path}")
    
    # 5. Show debugging examples
    if args.debug and "extraction_debug" in metrics:
        print(f"\n🔍 EXTRACTION EXAMPLES")
        print("=" * 40)
        for example in metrics["extraction_debug"]:
            print(f"\nImage: {example['image_id']}")
            print(f"GT: {example['ground_truth']}")
            print(f"Raw: {example['raw_prediction']}")
            print(f"Extracted: {example['extracted']}")
            gt_norm = normalize_idiom(example['ground_truth'])
            ext_norm = normalize_idiom(example['extracted'])
            match = "✅" if gt_norm == ext_norm else "❌"
            print(f"Match: {match} ('{gt_norm}' vs '{ext_norm}')")


if __name__ == "__main__":
    main()
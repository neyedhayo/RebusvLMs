import os
import json
import argparse
from typing import List, Dict, Any
from experiments.evaluate import extract_idiom, normalize_idiom, clean_extracted_idiom


def load_results_for_debug(logs_dir: str, timestamp: str) -> List[Dict[str, Any]]:
    """Load results from a specific timestamp for debugging."""
    results_path = os.path.join(logs_dir, timestamp, "results.json")
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"Results file not found: {results_path}")
    
    with open(results_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def debug_extraction_for_sample(sample: Dict[str, Any], sample_id: int) -> Dict[str, Any]:
    """Debug extraction process for a single sample."""
    ground_truth = sample["ground_truth"]
    raw_prediction = sample["prediction"]
    
    # Apply extraction
    extracted_prediction = extract_idiom(raw_prediction)
    
    # Apply normalization
    normalized_gt = normalize_idiom(ground_truth)
    normalized_pred = normalize_idiom(extracted_prediction)
    normalized_raw = normalize_idiom(raw_prediction)
    
    # Check matches
    raw_match = normalized_gt == normalized_raw
    extracted_match = normalized_gt == normalized_pred
    
    return {
        "sample_id": sample_id,
        "image_id": sample.get("image_id", f"sample_{sample_id}"),
        "ground_truth": ground_truth,
        "raw_prediction": raw_prediction,
        "extracted_prediction": extracted_prediction,
        "normalized_gt": normalized_gt,
        "normalized_raw": normalized_raw,
        "normalized_extracted": normalized_pred,
        "raw_match": raw_match,
        "extracted_match": extracted_match,
        "extraction_helped": extracted_match and not raw_match,
        "extraction_hurt": raw_match and not extracted_match
    }


def analyze_extraction_performance(debug_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze overall extraction performance."""
    total_samples = len(debug_results)
    raw_correct = sum(1 for r in debug_results if r["raw_match"])
    extracted_correct = sum(1 for r in debug_results if r["extracted_match"])
    extraction_helped = sum(1 for r in debug_results if r["extraction_helped"])
    extraction_hurt = sum(1 for r in debug_results if r["extraction_hurt"])
    
    return {
        "total_samples": total_samples,
        "raw_accuracy": raw_correct / total_samples if total_samples > 0 else 0,
        "extracted_accuracy": extracted_correct / total_samples if total_samples > 0 else 0,
        "extraction_helped_count": extraction_helped,
        "extraction_hurt_count": extraction_hurt,
        "net_improvement": extraction_helped - extraction_hurt,
        "improvement_rate": (extracted_correct - raw_correct) / total_samples if total_samples > 0 else 0
    }


def print_debug_summary(analysis: Dict[str, Any]):
    """Print a summary of the extraction analysis."""
    print("\n" + "="*60)
    print("EXTRACTION DEBUGGING SUMMARY")
    print("="*60)
    print(f"Total samples: {analysis['total_samples']}")
    print(f"Raw accuracy: {analysis['raw_accuracy']:.4f}")
    print(f"Extracted accuracy: {analysis['extracted_accuracy']:.4f}")
    print(f"Improvement: {analysis['improvement_rate']:+.4f}")
    print(f"Extraction helped: {analysis['extraction_helped_count']} samples")
    print(f"Extraction hurt: {analysis['extraction_hurt_count']} samples")
    print(f"Net improvement: {analysis['net_improvement']:+d} samples")


def print_sample_details(debug_results: List[Dict[str, Any]], 
                        show_all: bool = False, 
                        show_helped: bool = False, 
                        show_hurt: bool = False,
                        max_samples: int = 10):
    """Print detailed information for specific samples."""
    
    if show_all:
        samples_to_show = debug_results[:max_samples]
        print(f"\n=== SHOWING ALL SAMPLES (first {max_samples}) ===")
    elif show_helped:
        samples_to_show = [r for r in debug_results if r["extraction_helped"]][:max_samples]
        print(f"\n=== SAMPLES WHERE EXTRACTION HELPED (first {max_samples}) ===")
    elif show_hurt:
        samples_to_show = [r for r in debug_results if r["extraction_hurt"]][:max_samples]
        print(f"\n=== SAMPLES WHERE EXTRACTION HURT (first {max_samples}) ===")
    else:
        # Show a mix: some that helped, some that hurt, some that didn't change
        helped = [r for r in debug_results if r["extraction_helped"]][:3]
        hurt = [r for r in debug_results if r["extraction_hurt"]][:3]
        unchanged = [r for r in debug_results if not r["extraction_helped"] and not r["extraction_hurt"]][:4]
        samples_to_show = helped + hurt + unchanged
        print(f"\n=== SAMPLE DETAILS (mixed selection) ===")
    
    for i, sample in enumerate(samples_to_show):
        print(f"\n--- Sample {sample['sample_id']} (Image: {sample['image_id']}) ---")
        print(f"Ground Truth: {sample['ground_truth']}")
        print(f"Raw Prediction: {sample['raw_prediction']}")
        print(f"Extracted: {sample['extracted_prediction']}")
        print(f"Normalized GT: {sample['normalized_gt']}")
        print(f"Normalized Raw: {sample['normalized_raw']}")
        print(f"Normalized Extracted: {sample['normalized_extracted']}")
        print(f"Raw Match: {sample['raw_match']}")
        print(f"Extracted Match: {sample['extracted_match']}")
        
        if sample["extraction_helped"]:
            print("✅ EXTRACTION HELPED")
        elif sample["extraction_hurt"]:
            print("❌ EXTRACTION HURT")
        else:
            print("➖ NO CHANGE")


def save_debug_results(debug_results: List[Dict[str, Any]], 
                      analysis: Dict[str, Any], 
                      output_path: str):
    """Save detailed debug results to a JSON file."""
    debug_data = {
        "analysis": analysis,
        "sample_details": debug_results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(debug_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed debug results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Debug idiom extraction results")
    parser.add_argument("--timestamp", required=True, 
                       help="Timestamp of the run to debug")
    parser.add_argument("--logs-dir", default="logs", 
                       help="Logs directory")
    parser.add_argument("--show-all", action="store_true",
                       help="Show details for all samples")
    parser.add_argument("--show-helped", action="store_true",
                       help="Show only samples where extraction helped")
    parser.add_argument("--show-hurt", action="store_true",
                       help="Show only samples where extraction hurt")
    parser.add_argument("--max-samples", type=int, default=10,
                       help="Maximum number of samples to show in detail")
    parser.add_argument("--save-debug", action="store_true",
                       help="Save detailed debug results to JSON")
    
    args = parser.parse_args()
    
    # Load results
    try:
        results = load_results_for_debug(args.logs_dir, args.timestamp)
        print(f"Loaded {len(results)} samples from {args.timestamp}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Debug each sample
    debug_results = []
    for i, sample in enumerate(results):
        debug_info = debug_extraction_for_sample(sample, i)
        debug_results.append(debug_info)
    
    # Analyze performance
    analysis = analyze_extraction_performance(debug_results)
    
    # Print summary
    print_debug_summary(analysis)
    
    # Print sample details if requested
    if args.show_all or args.show_helped or args.show_hurt or True:  # Always show some samples
        print_sample_details(
            debug_results,
            show_all=args.show_all,
            show_helped=args.show_helped,
            show_hurt=args.show_hurt,
            max_samples=args.max_samples
        )
    
    # Save debug results if requested
    if args.save_debug:
        debug_output_path = os.path.join(args.logs_dir, args.timestamp, "debug_extraction.json")
        save_debug_results(debug_results, analysis, debug_output_path)


if __name__ == "__main__":
    main()
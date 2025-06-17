import os
import json
import argparse
from typing import List, Dict
from experiments.evaluate import extract_idiom, normalize_idiom, evaluate


def quick_test_sample():
    """Quick test with sample data."""
    print("🚀 Quick Evaluation Test")
    print("=" * 40)
    
    # Sample test data
    sample_data = [
        {
            "image_id": "001", 
            "ground_truth": "a drop in the bucket",
            "prediction": 'The idiom shown is {{{a drop in the bucket}}}'  # Triple bracket format
        },
        {
            "image_id": "002",
            "ground_truth": "piece of cake", 
            "prediction": "This rebus represents {{{piece of cake}}}"  # Triple bracket format
        },
        {
            "image_id": "003",
            "ground_truth": "break the ice",
            "prediction": "Looking at this image, I think it shows {{{break the ice}}}"  # Triple bracket format
        },
        {
            "image_id": "004", 
            "ground_truth": "spill the beans",
            "prediction": "spill beans"  # Missing article - test extraction
        },
        {
            "image_id": "005",
            "ground_truth": "kick the bucket", 
            "prediction": "This is clearly about kicking a bucket - {{{kick the bucket}}}!"  # Triple bracket format
        }
    ]
    
    print(f"Testing with {len(sample_data)} sample predictions...")
    
    # Test without extraction
    print("\n--- WITHOUT EXTRACTION ---")
    metrics_no_extract = evaluate(sample_data, use_f1=True, use_extraction=False)
    print(f"Raw accuracy: {metrics_no_extract['raw_accuracy']:.4f}")
    print(f"Exact match: {metrics_no_extract['exact_match_accuracy']:.4f}")
    print(f"Macro F1: {metrics_no_extract.get('macro_f1', 0):.4f}")
    
    # Test with extraction
    print("\n--- WITH EXTRACTION ---")
    metrics_with_extract = evaluate(sample_data, use_f1=True, use_extraction=True)
    print(f"Raw accuracy: {metrics_with_extract['raw_accuracy']:.4f}")
    print(f"Exact match: {metrics_with_extract['exact_match_accuracy']:.4f}")
    print(f"Macro F1: {metrics_with_extract.get('macro_f1', 0):.4f}")
    
    # Show extraction details
    print("\n--- EXTRACTION DETAILS ---")
    for i, sample in enumerate(sample_data):
        print(f"\nSample {i+1} ({sample['image_id']}):")
        print(f"  Ground truth: {sample['ground_truth']}")
        print(f"  Raw prediction: {sample['prediction']}")
        
        extracted = extract_idiom(sample['prediction'])
        print(f"  Extracted: {extracted}")
        
        # Normalize for comparison
        gt_norm = normalize_idiom(sample['ground_truth'])
        raw_norm = normalize_idiom(sample['prediction'])
        extract_norm = normalize_idiom(extracted)
        
        raw_match = gt_norm == raw_norm
        extract_match = gt_norm == extract_norm
        
        print(f"  Raw match: {raw_match}")
        print(f"  Extract match: {extract_match}")
        
        if extract_match and not raw_match:
            print("  ✅ Extraction helped!")
        elif raw_match and not extract_match:
            print("  ❌ Extraction hurt!")
        else:
            print("  ➖ No change")


def quick_evaluate_existing(logs_dir: str, timestamp: str, sample_size: int = None):
    """Quick evaluation of existing results."""
    results_path = os.path.join(logs_dir, timestamp, "results.json")
    
    if not os.path.exists(results_path):
        print(f"❌ Results file not found: {results_path}")
        return
    
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    if sample_size:
        results = results[:sample_size]
        print(f"🔍 Quick evaluation of first {sample_size} samples from {timestamp}")
    else:
        print(f"🔍 Quick evaluation of all {len(results)} samples from {timestamp}")
    
    print("=" * 60)
    
    # Evaluate without extraction
    metrics_no_extract = evaluate(results, use_f1=True, use_extraction=False)
    
    # Evaluate with extraction  
    metrics_with_extract = evaluate(results, use_f1=True, use_extraction=True)
    
    # Print comparison
    print("COMPARISON RESULTS:")
    print("-" * 30)
    print(f"{'Metric':<25} {'No Extract':<12} {'With Extract':<12} {'Diff':<10}")
    print("-" * 60)
    
    raw_acc_diff = metrics_with_extract['raw_accuracy'] - metrics_no_extract['raw_accuracy']
    exact_acc_diff = metrics_with_extract['exact_match_accuracy'] - metrics_no_extract['exact_match_accuracy']
    f1_diff = metrics_with_extract.get('macro_f1', 0) - metrics_no_extract.get('macro_f1', 0)
    
    print(f"{'Raw Accuracy':<25} {metrics_no_extract['raw_accuracy']:<12.4f} {metrics_with_extract['raw_accuracy']:<12.4f} {raw_acc_diff:+.4f}")
    print(f"{'Exact Match Accuracy':<25} {metrics_no_extract['exact_match_accuracy']:<12.4f} {metrics_with_extract['exact_match_accuracy']:<12.4f} {exact_acc_diff:+.4f}")
    print(f"{'Macro F1':<25} {metrics_no_extract.get('macro_f1', 0):<12.4f} {metrics_with_extract.get('macro_f1', 0):<12.4f} {f1_diff:+.4f}")
    
    print(f"\nTotal samples: {len(results)}")
    
    if 'raw_exact_match_accuracy' in metrics_with_extract:
        print(f"Raw exact match (baseline): {metrics_with_extract['raw_exact_match_accuracy']:.4f}")
    
    # Show a few examples where extraction made a difference
    print("\n--- SAMPLE EXTRACTION EXAMPLES ---")
    shown = 0
    for i, sample in enumerate(results[:20]):  # Check first 20
        if shown >= 5:  # Show max 5 examples
            break
            
        gt = sample['ground_truth']
        pred = sample['prediction']
        extracted = extract_idiom(pred)
        
        gt_norm = normalize_idiom(gt)
        pred_norm = normalize_idiom(pred)
        extract_norm = normalize_idiom(extracted)
        
        raw_match = gt_norm == pred_norm
        extract_match = gt_norm == extract_norm
        
        if raw_match != extract_match:  # Extraction made a difference
            print(f"\nExample {shown + 1} (Sample {i}):")
            print(f"  GT: {gt}")
            print(f"  Raw: {pred}")
            print(f"  Extracted: {extracted}")
            print(f"  Raw match: {raw_match}, Extract match: {extract_match}")
            if extract_match and not raw_match:
                print("  ✅ Extraction helped!")
            else:
                print("  ❌ Extraction hurt!")
            shown += 1


def main():
    parser = argparse.ArgumentParser(description="Quick evaluation tool")
    parser.add_argument("--test-sample", action="store_true",
                       help="Run quick test with sample data")
    parser.add_argument("--timestamp", 
                       help="Evaluate existing results from timestamp")
    parser.add_argument("--logs-dir", default="logs",
                       help="Logs directory (default: logs)")
    parser.add_argument("--sample-size", type=int,
                       help="Only evaluate first N samples (for speed)")
    
    args = parser.parse_args()
    
    if args.test_sample:
        quick_test_sample()
    elif args.timestamp:
        quick_evaluate_existing(args.logs_dir, args.timestamp, args.sample_size)
    else:
        print("❌ Please specify either --test-sample or --timestamp")
        print("Examples:")
        print("  python quick_evaluate.py --test-sample")
        print("  python quick_evaluate.py --timestamp 20250617_143000")
        print("  python quick_evaluate.py --timestamp 20250617_143000 --sample-size 50")


if __name__ == "__main__":
    main()
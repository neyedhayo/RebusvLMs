#!/usr/bin/env python3
"""
Script to retry processing failed images from a previous experiment run.
"""

import os
import json
import argparse
import time
import sys
from pathlib import Path

# Add project root to Python path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env file if it exists
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def parse_args():
    parser = argparse.ArgumentParser(description="Retry failed images from experiment")
    parser.add_argument("--timestamp", required=True, 
                       help="Timestamp of the experiment to complete")
    parser.add_argument("--config", required=True,
                       help="Config file used in original experiment")
    parser.add_argument("--prompt-style", required=True,
                       help="Prompt style used in original experiment")
    parser.add_argument("--examples-count", type=int, default=2,
                       help="Examples count used in original experiment")
    parser.add_argument("--delay", type=float, default=10.0,
                       help="Delay between requests in seconds (default: 10)")
    return parser.parse_args()

def find_missing_images(timestamp: str, all_images_dir: str) -> list:
    """Find images that don't have results in the timestamp folder"""
    results_dir = Path(f"logs/{timestamp}/responses")
    
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return []
    
    # Get all expected images
    all_images = []
    for img_file in Path(all_images_dir).glob("*.jpg"):
        img_id = img_file.stem
        all_images.append(img_id)
    
    # Get processed images
    processed_images = set()
    for response_file in results_dir.glob("*.json"):
        img_id = response_file.stem
        processed_images.add(img_id)
    
    # Find missing
    missing = [img_id for img_id in all_images if img_id not in processed_images]
    
    print(f"📊 Found {len(all_images)} total images")
    print(f"✅ {len(processed_images)} already processed")
    print(f"❌ {len(missing)} missing: {sorted(missing)}")
    
    return missing

def retry_missing_images(args, missing_images: list):
    """Retry processing missing images with delays"""
    if not missing_images:
        print("✅ No missing images to retry!")
        return
    
    print(f"\n🔄 Retrying {len(missing_images)} missing images...")
    print(f"⏱️  Using {args.delay}s delay between requests")
    
    # Import necessary modules
    import yaml
    from data.load_data import load_dataset
    from prompts.builder import PromptBuilder
    from experiments.run_experiment import get_model_client
    from experiments.utils import expand_env_vars_recursive
    
    # Load config (same as in run_experiment.py)
    base = yaml.safe_load(open("config/base.yaml"))
    model = yaml.safe_load(open(f"config/{args.config}"))
    cfg = {**base, **model}
    
    # ✅ FIX: Use the proper utility function to expand ALL environment variables
    cfg = expand_env_vars_recursive(cfg)
    
    print(f"🔧 Using model: {cfg['model']['name']}")
    print(f"🔧 API type: {cfg['model'].get('api_type', 'studio')}")
    if not cfg["model"].get("use_vertexai", False):
        api_key_preview = cfg['model']['api_key'][:10] + "..." if len(cfg['model']['api_key']) > 10 else cfg['model']['api_key']
        print(f"🔧 API key: {api_key_preview}")
    
    # Setup
    builder = PromptBuilder(cfg)
    client = get_model_client(cfg)
    
    # Load dataset to get image paths and truths
    dataset = load_dataset(
        cfg["dataset"]["images_dir"],
        cfg["dataset"]["annotations_file"]
    )
    
    # Create lookup
    dataset_lookup = {
        os.path.splitext(os.path.basename(img_path))[0]: (img_path, truth)
        for img_path, truth in dataset
    }
    
    # Setup output directories
    timestamp = args.timestamp
    prompts_dir = f"logs/{timestamp}/prompts"
    responses_dir = f"logs/{timestamp}/responses"
    
    successful = 0
    failed = []
    
    for i, img_id in enumerate(missing_images):
        if img_id not in dataset_lookup:
            print(f"⚠️  {img_id} not found in dataset, skipping")
            continue
            
        img_path, truth = dataset_lookup[img_id]
        
        print(f"\n🔄 [{i+1}/{len(missing_images)}] Processing {img_id}...")
        
        try:
            # Build prompt
            prompt = builder.build(args.prompt_style, args.examples_count, img_path)
            
            # Save prompt
            with open(f"{prompts_dir}/{img_id}.txt", "w", encoding="utf-8") as f:
                f.write(prompt)
            
            # Generate with delay
            time.sleep(args.delay)  # Pre-request delay
            pred = client.generate(prompt, img_path)
            
            # Save response
            with open(f"{responses_dir}/{img_id}.json", "w", encoding="utf-8") as f:
                json.dump({"prediction": pred}, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Successfully processed {img_id}")
            successful += 1
            
        except Exception as e:
            print(f"❌ Failed to process {img_id}: {e}")
            failed.append(img_id)
    
    print(f"\n📊 Retry Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {len(failed)}")
    if failed:
        print(f"Failed images: {failed}")
    
    # Update results.json
    if successful > 0:
        update_results_json(timestamp, cfg)

def update_results_json(timestamp: str, cfg: dict):
    """Regenerate the complete results.json file"""
    print(f"\n🔄 Updating results.json...")
    
    from data.load_data import load_dataset
    
    dataset = load_dataset(
        cfg["dataset"]["images_dir"],
        cfg["dataset"]["annotations_file"]
    )
    
    responses_dir = Path(f"logs/{timestamp}/responses")
    results = []
    
    for img_path, truth in dataset:
        img_id = os.path.splitext(os.path.basename(img_path))[0]
        response_file = responses_dir / f"{img_id}.json"
        
        if response_file.exists():
            with open(response_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pred = data.get("prediction", "")
            
            results.append({
                "image_id": img_id,
                "ground_truth": truth,
                "prediction": pred
            })
    
    # Write updated results
    results_file = f"logs/{timestamp}/results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated {results_file} with {len(results)} results")

def main():
    args = parse_args()
    
    # Load config to get images directory
    import yaml
    base = yaml.safe_load(open("config/base.yaml"))
    model = yaml.safe_load(open(f"config/{args.config}"))
    cfg = {**base, **model}
    
    # Expand environment variables
    cfg["project"] = os.path.expandvars(cfg["project"])
    cfg["location"] = os.path.expandvars(cfg["location"])
    cfg["use_vertexai"] = os.path.expandvars(cfg["use_vertexai"])
    
    # Find missing images
    missing = find_missing_images(args.timestamp, cfg["dataset"]["images_dir"])
    
    if not missing:
        print("✅ No missing images found!")
        return
    
    # Ask for confirmation
    print(f"\n❓ Retry {len(missing)} missing images? (y/n): ", end="")
    if input().lower() != 'y':
        print("❌ Cancelled")
        return
    
    # Retry missing images
    retry_missing_images(args, missing)

if __name__ == "__main__":
    main()
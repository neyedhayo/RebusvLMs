import os
import sys
import yaml
import argparse
import datetime
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.load_data import load_dataset
from prompts.builder import PromptBuilder
from models.gemini1_5 import Gemini15Client
from models.gemini2_0 import Gemini20Client
from models.gemini2_5 import Gemini25Client
from experiments.utils import ensure_dir

def load_config_files(config_name):
    """Load and merge base config with model-specific config"""
    base_config_path = os.path.join(project_root, "config", "base.yaml")
    model_config_path = os.path.join(project_root, "config", config_name)
    
    if not os.path.exists(base_config_path):
        raise FileNotFoundError(f"Base config not found: {base_config_path}")
    if not os.path.exists(model_config_path):
        raise FileNotFoundError(f"Model config not found: {model_config_path}")
    
    with open(base_config_path, 'r') as f:
        base_config = yaml.safe_load(f)
    
    with open(model_config_path, 'r') as f:
        model_config = yaml.safe_load(f)
    
    # Merge configs (model config overrides base config)
    merged_config = {**base_config, **model_config}
    
    # Expand ALL environment variables recursively
    merged_config = expand_env_vars_recursive(merged_config)
    
    return merged_config

def expand_env_vars_recursive(obj):
    """Recursively expand environment variables in config object"""
    if isinstance(obj, dict):
        return {k: expand_env_vars_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars_recursive(item) for item in obj]
    elif isinstance(obj, str):
        return os.path.expandvars(obj)
    else:
        return obj

def get_model_client(cfg):
    """Dispatch to the right client based on use_vertexai and model name."""
    name = cfg["model"]["name"]
    if not cfg["model"].get("use_vertexai", False):
        return Gemini15Client(cfg)
    if "2.0-flash" in name:
        return Gemini20Client(cfg)
    if "2.5-flash" in name:
        return Gemini25Client(cfg)
    raise ValueError(f"Unrecognized model in config: {name}")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True,
                   help="e.g. gemini2.0.yaml")
    p.add_argument("--prompt-style", required=True,
                   choices=[
                     "zero_shot",
                     "fewshot2_cot", "fewshot3_cot",
                     "fewshot2_nocot", "fewshot3_nocot"
                   ])
    p.add_argument("--examples-count", type=int, default=2,
                   help="Number of few-shot examples")
    p.add_argument("--images-dir", help="Override dataset.images_dir")
    return p.parse_args()

def main():
    args = parse_args()

    try:
        # 1) Load & merge configs
        print(f"[run_experiment] Loading config: {args.config}")
        cfg = load_config_files(args.config)
        
        # 2) Override images_dir if requested
        if args.images_dir:
            cfg["dataset"]["images_dir"] = args.images_dir
            
        # 3) Ensure paths are absolute
        cfg["dataset"]["images_dir"] = os.path.join(project_root, cfg["dataset"]["images_dir"])
        cfg["dataset"]["annotations_file"] = os.path.join(project_root, cfg["dataset"]["annotations_file"])
        cfg["dataset"]["examples_dir"] = os.path.join(project_root, cfg["dataset"]["examples_dir"])

        # 4) Enforce supports_cot
        style = args.prompt_style
        if style.endswith("_cot") and not cfg["model"]["supports_cot"]:
            style = style.replace("_cot", "_nocot")
            print(f"[run_experiment] Model lacks CoT → switching style to '{style}'")

        # 5) Setup logging
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        logs_dir = os.path.join(project_root, cfg["logging"]["dir"])
        out_dir = os.path.join(logs_dir, ts)
        prompts_dir = os.path.join(out_dir, "prompts")
        responses_dir = os.path.join(out_dir, "responses")
        
        ensure_dir(prompts_dir)
        ensure_dir(responses_dir)
        
        print(f"[run_experiment] Output directory: {out_dir}")

        # 6) Build components
        print(f"[run_experiment] Initializing prompt builder...")
        builder = PromptBuilder(cfg)
        
        print(f"[run_experiment] Initializing model client...")
        client = get_model_client(cfg)
        
        print(f"[run_experiment] Loading dataset...")
        dataset = load_dataset(
            cfg["dataset"]["images_dir"],
            cfg["dataset"]["annotations_file"]
        )
        
        print(f"[run_experiment] Found {len(dataset)} images to process")

        # 7) Process each image
        results = []
        for i, (img_path, truth) in enumerate(dataset, 1):
            img_id = os.path.splitext(os.path.basename(img_path))[0]
            print(f"[run_experiment] Processing {i}/{len(dataset)}: {img_id}")
            
            try:
                # Build prompt
                prompt = builder.build(style, args.examples_count, img_path)
                
                # Save prompt
                prompt_file = os.path.join(prompts_dir, f"{img_id}.txt")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(prompt)

                # Generate prediction
                pred = client.generate(prompt, img_path)

                # Save response
                response_file = os.path.join(responses_dir, f"{img_id}.json")
                with open(response_file, "w", encoding="utf-8") as f:
                    json.dump({"prediction": pred}, f, ensure_ascii=False, indent=2)

                results.append({
                    "image_id": img_id,
                    "ground_truth": truth,
                    "prediction": pred
                })
                
                print(f"[run_experiment] ✅ {img_id}: {pred}")
                
            except Exception as e:
                print(f"[run_experiment] ❌ Error processing {img_id}: {e}")
                results.append({
                    "image_id": img_id,
                    "ground_truth": truth,
                    "prediction": f"ERROR: {str(e)}"
                })

        # 8) Write aggregate results
        results_file = os.path.join(out_dir, "results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"[run_experiment] ✅ Completed! Processed {len(results)} images")
        print(f"[run_experiment] Results saved to: {out_dir}")
        print(f"[run_experiment] To evaluate: python -m experiments.evaluate --timestamp {ts}")

    except Exception as e:
        print(f"[run_experiment] ❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
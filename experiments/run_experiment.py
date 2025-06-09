import os
import yaml
import argparse
import datetime
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.load_data import load_dataset
from prompts.builder import PromptBuilder
from models.gemini1_5 import Gemini15Client
from models.gemini2_0 import Gemini20Client
from models.gemini2_5 import Gemini25Client
from experiments.utils import ensure_dir

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

def load_config_files(config_name):
    """Load and merge config files with proper path resolution."""
    # Get absolute paths relative to project root
    base_config_path = os.path.join(project_root, "config", "base.yaml")
    model_config_path = os.path.join(project_root, "config", config_name)
    
    if not os.path.exists(base_config_path):
        raise FileNotFoundError(f"Base config not found: {base_config_path}")
    if not os.path.exists(model_config_path):
        raise FileNotFoundError(f"Model config not found: {model_config_path}")
    
    with open(base_config_path) as f:
        base = yaml.safe_load(f)
    with open(model_config_path) as f:
        model = yaml.safe_load(f)
    
    # Merge configs (shallow merge for now)
    cfg = {**base, **model}
    return cfg

def validate_environment_vars(cfg):
    """Validate that required environment variables are set."""
    required_vars = []
    
    if cfg["model"].get("use_vertexai", False):
        required_vars.extend(["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"])
    else:
        required_vars.append("GEMINI_API_KEY")
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {missing_vars}")

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
    p.add_argument("--images-dir",    help="Override dataset.images_dir")
    return p.parse_args()

def main():
    args = parse_args()

    # 1) Load & merge configs with proper path handling
    cfg = load_config_files(args.config)
    
    # 2) Validate environment variables
    validate_environment_vars(cfg)

    # 3) Expand env vars in model name
    cfg["model"]["name"] = os.path.expandvars(cfg["model"]["name"])

    # 4) Override images_dir if requested
    if args.images_dir:
        cfg["dataset"]["images_dir"] = args.images_dir

    # 5) Enforce supports_cot
    style = args.prompt_style
    if style.endswith("_cot") and not cfg["model"]["supports_cot"]:
        style = style.replace("_cot","_nocot")
        print(f"[run_experiment] Model lacks CoT → switching style to '{style}'")

    # 6) Setup logging with absolute paths
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_base = os.path.join(project_root, cfg["logging"]["dir"])
    out = os.path.join(logs_base, ts)
    prompts_dir = os.path.join(out, "prompts")
    responses_dir = os.path.join(out, "responses")
    ensure_dir(prompts_dir)
    ensure_dir(responses_dir)
    
    # 7) Build & call
    try:
        builder = PromptBuilder(cfg)
        client = get_model_client(cfg)
        
        # Use absolute paths for dataset
        images_dir = cfg["dataset"]["images_dir"]
        if not os.path.isabs(images_dir):
            images_dir = os.path.join(project_root, images_dir)
        
        annotations_file = cfg["dataset"]["annotations_file"]
        if not os.path.isabs(annotations_file):
            annotations_file = os.path.join(project_root, annotations_file)
        
        dataset = load_dataset(images_dir, annotations_file)
        
        if not dataset:
            print("Warning: No valid image-annotation pairs found!")
            return
            
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise

    results = []
    for img_path, truth in dataset:
        try:
            prompt = builder.build(style, args.examples_count, img_path)
            img_id = os.path.splitext(os.path.basename(img_path))[0]

            # Save prompt
            with open(f"{prompts_dir}/{img_id}.txt", "w", encoding="utf-8") as f:
                f.write(prompt)

            # Generate - FIXED: Remove model_name parameter
            pred = client.generate(prompt, img_path)

            # Save response
            with open(f"{responses_dir}/{img_id}.json", "w", encoding="utf-8") as f:
                json.dump({"prediction": pred}, f, ensure_ascii=False, indent=2)

            results.append({
                "image_id": img_id,
                "ground_truth": truth,
                "prediction": pred
            })
            
            print(f"Processed {img_id}: {pred[:50]}...")
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue

    # 8) Write aggregate
    with open(f"{out}/results.json","w",encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[run_experiment] Completed! Processed {len(results)} images. Logs → {out}")

if __name__=="__main__":
    main()

import os
import sys
import yaml
import argparse
import datetime
import json
from pathlib import Path

project_root = Path(__file__).parent.parent  # Go up from experiments/ to RebusvLMs/
sys.path.insert(0, str(project_root))

from data.load_data import load_dataset
from prompts.builder import PromptBuilder
from models.gemini1_5 import Gemini15Client
from models.gemini2_0 import Gemini20Client
from models.gemini2_5 import Gemini25Client
from experiments.utils import ensure_dir, expand_env_vars_recursive


def load_config(base_path: str, model_path: str):
    """Load and merge configuration files with environment variable expansion."""
    try:
        # Load base config
        with open(base_path, 'r', encoding='utf-8') as f:
            base_config = yaml.safe_load(f)
        
        # Load model config
        with open(model_path, 'r', encoding='utf-8') as f:
            model_config = yaml.safe_load(f)
        
        # Merge configs (model overrides base)
        merged_config = {**base_config, **model_config}
        
        # Expand environment variables
        expanded_config = expand_env_vars_recursive(merged_config)
        
        return expanded_config
        
    except FileNotFoundError as e:
        print(f"❌ Config file not found: {e}")
        raise
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        raise


def get_model_client(cfg):
    """Dispatch to the right client based on use_vertexai and model name."""
    try:
        name = cfg["model"]["name"]
        if not cfg["model"].get("use_vertexai", False):
            return Gemini15Client(cfg)
        if "2.0-flash" in name:
            return Gemini20Client(cfg)
        if "2.5-flash" in name:
            return Gemini25Client(cfg)
        raise ValueError(f"Unrecognized model in config: {name}")
    except KeyError as e:
        print(f"❌ Missing required config key: {e}")
        raise
    except Exception as e:
        print(f"❌ Error creating model client: {e}")
        raise


def validate_config(cfg):
    """Validate that required config sections exist."""
    required_sections = ["model", "dataset", "logging"]
    missing_sections = []
    
    for section in required_sections:
        if section not in cfg:
            missing_sections.append(section)
    
    if missing_sections:
        raise ValueError(f"Missing required config sections: {missing_sections}")
    
    # Check required model fields
    required_model_fields = ["name", "max_output_tokens"]
    missing_model_fields = []
    
    for field in required_model_fields:
        if field not in cfg["model"]:
            missing_model_fields.append(field)
    
    if missing_model_fields:
        raise ValueError(f"Missing required model config fields: {missing_model_fields}")
    
    # Check dataset paths exist
    images_dir = cfg["dataset"]["images_dir"]
    annotations_file = cfg["dataset"]["annotations_file"]
    
    if not os.path.exists(images_dir):
        print(f"⚠️  Warning: Images directory not found: {images_dir}")
        print(f"   Create the directory and add your rebus images there.")
    
    if not os.path.exists(annotations_file):
        print(f"⚠️  Warning: Annotations file not found: {annotations_file}")
        print(f"   Make sure your CSV file exists with 'Filename' and 'Solution' columns.")


def parse_args():
    p = argparse.ArgumentParser(description="Run VLM rebus puzzle experiments")
    p.add_argument("--config", required=True,
                   help="Model config file (e.g. gemini2.0.yaml)")
    p.add_argument("--prompt-style", required=True,
                   choices=[
                     "zero_shot",
                     "fewshot2_cot", "fewshot3_cot",
                     "fewshot2_nocot", "fewshot3_nocot"
                   ],
                   help="Prompt style to use")
    p.add_argument("--examples-count", type=int, default=2,
                   help="Number of few-shot examples (ignored for zero_shot)")
    p.add_argument("--images-dir", 
                   help="Override dataset.images_dir")
    p.add_argument("--dry-run", action="store_true",
                   help="Validate setup without running experiments")
    p.add_argument("--max-samples", type=int,
                   help="Limit to first N samples (for testing)")
    return p.parse_args()


def main():
    args = parse_args()

    print("🚀 RebusvLMs Experiment Runner")
    print("=" * 50)

    try:
        # 1) Load & merge configs
        print("📋 Loading configuration...")
        base_config_path = "config/base.yaml"
        model_config_path = f"config/{args.config}"
        
        cfg = load_config(base_config_path, model_config_path)
        print(f"  ✅ Loaded {base_config_path} and {model_config_path}")

        # 2) Validate configuration
        print("🔍 Validating configuration...")
        validate_config(cfg)
        print("  ✅ Configuration validated")

        # 3) Override images_dir if requested
        if args.images_dir:
            cfg["dataset"]["images_dir"] = args.images_dir
            print(f"  📁 Overrode images_dir: {args.images_dir}")

        # 4) Enforce supports_cot
        style = args.prompt_style
        if style.endswith("_cot") and not cfg["model"].get("supports_cot", True):
            style = style.replace("_cot", "_nocot")
            print(f"⚠️  Model lacks CoT support → switching to '{style}'")

        # 5) Setup logging
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(cfg["logging"]["dir"], ts)
        prompts_dir = os.path.join(out_dir, "prompts")
        responses_dir = os.path.join(out_dir, "responses")
        
        ensure_dir(prompts_dir)
        ensure_dir(responses_dir)
        print(f"📁 Created output directory: {out_dir}")

        # 6) Initialize components
        print("🔧 Initializing components...")
        
        # Check if examples directory exists for few-shot
        if style != "zero_shot":
            examples_dir = cfg["dataset"]["examples_dir"]
            if not os.path.exists(examples_dir):
                print(f"⚠️  Examples directory not found: {examples_dir}")
                print(f"   Creating it and adding sample data...")
                ensure_dir(examples_dir)
                # Could create sample data here if needed
        
        builder = PromptBuilder(cfg)
        print("  ✅ Prompt builder initialized")
        
        if args.dry_run:
            print("🏃 Dry run mode - skipping model initialization and execution")
            print("✅ Setup validation completed successfully!")
            return
        
        client = get_model_client(cfg)
        print("  ✅ Model client initialized")
        
        # 7) Load dataset
        print("📊 Loading dataset...")
        try:
            dataset = load_dataset(
                cfg["dataset"]["images_dir"],
                cfg["dataset"]["annotations_file"]
            )
            print(f"  ✅ Loaded {len(dataset)} image-answer pairs")
            
            if args.max_samples:
                dataset = dataset[:args.max_samples]
                print(f"  🔢 Limited to first {args.max_samples} samples")
                
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            print("   Make sure your images and annotations file exist.")
            raise

        # 8) Run experiments
        print(f"🧪 Running experiment with {style} prompting...")
        print(f"   Model: {cfg['model']['name']}")
        print(f"   Samples: {len(dataset)}")
        
        results = []
        for i, (img_path, truth) in enumerate(dataset):
            print(f"  Processing {i+1}/{len(dataset)}: {os.path.basename(img_path)}")
            
            try:
                # Build prompt
                prompt = builder.build(style, args.examples_count, img_path)
                img_id = os.path.splitext(os.path.basename(img_path))[0]

                # Save prompt
                prompt_file = os.path.join(prompts_dir, f"{img_id}.txt")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(prompt)

                # Generate response
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
                
            except Exception as e:
                print(f"    ❌ Error processing {img_path}: {e}")
                # Continue with next sample
                continue

        # 9) Save aggregate results
        results_file = os.path.join(out_dir, "results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # 10) Save experiment metadata
        metadata = {
            "timestamp": ts,
            "config_file": args.config,
            "prompt_style": style,
            "examples_count": args.examples_count,
            "total_samples": len(dataset),
            "successful_samples": len(results),
            "model_name": cfg["model"]["name"],
            "images_dir": cfg["dataset"]["images_dir"],
            "annotations_file": cfg["dataset"]["annotations_file"]
        }
        
        metadata_file = os.path.join(out_dir, "metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"\n🎉 Experiment completed!")
        print(f"   Processed: {len(results)}/{len(dataset)} samples")
        print(f"   Results saved to: {out_dir}")
        print(f"\nNext steps:")
        print(f"   1. Evaluate: python experiments/evaluate.py --timestamp {ts}")
        print(f"   2. Debug: python debug_results.py --timestamp {ts}")
        print(f"   3. Quick check: python quick_evaluate.py --timestamp {ts}")

    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        raise


if __name__ == "__main__":
    main()
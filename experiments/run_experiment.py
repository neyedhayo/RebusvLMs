import os
import yaml
import argparse
import datetime
import json

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

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config",       required=True,
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

    # 1) Load & merge configs
    base = yaml.safe_load(open("config/base.yaml"))
    model = yaml.safe_load(open(f"config/{args.config}"))
    cfg = {**base, **model}

    # 2) Expand env vars in model name
    cfg["model"]["name"] = os.path.expandvars(cfg["model"]["name"])

    # 3) Override images_dir if requested
    if args.images_dir:
        cfg["dataset"]["images_dir"] = args.images_dir

    # 4) Enforce supports_cot
    style = args.prompt_style
    if style.endswith("_cot") and not cfg["model"]["supports_cot"]:
        style = style.replace("_cot","_nocot")
        print(f"[run_experiment] Model lacks CoT → switching style to '{style}'")

    # 5) Setup logging
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(cfg["logging"]["dir"], ts)
    prompts_dir   = os.path.join(out, "prompts")
    responses_dir = os.path.join(out, "responses")
    ensure_dir(prompts_dir); ensure_dir(responses_dir)

    # 6) Build & call
    builder = PromptBuilder(cfg)
    client  = get_model_client(cfg)
    dataset = load_dataset(
        cfg["dataset"]["images_dir"],
        cfg["dataset"]["annotations_file"]
    )

    results = []
    for img_path, truth in dataset:
        prompt = builder.build(style, args.examples_count, img_path)
        img_id = os.path.splitext(os.path.basename(img_path))[0]

        # Save prompt
        with open(f"{prompts_dir}/{img_id}.txt","w",encoding="utf-8") as f:
            f.write(prompt)

        # Generate
        pred = client.generate(cfg["model"]["name"], prompt, img_path)

        # Save response
        with open(f"{responses_dir}/{img_id}.json","w",encoding="utf-8") as f:
            json.dump({"prediction": pred}, f, ensure_ascii=False, indent=2)

        results.append({
            "image_id":     img_id,
            "ground_truth": truth,
            "prediction":   pred
        })

    # 7) Write aggregate
    with open(f"{out}/results.json","w",encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[run_experiment] Completed! Logs → {out}")

if __name__=="__main__":
    main()

import os
import json
from typing import Any, Dict, List
from jinja2 import Environment, FileSystemLoader

class PromptBuilder:
    def __init__(self, config: Dict[str,Any]):
        base = os.path.dirname(os.path.abspath(__file__))
        self.templates_dir = os.path.join(base, "templates")
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up from prompts/ to RebusvLMs/
        self.examples_dir = os.path.join(project_root, config["dataset"]["examples_dir"])
        self.prompts_json = os.path.join(self.examples_dir, "rebus_prompts.json")

        # load the JSON once
        if not os.path.exists(self.prompts_json):
            raise FileNotFoundError(f"Sample prompts file not found: {self.prompts_json}")
            
        with open(self.prompts_json, 'r', encoding='utf-8') as f:
            self.sample_prompts = json.load(f)

        # the question you want to ask for every target image
        self.question = config.get(
            "prompt_question",
            "This rebus puzzle is an Idiom which may contain text, figures, and other logical clues to represent the Idiom. Can you figure out what this Idiom is?"
        )

        # set up Jinja2
        self.jinja = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def load_examples(self, style: str, count: int) -> List[Dict[str,str]]:
        """
        For style in {fewshot2_cot, fewshot3_cot, fewshot2_nocot, fewshot3_nocot},
        pick the first `count` items from the corresponding JSON array.
        For zero_shot, just return the single entry in "zero_shot".
        """
        if style.startswith("fewshot") and style.endswith("_cot"):
            key = "fewshot_cot"
        elif style.startswith("fewshot") and style.endswith("_nocot"):
            key = "fewshot_nocot"
        elif style == "zero_shot":
            key = "zero_shot"
        else:
            raise ValueError(f"Unknown prompt style: {style}")

        items = self.sample_prompts.get(key, [])
        # zero-shot uses only one example block (but template ignores examples anyway)
        if style == "zero_shot":
            return items[:1]
        return items[:count]

    def build(self, style: str, examples_count: int, target_image_path: str) -> str:
        """
        Renders the prompt for:
          - style: zero_shot, fewshot2_cot, fewshot3_nocot, etc.
          - examples_count: 2 or 3 (ignored for zero_shot)
          - target_image_path: e.g. data/raw/img/042.jpg
        """
        # pick the right template file
        template = self.jinja.get_template(f"{style}.txt")

        # load examples if needed
        examples = []
        if style != "zero_shot":
            examples = self.load_examples(style, examples_count)

        context: Dict[str,Any] = {
            "examples":        examples,
            "target_filename": os.path.basename(target_image_path),
            "question":        self.question,
            # cot = True for styles ending with "_cot"
            "cot":             style.endswith("_cot"),
        }

        return template.render(**context)


if __name__ == "__main__":
    # quick sanity check:
    import yaml
    # merge base + model (example for 2.0)
    base = yaml.safe_load(open("config/base.yaml"))
    mod  = yaml.safe_load(open("config/gemini2.0.yaml"))
    cfg  = {**base, **mod}

    builder = PromptBuilder(cfg)
    prompt = builder.build(
        style="fewshot2_cot",
        examples_count=2,
        target_image_path="data/raw/img/001.jpg"
    )
    print(prompt)

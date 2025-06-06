# RebusvLMs

This project outlines the proposed codebase structure, directory layout, and key components for running zero-shot and few-shot (with and without CoT) experiments on Gemini 1.5, 2.0, and 2.5 VLMs using the Idioms Rebus Puzzle dataset.

---

## 1. Directory Layout

```
vlm_rebus_experiments/
├── .env                      # Environment variables for GCP and API keys
├── README.md                 # Project overview and instructions
├── requirements.txt          # Python dependencies
├── config/                   # Configuration files for experiments
│   ├── base.yaml             # Base settings (dataset paths, logging)
│   ├── gemini1.5.yaml        # Model-specific overrides
│   ├── gemini2.0.yaml
│   └── gemini2.5.yaml
│
├── data/                     # Dataset: raw images & annotations
│   ├── raw/                  # Original puzzle images + annotations
│   │   ├── images/           # Raw puzzle images
│   │   └── annotations.csv   # Ground-truth answers
│   └── load_data.py          # Functions to list and load raw images and annotations
├── prompts/                  # Prompt templates and builders
│   ├── templates/            # Jinja2 or .txt templates for each style
│   │   ├── zero_shot.txt
│   │   ├── fewshot2_cot.txt
│   │   ├── fewshot3_cot.txt
│   │   ├── fewshot2_nocot.txt
│   │   └── fewshot3_nocot.txt
│   └── builder.py            # Functions to render prompts given examples
│
├── experiments/              # Experiment orchestration
│   ├── run_experiment.py     # CLI entrypoint to run a single config
│   ├── evaluate.py           # Scoring and metrics
│   └── utils.py              # Helpers (logging, retry, batching)
│
├── models/                   # Model wrappers and clients
│   ├── base_client.py        # Wrapper around google-genai client setup
│   ├── gemini1_5.py          # Instantiates 1.5 model with config
│   ├── gemini2_0.py          # Instantiates 2.0-flash model
│   └── gemini2_5.py          # Instantiates 2.5-pro model
│
├── logs/                     # Generated logs and outputs
│   └── <timestamp>/          # Per-experiment output directories
│       ├── prompts/          # Raw prompts sent
│       ├── responses/        # JSON or text responses
│       └── metrics.json      # Evaluation metrics
│
└── notebooks/                # Jupyter notebooks for analysis
    ├── explore_data.ipynb
    └── compare_results.ipynb
```

---

## 2. Key Components

### 2.1 Configuration (`config/`)

This folder holds YAML files defining experiment settings. We load these configurations at runtime and merge base + model-specific overrides.

* **config/base.yaml**:

```yaml
project: ${GOOGLE_CLOUD_PROJECT}
location: ${GOOGLE_CLOUD_LOCATION}
use_vertexai: ${GOOGLE_GENAI_USE_VERTEXAI}

dataset:
  images_dir:       "data/raw/images"
  annotations_file: "data/raw/annotations.csv"
  examples_dir:     "data/examples"

logging:
  level: "INFO"
  dir:   "logs"

prompt_styles:
  - zero_shot
  - fewshot2_cot
  - fewshot3_cot
  - fewshot2_nocot
  - fewshot3_nocot

request:
  batch_size:      4
  timeout_seconds: 60
```

* **config/gemini1.5.yaml**:

```yaml
model:
  name:            "gemini-1.5-flash"
  api_type:        "studio"
  api_key:         ${GEMINI_API_KEY}
  use_vertexai:    false
  max_output_tokens: 8192
  supports_cot:    true
  context_window:  1048576
```

* **config/gemini2.0.yaml**:

```yaml
model:
  name:             "projects/${GOOGLE_CLOUD_PROJECT}/locations/${GOOGLE_CLOUD_LOCATION}/publishers/google/models/gemini-2.0-flash-001"
  api_type:         "vertex"
  use_vertexai:     true
  max_output_tokens: 8192
  supports_cot:     true
  context_window:   1048576
```

* **config/gemini2.5.yaml**:

```yaml
model:
  name:             "projects/${GOOGLE_CLOUD_PROJECT}/locations/${GOOGLE_CLOUD_LOCATION}/publishers/google/models/gemini-2.5-flash-preview-04-17"
  api_type:         "vertex"
  use_vertexai:     true
  max_output_tokens: 65535
  supports_cot:     true
  context_window:   1048576
```

Loading the YAML in Python:

```python
import os, yaml
from pathlib import Path

def load_config(cfg_filename):
    base = yaml.safe_load(Path("config/base.yaml").read_text())
    override = yaml.safe_load(Path(f"config/{cfg_filename}").read_text())
    # simple merge: override keys replace base
    base.update(override)
    return base
```

## 2.2 Data Loading (`data/load_data.py`)

* Read all images directly from `dataset.images_dir` and ground truth from `dataset.annotations_file`.
* No preprocessing is performed; raw images are fed to the models at inference time.
* `load_data.py` should provide functions to iterate over image paths and retrieve corresponding annotations for evaluation.

## 2.3 Prompt Templates & Builder (`prompts/`) Prompt Templates & Builder (`prompts/`)

* Templates in `prompts/templates/` use placeholder tokens for examples and target.
* `builder.py` renders a template using Jinja2 (or Python `.format`) with:

  * A list of `examples_count` from `dataset.examples_dir` and `demo_answers.yaml`.
  * The target image path.
  * Optionally adding “Let’s think step by step.” if CoT is enabled.

## 2.4 Model Wrappers (`models/`)

* `base_client.py`: initializes either Studio or VertexAI client based on `config.model.api_type`.
* Each `gemini*.py` exposes a `generate(prompt, image_paths)` function handling:

  * API calls with retries, error handling, and logging.

## 2.5 Experiment Runner (`experiments/run_experiment.py`)

CLI usage:

```bash
python run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2
```

Steps:

1. Load merged config.
2. Resolve `prompt_style`, adjust for `supports_cot`.
3. Iterate all images in `images_dir`.
4. For each, select `examples_count` demos, build prompt, call model, and write to `logs/<timestamp>`.

## 2.6 Evaluation (`experiments/evaluate.py`)

* Load `logs/<timestamp>/responses/` and corresponding ground truth.
* Compute metrics: exact match, F1, optionally other scores.
* Output a summary JSON in the same `logs/<timestamp>`.

## 2.7 Notebooks (`notebooks/`)

* **explore\_data.ipynb**: inspect sample images, answer distributions.
* **compare\_results.ipynb**: load metrics from multiple runs and plot comparisons.

---

## 3. Usage Workflow

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: set your `.env` with credentials.
3. **Run**:

```bash
python experiments/run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot3_nocot \
  --examples-count 3
```

4. **Evaluate**:

```bash
python experiments/evaluate.py --timestamp 20250520_120000
```

5. **Analyze**: open `notebooks/compare_results.ipynb`.

Use this outline to guide the implementation top to bottom.

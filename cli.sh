# --------------- GEMINI-1.5 (STUDIO API) ON 5 PROMPT STYLES -----------------
# Zero‐Shot (no examples_count needed)
python -m experiments.run_experiment --config gemini1.5.yaml --prompt-style zero_shot

python -m experiments.run_experiment \
  --config gemini1.5.yaml \
  --prompt-style zero_shot \
  --delay 10

python experiments/retry_failed_exp.py \
  --timestamp 20250619_232852 \
  --config gemini1.5.yaml \
  --prompt-style zero_shot \
  --delay 10

python quick_evaluate.py --timestamp 20250619_232852
python experiments/evaluate.py --timestamp 20250619_232852 --use-extraction --use-f1


# 2-Shot + CoT
python -m experiments.run_experiment \
  --config gemini1.5.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2

python experiments/retry_failed_exp.py \
  --timestamp 20250620_004110 \
  --config gemini1.5.yaml \
  --prompt-style fewshot2_cot \
  --delay 10

python quick_evaluate.py --timestamp 20250620_004110
python experiments/evaluate.py --timestamp 20250620_004110 --use-extraction --use-f1

# 3-Shot + CoT
python -m experiments.run_experiment \
  --config gemini1.5.yaml \
  --prompt-style fewshot3_cot \
  --examples-count 3

python experiments/retry_failed_exp.py \
  --timestamp 20250620_010625 \
  --config gemini1.5.yaml \
  --prompt-style fewshot3_cot \
  --delay 10

python quick_evaluate.py --timestamp 20250620_010625
python experiments/evaluate.py --timestamp 20250620_010625

# 2-Shot, No CoT
python -m experiments.run_experiment \
  --config gemini1.5.yaml \
  --prompt-style fewshot2_nocot \
  --examples-count 2

python experiments/retry_failed_exp.py \
  --timestamp 20250620_012921 \
  --config gemini1.5.yaml \
  --prompt-style fewshot2_nocot \
  --delay 10

python quick_evaluate.py --timestamp 20250620_012921
python experiments/evaluate.py --timestamp 20250620_012921

# 3-Shot, No CoT
python -m experiments.run_experiment \
  --config gemini1.5.yaml \
  --prompt-style fewshot3_nocot \
  --examples-count 3


# --------------- GEMINI-2.0 (VERTEX AI) ON 5 PROMPT STYLES -----------------
# Zero‐Shot
python -m experiments.run_experiment --config gemini2.0.yaml --prompt-style zero_shot

# 2-Shot + CoT
python -m experiments.run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2

# 3-Shot + CoT
python -m experiments.run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot3_cot \
  --examples-count 3

# 2-Shot, No CoT
python -m experiments.run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot2_nocot \
  --examples-count 2

# 3-Shot, No CoT
python -m experiments.run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot3_nocot \
  --examples-count 3


# --------------- GEMINI-2.5 (VERTEX AI) ON 5 PROMPT STYLES -----------------
# Zero‐Shot
python -m experiments.run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style zero_shot

# 2-Shot + CoT
python -m experiments.run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2

# 3-Shot + CoT
python -m experiments.run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot3_cot \
  --examples-count 3

# 2-Shot, No CoT
python -m experiments.run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot2_nocot \
  --examples-count 2

# 3-Shot, No CoT
python -m experiments.run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot3_nocot \
  --examples-count 3


# --------------- EVALUATED COMPLETED RUN BY LOGS TIMESTAMP -----------------
# Exact‐match accuracy only
python -m experiments.evaluate.py \
  --timestamp 20250520_154512

# Exact‐match + token‐level Macro F1
python -m experiments.evaluate.py \
  --timestamp 20250520_154512 \
  --use-f1

# After each experiment, just run:
python -m experiments.evaluate --timestamp $(ls logs/ | tail -1) --use-f1

# --------------- DRY RUN (5 SAMPLES) -----------------
python -m experiments.run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2 \
  --dataset.images_dir data/sample

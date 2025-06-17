# ========================================================================
# GEMINI 2.0 VERTEX AI EXPERIMENTS (5 experiments)
# ========================================================================

# 🔵 Experiment 1: Gemini 2.0 - Zero Shot
echo "📋 [1/10] Gemini 2.0 - Zero Shot"
python experiments/run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style zero_shot

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🔵 Experiment 2: Gemini 2.0 - Few-Shot 2 CoT
echo "📋 [2/10] Gemini 2.0 - Few-Shot 2 CoT"
python experiments/run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🔵 Experiment 3: Gemini 2.0 - Few-Shot 2 No CoT
echo "📋 [3/10] Gemini 2.0 - Few-Shot 2 No CoT"
python experiments/run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot2_nocot \
  --examples-count 2

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🔵 Experiment 4: Gemini 2.0 - Few-Shot 3 CoT
echo "📋 [4/10] Gemini 2.0 - Few-Shot 3 CoT"
python experiments/run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot3_cot \
  --examples-count 3

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🔵 Experiment 5: Gemini 2.0 - Few-Shot 3 No CoT
echo "📋 [5/10] Gemini 2.0 - Few-Shot 3 No CoT"
python experiments/run_experiment.py \
  --config gemini2.0.yaml \
  --prompt-style fewshot3_nocot \
  --examples-count 3

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# ========================================================================
# GEMINI 2.5 VERTEX AI EXPERIMENTS (5 experiments)
# ========================================================================

# 🟢 Experiment 6: Gemini 2.5 - Zero Shot
echo "📋 [6/10] Gemini 2.5 - Zero Shot"
python experiments/run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style zero_shot

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🟢 Experiment 7: Gemini 2.5 - Few-Shot 2 CoT
echo "📋 [7/10] Gemini 2.5 - Few-Shot 2 CoT"
python experiments/run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🟢 Experiment 8: Gemini 2.5 - Few-Shot 2 No CoT
echo "📋 [8/10] Gemini 2.5 - Few-Shot 2 No CoT"
python experiments/run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot2_nocot \
  --examples-count 2

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🟢 Experiment 9: Gemini 2.5 - Few-Shot 3 CoT
echo "📋 [9/10] Gemini 2.5 - Few-Shot 3 CoT"
python experiments/run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot3_cot \
  --examples-count 3

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP

# 🟢 Experiment 10: Gemini 2.5 - Few-Shot 3 No CoT
echo "📋 [10/10] Gemini 2.5 - Few-Shot 3 No CoT"
python experiments/run_experiment.py \
  --config gemini2.5.yaml \
  --prompt-style fewshot3_nocot \
  --examples-count 3

# ⚠️ COPY THE TIMESTAMP FROM OUTPUT ABOVE, then run:
python experiments/evaluate.py --timestamp REPLACE_WITH_TIMESTAMP --use-extraction --use-f1
python quick_evaluate.py --timestamp REPLACE_WITH_TIMESTAMP


# See all experiment timestamps
ls -la logs/

# Get most recent experiment
ls -t logs/ | head -1

# Quick check of latest experiment
LATEST=$(ls -t logs/ | head -1)
python quick_evaluate.py --timestamp $LATEST
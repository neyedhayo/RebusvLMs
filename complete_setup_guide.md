# Complete Setup Guide for RebusvLMs

## 🎯 Overview

This guide will get your RebusvLMs project fully working. I've fixed all the issues identified in your verification script and added comprehensive tools for evaluation and debugging.

## 📋 Quick Status Check

Run this first to see what needs to be done:
```bash
python test/verify_setup.py
```

## 🚀 Step-by-Step Setup

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Create Missing Files** 

I've provided all the missing files in the artifacts above. Save them as:

**Core Enhanced Files:**
- `experiments/evaluate.py` (use the enhanced version)
- `experiments/utils.py` (use the enhanced version) 
- `experiments/run_experiment.py` (use the enhanced version)
- `data/load_data.py` (use the enhanced version)
- `config/base.yaml` (use the enhanced version)

**New Utility Files:**
- `debug_results.py`
- `quick_evaluate.py` 
- `test/test_extraction.py`
- `test/integration_test.py`
- `test/verify_setup.py`
- `setup_files.py`

**Data Files:**
- `data/sample/rebus_prompts.json`

**Init Files:**
- `models/__init__.py`
- `experiments/__init__.py`
- `prompts/__init__.py`
- `data/__init__.py`
- `test/__init__.py`

### 3. **Run Setup Script (Optional)**
```bash
python setup_files.py
```
This automatically creates directories and missing files.

### 4. **Verify Setup**
```bash
python test/verify_setup.py
```
Should now show 100% success.

### 5. **Test Everything Works**
```bash
# Test extraction functions
python test/test_extraction.py

# Run integration tests
python test/integration_test.py

# Quick evaluation test
python quick_evaluate.py --test-sample
```

## 🧪 Testing Your Setup

### **Validation Tests**
```bash
# Check file structure and imports
python test/verify_setup.py

# Test all functions work correctly  
python test/test_extraction.py

# Test complete pipeline integration
python test/integration_test.py
```

### **Quick Functionality Test**
```bash
# Test with sample data
python quick_evaluate.py --test-sample

# Test data loading
python data/load_data.py

# Dry run experiment (no API calls)
python experiments/run_experiment.py \
  --config gemini1.5.yaml \
  --prompt-style zero_shot \
  --dry-run
```

## 📊 What's New & Fixed

### **Enhanced Evaluation (`experiments/evaluate.py`)**
- ✅ `extract_idiom()` - Smart extraction from messy responses
- ✅ `normalize_idiom()` - Text normalization for fair comparison  
- ✅ `clean_extracted_idiom()` - Clean up extracted text
- ✅ `is_likely_idiom()` - Validate extracted text looks like idiom
- ✅ `calculate_token_f1()` - Advanced F1 scoring
- ✅ Support for `--use-extraction` flag

### **New Debugging Tools**
- 📊 `debug_results.py` - Analyze where extraction helps/hurts
- ⚡ `quick_evaluate.py` - Fast evaluation for development
- 🧪 `test/test_extraction.py` - Comprehensive test suite
- 🔧 `test/integration_test.py` - End-to-end testing

### **Enhanced Data Loading (`data/load_data.py`)**
- ✅ Better error messages and validation
- ✅ Flexible column name matching (filename/file/image, solution/answer/truth)
- ✅ Dataset validation without full loading
- ✅ Support for multiple image formats

### **Enhanced Experiment Runner (`experiments/run_experiment.py`)**
- ✅ Better error handling and validation
- ✅ Dry-run mode for testing setup
- ✅ Progress tracking and metadata saving
- ✅ Graceful handling of missing files

## 🎮 Usage Examples

### **Run Experiments**
```bash
# Dry run first (validates setup without API calls)
python experiments/run_experiment.py \
  --config gemini1.5.yaml \
  --prompt-style zero_shot \
  --dry-run

# Real experiment
python experiments/run_experiment.py \
  --config gemini1.5.yaml \
  --prompt-style fewshot2_cot \
  --examples-count 2
```

### **Evaluate Results**
```bash
# Standard evaluation
python experiments/evaluate.py --timestamp 20250617_143000

# With advanced extraction and F1
python experiments/evaluate.py \
  --timestamp 20250617_143000 \
  --use-extraction \
  --use-f1

# Quick check
python quick_evaluate.py --timestamp 20250617_143000
```

### **Debug Extraction**
```bash
# Show samples where extraction helped
python debug_results.py \
  --timestamp 20250617_143000 \
  --show-helped

# Save detailed debug info
python debug_results.py \
  --timestamp 20250617_143000 \
  --save-debug
```

## 🔧 Advanced Features

### **Smart Idiom Extraction**
The new extraction system handles:
- Quoted idioms: `"piece of cake"`
- Explanatory text: `The idiom is: break the ice` 
- Reasoning chains: `Looking at this image... Therefore, it's "spill the beans"`
- Multi-line responses with reasoning
- Various response formats from different models

### **Enhanced Evaluation Metrics**
- **Exact Match**: Direct string comparison
- **Normalized Match**: After text normalization  
- **Token F1**: Token-level overlap scoring
- **Extraction Impact**: Compare with/without extraction

### **Debugging Tools**
- **Sample Analysis**: See exactly where extraction helps/hurts
- **Performance Metrics**: Quantify extraction improvements
- **Detailed Logging**: Full pipeline visibility

## 🐛 Troubleshooting

### **Import Errors**
```bash
# Make sure you're in project root
cd /path/to/RebusvLMs

# Verify __init__.py files exist
ls models/__init__.py experiments/__init__.py prompts/__init__.py data/__init__.py

# Run verification
python test/verify_setup.py
```

### **Missing Dependencies**
```bash
pip install -r requirements.txt
```

### **File Not Found Errors**
```bash
# Check directory structure
python setup_files.py

# Validate data setup
python data/load_data.py
```

### **Google Cloud Setup**
```bash
# Set environment variables in .env
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GEMINI_API_KEY="your-api-key"
```

## ✅ Final Verification

Run this complete check:
```bash
echo "🔍 Complete Verification"
echo "========================"

# 1. File structure
python test/verify_setup.py

# 2. Function tests  
python test/test_extraction.py

# 3. Integration tests
python test/integration_test.py

# 4. Quick functionality test
python quick_evaluate.py --test-sample

echo "🎉 If all passed, you're ready to run experiments!"
```

## 🚀 Ready to Go!

Your enhanced RebusvLMs setup now includes:
- ✅ Smart idiom extraction from messy model responses
- ✅ Robust evaluation with multiple metrics
- ✅ Comprehensive debugging and analysis tools
- ✅ Better error handling and validation
- ✅ Complete test suite for confidence

Run your experiments with confidence! 🎯
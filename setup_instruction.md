# Setup Instructions for RebusvLMs

## 🔧 Quick Fix Summary

The verification errors you encountered have been fixed. Here's what was missing and what I've provided:

### 1. **Missing Files Created:**
- `debug_results.py` - Advanced debugging tool for extraction results
- `test/test_extraction.py` - Comprehensive test suite for extraction functions  
- `quick_evaluate.py` - Quick evaluation tool for testing
- `data/sample/rebus_prompts.json` - Example prompts for few-shot learning
- Updated `requirements.txt` - Complete dependency list
- All missing `__init__.py` files

### 2. **Enhanced evaluate.py:**
- Added all missing extraction functions:
  - `extract_idiom()` - Smart idiom extraction from model responses
  - `normalize_idiom()` - Text normalization for fair comparison
  - `clean_extracted_idiom()` - Clean up extracted text
  - `is_description_text()` - Detect descriptive vs idiom text
  - `is_likely_idiom()` - Validate if text looks like an idiom
  - `select_best_idiom_candidate()` - Choose best from multiple candidates
  - `calculate_token_f1()` - Token-level F1 scoring

### 3. **Enhanced utils.py:**
- Added `expand_env_vars_recursive()` - Environment variable expansion
- Added `load_config_files()` - Config file loading with variable expansion

## 📦 Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Missing Directories
```bash
mkdir -p data/sample
mkdir -p test  
mkdir -p logs
```

### 3. Create __init__.py Files
Create these files with the content I provided:
- `models/__init__.py`
- `experiments/__init__.py`
- `prompts/__init__.py`
- `data/__init__.py`
- `test/__init__.py`

### 4. Create Missing Files
Save the artifacts I created as:
- `experiments/evaluate.py` (enhanced version)
- `experiments/utils.py` (enhanced version)
- `debug_results.py` 
- `test/test_extraction.py`
- `quick_evaluate.py`
- `data/sample/rebus_prompts.json`
- `test/verify_setup.py` (new verification script)

## 🧪 Testing Your Setup

### 1. Run the New Verification Script
```bash
python test/verify_setup.py
```

### 2. Test the Extraction Functions
```bash
python test/test_extraction.py
```

### 3. Quick Evaluation Test
```bash
python quick_evaluate.py --test-sample
```

## 🚀 Usage Examples

### 1. Run a Quick Test
```bash
# Test extraction functions
python test/test_extraction.py

# Test with sample data
python quick_evaluate.py --test-sample
```

### 2. Debug Existing Results
```bash
# Debug a specific run (replace with your timestamp)
python debug_results.py --timestamp 20250617_143000 --show-helped

# Save detailed debug results
python debug_results.py --timestamp 20250617_143000 --save-debug
```

### 3. Enhanced Evaluation
```bash
# Evaluate with advanced extraction
python experiments/evaluate.py --timestamp 20250617_143000 --use-extraction --use-f1

# Quick evaluation of first 50 samples
python quick_evaluate.py --timestamp 20250617_143000 --sample-size 50
```

## 🔍 What Each New Tool Does

### **debug_results.py**
- Analyzes where extraction helps vs hurts performance
- Shows detailed sample-by-sample comparisons
- Saves detailed debug information to JSON

### **test/test_extraction.py** 
- Comprehensive test suite for all extraction functions
- Tests various response formats and edge cases
- Validates extraction pipeline integration

### **quick_evaluate.py**
- Fast evaluation for development and testing
- Compares with/without extraction performance
- Shows example improvements/regressions

### **Enhanced evaluate.py**
- Smart idiom extraction from messy model responses
- Handles quoted text, explanations, reasoning chains
- Robust normalization for fair comparison
- Advanced F1 scoring with token-level matching

## 🎯 Next Steps

1. **Run verification**: `python test/verify_setup.py`
2. **Test extraction**: `python test/test_extraction.py`  
3. **Try quick eval**: `python quick_evaluate.py --test-sample`
4. **Run your experiments** with the enhanced evaluation tools

## 🐛 Common Issues & Fixes

### Import Errors
- Make sure all `__init__.py` files are created
- Run from project root directory
- Check Python path includes project root

### Missing Dependencies
- Run `pip install -r requirements.txt`
- Make sure you're in the right virtual environment

### File Not Found Errors
- Check that all files from the artifacts are saved in correct locations
- Verify directory structure matches the README.md layout

### Environment Variables
- Make sure your `.env` file has the required variables
- Check that Google Cloud credentials are properly set up

The setup should now pass all verification checks. Let me know if you encounter any remaining issues!
#!/usr/bin/env python3
"""Test if all imports work correctly."""

import sys
import os

print("🔍 Testing Import Resolution")
print("=" * 40)

# Add current directory to path
sys.path.insert(0, os.getcwd())

print(f"Current directory: {os.getcwd()}")
print(f"Python path includes: {os.getcwd() in sys.path}")
print()

# Test each import
imports_to_test = [
    ("data.load_data", "load_dataset"),
    ("prompts.builder", "PromptBuilder"), 
    ("models.base_client", "BaseClient"),
    ("experiments.evaluate", "extract_idiom"),
    ("experiments.utils", "ensure_dir")
]

success_count = 0
for module_name, item_name in imports_to_test:
    try:
        module = __import__(module_name, fromlist=[item_name])
        getattr(module, item_name)
        print(f"✅ {module_name}.{item_name}")
        success_count += 1
    except ImportError as e:
        print(f"❌ {module_name}.{item_name}: {e}")
    except AttributeError as e:
        print(f"⚠️  {module_name}.{item_name}: {e}")

print()
print(f"📊 Import Success: {success_count}/{len(imports_to_test)}")

if success_count == len(imports_to_test):
    print("🎉 All imports working! Dry-run should work now.")
else:
    print("🔧 Some imports failed. Check __init__.py files.")

# Test directory structure
print("\n📁 Directory Structure Check:")
required_dirs = ["data", "experiments", "models", "prompts", "config"]
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        init_file = os.path.join(dir_name, "__init__.py")
        if os.path.exists(init_file):
            print(f"✅ {dir_name}/ (with __init__.py)")
        else:
            print(f"⚠️  {dir_name}/ (missing __init__.py)")
    else:
        print(f"❌ {dir_name}/ (directory missing)")
import os
import sys
import importlib.util
from pathlib import Path

def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return Path(filepath).exists()

def check_function_in_file(filepath: str, function_name: str) -> bool:
    """Check if function is defined in file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return f"def {function_name}" in content
    except:
        return False

def test_import(module_path: str, from_name: str = None) -> bool:
    """Test if module can be imported"""
    try:
        if from_name:
            spec = importlib.util.spec_from_file_location(from_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            exec(f"import {module_path}")
        return True
    except Exception as e:
        print(f"    ❌ Import error: {e}")
        return False

def verify_setup():
    """Verify all components are properly set up"""
    print("🔍 Verifying Complete Setup")
    print("=" * 50)
    
    checks = []
    
    # 1. Check file existence
    print("\n📁 Checking File Existence:")
    files_to_check = [
        "experiments/evaluate.py",
        "experiments/run_experiment.py", 
        "experiments/utils.py",
        "debug_results.py",
        "test_extraction.py",
        "quick_evaluate.py",
        "models/base_client.py",
        "models/gemini1_5.py",
        "models/gemini2_0.py",
        "models/gemini2_5.py",
        "data/load_data.py",
        "prompts/builder.py",
        "config/base.yaml",
        "config/gemini1.5.yaml",
        "config/gemini2.0.yaml",
        "config/gemini2.5.yaml",
        "requirements.txt"
    ]
    
    file_checks = 0
    for filepath in files_to_check:
        exists = check_file_exists(filepath)
        status = "✅" if exists else "❌"
        print(f"  {status} {filepath}")
        if exists:
            file_checks += 1
    
    checks.append(("File Existence", file_checks, len(files_to_check)))
    
    # 2. Check critical functions in evaluate.py
    print(f"\n🔧 Checking Functions in evaluate.py:")
    functions_to_check = [
        "extract_idiom",
        "normalize_idiom", 
        "clean_extracted_idiom",
        "is_description_text",
        "is_likely_idiom",
        "select_best_idiom_candidate",
        "calculate_token_f1",
        "evaluate",
        "main"
    ]
    
    function_checks = 0
    for func in functions_to_check:
        exists = check_function_in_file("experiments/evaluate.py", func)
        status = "✅" if exists else "❌"
        print(f"  {status} {func}")
        if exists:
            function_checks += 1
    
    checks.append(("Functions in evaluate.py", function_checks, len(functions_to_check)))
    
    # 3. Check environment variable expansion in run_experiment.py
    print(f"\n🔧 Checking Environment Variable Expansion:")
    has_expand_function = check_function_in_file("experiments/run_experiment.py", "expand_env_vars_recursive")
    has_load_config = check_function_in_file("experiments/run_experiment.py", "load_config_files")
    
    env_checks = 0
    print(f"  {'✅' if has_expand_function else '❌'} expand_env_vars_recursive function")
    if has_expand_function:
        env_checks += 1
    print(f"  {'✅' if has_load_config else '❌'} load_config_files function")
    if has_load_config:
        env_checks += 1
    
    checks.append(("Environment Variable Functions", env_checks, 2))
    
    # 4. Check extraction functions in debug_results.py
    print(f"\n🔧 Checking Functions in debug_results.py:")
    debug_functions = ["extract_idiom", "normalize_idiom", "clean_extracted_idiom"]
    
    debug_checks = 0
    for func in debug_functions:
        exists = check_function_in_file("debug_results.py", func)
        status = "✅" if exists else "❌"
        print(f"  {status} {func}")
        if exists:
            debug_checks += 1
    
    checks.append(("Functions in debug_results.py", debug_checks, len(debug_functions)))
    
    # 5. Check __init__.py files
    print(f"\n📦 Checking __init__.py Files:")
    init_files = [
        "models/__init__.py",
        "experiments/__init__.py",
        "prompts/__init__.py", 
        "data/__init__.py"
    ]
    
    init_checks = 0
    for init_file in init_files:
        exists = check_file_exists(init_file)
        status = "✅" if exists else "❌"
        print(f"  {status} {init_file}")
        if exists:
            init_checks += 1
    
    checks.append(("__init__.py files", init_checks, len(init_files)))
    
    # 6. Check requirements.txt content
    print(f"\n📦 Checking Requirements:")
    required_packages = [
        "google-cloud-aiplatform",
        "google-genai", 
        "google-generativeai",
        "Pillow",
        "pyyaml",
        "jinja2",
        "pandas",
        "scikit-learn"
    ]
    
    req_checks = 0
    try:
        with open("requirements.txt", 'r') as f:
            req_content = f.read()
            for package in required_packages:
                if package in req_content:
                    print(f"  ✅ {package}")
                    req_checks += 1
                else:
                    print(f"  ❌ {package}")
    except:
        print(f"  ❌ Could not read requirements.txt")
    
    checks.append(("Required packages", req_checks, len(required_packages)))
    
    # Summary
    print(f"\n📊 Verification Summary:")
    print("=" * 30)
    
    total_passed = sum(passed for _, passed, _ in checks)
    total_possible = sum(total for _, _, total in checks)
    
    for name, passed, total in checks:
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✅" if passed == total else "⚠️" if passed > total * 0.8 else "❌"
        print(f"  {status} {name}: {passed}/{total} ({percentage:.0f}%)")
    
    overall_percentage = (total_passed / total_possible * 100) if total_possible > 0 else 0
    
    print(f"\n🎯 Overall Status: {total_passed}/{total_possible} ({overall_percentage:.0f}%)")
    
    if overall_percentage >= 95:
        print("🎉 Setup is ready! You can run experiments.")
        return True
    elif overall_percentage >= 80:
        print("⚠️  Setup is mostly ready, but some issues need fixing.")
        return False
    else:
        print("❌ Setup has significant issues that need to be resolved.")
        return False

if __name__ == "__main__":
    success = verify_setup()
    
    if success:
        print(f"\n🚀 Next Steps:")
        print(f"1. Run: python test_extraction.py")
        print(f"2. Run: python -m experiments.run_experiment --config gemini1.5.yaml --prompt-style zero_shot")
        print(f"3. Run: python quick_evaluate.py")
    else:
        print(f"\n🔧 Fix the issues above before running experiments.")
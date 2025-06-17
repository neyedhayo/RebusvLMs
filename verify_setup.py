import os
import sys
import importlib.util
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return os.path.exists(filepath)


def check_function_exists(module_path: str, function_name: str) -> bool:
    """Check if a function exists in a module."""
    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        if spec is None or spec.loader is None:
            return False
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return hasattr(module, function_name)
    except Exception:
        return False


def check_import_works(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def verify_file_structure():
    """Verify that all required files exist."""
    print("📁 Checking File Existence:")
    
    required_files = [
        "experiments/evaluate.py",
        "experiments/run_experiment.py", 
        "experiments/utils.py",
        "debug_results.py",
        "test/test_extraction.py",
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
    
    passed = 0
    for file_path in required_files:
        if check_file_exists(file_path):
            print(f"  ✅ {file_path}")
            passed += 1
        else:
            print(f"  ❌ {file_path}")
    
    return passed, len(required_files)


def verify_evaluate_functions():
    """Verify that evaluate.py has all required functions."""
    print("🔧 Checking Functions in evaluate.py:")
    
    required_functions = [
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
    
    evaluate_path = "experiments/evaluate.py"
    passed = 0
    
    for func_name in required_functions:
        if check_function_exists(evaluate_path, func_name):
            print(f"  ✅ {func_name}")
            passed += 1
        else:
            print(f"  ❌ {func_name}")
    
    return passed, len(required_functions)


def verify_debug_functions():
    """Verify that debug_results.py has required functions."""
    print("🔧 Checking Functions in debug_results.py:")
    
    required_functions = [
        "extract_idiom",  # Should be imported from experiments.evaluate
        "normalize_idiom", # Should be imported from experiments.evaluate  
        "clean_extracted_idiom"  # Should be imported from experiments.evaluate
    ]
    
    debug_path = "debug_results.py"
    passed = 0
    
    if not check_file_exists(debug_path):
        print(f"  ❌ {debug_path} not found")
        return 0, len(required_functions)
    
    # For debug_results.py, we just check if the file imports correctly
    # The functions are imported from experiments.evaluate
    try:
        spec = importlib.util.spec_from_file_location("debug_results", debug_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the imports worked
            if hasattr(module, 'extract_idiom'):
                print(f"  ✅ extract_idiom (imported)")
                passed += 1
            else:
                print(f"  ❌ extract_idiom")
                
            if hasattr(module, 'normalize_idiom'):
                print(f"  ✅ normalize_idiom (imported)")
                passed += 1
            else:
                print(f"  ❌ normalize_idiom")
                
            if hasattr(module, 'clean_extracted_idiom'):
                print(f"  ✅ clean_extracted_idiom (imported)")
                passed += 1
            else:
                print(f"  ❌ clean_extracted_idiom")
    except Exception as e:
        print(f"  ❌ Error loading debug_results.py: {e}")
    
    return passed, len(required_functions)


def verify_init_files():
    """Verify that __init__.py files exist."""
    print("📦 Checking __init__.py Files:")
    
    required_init_dirs = [
        "models",
        "experiments", 
        "prompts",
        "data"
    ]
    
    passed = 0
    for dir_name in required_init_dirs:
        init_path = os.path.join(dir_name, "__init__.py")
        if check_file_exists(init_path):
            print(f"  ✅ {init_path}")
            passed += 1
        else:
            print(f"  ❌ {init_path}")
    
    return passed, len(required_init_dirs)


def verify_imports():
    """Verify that key modules can be imported."""
    print("📦 Checking Module Imports:")
    
    modules_to_test = [
        "experiments.evaluate",
        "experiments.utils", 
        "models.base_client",
        "data.load_data",
        "prompts.builder"
    ]
    
    passed = 0
    for module_name in modules_to_test:
        if check_import_works(module_name):
            print(f"  ✅ {module_name}")
            passed += 1
        else:
            print(f"  ❌ {module_name}")
    
    return passed, len(modules_to_test)


def verify_requirements():
    """Verify that requirements.txt has necessary packages."""
    print("📦 Checking Requirements:")
    
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
    
    requirements_path = "requirements.txt"
    passed = 0
    
    if not check_file_exists(requirements_path):
        print(f"  ❌ {requirements_path} not found")
        return 0, len(required_packages)
    
    with open(requirements_path, 'r') as f:
        requirements_content = f.read()
    
    for package in required_packages:
        if package.lower() in requirements_content.lower():
            print(f"  ✅ {package}")
            passed += 1
        else:
            print(f"  ❌ {package}")
    
    return passed, len(required_packages)

def check_triple_bracket_extraction():
    """Check if triple bracket extraction works."""
    print("🔗 Checking Triple Bracket Extraction:")
    
    try:
        from experiments.evaluate import extract_idiom
        
        # Test cases for triple bracket format
        test_cases = [
            ('The answer is {{{piece of cake}}}', "piece of cake"),
            ('Looking at this... {{{break the ice}}}', "break the ice"),
            ('Mixed format "quoted" but {{{drop in bucket}}}', "drop in bucket"),
            ('{{{face the music}}} is shown here', "face the music")
        ]
        
        passed = 0
        for text, expected in test_cases:
            result = extract_idiom(text)
            # Normalize for comparison
            if expected.lower().replace(" ", "") in result.lower().replace(" ", ""):
                print(f"  ✅ {expected}")
                passed += 1
            else:
                print(f"  ❌ Expected: {expected}, Got: {result}")
        
        success_rate = f"{passed}/{len(test_cases)}"
        print(f"  📊 Triple bracket extraction: {success_rate}")
        return passed, len(test_cases)
        
    except Exception as e:
        print(f"  ❌ Triple bracket test failed: {e}")
        return 0, 4

def main():
    """Run complete setup verification."""
    print("🔍 Verifying Complete Setup")
    print("=" * 50)
    
    # Run all verification checks
    checks = [
        ("File Existence", verify_file_structure),
        ("Functions in evaluate.py", verify_evaluate_functions),
        ("Functions in debug_results.py", verify_debug_functions),
        ("__init__.py files", verify_init_files),
        ("Module Imports", verify_imports),
        ("Required packages", verify_requirements)
    ]
    
    total_passed = 0
    total_checks = 0
    results = []
    
    for check_name, check_func in checks:
        try:
            passed, total = check_func()
            total_passed += passed
            total_checks += total
            success_rate = f"{passed}/{total} ({passed/total*100:.0f}%)"
            
            if passed == total:
                status = "✅"
            elif passed > total * 0.8:
                status = "⚠️ "
            else:
                status = "❌"
            
            results.append((check_name, status, success_rate, passed == total))
            print()
            
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, "❌", "0/? (Error)", False))
            print()
    
    # Print summary
    print("📊 Verification Summary:")
    print("=" * 30)
    for check_name, status, success_rate, _ in results:
        print(f"  {status} {check_name}: {success_rate}")
    
    overall_rate = f"{total_passed}/{total_checks} ({total_passed/total_checks*100:.0f}%)"
    print(f"🎯 Overall Status: {overall_rate}")
    
    all_passed = all(result[3] for result in results)
    if all_passed:
        print("🎉 All checks passed! Setup is complete.")
    elif total_passed / total_checks > 0.9:
        print("✅ Setup is mostly ready, minor issues to fix.")
    else:
        print("⚠️  Setup is mostly ready, but some issues need fixing.")
        print("🔧 Fix the issues above before running experiments.")


if __name__ == "__main__":
    main()
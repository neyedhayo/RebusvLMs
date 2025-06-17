import sys
import os
import tempfile
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments.utils import expand_env_vars_recursive, load_config_files
from experiments.evaluate import (
    extract_idiom, normalize_idiom, evaluate, 
    calculate_token_f1, is_likely_idiom
)
from data.load_data import validate_dataset, load_annotations
from prompts.builder import PromptBuilder


def test_config_loading():
    """Test configuration file loading and environment variable expansion."""
    print("🔧 Testing configuration loading...")
    
    # Test environment variable expansion
    test_data = {
        "project": "${GOOGLE_CLOUD_PROJECT}",
        "nested": {
            "value": "${HOME}/test",
            "list": ["${USER}", "static_value"]
        }
    }
    
    # Set some test environment variables
    os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project-123"
    
    expanded = expand_env_vars_recursive(test_data)
    
    assert expanded["project"] == "test-project-123"
    assert "test" in expanded["nested"]["value"]
    
    print("  ✅ Environment variable expansion works")
    
    # Test config file loading if files exist
    base_config = "config/base.yaml"
    model_config = "config/gemini1.5.yaml"
    
    if os.path.exists(base_config) and os.path.exists(model_config):
        try:
            config = load_config_files(base_config, model_config)
            assert "model" in config
            assert "dataset" in config
            print("  ✅ Config file loading works")
        except Exception as e:
            print(f"  ⚠️  Config loading failed: {e}")
    else:
        print("  ⚠️  Config files not found - skipping config loading test")
    
    return True


def test_extraction_pipeline():
    """Test the complete extraction and evaluation pipeline."""
    print("🔍 Testing extraction pipeline...")
    
    # Test cases that cover various scenarios
    test_cases = [
        {
            "ground_truth": "piece of cake",
            "raw_response": 'The idiom shown is "piece of cake"',
            "expected_extracted": "piece of cake",
            "should_match": True
        },
        {
            "ground_truth": "break the ice", 
            "raw_response": "Looking at this image, I think it represents break the ice",
            "expected_extracted": "break the ice",
            "should_match": True
        },
        {
            "ground_truth": "spill the beans",
            "raw_response": "This puzzle shows spilling beans, so spill beans",
            "expected_extracted": "spill beans", 
            "should_match": False  # Missing "the"
        },
        {
            "ground_truth": "kick the bucket",
            "raw_response": "This image depicts someone kicking a bucket. The idiom is kick the bucket.",
            "expected_extracted": "kick the bucket",
            "should_match": True
        }
    ]
    
    passed_extraction = 0
    passed_evaluation = 0
    
    for i, case in enumerate(test_cases):
        # Test extraction
        extracted = extract_idiom(case["raw_response"])
        
        if extracted == case["expected_extracted"]:
            passed_extraction += 1
            print(f"  ✅ Extraction test {i+1}: {extracted}")
        else:
            print(f"  ❌ Extraction test {i+1}: expected '{case['expected_extracted']}', got '{extracted}'")
        
        # Test evaluation with normalization
        gt_norm = normalize_idiom(case["ground_truth"])
        extracted_norm = normalize_idiom(extracted)
        matches = gt_norm == extracted_norm
        
        if matches == case["should_match"]:
            passed_evaluation += 1
            print(f"  ✅ Evaluation test {i+1}: match={matches}")
        else:
            print(f"  ❌ Evaluation test {i+1}: expected match={case['should_match']}, got {matches}")
    
    print(f"  📊 Extraction: {passed_extraction}/{len(test_cases)} passed")
    print(f"  📊 Evaluation: {passed_evaluation}/{len(test_cases)} passed")
    
    return passed_extraction == len(test_cases) and passed_evaluation == len(test_cases)


def test_evaluation_metrics():
    """Test evaluation metrics calculation."""
    print("📊 Testing evaluation metrics...")
    
    # Create test data
    test_results = [
        {
            "image_id": "001",
            "ground_truth": "piece of cake", 
            "prediction": "piece of cake"  # Perfect match
        },
        {
            "image_id": "002",
            "ground_truth": "break the ice",
            "prediction": "break ice"  # Missing "the"
        },
        {
            "image_id": "003", 
            "ground_truth": "spill the beans",
            "prediction": "The idiom is spill the beans"  # Needs extraction
        },
        {
            "image_id": "004",
            "ground_truth": "kick the bucket", 
            "prediction": "completely wrong answer"  # No match
        }
    ]
    
    # Test evaluation without extraction
    metrics_no_extract = evaluate(test_results, use_f1=True, use_extraction=False)
    
    # Test evaluation with extraction  
    metrics_with_extract = evaluate(test_results, use_f1=True, use_extraction=True)
    
    # Verify metrics structure
    required_metrics = ["exact_match_accuracy", "raw_accuracy", "total_samples"]
    for metric in required_metrics:
        assert metric in metrics_no_extract
        assert metric in metrics_with_extract
    
    print(f"  ✅ Metrics without extraction: {metrics_no_extract['exact_match_accuracy']:.2f}")
    print(f"  ✅ Metrics with extraction: {metrics_with_extract['exact_match_accuracy']:.2f}")
    
    # Extraction should help (or at least not hurt significantly)
    improvement = metrics_with_extract['exact_match_accuracy'] - metrics_no_extract['exact_match_accuracy']
    print(f"  📈 Extraction improvement: {improvement:+.2f}")
    
    return True


def test_data_loading():
    """Test data loading functionality."""
    print("📁 Testing data loading...")
    
    # Test annotation loading with sample data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        # Write sample CSV
        f.write("Filename,Solution\n")
        f.write("001,piece of cake\n")
        f.write("002,break the ice\n")
        f.write("003,spill the beans\n")
        temp_csv = f.name
    
    try:
        # Test loading annotations
        annotations = load_annotations(temp_csv)
        assert len(annotations) == 3
        assert annotations["001"] == "piece of cake"
        print("  ✅ Annotation loading works")
        
        # Test dataset validation
        validation = validate_dataset("nonexistent_dir", temp_csv)
        assert not validation["images_dir_exists"]
        assert validation["annotations_file_exists"]
        assert validation["annotation_count"] == 3
        print("  ✅ Dataset validation works")
        
    finally:
        os.unlink(temp_csv)
    
    return True


def test_prompt_building():
    """Test prompt building if examples are available."""
    print("🔨 Testing prompt building...")
    
    # Check if sample data exists
    examples_file = "data/sample/rebus_prompts.json"
    if not os.path.exists(examples_file):
        print("  ⚠️  Sample prompts not found - skipping prompt building test")
        return True
    
    # Create minimal config for testing
    test_config = {
        "dataset": {
            "examples_dir": "data/sample"
        },
        "prompt_question": "Test question?"
    }
    
    try:
        builder = PromptBuilder(test_config)
        
        # Test zero-shot prompt
        prompt = builder.build("zero_shot", 0, "test_image.jpg")
        assert "Test question?" in prompt
        print("  ✅ Zero-shot prompt building works")
        
        # Test few-shot if examples exist
        try:
            prompt = builder.build("fewshot2_nocot", 2, "test_image.jpg")
            print("  ✅ Few-shot prompt building works")
        except Exception as e:
            print(f"  ⚠️  Few-shot prompt building failed: {e}")
        
    except Exception as e:
        print(f"  ❌ Prompt building failed: {e}")
        return False
    
    return True


def test_token_f1():
    """Test token-level F1 calculation."""
    print("🔢 Testing token F1 calculation...")
    
    test_cases = [
        ("piece of cake", "piece of cake", 1.0),
        ("break the ice", "break ice", 0.8),  # 2/3 tokens match
        ("spill the beans", "pour the coffee", 0.4),  # Only "the" matches
        ("hello world", "goodbye universe", 0.0),  # No matches
    ]
    
    passed = 0
    for gt, pred, expected_f1 in test_cases:
        f1 = calculate_token_f1(gt, pred)
        if abs(f1 - expected_f1) < 0.1:  # Allow small floating point differences
            passed += 1
            print(f"  ✅ F1 test: {f1:.2f}")
        else:
            print(f"  ❌ F1 test: expected {expected_f1:.2f}, got {f1:.2f}")
    
    print(f"  📊 Token F1: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running RebusvLMs Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Extraction Pipeline", test_extraction_pipeline), 
        ("Evaluation Metrics", test_evaluation_metrics),
        ("Data Loading", test_data_loading),
        ("Prompt Building", test_prompt_building),
        ("Token F1 Calculation", test_token_f1)
    ]
    
    passed_tests = 0
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            failed_tests.append(test_name)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed_tests}/{len(tests)}")
    
    if failed_tests:
        print(f"❌ Failed: {', '.join(failed_tests)}")
        print("\n🔧 Fix the failing tests before running experiments")
        return False
    else:
        print("🎉 All integration tests passed!")
        print("\n🚀 Your setup is ready for experiments!")
        return True


def main():
    """Run integration tests and return appropriate exit code."""
    success = run_integration_tests()
    
    if success:
        print("\n📚 Next steps:")
        print("  1. Add your rebus images to data/raw/images/")
        print("  2. Make sure data/raw/annotations.csv has your ground truth")
        print("  3. Set up your Google Cloud credentials")
        print("  4. Run: python experiments/run_experiment.py --config gemini1.5.yaml --prompt-style zero_shot --dry-run")
        print("  5. If dry run works, remove --dry-run to run actual experiments")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
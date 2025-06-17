import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.evaluate import (
    extract_idiom, 
    normalize_idiom, 
    clean_extracted_idiom,
    is_description_text,
    is_likely_idiom,
    select_best_idiom_candidate,
    calculate_token_f1
)


def test_extract_idiom():
    """Test the extract_idiom function with various input formats."""
    print("🧪 Testing extract_idiom function...")
    
    test_cases = [
        # Simple quoted cases
        ('The idiom is "a drop in the bucket".', "a drop in the bucket"),
        ("'kick the bucket'", "kick the bucket"),
        ('This puzzle represents "break the ice"', "break the ice"),
        
        # Cases with explanatory text
        ('The idiom is: piece of cake', "piece of cake"),
        ('This idiom means spill the beans.', "spill the beans"),
        ('The answer is hold your horses', "hold your horses"),
        
        # Cases with extra description
        ('This rebus puzzle shows "barking up the wrong tree" which means...', "barking up the wrong tree"),
        ('Looking at this image, I can see it represents "face the music"', "face the music"),
        
        # Multi-line responses
        ('This is a visual representation.\n\nThe idiom is "catch my drift"\n\nIt means...', "catch my drift"),
        
        # Complex responses with reasoning
        ('Let me think step by step. The image shows... This represents "cut corners"', "cut corners"),
        
        # Edge cases
        ('', ""),
        ('Just some random text without an idiom', "Just some random text without an idiom"),
        ('Multiple "quoted" "phrases" here', "quoted"),  # Should pick the first reasonable one
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        result = extract_idiom(input_text)
        if result == expected:
            print(f"  ✅ Test {i+1}: PASS")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     Input: {repr(input_text)}")
            print(f"     Expected: {repr(expected)}")
            print(f"     Got: {repr(result)}")
            failed += 1
    
    print(f"extract_idiom: {passed} passed, {failed} failed")
    return failed == 0


def test_normalize_idiom():
    """Test the normalize_idiom function."""
    print("\n🧪 Testing normalize_idiom function...")
    
    test_cases = [
        ("A Drop in the Bucket", "drop in the bucket"),
        ("  KICK THE BUCKET  ", "kick the bucket"),
        ("Break-the-ice", "break the ice"),
        ("The piece of cake", "piece of cake"),  # Remove leading article
        ("spill_the_beans", "spill the beans"),
        ("hold   your    horses", "hold your horses"),  # Multiple spaces
        ("", ""),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        result = normalize_idiom(input_text)
        if result == expected:
            print(f"  ✅ Test {i+1}: PASS")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     Input: {repr(input_text)}")
            print(f"     Expected: {repr(expected)}")
            print(f"     Got: {repr(result)}")
            failed += 1
    
    print(f"normalize_idiom: {passed} passed, {failed} failed")
    return failed == 0


def test_clean_extracted_idiom():
    """Test the clean_extracted_idiom function."""
    print("\n🧪 Testing clean_extracted_idiom function...")
    
    test_cases = [
        ('The idiom is: piece of cake', 'piece of cake'),
        ('I think this is "break the ice"', '"break the ice"'),
        ('This puzzle represents barking up the wrong tree.', 'barking up the wrong tree'),
        ('"a drop in the bucket"', 'a drop in the bucket'),  # Remove quotes
        ("'kick the bucket'", 'kick the bucket'),
        ('spill the beans idiom', 'spill the beans'),
        ('', ''),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        result = clean_extracted_idiom(input_text)
        if result == expected:
            print(f"  ✅ Test {i+1}: PASS")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     Input: {repr(input_text)}")
            print(f"     Expected: {repr(expected)}")
            print(f"     Got: {repr(result)}")
            failed += 1
    
    print(f"clean_extracted_idiom: {passed} passed, {failed} failed")
    return failed == 0


def test_is_description_text():
    """Test the is_description_text function."""
    print("\n🧪 Testing is_description_text function...")
    
    test_cases = [
        ("This idiom represents...", True),
        ("The rebus shows...", True),
        ("Looking at this image...", True),
        ("piece of cake", False),
        ("break the ice", False),
        ("I can see this puzzle means...", True),
        ("", True),  # Empty is considered description
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        result = is_description_text(input_text)
        if result == expected:
            print(f"  ✅ Test {i+1}: PASS")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     Input: {repr(input_text)}")
            print(f"     Expected: {expected}")
            print(f"     Got: {result}")
            failed += 1
    
    print(f"is_description_text: {passed} passed, {failed} failed")
    return failed == 0


def test_is_likely_idiom():
    """Test the is_likely_idiom function."""
    print("\n🧪 Testing is_likely_idiom function...")
    
    test_cases = [
        ("piece of cake", True),
        ("break the ice", True),
        ("a drop in the bucket", True),
        ("x", False),  # Too short
        ("This is a very long description that goes on and on and is clearly not an idiom", False),  # Too long
        ("This idiom represents", False),  # Description text
        ("", False),  # Empty
        ("jump", False),  # Single word, too short
        ("spill the beans", True),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        result = is_likely_idiom(input_text)
        if result == expected:
            print(f"  ✅ Test {i+1}: PASS")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     Input: {repr(input_text)}")
            print(f"     Expected: {expected}")
            print(f"     Got: {result}")
            failed += 1
    
    print(f"is_likely_idiom: {passed} passed, {failed} failed")
    return failed == 0


def test_calculate_token_f1():
    """Test the calculate_token_f1 function."""
    print("\n🧪 Testing calculate_token_f1 function...")
    
    test_cases = [
        ("piece of cake", "piece of cake", 1.0),  # Perfect match
        ("piece of cake", "a piece of cake", 1.0),  # Perfect match after normalization
        ("break the ice", "break ice", 0.8),  # Partial match
        ("spill the beans", "drop the bucket", 0.4),  # Some overlap ("the")
        ("hello world", "goodbye universe", 0.0),  # No overlap
        ("", "", 1.0),  # Both empty
        ("test", "", 0.0),  # One empty
    ]
    
    passed = 0
    failed = 0
    
    for i, (gt, pred, expected) in enumerate(test_cases):
        result = calculate_token_f1(gt, pred)
        if abs(result - expected) < 0.1:  # Allow small floating point differences
            print(f"  ✅ Test {i+1}: PASS (F1: {result:.3f})")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     GT: {repr(gt)}")
            print(f"     Pred: {repr(pred)}")
            print(f"     Expected F1: {expected}")
            print(f"     Got F1: {result}")
            failed += 1
    
    print(f"calculate_token_f1: {passed} passed, {failed} failed")
    return failed == 0


def test_integration():
    """Test the integration of extraction and evaluation."""
    print("\n🧪 Testing integration scenario...")
    
    # Simulate a full extraction and evaluation scenario
    test_responses = [
        'The idiom shown in this rebus is "a drop in the bucket"',
        'Looking at the image, I can see this represents "piece of cake"',
        'This puzzle shows kick the bucket',
        '"Break the ice" - this is a common idiom',
        'The answer is: spill the beans.',
    ]
    
    expected_idioms = [
        "a drop in the bucket",
        "piece of cake", 
        "kick the bucket",
        "break the ice",
        "spill the beans"
    ]
    
    print("  Testing full extraction pipeline...")
    passed = 0
    
    for i, (response, expected) in enumerate(zip(test_responses, expected_idioms)):
        extracted = extract_idiom(response)
        normalized_extracted = normalize_idiom(extracted)
        normalized_expected = normalize_idiom(expected)
        
        if normalized_extracted == normalized_expected:
            print(f"    ✅ Integration test {i+1}: PASS")
            passed += 1
        else:
            print(f"    ❌ Integration test {i+1}: FAIL")
            print(f"       Response: {repr(response)}")
            print(f"       Expected: {repr(expected)}")
            print(f"       Extracted: {repr(extracted)}")
            print(f"       Normalized Expected: {repr(normalized_expected)}")
            print(f"       Normalized Extracted: {repr(normalized_extracted)}")
    
    print(f"Integration tests: {passed}/{len(test_responses)} passed")
    return passed == len(test_responses)


def main():
    """Run all tests."""
    print("🧪 Running extraction function tests...\n")
    
    all_tests = [
        test_extract_idiom,
        test_normalize_idiom, 
        test_clean_extracted_idiom,
        test_is_description_text,
        test_is_likely_idiom,
        test_calculate_token_f1,
        test_integration
    ]
    
    passed_tests = 0
    total_tests = len(all_tests)
    
    for test_func in all_tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with error: {e}")
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed_tests}/{total_tests} test suites passed")
    print(f"{'='*60}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
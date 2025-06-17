import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.evaluate import extract_idiom, normalize_idiom


def test_triple_bracket_extraction():
    """Test the triple bracket format extraction."""
    print("🔗 Testing Triple Bracket Extraction")
    print("=" * 40)
    
    test_cases = [
        # Triple bracket format (should have highest priority)
        ('Looking at this image, I can see it represents {{{piece of cake}}}', "piece of cake"),
        ('The answer is {{{break the ice}}} because...', "break the ice"),
        ('This puzzle shows {{{spill the beans}}} clearly.', "spill the beans"),
        ('After thinking step by step, {{{kick the bucket}}}', "kick the bucket"),
        
        # Mixed formats - should still pick triple brackets
        ('The idiom "something else" but actually {{{drop in the bucket}}}', "drop in the bucket"),
        ('I think "wrong answer" however {{{hold your horses}}}', "hold your horses"),
        
        # Edge cases with extra content
        ('{{{face the music}}} is the idiom shown here', "face the music"),
        ('Multiple {{{first}}} and {{{second option}}} brackets', "first"),  # Should pick first one
        
        # Fallback to old methods when no triple brackets
        ('The idiom is "cut corners" without brackets', "cut corners"),
        ('This represents barking up the wrong tree', "barking up the wrong tree"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        result = extract_idiom(input_text)
        normalized_result = normalize_idiom(result)
        normalized_expected = normalize_idiom(expected)
        
        if normalized_result == normalized_expected:
            print(f"  ✅ Test {i+1}: PASS")
            print(f"     Input: {input_text[:60]}{'...' if len(input_text) > 60 else ''}")
            print(f"     Expected: {expected}")
            print(f"     Got: {result}")
            passed += 1
        else:
            print(f"  ❌ Test {i+1}: FAIL")
            print(f"     Input: {input_text}")
            print(f"     Expected: {expected}")
            print(f"     Got: {result}")
            print(f"     Normalized Expected: {normalized_expected}")
            print(f"     Normalized Got: {normalized_result}")
            failed += 1
        print()
    
    print(f"📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_format_examples():
    """Test with examples similar to your colleague's output."""
    print("\n🎯 Testing Colleague-Style Examples")
    print("=" * 40)
    
    # Examples based on the format from your colleague's code
    colleague_examples = [
        'The idiom shown is {{{a drop in the bucket}}}.',
        'Looking at this image, I can see... Therefore, the answer is {{{piece of cake}}}.',
        'This rebus puzzle represents {{{break the ice}}} which means...',
        '{{{kick the bucket}}} - this is a common idiom',
        'After analyzing step by step... {{{spill the beans}}}',
    ]
    
    expected_answers = [
        "a drop in the bucket",
        "piece of cake", 
        "break the ice",
        "kick the bucket",
        "spill the beans"
    ]
    
    print("Testing extraction from colleague-style responses...")
    passed = 0
    
    for i, (response, expected) in enumerate(zip(colleague_examples, expected_answers)):
        extracted = extract_idiom(response)
        normalized_extracted = normalize_idiom(extracted)
        normalized_expected = normalize_idiom(expected)
        
        if normalized_extracted == normalized_expected:
            print(f"  ✅ Example {i+1}: {extracted}")
            passed += 1
        else:
            print(f"  ❌ Example {i+1}: Expected '{expected}', got '{extracted}'")
    
    print(f"\n📊 Colleague-style examples: {passed}/{len(colleague_examples)} passed")
    return passed == len(colleague_examples)


def main():
    """Run all triple bracket tests."""
    print("🧪 Testing Triple Bracket Format Integration\n")
    
    test1_passed = test_triple_bracket_extraction()
    test2_passed = test_format_examples()
    
    print("\n" + "=" * 50)
    print("TRIPLE BRACKET TEST SUMMARY")
    print("=" * 50)
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed!")
        print("✅ Triple bracket extraction is working correctly")
        print("✅ Your system is ready for experiments with formatted answers")
        print("\nNext steps:")
        print("1. Run experiments with the updated prompts")
        print("2. Models should now output answers as {{{idiom}}}")
        print("3. Extraction will prioritize this format for better accuracy")
        return True
    else:
        print("❌ Some tests failed")
        print("🔧 Check the extraction logic in experiments/evaluate.py")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
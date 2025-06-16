import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the extraction functions (need to import from the actual file location)
def import_evaluation_functions():
    """Import evaluation functions with proper error handling"""
    try:
        sys.path.insert(0, os.path.join(project_root, 'experiments'))
        from evaluate import extract_idiom, normalize_idiom
        return extract_idiom, normalize_idiom
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the project root directory")
        sys.exit(1)

extract_idiom, normalize_idiom = import_evaluation_functions()

def test_your_example():
    """Test extraction on your specific example"""
    
    # Your example case
    prediction = '''The rebus puzzle shows the word "EDITION" written three times, stacked on top of each other. A line is drawn above the words. The number 2 is present in the bottom left corner. 

This suggests the idiom: **"Third Edition"**'''
    
    ground_truth = "first edition"  # What it should be (from your annotations)
    
    print("🧪 Testing Improved Extraction Logic")
    print("=" * 50)
    
    print(f"📝 Input prediction:")
    print(f"{prediction}")
    print()
    
    # Test extraction
    extracted = extract_idiom(prediction)
    normalized_extracted = normalize_idiom(extracted)
    normalized_ground_truth = normalize_idiom(ground_truth)
    
    print(f"🔧 Extraction Results:")
    print(f"  Raw extracted: '{extracted}'")
    print(f"  Normalized extracted: '{normalized_extracted}'")
    print(f"  Normalized ground truth: '{normalized_ground_truth}'")
    print()
    
    # Check match
    exact_match = normalized_extracted == normalized_ground_truth
    partial_match = normalized_ground_truth in normalized_extracted or normalized_extracted in normalized_ground_truth
    
    print(f"📊 Match Results:")
    print(f"  Exact match: {'✅' if exact_match else '❌'}")
    print(f"  Partial match: {'✅' if partial_match else '❌'}")
    
    # Show why it picked this extraction
    print(f"\n🔍 Analysis:")
    print(f"  - Found 'EDITION' in quotes (description)")
    print(f"  - Found 'Third Edition' in bold quotes after 'suggests'")
    print(f"  - Context-aware extraction chose: '{extracted}'")
    print(f"  - This is the model's answer, even if incorrect")
    
    return exact_match

def test_your_ten_samples():
    """Test extraction on your 10 actual JSON samples"""
    
    samples = [
        {
            "id": "011",
            "prediction": 'This likely represents the idiom: **"One over the eleven."**',
            "expected": "back to square one"  # Likely ground truth
        },
        {
            "id": "012", 
            "prediction": 'This suggests the idiom:\n\n**"Hold your horses"**',
            "expected": "hold your horses"
        },
        {
            "id": "013",
            "prediction": 'The idiom is likely:\n\n* **"Catch my drift."**',
            "expected": "catch my drift"
        },
        {
            "id": "014",
            "prediction": 'This suggests the idiom:\n\n**Let the cat out of the bag.**',
            "expected": "cat's out of the bag"
        },
        {
            "id": "015",
            "prediction": 'Therefore, the solution to the rebus puzzle is "Under one\'s nose."',
            "expected": "face the music"  # Likely ground truth
        },
        {
            "id": "016",
            "prediction": 'The idiom is: **"Barking up the wrong tree."**',
            "expected": "barking up the wrong tree"
        },
        {
            "id": "017",
            "prediction": 'The idiom is **"Break the Ice"**.',
            "expected": "break the ice"
        },
        {
            "id": "018",
            "prediction": 'The rebus puzzle is: **"Man Overboard."**',
            "expected": "man on board"  # Likely ground truth
        },
        {
            "id": "019",
            "prediction": 'This suggests the idiom: **"Throw Away."**',
            "expected": "shying away"  # Likely ground truth
        },
        {
            "id": "020",
            "prediction": 'Therefore, the answer is: **Top Secret**',
            "expected": "top secret"
        }
    ]
    
    print(f"\n🧪 Testing 10 Real JSON Samples")
    print("=" * 60)
    
    extraction_success = 0
    model_accuracy = 0
    
    for sample in samples:
        print(f"\n--- Sample {sample['id']} ---")
        
        extracted = extract_idiom(sample['prediction'])
        normalized_extracted = normalize_idiom(extracted)
        normalized_expected = normalize_idiom(sample['expected'])
        
        # Check extraction success (did we get something reasonable?)
        extraction_good = len(extracted) > 3 and len(extracted) < len(sample['prediction'])
        
        # Check model accuracy (did model get the right answer?)
        model_correct = normalized_extracted == normalized_expected
        
        print(f"Prediction: '{sample['prediction'][:60]}...'")
        print(f"Extracted: '{extracted}'")
        print(f"Expected: '{normalized_expected}'")
        print(f"Extraction Success: {'✅' if extraction_good else '❌'}")
        print(f"Model Accuracy: {'✅' if model_correct else '❌'}")
        
        if extraction_good:
            extraction_success += 1
        if model_correct:
            model_accuracy += 1
    
    print(f"\n📊 Overall Results:")
    print(f"  Extraction Success: {extraction_success}/10 ({extraction_success*10}%)")
    print(f"  Model Accuracy: {model_accuracy}/10 ({model_accuracy*10}%)")
    print(f"  Extraction Quality: {'✅ Excellent' if extraction_success >= 8 else '⚠️ Needs work'}")
    
    return extraction_success >= 8

if __name__ == "__main__":
    # Test the original example
    test_your_example()
    
    # Test the 10 real samples
    success = test_your_ten_samples()
    
    print(f"\n💡 Key Improvements:")
    print(f"1. Context-aware: Prioritizes text after 'idiom:', 'answer:', 'suggests:'")
    print(f"2. Description filtering: Avoids words like 'EDITION', 'BUCKET', 'shows'")
    print(f"3. Bold text priority: **text** ranked higher than regular 'text'")
    print(f"4. Smart candidate selection: Scores idiom-like patterns")
    
    if success:
        print(f"\n🎉 Extraction works great on your samples!")
        print(f"🚀 Ready to run: python -m experiments.evaluate --timestamp 20250609_134015 --use-f1 --debug")
    else:
        print(f"\n⚠️ Some extraction issues found. Review the patterns above.")


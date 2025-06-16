import json
import sys
import os
import re
from collections import Counter
from typing import List

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def extract_idiom(prediction: str) -> str:
    """Same improved extraction logic as in evaluate.py"""
    if not prediction or not isinstance(prediction, str):
        return ""
    
    text = prediction.strip()
    
    # Priority 1: Context-aware patterns
    context_patterns = [
        r'(?:idiom|answer|represents|solution|puzzle)\s*(?:is)?[:\s]+\*\*["\']?([^"\'*\n]+)["\']?\*\*',
        r'(?:idiom|answer|represents|solution|puzzle)\s*(?:is)?[:\s]+["\']([^"\'.\n]+)["\']',
        r'(?:idiom|answer|represents|solution|puzzle)\s*(?:is)?[:\s]+\*\*([^*\n]+)\*\*',
        r'(?:suggests|therefore)[^:]*[:\s]+\*\*["\']?([^"\'*\n]+)["\']?\*\*',
        r'(?:suggests|therefore)[^:]*[:\s]+["\']([^"\'.\n]+)["\']',
    ]
    
    for pattern in context_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            idiom = clean_extracted_idiom(matches[0])
            if len(idiom) > 2:
                return idiom
    
    # Priority 2: Bold text with filtering
    bold_patterns = [
        r'\*\*["\']([^"\']+)["\']?\*\*',
        r'\*\*([^*]+)\*\*',
    ]
    
    for pattern in bold_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            valid_matches = []
            for match in matches:
                cleaned = clean_extracted_idiom(match)
                if not is_description_text(cleaned):
                    valid_matches.append(cleaned)
            
            if valid_matches:
                idiom = select_best_idiom_candidate(valid_matches)
                if idiom:
                    return idiom
    
    # Priority 3: Filtered quotes
    quote_matches = re.findall(r'["\']([^"\']{4,30})["\']', text)
    if quote_matches:
        valid_matches = []
        for match in quote_matches:
            cleaned = clean_extracted_idiom(match)
            if is_likely_idiom(cleaned) and not is_description_text(cleaned):
                valid_matches.append(cleaned)
        
        if valid_matches:
            idiom = select_best_idiom_candidate(valid_matches)
            if idiom:
                return idiom
    
    return text[:50].lower().strip()

def clean_extracted_idiom(idiom: str) -> str:
    """Clean up extracted idiom text"""
    if not idiom:
        return ""
    
    cleaned = idiom.strip()
    cleaned = re.sub(r'^(the\s+)?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[.,!?;:]*$', '', cleaned)
    return cleaned

def normalize_idiom(idiom: str) -> str:
    """Same normalization logic as in evaluate.py"""
    if not idiom:
        return ""
    
    normalized = idiom.lower().strip()
    normalized = re.sub(r'^(a\s+|an\s+|the\s+)', '', normalized)
    normalized = re.sub(r'[.,!?;:]*$', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()

def analyze_prediction_patterns(results: List[dict]) -> dict:
    """Analyze common patterns in predictions"""
    patterns = {
        'has_bold_text': 0,
        'has_quotes': 0,
        'has_answer_keyword': 0,
        'has_idiom_keyword': 0,
        'has_explanation': 0,
        'average_length': 0,
        'extraction_patterns': Counter()
    }
    
    total_length = 0
    
    for result in results:
        pred = result['prediction']
        total_length += len(pred)
        
        if '**' in pred:
            patterns['has_bold_text'] += 1
        if '"' in pred or "'" in pred:
            patterns['has_quotes'] += 1
        if re.search(r'answer\s+is', pred, re.IGNORECASE):
            patterns['has_answer_keyword'] += 1
        if re.search(r'idiom', pred, re.IGNORECASE):
            patterns['has_idiom_keyword'] += 1
        if len(pred) > 50:  # Likely has explanation
            patterns['has_explanation'] += 1
        
        # Track which pattern successfully extracted
        extracted = extract_idiom(pred)
        if extracted and len(extracted) < len(pred):
            # Determine which pattern worked
            if '**' in pred and extracted in pred.replace('*', ''):
                patterns['extraction_patterns']['bold_text'] += 1
            elif '"' in pred:
                patterns['extraction_patterns']['quotes'] += 1
            elif 'answer' in pred.lower():
                patterns['extraction_patterns']['answer_keyword'] += 1
            else:
                patterns['extraction_patterns']['fallback'] += 1
        else:
            patterns['extraction_patterns']['failed'] += 1
    
    patterns['average_length'] = total_length / len(results) if results else 0
    
    return patterns

def debug_results(timestamp: str):
    """Examine the results file to understand accuracy and extraction issues"""
    results_path = f"logs/{timestamp}/results.json"
    
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        print(f"🔍 Debugging Results for {timestamp}")
        print("=" * 60)
        print(f"📊 Total samples: {len(results)}")
        
        # Analyze prediction patterns
        patterns = analyze_prediction_patterns(results)
        
        print(f"\n📋 Prediction Patterns:")
        print(f"  📝 Average prediction length: {patterns['average_length']:.0f} characters")
        print(f"  📝 Has bold text (**): {patterns['has_bold_text']}/{len(results)} ({patterns['has_bold_text']/len(results)*100:.1f}%)")
        print(f"  📝 Has quotes: {patterns['has_quotes']}/{len(results)} ({patterns['has_quotes']/len(results)*100:.1f}%)")
        print(f"  📝 Has 'answer' keyword: {patterns['has_answer_keyword']}/{len(results)} ({patterns['has_answer_keyword']/len(results)*100:.1f}%)")
        print(f"  📝 Has 'idiom' keyword: {patterns['has_idiom_keyword']}/{len(results)} ({patterns['has_idiom_keyword']/len(results)*100:.1f}%)")
        print(f"  📝 Has explanations (>50 chars): {patterns['has_explanation']}/{len(results)} ({patterns['has_explanation']/len(results)*100:.1f}%)")
        
        print(f"\n🔧 Extraction Success by Pattern:")
        for pattern, count in patterns['extraction_patterns'].most_common():
            percentage = count / len(results) * 100
            print(f"  {pattern}: {count}/{len(results)} ({percentage:.1f}%)")
        
        # Show examples with extraction analysis
        print(f"\n📋 Sample Extractions (First 10):")
        exact_matches = 0
        partial_matches = 0
        
        for i, result in enumerate(results[:10]):
            print(f"\n--- Example {i+1}: {result['image_id']} ---")
            
            ground_truth = normalize_idiom(result['ground_truth'])
            raw_prediction = result['prediction']
            extracted = extract_idiom(raw_prediction)
            normalized_pred = normalize_idiom(extracted)
            
            print(f"Ground Truth: '{ground_truth}'")
            print(f"Raw Prediction: '{raw_prediction[:80]}...'")
            print(f"Extracted: '{extracted}'")
            print(f"Normalized: '{normalized_pred}'")
            
            exact_match = ground_truth == normalized_pred
            partial_match = ground_truth in normalized_pred or normalized_pred in ground_truth
            
            print(f"Exact Match: {'✅' if exact_match else '❌'}")
            print(f"Partial Match: {'✅' if partial_match else '❌'}")
            
            if exact_match:
                exact_matches += 1
            if partial_match:
                partial_matches += 1
        
        # Calculate overall accuracy estimates
        print(f"\n📊 Accuracy Estimates (from sample):")
        sample_size = min(10, len(results))
        estimated_exact = exact_matches / sample_size * 100
        estimated_partial = partial_matches / sample_size * 100
        
        print(f"  Estimated Exact Match: ~{estimated_exact:.1f}%")
        print(f"  Estimated Partial Match: ~{estimated_partial:.1f}%")
        
        # Show some successful extractions
        print(f"\n✅ Examples of Successful Extractions:")
        success_count = 0
        for result in results:
            if success_count >= 5:
                break
                
            ground_truth = normalize_idiom(result['ground_truth'])
            extracted = extract_idiom(result['prediction'])
            normalized_pred = normalize_idiom(extracted)
            
            if ground_truth == normalized_pred:
                success_count += 1
                print(f"\n{success_count}. {result['image_id']}")
                print(f"   Expected: '{ground_truth}'")
                print(f"   Extracted: '{normalized_pred}' ✅")
                print(f"   From: '{result['prediction'][:60]}...'")
        
        print(f"\n💡 Recommendations:")
        print(f"1. Run: python -m experiments.evaluate --timestamp {timestamp} --use-f1 --debug")
        print(f"2. The extraction should improve accuracy from ~0% to ~{estimated_exact:.0f}%")
        print(f"3. Partial matching should reach ~{estimated_partial:.0f}%")
        
    except FileNotFoundError:
        print(f"❌ Results file not found: {results_path}")
        print(f"💡 Make sure you've run an experiment first:")
        print(f"   python -m experiments.run_experiment --config gemini1.5.yaml --prompt-style zero_shot")
    except Exception as e:
        print(f"❌ Error reading results: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_results.py <timestamp>")
        print("Example: python debug_results.py 20250609_134015")
        sys.exit(1)
    
    timestamp = sys.argv[1]
    debug_results(timestamp)

def is_description_text(text: str) -> bool:
    """Check if text looks like description rather than an idiom"""
    if not text:
        return True
    
    description_words = [
        'word', 'letter', 'image', 'puzzle', 'shows', 'written', 'drawn', 
        'depicts', 'represents', 'visual', 'graphic', 'picture', 'illustration',
        'stacked', 'positioned', 'placed', 'arranged', 'times', 'bottom', 'top',
        'left', 'right', 'corner', 'above', 'below', 'line', 'number'
    ]
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in description_words):
        return True
    
    if len(text.split()) == 1 and text.upper() == text:
        return True
    
    return False

def is_likely_idiom(text: str) -> bool:
    """Check if text looks like a real idiom"""
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    if len(text_lower) < 3 or len(text_lower) > 50:
        return False
    
    idiom_patterns = [
        r'\b\w+\s+the\s+\w+',
        r'\b\w+\s+(in|on|under|over|up|down|out|off)\s+',
        r'\b(break|cut|kick|jump|throw|catch|hit|run|get|put|take)\s+',
    ]
    
    for pattern in idiom_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return len(text.split()) >= 2

def select_best_idiom_candidate(candidates: List[str]) -> str:
    """Select the best idiom candidate from a list"""
    if not candidates:
        return ""
    
    if len(candidates) == 1:
        return candidates[0]
    
    scored_candidates = []
    
    for candidate in candidates:
        score = 0
        candidate_lower = candidate.lower()
        
        if re.search(r'\w+\s+the\s+\w+', candidate_lower):
            score += 10
        if any(word in candidate_lower for word in ['kick', 'jump', 'cut', 'break', 'throw']):
            score += 5
        if any(word in candidate_lower for word in ['under', 'over', 'in', 'on', 'out']):
            score += 3
        
        if any(word in candidate_lower for word in ['word', 'letter', 'shows', 'depicts']):
            score -= 10
        
        word_count = len(candidate.split())
        if 2 <= word_count <= 5:
            score += word_count
        
        scored_candidates.append((score, candidate))
    
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return scored_candidates[0][1]

def normalize_idiom(idiom: str) -> str:
    """Same normalization logic as in evaluate.py"""
    if not idiom:
        return ""
    
    normalized = idiom.lower().strip()
    normalized = re.sub(r'^(a\s+|an\s+|the\s+)', '', normalized)
    normalized = re.sub(r'[.,!?;:]*$', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()

def analyze_prediction_patterns(results: List[dict]) -> dict:
    """Analyze common patterns in predictions"""
    patterns = {
        'has_bold_text': 0,
        'has_quotes': 0,
        'has_answer_keyword': 0,
        'has_idiom_keyword': 0,
        'has_explanation': 0,
        'average_length': 0,
        'extraction_patterns': Counter()
    }
    
    total_length = 0
    
    for result in results:
        pred = result['prediction']
        total_length += len(pred)
        
        if '**' in pred:
            patterns['has_bold_text'] += 1
        if '"' in pred or "'" in pred:
            patterns['has_quotes'] += 1
        if re.search(r'answer\s+is', pred, re.IGNORECASE):
            patterns['has_answer_keyword'] += 1
        if re.search(r'idiom', pred, re.IGNORECASE):
            patterns['has_idiom_keyword'] += 1
        if len(pred) > 50:  # Likely has explanation
            patterns['has_explanation'] += 1
        
        # Track which pattern successfully extracted
        extracted = extract_idiom(pred)
        if extracted and len(extracted) < len(pred):
            # Determine which pattern worked
            if '**' in pred and extracted in pred.replace('*', ''):
                patterns['extraction_patterns']['bold_text'] += 1
            elif '"' in pred:
                patterns['extraction_patterns']['quotes'] += 1
            elif 'answer' in pred.lower():
                patterns['extraction_patterns']['answer_keyword'] += 1
            else:
                patterns['extraction_patterns']['fallback'] += 1
        else:
            patterns['extraction_patterns']['failed'] += 1
    
    patterns['average_length'] = total_length / len(results) if results else 0
    
    return patterns

def debug_results(timestamp: str):
    """Examine the results file to understand accuracy and extraction issues"""
    results_path = f"logs/{timestamp}/results.json"
    
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        print(f"🔍 Debugging Results for {timestamp}")
        print("=" * 60)
        print(f"📊 Total samples: {len(results)}")
        
        # Analyze prediction patterns
        patterns = analyze_prediction_patterns(results)
        
        print(f"\n📋 Prediction Patterns:")
        print(f"  📝 Average prediction length: {patterns['average_length']:.0f} characters")
        print(f"  📝 Has bold text (**): {patterns['has_bold_text']}/{len(results)} ({patterns['has_bold_text']/len(results)*100:.1f}%)")
        print(f"  📝 Has quotes: {patterns['has_quotes']}/{len(results)} ({patterns['has_quotes']/len(results)*100:.1f}%)")
        print(f"  📝 Has 'answer' keyword: {patterns['has_answer_keyword']}/{len(results)} ({patterns['has_answer_keyword']/len(results)*100:.1f}%)")
        print(f"  📝 Has 'idiom' keyword: {patterns['has_idiom_keyword']}/{len(results)} ({patterns['has_idiom_keyword']/len(results)*100:.1f}%)")
        print(f"  📝 Has explanations (>50 chars): {patterns['has_explanation']}/{len(results)} ({patterns['has_explanation']/len(results)*100:.1f}%)")
        
        print(f"\n🔧 Extraction Success by Pattern:")
        for pattern, count in patterns['extraction_patterns'].most_common():
            percentage = count / len(results) * 100
            print(f"  {pattern}: {count}/{len(results)} ({percentage:.1f}%)")
        
        # Show examples with extraction analysis
        print(f"\n📋 Sample Extractions (First 10):")
        exact_matches = 0
        partial_matches = 0
        
        for i, result in enumerate(results[:10]):
            print(f"\n--- Example {i+1}: {result['image_id']} ---")
            
            ground_truth = normalize_idiom(result['ground_truth'])
            raw_prediction = result['prediction']
            extracted = extract_idiom(raw_prediction)
            normalized_pred = normalize_idiom(extracted)
            
            print(f"Ground Truth: '{ground_truth}'")
            print(f"Raw Prediction: '{raw_prediction[:80]}...'")
            print(f"Extracted: '{extracted}'")
            print(f"Normalized: '{normalized_pred}'")
            
            exact_match = ground_truth == normalized_pred
            partial_match = ground_truth in normalized_pred or normalized_pred in ground_truth
            
            print(f"Exact Match: {'✅' if exact_match else '❌'}")
            print(f"Partial Match: {'✅' if partial_match else '❌'}")
            
            if exact_match:
                exact_matches += 1
            if partial_match:
                partial_matches += 1
        
        # Calculate overall accuracy estimates
        print(f"\n📊 Accuracy Estimates (from sample):")
        sample_size = min(10, len(results))
        estimated_exact = exact_matches / sample_size * 100
        estimated_partial = partial_matches / sample_size * 100
        
        print(f"  Estimated Exact Match: ~{estimated_exact:.1f}%")
        print(f"  Estimated Partial Match: ~{estimated_partial:.1f}%")
        
        # Show some successful extractions
        print(f"\n✅ Examples of Successful Extractions:")
        success_count = 0
        for result in results:
            if success_count >= 5:
                break
                
            ground_truth = normalize_idiom(result['ground_truth'])
            extracted = extract_idiom(result['prediction'])
            normalized_pred = normalize_idiom(extracted)
            
            if ground_truth == normalized_pred:
                success_count += 1
                print(f"\n{success_count}. {result['image_id']}")
                print(f"   Expected: '{ground_truth}'")
                print(f"   Extracted: '{normalized_pred}' ✅")
                print(f"   From: '{result['prediction'][:60]}...'")
        
        print(f"\n💡 Recommendations:")
        print(f"1. Run: python -m experiments.evaluate --timestamp {timestamp} --use-f1 --debug")
        print(f"2. The extraction should improve accuracy from ~0% to ~{estimated_exact:.0f}%")
        print(f"3. Partial matching should reach ~{estimated_partial:.0f}%")
        
    except FileNotFoundError:
        print(f"❌ Results file not found: {results_path}")
        print(f"💡 Make sure you've run an experiment first:")
        print(f"   python -m experiments.run_experiment --config gemini1.5.yaml --prompt-style zero_shot")
    except Exception as e:
        print(f"❌ Error reading results: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_results.py <timestamp>")
        print("Example: python debug_results.py 20250609_134015")
        sys.exit(1)
    
    timestamp = sys.argv[1]
    debug_results(timestamp)
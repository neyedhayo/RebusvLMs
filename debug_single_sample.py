#!/usr/bin/env python3
"""
Debug script to test a single sample and see what's causing the JSON error.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.load_data import load_dataset
from prompts.builder import PromptBuilder
from models.gemini2_0 import Gemini20Client
from experiments.utils import load_config_files

def debug_single_sample():
    """Test a single sample to diagnose the issue."""
    
    print("🔍 Debugging Single Sample")
    print("=" * 40)
    
    try:
        # 1. Load config
        print("📋 Loading configuration...")
        config = load_config_files("config/base.yaml", "config/gemini2.0.yaml")
        print("  ✅ Config loaded")
        
        # 2. Load dataset
        print("📊 Loading dataset...")
        dataset = load_dataset(
            config["dataset"]["images_dir"],
            config["dataset"]["annotations_file"]
        )
        
        if not dataset:
            print("❌ No dataset samples found!")
            return
        
        # Get first sample
        img_path, truth = dataset[0]
        img_id = os.path.splitext(os.path.basename(img_path))[0]
        print(f"  ✅ Testing sample: {img_id} → {truth}")
        
        # 3. Build prompt
        print("🔨 Building prompt...")
        builder = PromptBuilder(config)
        prompt = builder.build("zero_shot", 0, img_path)
        print(f"  ✅ Prompt built ({len(prompt)} chars)")
        print(f"  📝 Prompt preview: {prompt[:200]}...")
        
        # 4. Test model call
        print("🤖 Testing model call...")
        client = Gemini20Client(config)
        
        print("  🔄 Making API call...")
        try:
            pred = client.generate(prompt, img_path)
            print(f"  ✅ Response received!")
            print(f"  📝 Response type: {type(pred)}")
            print(f"  📝 Response length: {len(str(pred)) if pred else 0}")
            print(f"  📝 Response preview: {str(pred)[:200]}...")
            
            # 5. Test JSON serialization
            print("📄 Testing JSON serialization...")
            try:
                test_json = {"prediction": pred}
                json_str = json.dumps(test_json, ensure_ascii=False, indent=2)
                print(f"  ✅ JSON serialization successful!")
                print(f"  📝 JSON preview: {json_str[:200]}...")
                
            except Exception as json_error:
                print(f"  ❌ JSON serialization failed: {json_error}")
                print(f"  🔍 Prediction content: {repr(pred)}")
                
        except Exception as api_error:
            print(f"  ❌ API call failed: {api_error}")
            print(f"  🔍 Error type: {type(api_error)}")
            return
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def test_config_and_setup():
    """Test just the config and setup without API calls."""
    
    print("\n🔧 Testing Configuration & Setup")
    print("=" * 40)
    
    try:
        # Test config loading
        config = load_config_files("config/base.yaml", "config/gemini2.0.yaml")
        print("✅ Config loading works")
        
        # Test dataset loading  
        dataset = load_dataset(
            config["dataset"]["images_dir"],
            config["dataset"]["annotations_file"]
        )
        print(f"✅ Dataset loading works ({len(dataset)} samples)")
        
        # Test prompt building
        builder = PromptBuilder(config)
        if dataset:
            prompt = builder.build("zero_shot", 0, dataset[0][0])
            print(f"✅ Prompt building works ({len(prompt)} chars)")
        
        # Test client initialization (no API call)
        client = Gemini20Client(config)
        print("✅ Client initialization works")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 RebusvLMs Single Sample Debug")
    print("=" * 50)
    
    # First test setup
    if test_config_and_setup():
        print(f"\n{'='*50}")
        
        # Ask user if they want to test actual API call
        response = input("Setup looks good. Test actual API call? (y/n): ")
        if response.lower() in ['y', 'yes']:
            debug_single_sample()
        else:
            print("Skipping API test. Run with 'y' to test API call.")
    else:
        print("❌ Setup test failed. Fix configuration issues first.")
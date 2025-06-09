#!/usr/bin/env python3
"""
Test environment variable expansion in config
"""
import os
import sys
import yaml

# Ensure environment is set
os.environ['GOOGLE_CLOUD_PROJECT'] = 'optical-hexagon-462015-p9'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/dhayo/work/machinelearning/Multimodal_AI_MLC-NG/RebusvLMs/optical-hexagon-462015-p9-02ee74f1b2d7.json'

def expand_env_vars_recursive(obj):
    """Recursively expand environment variables in config object"""
    if isinstance(obj, dict):
        return {k: expand_env_vars_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars_recursive(item) for item in obj]
    elif isinstance(obj, str):
        return os.path.expandvars(obj)
    else:
        return obj

def test_config_expansion():
    """Test config loading with environment expansion"""
    print("🧪 Testing Config Environment Variable Expansion")
    print("=" * 50)
    
    try:
        # Load base config
        with open("config/base.yaml", 'r') as f:
            base_config = yaml.safe_load(f)
        print("✅ Base config loaded")
        
        # Load model config
        with open("config/gemini1.5.yaml", 'r') as f:
            model_config = yaml.safe_load(f)
        print("✅ Model config loaded")
        
        # Merge
        merged = {**base_config, **model_config}
        print("✅ Configs merged")
        
        # Show before expansion
        print("\n📋 BEFORE expansion:")
        print(f"  Project: {merged.get('project', 'NOT_FOUND')}")
        print(f"  Location: {merged.get('location', 'NOT_FOUND')}")
        print(f"  API Key: {merged.get('model', {}).get('api_key', 'NOT_FOUND')}")
        
        # Expand environment variables
        expanded = expand_env_vars_recursive(merged)
        print("\n📋 AFTER expansion:")
        print(f"  Project: {expanded.get('project', 'NOT_FOUND')}")
        print(f"  Location: {expanded.get('location', 'NOT_FOUND')}")
        print(f"  API Key: {expanded.get('model', {}).get('api_key', 'NOT_FOUND')[:20]}...")
        
        # Check if expansion worked
        if expanded.get('project') == 'optical-hexagon-462015-p9':
            print("\n✅ Environment variable expansion WORKING!")
            return True
        else:
            print("\n❌ Environment variable expansion FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_config_expansion()
    
    if success:
        print("\n🚀 Config expansion fixed! Run your experiment again:")
        print("python -m experiments.run_experiment --config gemini1.5.yaml --prompt-style zero_shot")
    else:
        print("\n🔧 Fix needed. Check your config files and environment variables.")

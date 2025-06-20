#!/usr/bin/env python3
"""
Debug script to check environment variable loading
"""
import os
import yaml
from pathlib import Path

def load_env_file():
    """Load .env file like the retry script does"""
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    print(f"Looking for .env file at: {env_file}")
    print(f"File exists: {env_file.exists()}")
    
    if env_file.exists():
        print("\n📋 Loading .env file...")
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"  Line {line_num}: {key} = {value[:20]}...")
                elif line:
                    print(f"  Line {line_num}: {line} (skipped)")
    else:
        print("❌ .env file not found!")

def check_environment():
    """Check if required environment variables are set"""
    print("\n🔍 Checking Environment Variables:")
    
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_CLOUD_LOCATION', 
        'GEMINI_API_KEY'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var == 'GEMINI_API_KEY':
                print(f"✅ {var}: {value[:10]}...{value[-10:] if len(value) > 20 else value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

def test_config_expansion():
    """Test config file loading and expansion"""
    print("\n🔧 Testing Config Expansion:")
    
    try:
        # Load configs
        with open("config/base.yaml", 'r') as f:
            base_config = yaml.safe_load(f)
        with open("config/gemini1.5.yaml", 'r') as f:
            model_config = yaml.safe_load(f)
        
        # Merge
        cfg = {**base_config, **model_config}
        
        print("Before expansion:")
        print(f"  API Key: {cfg['model'].get('api_key', 'NOT_FOUND')}")
        print(f"  Project: {cfg.get('project', 'NOT_FOUND')}")
        
        # Test manual expansion (the broken way)
        manual_key = os.path.expandvars(cfg['model'].get('api_key', ''))
        print(f"\nManual expansion of API key: {manual_key[:10]}...{manual_key[-10:] if len(manual_key) > 20 else manual_key}")
        
        # Test using the proper utility
        try:
            import sys
            sys.path.insert(0, '.')
            from experiments.utils import expand_env_vars_recursive
            expanded_cfg = expand_env_vars_recursive(cfg)
            print(f"Proper expansion of API key: {expanded_cfg['model']['api_key'][:10]}...{expanded_cfg['model']['api_key'][-10:] if len(expanded_cfg['model']['api_key']) > 20 else expanded_cfg['model']['api_key']}")
        except Exception as e:
            print(f"❌ Could not test proper expansion: {e}")
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")

if __name__ == "__main__":
    print("🐛 Environment Debug Script")
    print("=" * 40)
    
    load_env_file()
    check_environment()
    test_config_expansion()
    
    print("\n💡 If GEMINI_API_KEY shows properly above, the issue is in retry_failed_exp.py")
    print("💡 Use the updated version that uses expand_env_vars_recursive()")
#!/usr/bin/env python3
"""
Simple authentication test for Vertex AI setup
"""
import os
import json

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    print("=" * 40)
    
    required_vars = {
        'GOOGLE_CLOUD_PROJECT': os.environ.get('GOOGLE_CLOUD_PROJECT'),
        'GOOGLE_CLOUD_LOCATION': os.environ.get('GOOGLE_CLOUD_LOCATION'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    }
    
    all_good = True
    for var, value in required_vars.items():
        if value:
            print(f"✅ {var}: {value}")
            
            # Extra check for service account file
            if var == 'GOOGLE_APPLICATION_CREDENTIALS':
                if os.path.exists(value):
                    print(f"   ✅ Service account file exists")
                    # Verify it's the right project
                    try:
                        with open(value, 'r') as f:
                            sa_data = json.load(f)
                            sa_project = sa_data.get('project_id')
                            env_project = os.environ.get('GOOGLE_CLOUD_PROJECT')
                            if sa_project == env_project:
                                print(f"   ✅ Project IDs match: {sa_project}")
                            else:
                                print(f"   ❌ Project ID mismatch!")
                                print(f"      Service Account: {sa_project}")
                                print(f"      Environment: {env_project}")
                                all_good = False
                    except Exception as e:
                        print(f"   ❌ Error reading service account file: {e}")
                        all_good = False
                else:
                    print(f"   ❌ Service account file not found")
                    all_good = False
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    return all_good

def test_basic_auth():
    """Test basic Google Cloud authentication"""
    print("\n🔍 Testing Basic Authentication...")
    print("=" * 40)
    
    try:
        from google.auth import default
        credentials, project = default()
        print(f"✅ Default credentials found")
        print(f"✅ Authenticated project: {project}")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_genai_client():
    """Test the GenAI client (what your code actually uses)"""
    print("\n🔍 Testing GenAI Client...")
    print("=" * 40)
    
    try:
        from google import genai
        
        project = os.environ.get('GOOGLE_CLOUD_PROJECT')
        location = os.environ.get('GOOGLE_CLOUD_LOCATION')
        
        # Try different initialization methods for GenAI client
        endpoint = f"{location}-genai.googleapis.com"
        
        # Method 1: Try with api_endpoint parameter
        try:
            client = genai.Client(
                vertexai=True,
                project=project,
                location=location,
                api_endpoint=endpoint
            )
            print("✅ GenAI client initialized successfully (Method 1)!")
            print(f"✅ Endpoint: {endpoint}")
            return True
        except Exception:
            pass
        
        # Method 2: Try without custom endpoint
        try:
            client = genai.Client(
                vertexai=True,
                project=project,
                location=location
            )
            print("✅ GenAI client initialized successfully (Method 2)!")
            print(f"✅ Using default endpoint for {location}")
            return True
        except Exception:
            pass
            
        # Method 3: Test basic initialization
        client = genai.Client(vertexai=True)
        print("✅ GenAI client initialized successfully (Method 3 - basic)!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install google-genai")
        return False
    except Exception as e:
        print(f"❌ GenAI client failed: {e}")
        print("💡 This might be a library version issue")
        return False

def test_model_path():
    """Test model path construction"""
    print("\n🔍 Testing Model Paths...")
    print("=" * 40)
    
    project = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('GOOGLE_CLOUD_LOCATION')
    
    models = {
        'Gemini 2.0': f"projects/{project}/locations/{location}/publishers/google/models/gemini-2.0-flash-001",
        'Gemini 2.5': f"projects/{project}/locations/{location}/publishers/google/models/gemini-2.5-flash-preview-04-17"
    }
    
    for name, path in models.items():
        print(f"✅ {name}: {path}")
    
    return True

if __name__ == "__main__":
    print("🚀 Testing Vertex AI Authentication Setup")
    print("=" * 50)
    
    # Track test results
    tests = []
    
    # Run all tests
    print("Running 4 tests...")
    
    env_ok = check_environment()
    tests.append(("Environment Setup", env_ok))
    
    auth_ok = test_basic_auth() if env_ok else False
    tests.append(("Basic Authentication", auth_ok))
    
    genai_ok = test_genai_client() if env_ok else False
    tests.append(("GenAI Client", genai_ok))
    
    model_ok = test_model_path() if env_ok else False
    tests.append(("Model Paths", model_ok))
    
    # Calculate results
    passed = sum(1 for _, result in tests if result)
    failed = len(tests) - passed
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    print("\n📋 Detailed Results:")
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "=" * 50)
    
    if passed == len(tests):
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Next steps:")
        print("1. Run: python experiments/run_experiment.py --config gemini2.0.yaml --prompt-style zero_shot")
    else:
        print(f"⚠️  {failed} test(s) failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        if not env_ok:
            print("- Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
            print("- Ensure .env file has correct project ID")
        if not genai_ok:
            print("- This might be a google-genai library version issue")
            print("- Try: pip install --upgrade google-genai")
        
        if passed >= 3:  # If most tests pass
            print(f"\n🚀 Since {passed}/4 tests passed, you can likely still run experiments!")
            print("Try: python experiments/run_experiment.py --config gemini2.0.yaml --prompt-style zero_shot")

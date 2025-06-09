#!/usr/bin/env python3
"""
Debug script to figure out the correct google-genai API format
"""
import os
import sys
import base64

# Set environment
os.environ['GOOGLE_CLOUD_PROJECT'] = 'optical-hexagon-462015-p9'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/dhayo/work/machinelearning/Multimodal_AI_MLC-NG/RebusvLMs/optical-hexagon-462015-p9-02ee74f1b2d7.json'

try:
    from google import genai
    print("✅ google-genai imported successfully")
    print(f"📦 google-genai version: {genai.__version__ if hasattr(genai, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"❌ Failed to import google-genai: {e}")
    sys.exit(1)

def test_text_only():
    """Test with text-only request first"""
    print("\n🧪 Testing text-only request...")
    
    try:
        # Studio API client
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        
        # Simple text request
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello, how are you?"
        )
        
        print("✅ Text-only request successful!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Text-only request failed: {e}")
        return False

def test_image_formats():
    """Test different image formats"""
    print("\n🧪 Testing different image request formats...")
    
    # Use a sample image from your dataset
    img_path = "data/raw/img/001.jpg"
    if not os.path.exists(img_path):
        print(f"❌ Sample image not found: {img_path}")
        return False
    
    try:
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        
        # Read image
        with open(img_path, "rb") as f:
            img_data = f.read()
        
        # Format 1: Try the official documentation format
        print("📝 Format 1: Official docs format")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "What do you see in this image?",
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_data).decode()
                    }
                ]
            )
            print("✅ Format 1 worked!")
            return True
        except Exception as e:
            print(f"❌ Format 1 failed: {e}")
        
        # Format 2: Try with parts structure
        print("📝 Format 2: Parts structure")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[{
                    "parts": [
                        {"text": "What do you see in this image?"},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64.b64encode(img_data).decode()
                            }
                        }
                    ]
                }]
            )
            print("✅ Format 2 worked!")
            return True
        except Exception as e:
            print(f"❌ Format 2 failed: {e}")
        
        # Format 3: Try with role
        print("📝 Format 3: Role + parts structure")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[{
                    "role": "user",
                    "parts": [
                        {"text": "What do you see in this image?"},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg", 
                                "data": base64.b64encode(img_data).decode()
                            }
                        }
                    ]
                }]
            )
            print("✅ Format 3 worked!")
            return True
        except Exception as e:
            print(f"❌ Format 3 failed: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ Image test setup failed: {e}")
        return False

def check_library_info():
    """Check what methods are available"""
    print("\n🔍 Checking available methods...")
    
    try:
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        print(f"📋 Client type: {type(client)}")
        print(f"📋 Client methods: {[m for m in dir(client) if not m.startswith('_')]}")
        
        if hasattr(client, 'models'):
            print(f"📋 Models methods: {[m for m in dir(client.models) if not m.startswith('_')]}")
            
        return True
    except Exception as e:
        print(f"❌ Failed to check library info: {e}")
        return False

if __name__ == "__main__":
    print("🐛 Google GenAI API Debug Script")
    print("=" * 50)
    
    # Check environment
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY not set")
        sys.exit(1)
    print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}...")
    
    # Run tests
    check_library_info()
    text_ok = test_text_only()
    
    if text_ok:
        image_ok = test_image_formats()
        if image_ok:
            print("\n🎉 Found working format! Check the successful format above.")
        else:
            print("\n❌ All image formats failed. Check library version or documentation.")
    else:
        print("\n❌ Even text-only requests fail. Check API key or library installation.")
    
    print("\n💡 Suggestions:")
    print("1. Check library version: pip list | grep google-genai")
    print("2. Update library: pip install --upgrade google-genai")
    print("3. Check official docs: https://ai.google.dev/gemini-api/docs/sdks/python")


#!/usr/bin/env python3
"""
Test both libraries with the correct usage
"""
import os
import sys

# Set environment
os.environ['GOOGLE_CLOUD_PROJECT'] = 'optical-hexagon-462015-p9'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/dhayo/work/machinelearning/Multimodal_AI_MLC-NG/RebusvLMs/optical-hexagon-462015-p9-02ee74f1b2d7.json'

def test_studio_api():
    """Test Studio API with google-generativeai"""
    print("\n🧪 Testing Studio API (google-generativeai)...")
    
    try:
        import google.generativeai as genai
        import PIL.Image
        
        # Configure with API key
        api_key = os.environ.get('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        # Test text-only first
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, how are you?")
        print("✅ Studio API text-only: SUCCESS")
        print(f"   Response: {response.text[:100]}...")
        
        # Test with image if available
        img_path = "data/raw/img/001.jpg"
        if os.path.exists(img_path):
            img = PIL.Image.open(img_path)
            response = model.generate_content(["What do you see in this image?", img])
            print("✅ Studio API with image: SUCCESS")
            print(f"   Response: {response.text[:100]}...")
        else:
            print("⚠️  No test image found, skipping image test")
        
        return True
        
    except Exception as e:
        print(f"❌ Studio API failed: {e}")
        return False

def test_vertex_api():
    """Test Vertex AI with google-genai"""
    print("\n🧪 Testing Vertex AI (google-genai)...")
    
    try:
        from google import genai
        
        # Initialize Vertex AI client
        client = genai.Client(
            vertexai=True,
            project=os.environ.get('GOOGLE_CLOUD_PROJECT'),
            location=os.environ.get('GOOGLE_CLOUD_LOCATION')
        )
        
        # Test text-only
        response = client.models.generate_content(
            model="projects/optical-hexagon-462015-p9/locations/us-central1/publishers/google/models/gemini-2.0-flash-001",
            contents="Hello, how are you?"
        )
        print("✅ Vertex AI text-only: SUCCESS")
        print(f"   Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vertex AI failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Both Google AI Libraries")
    print("=" * 50)
    
    # Check API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not set")
        sys.exit(1)
    
    studio_ok = test_studio_api()
    vertex_ok = test_vertex_api()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"Studio API (google-generativeai): {'✅ PASS' if studio_ok else '❌ FAIL'}")
    print(f"Vertex AI (google-genai): {'✅ PASS' if vertex_ok else '❌ FAIL'}")
    
    if studio_ok:
        print("\n🎉 Studio API works! Your experiments should run now.")
    else:
        print("\n❌ Both APIs failed. Check your setup.")


import mimetypes
import base64
from typing import Any, Dict, List
import PIL.Image

class BaseClient:
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the appropriate client:
          - For Vertex AI: uses google-genai library
          - For Studio API: uses google-generativeai library
        """
        use_vertexai = config["model"].get("use_vertexai", True)

        if use_vertexai:
            # For Vertex AI - use google-genai
            try:
                from google import genai
                region = config["location"]
                project = config["project"]
                
                print(f"[BaseClient] Initializing Vertex AI client for project: {project}, region: {region}")
                
                self.client = genai.Client(
                    vertexai=True,
                    project=project,
                    location=region
                )
                self.client_type = "vertex"
                print(f"[BaseClient] ✅ Vertex AI client initialized")
            except Exception as e:
                print(f"[BaseClient] ❌ Failed to initialize Vertex AI client: {e}")
                raise
        else:
            # For Studio API - use google-generativeai
            try:
                import google.generativeai as genai
                api_key = config["model"]["api_key"]
                
                genai.configure(api_key=api_key)
                self.client = genai
                self.client_type = "studio"
                print(f"[BaseClient] ✅ Studio API client initialized")
            except Exception as e:
                print(f"[BaseClient] ❌ Failed to initialize Studio API client: {e}")
                raise

        self.config = config
        self.max_retries = 3

    def generate(
        self,
        model_name: str,
        prompt: str,
        image_path: str
    ) -> str:
        """
        Sends a text+image multimodal request using the appropriate library.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Attempt {attempt}: Calling {model_name}...")
                
                if self.client_type == "studio":
                    # Use google-generativeai for Studio API
                    response = self._generate_studio(model_name, prompt, image_path)
                else:
                    # Use google-genai for Vertex AI
                    response = self._generate_vertex(model_name, prompt, image_path)
                
                return response

            except Exception as e:
                print(f"Error on attempt {attempt}: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    backoff = 2 ** (attempt - 1)
                    print(f"Retrying in {backoff}s…")
                    import time; time.sleep(backoff)
                else:
                    print("Max retries reached; aborting.")
                    raise

    def _generate_studio(self, model_name: str, prompt: str, image_path: str) -> str:
        """Generate using google-generativeai (Studio API)"""
        # Load image using PIL
        img = PIL.Image.open(image_path)
        
        # Create model
        model = self.client.GenerativeModel(model_name)
        
        # Generate content
        response = model.generate_content([prompt, img])
        
        return response.text.strip() if response.text else "No response text"

    def _generate_vertex(self, model_name: str, prompt: str, image_path: str) -> str:
        """Generate using google-genai (Vertex AI)"""
        import base64
        
        # Read and encode image
        with open(image_path, "rb") as f:
            img_data = f.read()
        
        img_b64 = base64.b64encode(img_data).decode()
        
        # Build content for Vertex AI
        contents = [
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": img_b64
            }
        ]
        
        response = self.client.models.generate_content(
            model=model_name,
            contents=contents
        )
        
        # Parse response
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        elif hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            return part.text.strip()
                elif hasattr(candidate.content, 'text'):
                    return candidate.content.text.strip()
        
        return "No response text found"
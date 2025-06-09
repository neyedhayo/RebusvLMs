import mimetypes
from typing import Any, Dict, List

from google import genai
from google.genai import types  # type: ignore

class BaseClient:
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the GenAI client:
          - For Vertex AI, supplies vertexai=True, project, location
          - For Studio, supplies api_key.
        """
        use_vertexai = config["model"].get("use_vertexai", True)

        if use_vertexai:
            # For Vertex AI - try different initialization methods
            region = config["location"]
            project = config["project"]
            
            # Try Method 1: with api_endpoint parameter
            try:
                endpoint = f"{region}-genai.googleapis.com"
                self.client = genai.Client(
                    vertexai=True,
                    project=project,
                    location=region,
                    api_endpoint=endpoint
                )
                print(f"[BaseClient] Using Vertex AI with custom endpoint: {endpoint}")
            except Exception:
                # Try Method 2: without custom endpoint (fallback)
                try:
                    self.client = genai.Client(
                        vertexai=True,
                        project=project,
                        location=region
                    )
                    print(f"[BaseClient] Using Vertex AI with default endpoint")
                except Exception as e:
                    # Try Method 3: basic initialization
                    self.client = genai.Client(vertexai=True)
                    print(f"[BaseClient] Using Vertex AI with basic initialization")
        else:
            # For Studio API
            self.client = genai.Client(
                api_key=config["model"]["api_key"]
            )
            print(f"[BaseClient] Using Studio API")

        self.config = config
        self.max_retries = 3

    def generate(
        self,
        model_name: str,
        prompt: str,
        image_path: str
    ) -> str:
        """
        Sends a text+image multimodal request, retrying on network errors.
        """
        # 1) Figure out MIME
        mime_type, _ = mimetypes.guess_type(image_path)
        mime_type = mime_type or "application/octet-stream"

        # 2) Read the image
        with open(image_path, "rb") as f:
            img_bytes = f.read()

        # 3) Build the mixed content: prompt + image bytes
        contents: List[Any] = [
            prompt,
            types.Part.from_bytes(data=img_bytes, mime_type=mime_type),
        ]

        # 4) Call with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Attempt {attempt}: Calling {model_name}...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config={"max_output_tokens": self.config["model"]["max_output_tokens"]}
                )
                return getattr(response, "text", None) or response.candidates[0].content.strip()

            except Exception as e:
                print(f"Error on attempt {attempt}: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    backoff = 2 ** (attempt - 1)
                    print(f"Retrying in {backoff}s…")
                    import time; time.sleep(backoff)
                else:
                    print("Max retries reached; aborting.")
                    raise
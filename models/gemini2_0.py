from .base_client import BaseClient

class Gemini20Client(BaseClient):
    def __init__(self, config):
        super().__init__(config)
        # full resource path from config/gemini2.0.yaml
        self.model_name = config["model"]["name"]

    def generate(self, prompt: str, image_path: str) -> str:
        return super().generate(self.model_name, prompt, image_path)

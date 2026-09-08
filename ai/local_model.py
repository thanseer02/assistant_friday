import json
import urllib.request
import urllib.error
from .model import LanguageModel

class OllamaModel(LanguageModel):
    """
    Concrete implementation of LanguageModel that connects to a 
    locally running Ollama instance via HTTP.
    Make sure Ollama is installed and running on your machine!
    """
    def __init__(self, model_name="llama3", endpoint="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.endpoint = endpoint

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Ollama feature that forces the model to output JSON
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.endpoint, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", '{"intent": "UNKNOWN", "entities": {}}')
        except urllib.error.URLError:
            print("[System Warning] Could not connect to Ollama. Is it running?")
            return '{"intent": "UNKNOWN", "entities": {}}'
        except Exception as e:
            print(f"[System Error] LLM failed: {e}")
            return '{"intent": "UNKNOWN", "entities": {}}'

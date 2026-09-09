import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import logger

class AIService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 30.0 # 30 seconds timeout for LLM response

    async def generate_response(self, message: str) -> str:
        """
        Communicates with the local Ollama server to generate a response.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": message,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
                
        except httpx.TimeoutException:
            logger.error("Timeout connecting to Ollama server.")
            raise HTTPException(status_code=504, detail="AI engine response timeout")
            
        except httpx.RequestError as e:
            logger.error(f"Error communicating with Ollama server: {e}")
            raise HTTPException(status_code=503, detail="AI engine is currently unavailable")
            
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            raise HTTPException(status_code=500, detail="Internal server error in AI engine")

import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import logger

class AIService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 30.0 # 30 seconds timeout for LLM response

    async def generate_response(self, messages: list[dict], memories: list[str] = None) -> str:
        """
        Communicates with the local Ollama server to generate a response using chat history.
        Informs the AI about relevant long-term memories if provided.
        """
        url = f"{self.base_url}/api/chat"
        
        # Inject memories as a system prompt if provided
        final_messages = []
        if memories:
            memory_text = "\n".join([f"- {m}" for m in memories])
            system_msg = {
                "role": "system",
                "content": f"You are a helpful assistant. Here is some relevant information you know about the user:\n{memory_text}"
            }
            final_messages.append(system_msg)
            
        final_messages.extend(messages)
            
        payload = {
            "model": self.model,
            "messages": final_messages,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
                
        except httpx.TimeoutException:
            logger.error("Timeout connecting to Ollama server.")
            raise HTTPException(status_code=504, detail="AI engine response timeout")
            
        except httpx.RequestError as e:
            logger.error(f"Error communicating with Ollama server: {e}")
            raise HTTPException(status_code=503, detail="AI engine is currently unavailable")
            
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            raise HTTPException(status_code=500, detail="Internal server error in AI engine")

    async def extract_memories(self, message: str) -> list[dict]:
        """
        Makes a secondary lightweight call to Ollama to extract factual information from the user message.
        Returns a list of dictionaries with 'key', 'value', 'category' or an empty list if nothing important.
        """
        import json
        url = f"{self.base_url}/api/generate"
        
        prompt = f"""
You are an information extraction tool. Analyze the user's message below.
If the user states a fact about themselves, a preference, or long-term context (like a name, project name, favorite language, etc.), extract it.
If there is no long term fact to remember, output exactly an empty JSON array: []

Output ONLY valid JSON in this format:
[
    {{"key": "What the fact is about", "value": "The fact itself", "category": "preference/fact"}}
]

User message: "{message}"
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    text = response.json().get("response", "[]")
                    # Clean up formatting if ollama wrapped it
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                        
                    return json.loads(text)
        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            
        return []

from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with the given arguments."""
        pass
    
    def to_ollama_format(self) -> dict[str, Any]:
        """Convert the tool definition to Ollama's expected format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

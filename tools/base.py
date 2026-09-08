from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description to tell the LLM when to use this tool."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, str]:
        """A dictionary describing expected parameters and their types."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Executes the tool safely with the provided arguments and returns a string result."""
        pass

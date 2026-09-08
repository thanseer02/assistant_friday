from abc import ABC, abstractmethod

class LanguageModel(ABC):
    """
    Abstract base class for all LLM providers.
    This guarantees that the rest of the assistant doesn't care
    if we are using Ollama, HuggingFace, OpenAI, or a mock.
    """
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Takes a prompt string and returns the generated text.
        """
        pass

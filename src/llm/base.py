from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_code(self, prompt: str) -> str:
        """Generates code based on the provided prompt."""
        pass

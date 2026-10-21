from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseAIProvider(ABC):
    """
    Abstract base class for BYO-AI providers (OpenAI, Google Gemini).
    Ensures normalized interface for text generation, structured outputs, and key validation.
    """
    
    def __init__(self, api_key: str, default_model: Optional[str] = None):
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate text completion from provider."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate JSON structured response from provider."""
        pass

    @abstractmethod
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate whether the user's BYO API key is working and measure latency."""
        pass

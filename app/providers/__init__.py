from app.providers.base import BaseAIProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.demo_provider import DemoProvider

def get_provider(provider_name: str, api_key: str = None, model: str = None) -> BaseAIProvider:
    provider_name = (provider_name or "gemini").lower()
    if "demo" in provider_name or "local" in provider_name:
        return DemoProvider(api_key=api_key, default_model=model)
    elif "gemini" in provider_name:
        return GeminiProvider(api_key=api_key, default_model=model)
    elif "openai" in provider_name:
        return OpenAIProvider(api_key=api_key, default_model=model)
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}. Choose 'gemini', 'openai', or 'demo'.")

__all__ = ["BaseAIProvider", "GeminiProvider", "OpenAIProvider", "DemoProvider", "get_provider"]

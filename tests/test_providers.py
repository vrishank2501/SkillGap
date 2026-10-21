import pytest
from app.providers import get_provider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider

def test_provider_factory():
    gemini = get_provider("gemini", api_key="test-gemini-key", model="gemini-1.5-flash")
    assert isinstance(gemini, GeminiProvider)
    assert gemini.default_model == "gemini-1.5-flash"

    openai = get_provider("openai", api_key="test-openai-key", model="gpt-4o-mini")
    assert isinstance(openai, OpenAIProvider)
    assert openai.default_model == "gpt-4o-mini"

    with pytest.raises(ValueError):
        get_provider("unsupported_provider", api_key="key")

@pytest.mark.asyncio
async def test_openai_invalid_key_validation():
    # Test that invalid key returns handled error dict rather than unhandled crash
    provider = OpenAIProvider(api_key="invalid-sk-key-test")
    res = await provider.validate_connection()
    assert res["valid"] is False
    assert "error" in res

@pytest.mark.asyncio
async def test_gemini_invalid_key_validation():
    provider = GeminiProvider(api_key="invalid-gemini-key-test")
    res = await provider.validate_connection()
    assert res["valid"] is False
    assert "error" in res


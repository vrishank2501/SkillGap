import time
import logging
from typing import Optional, Dict, Any
from app.providers.base import BaseAIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI Provider supporting gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo.
    Instantiates an ephemeral client with the user's BYO API key.
    """
    
    SUPPORTED_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        super().__init__(api_key=api_key, default_model=default_model or "gpt-4o-mini")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def validate_connection(self) -> Dict[str, Any]:
        """
        Validates the user's OpenAI API key by testing credentials and checking completion quota.
        """
        start = time.time()
        try:
            # 1. First verify key authenticity
            await self.client.models.list()
            
            # 2. Test actual generation permission and credit balance with a minimal 1-token test
            await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            
            latency_ms = int((time.time() - start) * 1000)
            return {
                "valid": True,
                "provider": "openai",
                "model": self.default_model,
                "latency_ms": latency_ms,
                "message": f"Connected to OpenAI ({latency_ms}ms)"
            }
        except Exception as e:
            err_msg = str(e)
            if "insufficient_quota" in err_msg or "exceeded your current quota" in err_msg:
                return {
                    "valid": False,
                    "provider": "openai",
                    "code": "insufficient_quota",
                    "error": "OpenAI Account has $0 prepaid API balance. Even with a ChatGPT Plus subscription, OpenAI API requires prepaid credits at platform.openai.com/settings/organization/billing. Switch to Google Gemini (Free) or Demo Mode to test immediately."
                }
            elif "Incorrect API key provided" in err_msg or "invalid_api_key" in err_msg:
                return {
                    "valid": False,
                    "provider": "openai",
                    "code": "invalid_api_key",
                    "error": "Incorrect OpenAI API key provided."
                }
            else:
                return {
                    "valid": False,
                    "provider": "openai",
                    "error": err_msg
                }

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        model_name = model or self.default_model
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        model_name = model or self.default_model
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

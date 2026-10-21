import time
import asyncio
import logging
from typing import Optional, Dict, Any
from app.providers.base import BaseAIProvider

logger = logging.getLogger(__name__)


def _map_gemini_error(raw: str) -> str:
    """
    Converts raw Gemini SDK exception messages into user-friendly strings.

    The google-genai v2 SDK wraps HTTP errors as plain strings that include
    the JSON body, so we pattern-match on key phrases instead of exception types.
    """
    if "API_KEY_INVALID" in raw or "API key not valid" in raw:
        return "Invalid Google Gemini API key. Please check and re-enter it."
    if "RESOURCE_EXHAUSTED" in raw or "Quota exceeded" in raw or "quota" in raw.lower():
        return "Gemini quota exceeded or rate limit reached. Wait a moment and retry."
    if "404" in raw or "NOT_FOUND" in raw or "Model is not found" in raw or "no longer available" in raw:
        return (
            "Model not available for your API key. "
            "Try switching to 'gemini-3.8-flash' or 'gemini-flash-latest' in the model selector."
        )
    if "PERMISSION_DENIED" in raw or "403" in raw:
        return "Permission denied. Your key may not have access to this model or feature."
    if "INVALID_ARGUMENT" in raw:
        return "Invalid request sent to Gemini. Check your prompt or model settings."
    return f"Gemini error: {raw[:300]}"  # Truncate long raw messages


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini Provider supporting gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash.
    Instantiates an ephemeral client with the user's BYO API key.
    """
    
    # Models confirmed working (Oct 2026, google-genai v2.32.0):
    # gemini-3.5-flash   ✅ ~6.7s  ← fastest, use as default
    # gemini-flash-latest ✅ ~13s
    # gemini-3.8-flash   ✅ ~18s   ← slowest but reliable
    SUPPORTED_MODELS = [
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3.8-flash",
    ]

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        super().__init__(api_key=api_key, default_model=default_model or "gemini-3.5-flash")
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self._sdk_version = "google-genai"
        except ImportError:
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self.client = legacy_genai
                self._sdk_version = "legacy"
            except ImportError:
                raise ImportError("Neither 'google-genai' nor 'google-generativeai' package is installed.")

    async def validate_connection(self) -> Dict[str, Any]:
        """
        Validates the user's Gemini API key by performing a minimal real generation call.

        Why a real call instead of models.get()?
        - google-genai v2+ uses v1beta API where models.get() requires the full
          "models/<name>" path and still 404s for some models in certain regions.
        - A tiny generate_content() call is more reliable and confirms the key
          has actual generation permissions, not just metadata read access.
        """
        start = time.time()
        try:
            def _ping():
                if self._sdk_version == "google-genai":
                    from google.genai import types
                    # Minimal single-token generation to confirm key + model work
                    response = self.client.models.generate_content(
                        model=self.default_model,
                        contents="Hi",
                        config=types.GenerateContentConfig(max_output_tokens=1),
                    )
                    return response.text or ""
                else:
                    # Legacy google-generativeai SDK
                    model_inst = self.client.GenerativeModel(model_name=self.default_model)
                    response = model_inst.generate_content(
                        "Hi",
                        generation_config={"max_output_tokens": 1},
                    )
                    return response.text or ""

            await asyncio.to_thread(_ping)
            latency_ms = int((time.time() - start) * 1000)
            return {
                "valid": True,
                "provider": "gemini",
                "model": self.default_model,
                "latency_ms": latency_ms,
                "message": f"Connected to Gemini ({latency_ms}ms)",
            }
        except Exception as e:
            return {
                "valid": False,
                "provider": "gemini",
                "error": _map_gemini_error(str(e)),
            }

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        model_name = model or self.default_model

        def _call_gemini():
            if self._sdk_version == "google-genai":
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction if system_instruction else None,
                    temperature=temperature,
                )
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                return response.text or ""
            else:
                model_inst = self.client.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction,
                )
                response = model_inst.generate_content(prompt)
                return response.text or ""

        try:
            return await asyncio.to_thread(_call_gemini)
        except Exception as e:
            raise RuntimeError(_map_gemini_error(str(e))) from e

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        model_name = model or self.default_model

        def _call_gemini_json():
            if self._sdk_version == "google-genai":
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction if system_instruction else None,
                    temperature=temperature,
                    response_mime_type="application/json",
                )
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                return response.text or "{}"
            else:
                gen_config = {"response_mime_type": "application/json", "temperature": temperature}
                model_inst = self.client.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction,
                    generation_config=gen_config,
                )
                response = model_inst.generate_content(prompt)
                return response.text or "{}"

        try:
            return await asyncio.to_thread(_call_gemini_json)
        except Exception as e:
            raise RuntimeError(_map_gemini_error(str(e))) from e

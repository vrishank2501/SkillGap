import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.providers import get_provider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider

router = APIRouter(prefix="/providers", tags=["providers"])
logger = logging.getLogger(__name__)

class ValidateKeyRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None

class ModelOption(BaseModel):
    id: str
    name: str
    description: str

@router.post("/validate")
async def validate_provider_key(req: ValidateKeyRequest):
    """
    Validates a BYO-AI key in real time before using it in chat.
    Returns latency (ms) and status.
    """
    provider_name = req.provider.strip().lower()
    api_key = req.api_key.strip()

    if not api_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")

    try:
        provider_instance = get_provider(provider_name=provider_name, api_key=api_key, model=req.model)
        result = await provider_instance.validate_connection()
        return result
    except Exception as e:
        logger.error(f"Provider validation failed: {e}")
        return {
            "valid": False,
            "provider": provider_name,
            "error": str(e),
        }

@router.get("/models")
async def get_supported_models():
    """
    Returns available models for Gemini and OpenAI.
    """
    return {
        "gemini": [
            {"id": "gemini-3.5-flash",    "name": "Gemini 3.5 Flash ✦",    "recommended": True},
            {"id": "gemini-flash-latest",  "name": "Gemini Flash Latest",   "recommended": False},
            {"id": "gemini-3.8-flash",     "name": "Gemini 3.8 Flash",      "recommended": False},
        ],
        "openai": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "recommended": True},
            {"id": "gpt-4o", "name": "GPT-4o", "recommended": False},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "recommended": False},
        ]
    }


from fastapi import APIRouter
from app.core.config import settings
from app.core.supabase import get_supabase_client

router = APIRouter()

@router.get("/health")
async def health_check():
    client = get_supabase_client()
    supabase_status = "connected" if client is not None else "not_configured_or_offline"
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "supabase": supabase_status,
        "version": "1.0.0",
    }


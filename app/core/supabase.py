import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client = None
_supabase_auth_client = None

def get_supabase_auth_client():
    """Return an anon-key client used to validate Supabase access tokens."""
    global _supabase_auth_client
    if _supabase_auth_client is not None:
        return _supabase_auth_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise RuntimeError("Supabase Auth requires SUPABASE_URL and SUPABASE_ANON_KEY.")

    from supabase import create_client
    _supabase_auth_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _supabase_auth_client

def get_authenticated_user(access_token: str):
    """Validate an access token with Supabase Auth and return its user."""
    response = get_supabase_auth_client().auth.get_user(access_token)
    return response.user

def get_supabase_client():
    """
    Returns an initialized Supabase client using Service Role Key (for backend operations)
    or Anon key. Returns None if credentials are not configured.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not (settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY):
        logger.warning("Supabase credentials not fully configured in environment.")
        return None

    try:
        from supabase import create_client, Client
        key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        _supabase_client = create_client(settings.SUPABASE_URL, key)
        logger.info("Supabase client initialized successfully.")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None


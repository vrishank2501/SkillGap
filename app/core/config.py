import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    # Supabase credentials
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    
    # Direct database connection
    DATABASE_URL: str = ""
    
    # Storage
    DOCUMENT_STORAGE_DIR: str = str(BASE_DIR / "data" / "documents")
    MAX_UPLOAD_SIZE_MB: int = 25
    SKILLS_DIR: str = str(BASE_DIR / "skills")
    
    # Optional default API keys (Fallback if user does not supply per-session key)
    DEFAULT_GEMINI_API_KEY: str = ""
    DEFAULT_OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure local document storage directory exists
os.makedirs(settings.DOCUMENT_STORAGE_DIR, exist_ok=True)


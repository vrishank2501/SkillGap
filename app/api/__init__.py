from app.api.health import router as health_router
from app.api.documents import router as documents_router
from app.api.progress import router as progress_router
from app.api.chat import router as chat_router

__all__ = ["health_router", "documents_router", "progress_router", "chat_router"]


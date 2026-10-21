import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.supabase import get_authenticated_user
from app.api.health import router as health_router
from app.api.documents import router as documents_router
from app.api.progress import router as progress_router
from app.api.chat import router as chat_router
from app.api.providers import router as providers_router

app = FastAPI(
    title="SkillBridge AI",
    description="BYO-AI personalized skill-gap learning platform",
    version="1.0.0",
)

PUBLIC_API_PATHS = {"/api/health", "/api/auth/config"}

@app.middleware("http")
async def authenticate_api_requests(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/") and path not in PUBLIC_API_PATHS:
        authorization = request.headers.get("authorization", "")
        scheme, _, access_token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not access_token.strip():
            return JSONResponse(status_code=401, content={"detail": "Sign in to continue."})

        try:
            user = await run_in_threadpool(get_authenticated_user, access_token.strip())
        except RuntimeError as error:
            return JSONResponse(status_code=503, content={"detail": str(error)})
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Your session is invalid or expired. Sign in again."})

        if user is None:
            return JSONResponse(status_code=401, content={"detail": "Your session is invalid or expired. Sign in again."})
        request.state.user_id = str(user.id)

    return await call_next(request)

@app.get("/api/auth/config")
async def auth_config():
    return {
        "supabase_url": settings.SUPABASE_URL,
        "supabase_anon_key": settings.SUPABASE_ANON_KEY,
    }

# CORS middleware for local frontend development or API consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(providers_router, prefix="/api")

# Static UI serving
UI_DIR = Path(__file__).resolve().parent / "ui"
if UI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")

    @app.get("/")
    async def serve_ui():
        index_file = UI_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "SkillBridge AI API is online. UI file not found."}


import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

@app.middleware("http")
async def set_local_user(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        request.state.user_id = "dev-user-01"
    return await call_next(request)

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

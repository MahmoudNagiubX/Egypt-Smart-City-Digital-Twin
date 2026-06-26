from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

from backend.app.config import settings
from backend.app.weather_impact.router import router as weather_impact_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_impact_router)

# Resolve paths relative to PROJECT_ROOT
MAIN_FILE = Path(__file__).resolve()
PROJECT_ROOT = MAIN_FILE.parent.parent.parent
DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

# Mount static assets if the build directory exists
if os.path.exists(DIST_DIR):
    assets_dir = DIST_DIR / "assets"
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/")
def read_root():
    if os.path.exists(DIST_DIR):
        index_file = DIST_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    return {
        "project": "Egypt Smart City Digital Twin",
        "module": "Nasr City Weather-Impact Emergency Mobility Module",
        "case_study": "Nasr City, Cairo",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "backend",
        "module": "weather_impact"
    }

# SPA fallback route (registered last to prevent intercepting specific routes)
@app.get("/{catchall:path}")
def serve_spa(catchall: str):
    if os.path.exists(DIST_DIR):
        # Exclude API endpoints, docs, and health checks from being caught
        if catchall.startswith("api") or catchall in ["docs", "openapi.json", "health"]:
            raise HTTPException(status_code=404, detail="Not Found")
            
        target_file = DIST_DIR / catchall
        if target_file.exists() and target_file.is_file():
            return FileResponse(str(target_file))
            
        index_file = DIST_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
            
    raise HTTPException(status_code=404, detail="Not Found")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings

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

@app.get("/")
def read_root():
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

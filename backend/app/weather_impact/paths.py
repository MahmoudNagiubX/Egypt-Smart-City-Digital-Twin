"""Path definitions for the weather-impact module."""

from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
APP_ROOT = BACKEND_ROOT / "app"
MODULE_ROOT = APP_ROOT / "weather_impact"

# Data directories
DATA_DIR = APP_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = DATA_DIR / "outputs"
MAPS_DIR = DATA_DIR / "maps"
SAMPLES_DIR = DATA_DIR / "samples"
MODELS_DIR = DATA_DIR / "models"

# Nasr City specific paths
NASR_CITY_DIR = DATA_DIR / "nasr_city"
NASR_CITY_RAW = NASR_CITY_DIR / "raw"
NASR_CITY_PROCESSED = NASR_CITY_DIR / "processed"
NASR_CITY_OUTPUTS = NASR_CITY_DIR / "outputs"

# Nasr City output files
NASR_CITY_BOUNDARY_PATH = NASR_CITY_PROCESSED / "nasr_city_boundary.geojson"
NASR_CITY_GRAPH_PATH = NASR_CITY_PROCESSED / "nasr_city_graph.graphml"
NASR_CITY_NODES_PATH = NASR_CITY_PROCESSED / "nasr_city_nodes.geojson"
NASR_CITY_ROADS_PATH = NASR_CITY_PROCESSED / "nasr_city_roads.geojson"
NASR_CITY_FACILITIES_PATH = NASR_CITY_PROCESSED / "nasr_city_emergency_facilities.geojson"
SPATIAL_VALIDATION_REPORT_PATH = NASR_CITY_OUTPUTS / "spatial_validation_report.json"


def ensure_data_dirs():
    """Create all required data directories."""
    directories = [
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        OUTPUTS_DIR,
        MAPS_DIR,
        SAMPLES_DIR,
        MODELS_DIR,
        NASR_CITY_DIR,
        NASR_CITY_RAW,
        NASR_CITY_PROCESSED,
        NASR_CITY_OUTPUTS,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_data_path_summary():
    """Return a dict of all data paths for verification."""
    return {
        "project_root": str(PROJECT_ROOT),
        "backend_root": str(BACKEND_ROOT),
        "app_root": str(APP_ROOT),
        "module_root": str(MODULE_ROOT),
        "data_dir": str(DATA_DIR),
        "nasr_city_dir": str(NASR_CITY_DIR),
        "nasr_city_boundary": str(NASR_CITY_BOUNDARY_PATH),
        "nasr_city_graph": str(NASR_CITY_GRAPH_PATH),
        "nasr_city_nodes": str(NASR_CITY_NODES_PATH),
        "nasr_city_roads": str(NASR_CITY_ROADS_PATH),
        "nasr_city_facilities": str(NASR_CITY_FACILITIES_PATH),
        "spatial_validation_report": str(SPATIAL_VALIDATION_REPORT_PATH),
    }

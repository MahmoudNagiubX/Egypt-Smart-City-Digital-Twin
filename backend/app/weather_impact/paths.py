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
NASR_CITY_MAPS = NASR_CITY_DIR / "maps"
NASR_CITY_SAMPLES = NASR_CITY_DIR / "samples"

# Nasr City output files
NASR_CITY_BOUNDARY_PATH = NASR_CITY_PROCESSED / "nasr_city_boundary.geojson"
NASR_CITY_GRAPH_PATH = NASR_CITY_PROCESSED / "nasr_city_graph.graphml"
NASR_CITY_NODES_PATH = NASR_CITY_PROCESSED / "nasr_city_nodes.geojson"
NASR_CITY_ROADS_PATH = NASR_CITY_PROCESSED / "nasr_city_roads.geojson"
NASR_CITY_FACILITIES_PATH = NASR_CITY_PROCESSED / "nasr_city_emergency_facilities.geojson"
SPATIAL_VALIDATION_REPORT_PATH = NASR_CITY_OUTPUTS / "spatial_validation_report.json"
NASR_CITY_GRID_PATH = NASR_CITY_PROCESSED / "nasr_city_grid_500m.geojson"
ROADS_WITH_ZONE_IDS_PATH = NASR_CITY_PROCESSED / "roads_with_zone_ids.geojson"
SPATIAL_FOUNDATION_MAP_PATH = NASR_CITY_MAPS / "spatial_foundation_map.png"

# Weather output files
WEATHER_RAW_PATH = NASR_CITY_RAW / "weather_history_open_meteo.csv"
WEATHER_PROCESSED_PATH = NASR_CITY_PROCESSED / "weather_hourly_processed.csv"
WEATHER_SCENARIOS_PATH = NASR_CITY_SAMPLES / "weather_scenarios.json"
WEATHER_VALIDATION_REPORT_PATH = NASR_CITY_OUTPUTS / "weather_validation_report.json"

# Feature engineering output files
GRID_ROAD_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_road_features.csv"
GRID_WEATHER_SCENARIO_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_weather_scenario_features.csv"
GRID_ELEVATION_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_elevation_features.csv"
ZONE_FEATURES_CSV_PATH = NASR_CITY_PROCESSED / "zone_features_ml_ready.csv"
ZONE_FEATURES_GEOJSON_PATH = NASR_CITY_PROCESSED / "zone_features_ml_ready.geojson"
FEATURE_VALIDATION_REPORT_PATH = NASR_CITY_OUTPUTS / "feature_validation_report.json"

# Real observed dataset paths
WEATHER_HISTORY_2015_2025_PATH = NASR_CITY_RAW / "weather_history_open_meteo_2015_2025.csv"
REAL_RAIN_EVENTS_PATH = NASR_CITY_PROCESSED / "real_rain_events.csv"
GRID_GPM_RAINFALL_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_gpm_rainfall_features.csv"
GRID_BUILTUP_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_builtup_features.csv"
GRID_LANDCOVER_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_landcover_features.csv"
GRID_POPULATION_FEATURES_PATH = NASR_CITY_PROCESSED / "grid_population_features.csv"
REAL_OBSERVED_TRAINING_DATASET_PATH = NASR_CITY_PROCESSED / "real_observed_training_dataset.csv"
REAL_DATA_VALIDATION_REPORT_PATH = NASR_CITY_OUTPUTS / "real_data_validation_report.json"


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
        NASR_CITY_MAPS,
        NASR_CITY_SAMPLES,
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
        "nasr_city_grid": str(NASR_CITY_GRID_PATH),
        "roads_with_zone_ids": str(ROADS_WITH_ZONE_IDS_PATH),
        "spatial_foundation_map": str(SPATIAL_FOUNDATION_MAP_PATH),
        "weather_raw": str(WEATHER_RAW_PATH),
        "weather_processed": str(WEATHER_PROCESSED_PATH),
        "weather_scenarios": str(WEATHER_SCENARIOS_PATH),
        "weather_validation_report": str(WEATHER_VALIDATION_REPORT_PATH),
        "grid_road_features": str(GRID_ROAD_FEATURES_PATH),
        "grid_weather_scenario_features": str(GRID_WEATHER_SCENARIO_FEATURES_PATH),
        "grid_elevation_features": str(GRID_ELEVATION_FEATURES_PATH),
        "zone_features_ml_ready_csv": str(ZONE_FEATURES_CSV_PATH),
        "zone_features_ml_ready_geojson": str(ZONE_FEATURES_GEOJSON_PATH),
        "feature_validation_report": str(FEATURE_VALIDATION_REPORT_PATH),
        "weather_history_2015_2025": str(WEATHER_HISTORY_2015_2025_PATH),
        "real_rain_events": str(REAL_RAIN_EVENTS_PATH),
        "grid_gpm_rainfall_features": str(GRID_GPM_RAINFALL_FEATURES_PATH),
        "grid_builtup_features": str(GRID_BUILTUP_FEATURES_PATH),
        "grid_landcover_features": str(GRID_LANDCOVER_FEATURES_PATH),
        "grid_population_features": str(GRID_POPULATION_FEATURES_PATH),
        "real_observed_training_dataset": str(REAL_OBSERVED_TRAINING_DATASET_PATH),
        "real_data_validation_report": str(REAL_DATA_VALIDATION_REPORT_PATH),
    }

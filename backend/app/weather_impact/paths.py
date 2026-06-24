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
NASR_CITY_MODELS = NASR_CITY_DIR / "models"

# Nasr City output files
NASR_CITY_BOUNDARY_PATH = NASR_CITY_PROCESSED / "nasr_city_boundary.geojson"
NASR_CITY_GRAPH_PATH = NASR_CITY_PROCESSED / "nasr_city_graph.graphml"
NASR_CITY_NODES_PATH = NASR_CITY_PROCESSED / "nasr_city_nodes.geojson"
NASR_CITY_ROADS_PATH = NASR_CITY_PROCESSED / "nasr_city_roads.geojson"
NASR_CITY_FACILITIES_PATH = NASR_CITY_PROCESSED / "nasr_city_emergency_facilities.geojson"
NASR_CITY_POIS_PATH = NASR_CITY_PROCESSED / "nasr_city_pois.geojson"
PLACES_SUMMARY_REPORT_PATH = NASR_CITY_OUTPUTS / "places_summary_report.json"
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

# ML training output paths
ML_FEATURE_COLUMNS_PATH = NASR_CITY_MODELS / "ml_feature_columns.json"
TRAIN_TEST_SPLIT_SUMMARY_PATH = NASR_CITY_MODELS / "train_test_split_summary.json"
BASELINE_MODEL_METRICS_PATH = NASR_CITY_MODELS / "baseline_model_metrics.json"
RF_MODEL_PATH = NASR_CITY_MODELS / "weather_impact_rf_model.joblib"
RF_METRICS_PATH = NASR_CITY_MODELS / "weather_impact_rf_metrics.json"
HGB_MODEL_PATH = NASR_CITY_MODELS / "weather_impact_hgb_model.joblib"
HGB_METRICS_PATH = NASR_CITY_MODELS / "weather_impact_hgb_metrics.json"
MODEL_COMPARISON_PATH = NASR_CITY_MODELS / "model_comparison.json"
FEATURE_IMPORTANCE_PATH = NASR_CITY_MODELS / "feature_importance.csv"
FEATURE_IMPORTANCE_PLOT_PATH = NASR_CITY_MODELS / "feature_importance.png"
PREDICTION_SAMPLE_PATH = NASR_CITY_MODELS / "prediction_sample.csv"
MODEL_CARD_PATH = NASR_CITY_MODELS / "MODEL_CARD.md"
ML_TRAINING_REPORT_PATH = NASR_CITY_OUTPUTS / "ml_training_report.json"

# Prediction output paths
REAL_OBSERVED_PREDICTIONS_CSV_PATH = NASR_CITY_OUTPUTS / "real_observed_predictions.csv"
REAL_OBSERVED_PREDICTIONS_GEOJSON_PATH = NASR_CITY_OUTPUTS / "real_observed_predictions.geojson"
LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH = NASR_CITY_OUTPUTS / "latest_selected_event_risk.geojson"
TOP_RAIN_EVENT_RISK_GEOJSON_PATH = NASR_CITY_OUTPUTS / "top_rain_event_risk.geojson"
ZONE_RISK_SUMMARY_CSV_PATH = NASR_CITY_OUTPUTS / "zone_risk_summary.csv"
ZONE_RISK_SUMMARY_GEOJSON_PATH = NASR_CITY_OUTPUTS / "zone_risk_summary.geojson"
PREDICTION_OUTPUT_REPORT_PATH = NASR_CITY_OUTPUTS / "prediction_output_report.json"

# Routing paths
ROAD_RISK_WEIGHTS_TOP_RAIN_PATH = NASR_CITY_OUTPUTS / "road_risk_weights_top_rain.geojson"
ROAD_RISK_WEIGHTS_LATEST_PATH = NASR_CITY_OUTPUTS / "road_risk_weights_latest.geojson"
DEMO_ROUTE_TOP_RAIN_NORMAL_PATH = NASR_CITY_OUTPUTS / "demo_route_top_rain_normal.geojson"
DEMO_ROUTE_TOP_RAIN_SAFE_PATH = NASR_CITY_OUTPUTS / "demo_route_top_rain_safe.geojson"
DEMO_ROUTE_LATEST_NORMAL_PATH = NASR_CITY_OUTPUTS / "demo_route_latest_normal.geojson"
DEMO_ROUTE_LATEST_SAFE_PATH = NASR_CITY_OUTPUTS / "demo_route_latest_safe.geojson"
ROUTE_COMPARISON_TOP_RAIN_PATH = NASR_CITY_OUTPUTS / "route_comparison_top_rain.json"
ROUTE_COMPARISON_LATEST_PATH = NASR_CITY_OUTPUTS / "route_comparison_latest.json"
ROUTING_VALIDATION_REPORT_PATH = NASR_CITY_OUTPUTS / "routing_validation_report.json"

# Live Weather output paths
LIVE_WEATHER_SUMMARY_PATH = NASR_CITY_OUTPUTS / "live_weather_summary.json"
LIVE_WEATHER_RISK_GEOJSON_PATH = NASR_CITY_OUTPUTS / "live_weather_risk.geojson"
LIVE_WEATHER_RISK_PREDICTIONS_CSV_PATH = NASR_CITY_OUTPUTS / "live_weather_risk_predictions.csv"
LIVE_WEATHER_RISK_REPORT_PATH = NASR_CITY_OUTPUTS / "live_weather_risk_report.json"
LIVE_WEATHER_CACHE_DIR = NASR_CITY_DIR / "cache"
LIVE_WEATHER_FORECAST_CACHE_PATH = LIVE_WEATHER_CACHE_DIR / "live_open_meteo_forecast.json"

# System integrity audit paths
SYSTEM_INTEGRITY_AUDIT_REPORT_PATH = NASR_CITY_OUTPUTS / "system_integrity_audit_report.json"
EMERGENCY_FACILITY_REACHABILITY_AUDIT_PATH = NASR_CITY_OUTPUTS / "emergency_facility_reachability_audit.csv"
HIGH_RISK_ZONE_BEST_FACILITY_ROUTES_PATH = NASR_CITY_OUTPUTS / "high_risk_zone_best_facility_routes.csv"
BACKEND_READINESS_SUMMARY_PATH = NASR_CITY_OUTPUTS / "backend_readiness_summary.json"


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
        NASR_CITY_MODELS,
        LIVE_WEATHER_CACHE_DIR,
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

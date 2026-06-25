import os
from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
import pytest

# Define paths relative to the test file to ensure compatibility
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
PROCESSED_DIR = NASR_CITY_DIR / "processed"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"

ROAD_FEATURES_PATH = PROCESSED_DIR / "grid_road_features.csv"
WEATHER_FEATURES_PATH = PROCESSED_DIR / "grid_weather_scenario_features.csv"
ELEVATION_FEATURES_PATH = PROCESSED_DIR / "grid_elevation_features.csv"
ZONE_FEATURES_CSV_PATH = PROCESSED_DIR / "zone_features_ml_ready.csv"
ZONE_FEATURES_GEOJSON_PATH = PROCESSED_DIR / "zone_features_ml_ready.geojson"
REPORT_PATH = OUTPUTS_DIR / "feature_validation_report.json"


def test_feature_files_exist():
    """Verify that all feature engineering output files exist."""
    assert ROAD_FEATURES_PATH.exists(), f"Road features file not found: {ROAD_FEATURES_PATH}"
    assert WEATHER_FEATURES_PATH.exists(), f"Weather scenario features file not found: {WEATHER_FEATURES_PATH}"
    assert ELEVATION_FEATURES_PATH.exists(), f"Elevation features file not found: {ELEVATION_FEATURES_PATH}"
    assert ZONE_FEATURES_CSV_PATH.exists(), f"Final features CSV file not found: {ZONE_FEATURES_CSV_PATH}"
    assert ZONE_FEATURES_GEOJSON_PATH.exists(), f"Final features GeoJSON file not found: {ZONE_FEATURES_GEOJSON_PATH}"
    assert REPORT_PATH.exists(), f"Feature validation report file not found: {REPORT_PATH}"


def test_final_features_dataframe():
    """Verify final features CSV load and contents."""
    df = pd.read_csv(ZONE_FEATURES_CSV_PATH)
    assert len(df) == 2080, f"Expected 2080 rows, found {len(df)}"
    
    # Check key identification columns
    assert "zone_code" in df.columns, "zone_code column is missing"
    assert "scenario_id" in df.columns, "scenario_id column is missing"
    assert "elevation_source" in df.columns, "elevation_source column is missing"
    
    # Check scenario values
    scenarios = df["scenario_id"].unique().tolist()
    assert "heavy_rain_rush_hour" in scenarios
    assert "extreme_rain" in scenarios


def test_normalized_scores():
    """Verify normalized score columns presence and boundaries."""
    df = pd.read_csv(ZONE_FEATURES_CSV_PATH)
    
    score_cols = [
        "road_density_score", "road_count_score", "rainfall_score",
        "rainfall_accumulation_score", "temperature_score", "humidity_score",
        "wind_score", "rush_hour_score", "low_elevation_score", "low_slope_score",
        "builtup_proxy_score", "impervious_proxy_score", "low_vegetation_proxy_score"
    ]
    
    for col in score_cols:
        assert col in df.columns, f"Normalized score column '{col}' is missing"
        # Check that values are between 0.0 and 1.0
        series = df[col].dropna()
        assert (series >= 0.0).all(), f"Values in '{col}' are negative: {series.min()}"
        assert (series <= 1.0).all(), f"Values in '{col}' exceed 1.0: {series.max()}"


def test_geojson_readable():
    """Verify final GeoJSON is readable with GeoPandas and contains geometry."""
    gdf = gpd.read_file(ZONE_FEATURES_GEOJSON_PATH)
    assert not gdf.empty, "GeoJSON is empty"
    assert gdf.crs is not None, "GeoJSON has no CRS"
    assert "geometry" in gdf.columns, "GeoJSON is missing geometry"
    assert len(gdf) == 2080, f"Expected 2080 spatial rows, found {len(gdf)}"


def test_feature_validation_report():
    """Verify feature validation report contents and status."""
    with open(REPORT_PATH, "r") as f:
        report = json.load(f)
        
    assert "status" in report
    assert report["status"] in ["ok", "ok_with_warnings"], f"Validation status is failed: {report['status']}"
    assert report["actual_rows"] == 2080
    assert report["required_columns_present"] is True
    assert report["normalized_score_columns_valid"] is True

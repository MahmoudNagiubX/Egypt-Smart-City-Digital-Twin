import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
import pytest

# Define paths relative to this file
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"

PREDICTIONS_CSV_PATH = OUTPUTS_DIR / "real_observed_predictions.csv"
PREDICTIONS_GEOJSON_PATH = OUTPUTS_DIR / "real_observed_predictions.geojson"
LATEST_EVENT_GEOJSON_PATH = OUTPUTS_DIR / "latest_selected_event_risk.geojson"
TOP_RAIN_GEOJSON_PATH = OUTPUTS_DIR / "top_rain_event_risk.geojson"
ZONE_SUMMARY_CSV_PATH = OUTPUTS_DIR / "zone_risk_summary.csv"
ZONE_SUMMARY_GEOJSON_PATH = OUTPUTS_DIR / "zone_risk_summary.geojson"
REPORT_JSON_PATH = OUTPUTS_DIR / "prediction_output_report.json"


def test_files_existence():
    """Verify that all prediction outputs and report exist."""
    assert PREDICTIONS_CSV_PATH.exists(), f"Predictions CSV not found at: {PREDICTIONS_CSV_PATH}"
    assert PREDICTIONS_GEOJSON_PATH.exists(), f"Predictions GeoJSON not found at: {PREDICTIONS_GEOJSON_PATH}"
    assert LATEST_EVENT_GEOJSON_PATH.exists(), f"Latest event GeoJSON not found at: {LATEST_EVENT_GEOJSON_PATH}"
    assert TOP_RAIN_GEOJSON_PATH.exists(), f"Top rain event GeoJSON not found at: {TOP_RAIN_GEOJSON_PATH}"
    assert ZONE_SUMMARY_CSV_PATH.exists(), f"Zone summary CSV not found at: {ZONE_SUMMARY_CSV_PATH}"
    assert ZONE_SUMMARY_GEOJSON_PATH.exists(), f"Zone summary GeoJSON not found at: {ZONE_SUMMARY_GEOJSON_PATH}"
    assert REPORT_JSON_PATH.exists(), f"Report JSON not found at: {REPORT_JSON_PATH}"


def test_predictions_csv_content():
    """Verify predictions CSV content has rows > 0, y_pred in [0, 1], and valid risk classes."""
    df = pd.read_csv(PREDICTIONS_CSV_PATH)
    assert len(df) == 12480, f"Expected 12480 rows in predictions, got {len(df)}"
    
    assert "y_pred" in df.columns, "y_pred column missing in predictions CSV"
    assert "predicted_risk_class" in df.columns, "predicted_risk_class missing in predictions CSV"
    assert "y_true" in df.columns, "y_true column missing in predictions CSV"
    
    # Assert values are between 0 and 1
    assert df["y_pred"].min() >= 0.0, f"y_pred min is less than 0.0: {df['y_pred'].min()}"
    assert df["y_pred"].max() <= 1.0, f"y_pred max is greater than 1.0: {df['y_pred'].max()}"
    
    # Assert risk class
    classes = df["predicted_risk_class"].unique()
    for c in classes:
        assert c in ["low", "medium", "high"], f"Unexpected predicted risk class: {c}"


def test_geojson_layers_geopandas_readable():
    """Verify that the generated GeoJSON files are valid and readable by GeoPandas in EPSG:4326."""
    for path in [LATEST_EVENT_GEOJSON_PATH, TOP_RAIN_GEOJSON_PATH, ZONE_SUMMARY_GEOJSON_PATH]:
        gdf = gpd.read_file(path)
        assert len(gdf) > 0, f"GeoJSON layer {path.name} is empty"
        assert gdf.crs is not None, f"CRS is missing for GeoJSON layer {path.name}"
        assert gdf.crs.to_string() == "EPSG:4326", f"CRS for {path.name} is not EPSG:4326: {gdf.crs.to_string()}"


def test_zone_summary_rows_and_crs():
    """Verify zone summary has one row per zone (416 zones) and valid values."""
    df = pd.read_csv(ZONE_SUMMARY_CSV_PATH)
    assert len(df) == 416, f"Expected 416 rows (one per grid zone), got {len(df)}"
    
    assert "mean_predicted_score" in df.columns
    assert "dominant_risk_class" in df.columns
    
    assert df["mean_predicted_score"].min() >= 0.0
    assert df["mean_predicted_score"].max() <= 1.0
    
    for c in df["dominant_risk_class"].unique():
        assert c in ["low", "medium", "high"], f"Unexpected dominant risk class: {c}"


def test_prediction_output_report():
    """Verify that the prediction report contains correct status, warnings, and disclaimer flags."""
    with open(REPORT_JSON_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert "status" in report
    assert report["status"] in ["ok", "ok_with_warnings"], f"Report status is failed: {report['status']}"
    assert len(report["warnings"]) == 0, f"Found warnings in prediction report: {report['warnings']}"
    
    assert report["official_flood_labels_claimed"] is False, "Should not claim official flood labels"
    assert report["demo_scenarios_used_for_training"] is False, "Should not use demo scenarios for training"
    assert "prediction_rows" in report
    assert report["prediction_rows"] == 12480
    assert report["zone_count"] == 416
    assert report["event_count"] == 30
    
    # Check honesty note
    assert "honesty_note" in report
    note = report["honesty_note"].lower()
    assert "not verified street-level flood incident predictions" in note

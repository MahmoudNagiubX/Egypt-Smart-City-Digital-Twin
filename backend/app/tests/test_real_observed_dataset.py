import json
from pathlib import Path
import pandas as pd
import pytest

# Define paths relative to this file
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
PROCESSED_DIR = NASR_CITY_DIR / "processed"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"

TRAINING_DATASET_PATH = PROCESSED_DIR / "real_observed_training_dataset.csv"
VALIDATION_REPORT_PATH = OUTPUTS_DIR / "real_data_validation_report.json"


def test_real_dataset_exists():
    """Verify that the real observed training dataset exists."""
    assert TRAINING_DATASET_PATH.exists(), f"Real training dataset CSV not found at: {TRAINING_DATASET_PATH}"


def test_real_dataset_rows():
    """Verify that the dataset contains a valid number of rows."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert len(df) > 0, "Real training dataset is empty"
    # 30 events x 416 grid cells = 12,480 rows
    assert len(df) == 12480, f"Expected 12,480 rows, found {len(df)}"


def test_required_columns_exist():
    """Verify that the dataset contains all required columns."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    
    required_cols = [
        "zone_code", "timestamp", "event_id", "rain_1h_mm", "rain_3h_mm", "rain_6h_mm", "rain_24h_mm",
        "gpm_precipitation_mean", "gpm_precipitation_max", "gpm_precipitation_sum", "temperature_2m",
        "apparent_temperature", "relative_humidity_2m", "wind_speed_10m", "hour", "is_rush_hour",
        "road_density_m_per_km2", "road_count", "road_length_m", "elevation_mean", "slope_mean",
        "low_elevation_score", "low_slope_score", "built_surface_mean", "built_surface_sum",
        "builtup_landcover_ratio", "tree_cover_ratio", "grassland_ratio", "bare_sparse_ratio",
        "water_ratio", "population_sum", "population_density_proxy",
        "observed_rain_hazard_score", "observed_exposure_score", "data_driven_weather_impact_score", "target_type"
    ]
    
    for col in required_cols:
        assert col in df.columns, f"Required column '{col}' is missing from the dataset"


def test_target_type_integrity():
    """Verify that target_type is not fake and contains correct value."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert "target_type" in df.columns
    unique_targets = df["target_type"].unique().tolist()
    assert len(unique_targets) == 1
    assert unique_targets[0] == "engineered_from_real_observations", f"Incorrect target_type value: {unique_targets[0]}"
    
    # Verify we don't have fake flood labels
    assert "real_flood_label" not in df.columns, "Found forbidden column name 'real_flood_label'"


def test_no_scenario_id_required():
    """Verify that no demo scenario_id is present or required for training."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert "scenario_id" not in df.columns, "demo column 'scenario_id' should not be present in the real observed training dataset"


def test_validation_report():
    """Verify that the validation report exists and has correct status."""
    assert VALIDATION_REPORT_PATH.exists(), f"Validation report not found at: {VALIDATION_REPORT_PATH}"
    
    with open(VALIDATION_REPORT_PATH, "r") as f:
        report = json.load(f)
        
    assert "status" in report
    assert report["status"] in ["ok", "ok_with_warnings"], f"Validation status is failed: {report['status']}"
    assert report["output_rows"] == 12480
    assert len(report["missing_columns"]) == 0

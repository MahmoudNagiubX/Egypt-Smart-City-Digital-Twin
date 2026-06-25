import os
from pathlib import Path
import json
import pandas as pd
import pytest

# Define paths relative to the test file to ensure compatibility
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
RAW_DIR = NASR_CITY_DIR / "raw"
PROCESSED_DIR = NASR_CITY_DIR / "processed"
SAMPLES_DIR = NASR_CITY_DIR / "samples"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"

RAW_PATH = RAW_DIR / "weather_history_open_meteo.csv"
PROCESSED_PATH = PROCESSED_DIR / "weather_hourly_processed.csv"
SCENARIOS_PATH = SAMPLES_DIR / "weather_scenarios.json"
REPORT_PATH = OUTPUTS_DIR / "weather_validation_report.json"


def test_weather_files_exist():
    """Verify that all weather pipeline files exist."""
    assert RAW_PATH.exists(), f"Raw weather file not found: {RAW_PATH}"
    assert PROCESSED_PATH.exists(), f"Processed weather file not found: {PROCESSED_PATH}"
    assert SCENARIOS_PATH.exists(), f"Weather scenarios file not found: {SCENARIOS_PATH}"
    assert REPORT_PATH.exists(), f"Weather validation report not found: {REPORT_PATH}"


def test_processed_weather_read_and_columns():
    """Verify processed weather can be read with pandas and contains required columns."""
    df = pd.read_csv(PROCESSED_PATH)
    assert not df.empty, "Processed weather DataFrame is empty"
    
    required_cols = [
        "timestamp", "date", "hour", "temperature_2m", "relative_humidity_2m",
        "apparent_temperature", "precipitation", "rain", "wind_speed_10m",
        "rain_1h_mm", "rain_3h_mm", "rain_6h_mm", "rain_24h_mm",
        "rainfall_class", "is_rush_hour"
    ]
    for col in required_cols:
        assert col in df.columns, f"Required column '{col}' is missing from processed weather"


def test_scenarios():
    """Verify weather scenarios format, counts, and contents."""
    with open(SCENARIOS_PATH, "r") as f:
        scenarios = json.load(f)
        
    assert isinstance(scenarios, list), "Scenarios must be a JSON array"
    assert len(scenarios) >= 5, f"Expected at least 5 scenarios, found {len(scenarios)}"
    
    # Verify uniqueness of scenario IDs
    scenario_ids = [s.get("scenario_id") for s in scenarios]
    assert len(scenario_ids) == len(set(scenario_ids)), "Scenario IDs are not unique"
    
    # Verify specific key scenarios exist
    assert "heavy_rain_rush_hour" in scenario_ids, "heavy_rain_rush_hour scenario is missing"
    assert "extreme_rain" in scenario_ids, "extreme_rain scenario is missing"
    
    # Verify details of a scenario
    for s in scenarios:
        assert "scenario_id" in s
        assert "name" in s
        assert "rain_1h_mm" in s
        assert "rain_3h_mm" in s
        assert "rain_6h_mm" in s
        assert "rain_24h_mm" in s
        assert "temperature_2m" in s
        assert "is_rush_hour" in s


def test_validation_report():
    """Verify validation report exists and contains correct format/status."""
    with open(REPORT_PATH, "r") as f:
        report = json.load(f)
        
    assert "status" in report
    assert report["status"] in ["ok", "ok_with_warnings"], f"Validation status failed: {report['status']}"
    assert "raw_rows" in report
    assert "processed_rows" in report
    assert report["processed_rows"] > 0
    assert "scenario_count" in report
    assert report["scenario_count"] >= 5

import sys
from pathlib import Path
import json
import pytest
import pandas as pd
import geopandas as gpd
from fastapi.testclient import TestClient

# Adjust paths to match the app directory
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from backend.app.main import app
from backend.app.weather_impact import paths, weather, model, service

client = TestClient(app)

@pytest.fixture
def mock_forecast_data():
    """A standard mock forecast response payload from Open-Meteo API."""
    current_time_str = "2026-06-25T00:00"
    times = [f"2026-06-25T{h:02d}:00" for h in range(48)]
    
    # Make some rain in the first hours of the forecast
    rain_values = [0.0] * 48
    rain_values[1] = 1.5
    rain_values[2] = 2.5
    rain_values[3] = 4.0
    
    precip_values = [0.0] * 48
    precip_values[1] = 1.5
    precip_values[2] = 2.5
    precip_values[3] = 4.0
    
    prob_values = [0] * 48
    prob_values[1] = 50
    prob_values[2] = 80
    prob_values[3] = 95
    
    temps = [25.0] * 48
    humidity = [60.0] * 48
    apparent = [26.0] * 48
    wind = [10.0] * 48
    
    return {
        "current": {
            "time": current_time_str,
            "temperature_2m": 24.5,
            "rain": 0.0,
            "precipitation": 0.0,
            "wind_speed_10m": 8.5,
            "weather_code": 3
        },
        "hourly": {
            "time": times,
            "precipitation": precip_values,
            "rain": rain_values,
            "precipitation_probability": prob_values,
            "temperature_2m": temps,
            "relative_humidity_2m": humidity,
            "apparent_temperature": apparent,
            "wind_speed_10m": wind
        }
    }


def test_live_weather_summary_handles_mocked_forecast(mock_forecast_data):
    """1. Test that live weather summary function handles mocked forecast properly."""
    summary = weather.summarize_live_weather_forecast(mock_forecast_data, warnings=[])
    assert summary is not None
    assert isinstance(summary, dict)
    assert summary["status"] in ["ok", "ok_with_warnings"]
    assert "current" in summary
    assert "forecast_window" in summary


def test_rain_calculations(mock_forecast_data):
    """2. Test that rain_1h, rain_3h, rain_6h, rain_24h are correctly computed."""
    summary = weather.summarize_live_weather_forecast(mock_forecast_data, warnings=[])
    window = summary["forecast_window"]
    
    # Expected calculations:
    # rain_1h = rain[0] = 0.0
    # rain_3h = rain[0]+rain[1]+rain[2] = 0.0 + 1.5 + 2.5 = 4.0
    # rain_6h = rain[0]..rain[5] = 0.0 + 1.5 + 2.5 + 4.0 + 0.0 + 0.0 = 8.0
    # rain_24h = rain[0]..rain[23] = 8.0
    
    assert window["rain_1h_mm"] == pytest.approx(0.0)
    assert window["rain_3h_mm"] == pytest.approx(4.0)
    assert window["rain_6h_mm"] == pytest.approx(8.0)
    assert window["rain_24h_mm"] == pytest.approx(8.0)
    assert window["max_precipitation_probability"] == pytest.approx(95.0)


def test_live_feature_matrix_one_row_per_zone(mock_forecast_data):
    """3. Test that live feature matrix has one row per zone (416 zones)."""
    summary = weather.summarize_live_weather_forecast(mock_forecast_data, warnings=[])
    X, metadata, uses_gpm_proxy = model.build_live_weather_feature_matrix(summary)
    
    assert len(X) == 416
    assert len(metadata) == 416
    assert "zone_code" in metadata.columns


def test_feature_matrix_uses_ml_feature_columns(mock_forecast_data):
    """4. Test that the live feature matrix matches the expected ml_feature_columns.json columns."""
    summary = weather.summarize_live_weather_forecast(mock_forecast_data, warnings=[])
    X, metadata, uses_gpm_proxy = model.build_live_weather_feature_matrix(summary)
    
    expected_features = model.load_feature_columns()
    assert list(X.columns) == expected_features


def test_predictions_bounded_zero_one(monkeypatch, mock_forecast_data):
    """5. Test that live predictions are bounded between 0 and 1."""
    monkeypatch.setattr(weather, "fetch_live_weather_forecast", lambda *args, **kwargs: (mock_forecast_data, []))
    
    # Run service risk generation
    report = service.generate_live_weather_risk_layer()
    assert report["status"] in ["ok", "ok_with_warnings"]
    
    df_pred = pd.read_csv(paths.LIVE_WEATHER_RISK_PREDICTIONS_CSV_PATH)
    assert len(df_pred) == 416
    assert df_pred["live_predicted_score"].min() >= 0.0
    assert df_pred["live_predicted_score"].max() <= 1.0


def test_risk_classes_low_medium_high(monkeypatch, mock_forecast_data):
    """6. Test that risk classes are low/medium/high only."""
    monkeypatch.setattr(weather, "fetch_live_weather_forecast", lambda *args, **kwargs: (mock_forecast_data, []))
    service.generate_live_weather_risk_layer()
    
    df_pred = pd.read_csv(paths.LIVE_WEATHER_RISK_PREDICTIONS_CSV_PATH)
    unique_classes = set(df_pred["live_risk_class"].unique())
    assert unique_classes.issubset({"low", "medium", "high"})


def test_live_weather_risk_geojson_featurecollection(monkeypatch, mock_forecast_data):
    """7. Test that live_weather_risk.geojson is a valid GeoJSON FeatureCollection."""
    monkeypatch.setattr(weather, "fetch_live_weather_forecast", lambda *args, **kwargs: (mock_forecast_data, []))
    service.generate_live_weather_risk_layer()
    
    assert paths.LIVE_WEATHER_RISK_GEOJSON_PATH.exists()
    
    with open(paths.LIVE_WEATHER_RISK_GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data.get("type") == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) == 416
    
    # Check properties
    properties = data["features"][0]["properties"]
    assert "zone_code" in properties
    assert "live_predicted_score" in properties
    assert "live_risk_class" in properties
    assert "honesty_note" in properties
    assert "weather-impact risk" in properties["honesty_note"].lower()


def test_live_weather_risk_report_honesty_note(monkeypatch, mock_forecast_data):
    """8. Test that live_weather_risk_report.json has official_flood_labels_claimed false."""
    monkeypatch.setattr(weather, "fetch_live_weather_forecast", lambda *args, **kwargs: (mock_forecast_data, []))
    service.generate_live_weather_risk_layer()
    
    assert paths.LIVE_WEATHER_RISK_REPORT_PATH.exists()
    
    with open(paths.LIVE_WEATHER_RISK_REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert report["official_flood_labels_claimed"] is False
    assert report["official_emergency_dispatch_claimed"] is False
    assert "honesty_note" in report
    assert "weather-impact risk" in report["honesty_note"].lower()


def test_live_weather_api_endpoint(monkeypatch, mock_forecast_data):
    """9. Test that live weather API endpoint (/api/weather-impact/weather/live) returns 200 with report/summary."""
    monkeypatch.setattr(weather, "fetch_live_weather_forecast", lambda *args, **kwargs: (mock_forecast_data, []))
    
    response = client.get("/api/weather-impact/weather/live")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] in ["ok", "ok_with_warnings"]
    assert data["location"]["name"] == "Nasr City"
    assert data["current"]["temperature_2m"] == pytest.approx(24.5)
    assert data["forecast_window"]["rain_24h_mm"] == pytest.approx(8.0)


def test_live_prediction_layer_and_report_endpoints(monkeypatch, mock_forecast_data):
    """10. Test live prediction layer endpoint (/api/weather-impact/layers/predictions/live) returns FeatureCollection."""
    monkeypatch.setattr(weather, "fetch_live_weather_forecast", lambda *args, **kwargs: (mock_forecast_data, []))
    
    # Force regeneration by removing file
    if paths.LIVE_WEATHER_RISK_GEOJSON_PATH.exists():
        paths.LIVE_WEATHER_RISK_GEOJSON_PATH.unlink()
        
    response = client.get("/api/weather-impact/layers/predictions/live")
    assert response.status_code == 200
    
    data = response.json()
    assert data.get("type") == "FeatureCollection"
    assert len(data["features"]) == 416
    
    # Test report endpoint as well
    response_report = client.get("/api/weather-impact/weather/live/report")
    assert response_report.status_code == 200
    report_data = response_report.json()
    assert report_data["status"] in ["ok", "ok_with_warnings"]
    assert report_data["prediction_rows"] == 416
    assert report_data["official_flood_labels_claimed"] is False

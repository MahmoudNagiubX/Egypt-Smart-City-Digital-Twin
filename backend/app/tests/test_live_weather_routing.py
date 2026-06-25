import sys
import json
from pathlib import Path
import pytest
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
from backend.app.weather_impact import paths, routing, service

client = TestClient(app)


def test_live_routing_status_endpoint():
    """1. Test that GET /routing/live/status returns 200."""
    response = client.get("/api/weather-impact/routing/live/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "live_weather_available" in data
    assert "live_risk_layer_available" in data


def test_status_includes_honesty_note():
    """2. Test that status response includes honesty note."""
    response = client.get("/api/weather-impact/routing/live/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "honesty_note" in data
    assert "decision-support prototype outputs" in data["honesty_note"]
    assert "not official emergency dispatch instructions" in data["honesty_note"]


def test_emergency_dispatch_claimed_is_false():
    """3. Test that status says official_emergency_dispatch_claimed is false if included."""
    # The flag is included in the live_route_validation_report.json which is updated during status check
    response = client.get("/api/weather-impact/routing/live/status")
    assert response.status_code == 200
    
    assert paths.LIVE_ROUTE_VALIDATION_REPORT_PATH.exists()
    with open(paths.LIVE_ROUTE_VALIDATION_REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert report["official_emergency_dispatch_claimed"] is False
    assert report["official_flood_labels_claimed"] is False


def test_live_emergency_routing_valid_coordinates():
    """4. Test that POST /routing/live/emergency-route with valid Nasr City coordinates returns 200."""
    payload = {
        "origin": {"lat": 30.061, "lon": 31.344},
        "destination": {"lat": 30.044, "lon": 31.365},
        "route_preference": "both",
        "refresh_live_weather": False
    }
    response = client.post("/api/weather-impact/routing/live/emergency-route", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] in ["ok", "ok_with_warnings"]
    assert data["mode"] == "live_weather"


def test_live_routing_includes_geojson_routes():
    """5. Test that response includes normal_route and weather_safe_route FeatureCollections."""
    payload = {
        "origin": {"lat": 30.061, "lon": 31.344},
        "destination": {"lat": 30.044, "lon": 31.365},
        "route_preference": "both",
        "refresh_live_weather": False
    }
    response = client.post("/api/weather-impact/routing/live/emergency-route", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "normal_route" in data
    assert "weather_safe_route" in data
    assert data["normal_route"].get("type") == "FeatureCollection"
    assert data["weather_safe_route"].get("type") == "FeatureCollection"


def test_live_routing_includes_comparison():
    """6. Test that response includes comparison metrics."""
    payload = {
        "origin": {"lat": 30.061, "lon": 31.344},
        "destination": {"lat": 30.044, "lon": 31.365},
        "route_preference": "both",
        "refresh_live_weather": False
    }
    response = client.post("/api/weather-impact/routing/live/emergency-route", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "comparison" in data
    comp = data["comparison"]
    assert "safe_route_available" in comp
    assert "risk_reduction_percent" in comp
    assert "eta_tradeoff_percent" in comp
    assert "normal_distance_m" in comp
    assert "safe_distance_m" in comp


def test_live_routing_includes_recommendation():
    """7. Test that response includes routing recommendation."""
    payload = {
        "origin": {"lat": 30.061, "lon": 31.344},
        "destination": {"lat": 30.044, "lon": 31.365},
        "route_preference": "both",
        "refresh_live_weather": False
    }
    response = client.post("/api/weather-impact/routing/live/emergency-route", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "recommendation" in data
    assert data["recommendation"] in ["normal_route_acceptable", "weather_safe_route_recommended", "no_distinct_safer_alternative"]


def test_live_routing_missing_coordinates():
    """8. Test that missing coordinates returns validation error (422)."""
    payload = {
        "destination": {"lat": 30.044, "lon": 31.365},
        "route_preference": "both"
    }
    response = client.post("/api/weather-impact/routing/live/emergency-route", json=payload)
    assert response.status_code == 422


def test_live_routing_far_coordinates():
    """9. Test that coordinates far outside Nasr City return clear error (400 or 404)."""
    payload = {
        "origin": {"lat": 29.0, "lon": 30.0},
        "destination": {"lat": 30.044, "lon": 31.365},
        "route_preference": "both",
        "refresh_live_weather": False
    }
    response = client.post("/api/weather-impact/routing/live/emergency-route", json=payload)
    assert response.status_code in [400, 404]


def test_live_road_risk_weights_exists():
    """10. Test that live_road_risk_weights.geojson exists and is valid."""
    # Should exist since the generator script and routes were run
    assert paths.LIVE_ROAD_RISK_WEIGHTS_GEOJSON_PATH.exists()
    
    gdf = gpd.read_file(paths.LIVE_ROAD_RISK_WEIGHTS_GEOJSON_PATH)
    assert len(gdf) > 0
    assert "live_weather_weight" in gdf.columns
    assert "live_predicted_score" in gdf.columns
    assert "live_risk_class" in gdf.columns

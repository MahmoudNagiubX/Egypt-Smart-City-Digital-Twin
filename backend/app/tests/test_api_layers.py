import sys
from pathlib import Path

# Add project root (C:\Users\mahmo\Documents\Smart Digital Twin) to sys.path
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent  # C:\Users\mahmo\Documents\Smart Digital Twin

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_health():
    """Verify health endpoint returns status and disclaimer flags correctly."""
    response = client.get("/api/weather-impact/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["official_flood_labels_claimed"] is False
    assert data["demo_scenarios_used_for_training"] is False
    assert "Nasr City" in data["module_name"]


def test_api_spatial_layers():
    """Verify that spatial GeoJSON layer endpoints return 200 and valid GeoJSON FeatureCollections."""
    layers = ["boundary", "grid", "emergency-facilities"]
    for layer in layers:
        response = client.get(f"/api/weather-impact/layers/{layer}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) > 0


def test_api_prediction_metadata():
    """Verify prediction metadata endpoint returns correct counts and flags."""
    response = client.get("/api/weather-impact/predictions/metadata")
    assert response.status_code == 200
    
    data = response.json()
    assert data["prediction_rows"] > 0
    assert data["zone_count"] == 416
    assert data["event_count"] == 30
    assert data["official_flood_labels_claimed"] is False
    assert data["demo_scenarios_used_for_training"] is False
    assert "model_used" in data


def test_api_prediction_layers():
    """Verify prediction layers (latest, top-rain, risk-summary) are GeoJSON FeatureCollections."""
    layers = ["predictions/latest", "predictions/top-rain", "risk-summary"]
    for layer in layers:
        response = client.get(f"/api/weather-impact/layers/{layer}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) == 416


def test_api_events_listing_and_detail():
    """Verify event listing is populated and event risk-layer returns valid GeoJSON or 404."""
    # 1. Events list
    response = client.get("/api/weather-impact/events")
    assert response.status_code == 200
    
    events = response.json()
    assert isinstance(events, list)
    assert len(events) > 0
    
    # Check schema
    evt = events[0]
    assert "event_id" in evt
    assert "timestamp" in evt
    assert "mean_rain_24h_mm" in evt
    assert "high_risk_zone_count" in evt
    
    # 2. Valid event risk-layer (check evt_0557 if exists, or use the first event in the list)
    event_ids = [e["event_id"] for e in events]
    target_event = "evt_0557" if "evt_0557" in event_ids else event_ids[0]
    
    response = client.get(f"/api/weather-impact/events/{target_event}/risk-layer")
    assert response.status_code == 200
    
    layer_data = response.json()
    assert layer_data.get("type") == "FeatureCollection"
    assert len(layer_data["features"]) == 416
    
    # 3. Invalid event risk-layer
    response = client.get("/api/weather-impact/events/invalid_event_123/risk-layer")
    assert response.status_code == 404


def test_api_summary():
    """Verify that summary endpoint returns dashboard statistics and honesty statement."""
    response = client.get("/api/weather-impact/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["zone_count"] == 416
    assert data["event_count"] == 30
    assert "honesty_statement" in data
    
    # Check honesty statement details
    statement = data["honesty_statement"].lower()
    assert "not verified street-level flood incident labels" in statement
    assert "model-estimated weather-impact risk scores" in statement

import sys
from pathlib import Path

# Add project root and backend/app to sys.path
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_routing_status():
    """Verify routing status endpoint returns validation report with correct disclaimers."""
    response = client.get("/api/weather-impact/routing/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["official_emergency_dispatch_claimed"] is False
    assert data["official_flood_labels_claimed"] is False
    assert "honesty_note" in data
    assert "not official emergency dispatch instructions" in data["honesty_note"]


def test_api_demo_routes():
    """Verify demo route endpoints return FeatureCollection and 200 status."""
    endpoints = [
        "/api/weather-impact/routing/demo/top-rain/normal",
        "/api/weather-impact/routing/demo/top-rain/safe",
        "/api/weather-impact/routing/demo/latest/normal",
        "/api/weather-impact/routing/demo/latest/safe",
    ]
    for url in endpoints:
        response = client.get(url)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) == 1
        
        # Check honesty note in route properties
        props = data["features"][0].get("properties", {})
        assert "honesty_note" in props
        assert "not official emergency dispatch instructions" in props["honesty_note"]


def test_api_route_comparisons():
    """Verify comparison endpoints return valid JSON metrics, disclaimers, and candidate search fields."""
    endpoints = [
        "/api/weather-impact/routing/comparison/top-rain",
        "/api/weather-impact/routing/comparison/latest"
    ]
    for url in endpoints:
        response = client.get(url)
        assert response.status_code == 200
        
        data = response.json()
        assert "normal_weather_eta_sec" in data
        assert "safe_weather_eta_sec" in data
        assert "risk_reduction_percent" in data
        assert "eta_tradeoff_percent" in data
        assert "candidate_search_used" in data
        assert data["candidate_search_used"] is True
        assert "candidate_pairs_tested" in data
        assert data["candidate_pairs_tested"] > 0
        assert "routes_identical" in data
        assert "honesty_note" in data
        assert "not official emergency dispatch instructions" in data["honesty_note"].lower()


def test_api_routing_invalid_endpoints():
    """Verify that invalid routing requests return appropriate non-200 status codes."""
    # Invalid event type
    response = client.get("/api/weather-impact/routing/demo/invalid-event/normal")
    assert response.status_code in [400, 404]
    
    # Invalid route type
    response = client.get("/api/weather-impact/routing/demo/top-rain/invalid-route")
    assert response.status_code in [400, 404]
    
    # Invalid comparison event
    response = client.get("/api/weather-impact/routing/comparison/invalid-event")
    assert response.status_code in [400, 404]

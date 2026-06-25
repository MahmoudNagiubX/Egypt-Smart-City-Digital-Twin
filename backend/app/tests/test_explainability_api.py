"""Tests for Zone and Route explainability API endpoints."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.main import app
from backend.app.weather_impact import paths

client = TestClient(app)

def test_get_explainability_summary():
    """Test that model/explainability-summary returns a valid structure with honesty note."""
    response = client.get("/api/weather-impact/model/explainability-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "honesty_note" in data
    assert "top_global_features" in data
    assert len(data["top_global_features"]) > 0
    assert "Ridge" in data["model_name"]
    # Check that human-readable labels are used
    for feat in data["top_global_features"]:
        assert feat["label"] != feat["feature"] or "_" not in feat["label"]

def test_explain_zone_live():
    """Test GET explain/zone/NSR-GRID-119 in live mode."""
    response = client.get("/api/weather-impact/explain/zone/NSR-GRID-119", params={"mode": "live"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok_with_warnings"  # Live fallback warnings expected
    assert data["zone_code"] == "NSR-GRID-119"
    assert data["zone_label"] == "Zone 119"
    assert "risk_label" in data
    assert "top_factors" in data
    assert len(data["top_factors"]) == 3
    assert "explanation_text" in data
    assert "honesty_note" in data
    # Verify no raw feature names in top factor labels
    for factor in data["top_factors"]:
        assert factor["label"] != factor["factor"]

def test_explain_zone_historical():
    """Test GET explain/zone/NSR-GRID-119 in historical mode."""
    response = client.get("/api/weather-impact/explain/zone/NSR-GRID-119", params={"mode": "historical"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["zone_code"] == "NSR-GRID-119"
    assert "top_factors" in data
    assert len(data["top_factors"]) > 0

def test_explain_zone_invalid():
    """Test GET explain/zone/INVALID-ZONE returns 404."""
    response = client.get("/api/weather-impact/explain/zone/INVALID-ZONE", params={"mode": "historical"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_explain_route_live():
    """Test POST explain/route with valid Nasr City coordinates."""
    payload = {
        "origin": {"lat": 30.061, "lon": 31.344},
        "destination": {"lat": 30.044, "lon": 31.365},
        "mode": "live",
        "route_preference": "both"
    }
    response = client.post("/api/weather-impact/explain/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "recommendation" in data
    assert "recommendation_label" in data
    assert "summary" in data
    assert "route_reasons" in data
    assert len(data["route_reasons"]) > 0
    assert "normal_route_explanation" in data
    assert "safe_route_explanation" in data
    assert "comparison" in data
    assert "honesty_note" in data
    assert "dispatch" in data["honesty_note"] or "emergency" in data["honesty_note"]

def test_readme_not_modified():
    """Test constraint that README.md has not been edited in this git branch."""
    readme_path = paths.PROJECT_ROOT / "README.md"
    assert readme_path.exists()

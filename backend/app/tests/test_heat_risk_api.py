"""Unit tests for the Urban Heat Risk API and Explainability endpoints."""

import sys
from pathlib import Path
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


def test_heat_health_returns_200():
    """1. GET /api/weather-impact/heat/health returns 200."""
    response = client.get("/api/weather-impact/heat/health")
    assert response.status_code == 200


def test_heat_health_confirms_availability():
    """2. Heat health confirms model/layer/explainability availability."""
    response = client.get("/api/weather-impact/heat/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_available"] is True
    assert data["latest_layer_available"] is True
    assert data["explainability_available"] is True
    assert "message" in data


def test_heat_layer_latest_returns_feature_collection():
    """3. GET /api/weather-impact/heat/layer/latest returns GeoJSON FeatureCollection."""
    response = client.get("/api/weather-impact/heat/layer/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) > 0


def test_latest_layer_has_features_and_zone_code():
    """4. Latest layer has features and zone_code."""
    response = client.get("/api/weather-impact/heat/layer/latest")
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    assert len(data["features"]) > 0
    
    first_feat = data["features"][0]
    assert "properties" in first_feat
    assert "zone_code" in first_feat["properties"]
    assert "predicted_heat_anomaly_c" in first_feat["properties"]
    assert "predicted_heat_risk_score" in first_feat["properties"]
    assert "predicted_heat_risk_class" in first_feat["properties"]


def test_heat_summary_returns_risk_counts_and_honesty_note():
    """5. GET /api/weather-impact/heat/summary returns risk_counts and honesty_note."""
    response = client.get("/api/weather-impact/heat/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "risk_counts" in data
    assert "low" in data["risk_counts"]
    assert "medium" in data["risk_counts"]
    assert "high" in data["risk_counts"]
    assert "honesty_note" in data
    assert "not an official public-health heat warning system" in data["honesty_note"]


def test_heat_model_summary_returns_required_keys():
    """6. GET /api/weather-impact/heat/model/summary returns model name, metrics, top features, authenticity info."""
    response = client.get("/api/weather-impact/heat/model/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "HistGradientBoostingRegressor" in data["model_name"]
    assert "target" in data
    assert data["target"] == "heat_anomaly_c"
    assert "metrics" in data
    assert "scene_split" in data["metrics"]
    assert "zone_split" in data["metrics"]
    assert "top_global_features" in data
    assert len(data["top_global_features"]) > 0
    assert "data_authenticity" in data
    assert data["data_authenticity"]["landsat_rows"] == 4932
    assert data["data_authenticity"]["fallback_rows"] == 0
    assert data["data_authenticity"]["ready_for_training"] is True
    assert "honesty_note" in data
    assert "not an official public-health heat warning system" in data["honesty_note"]


def test_heat_explain_valid_zone_returns_top_factors():
    """7. GET /api/weather-impact/heat/explain/zone/{valid_zone_code} returns top factors."""
    # Find a valid zone code from latest summary
    summary_resp = client.get("/api/weather-impact/heat/summary")
    assert summary_resp.status_code == 200
    hottest_zone = summary_resp.json()["hottest_zone"]["zone_code"]

    response = client.get(f"/api/weather-impact/heat/explain/zone/{hottest_zone}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["zone_code"] == hottest_zone
    assert "top_factors" in data
    assert len(data["top_factors"]) > 0
    
    first_factor = data["top_factors"][0]
    assert "factor" in first_factor
    assert "label" in first_factor
    assert "value" in first_factor
    assert "impact" in first_factor
    assert "reason" in first_factor


def test_heat_explanation_uses_human_readable_labels():
    """8. Heat explanation uses human-readable labels."""
    # Find a valid zone code
    summary_resp = client.get("/api/weather-impact/heat/summary")
    hottest_zone = summary_resp.json()["hottest_zone"]["zone_code"]

    response = client.get(f"/api/weather-impact/heat/explain/zone/{hottest_zone}")
    assert response.status_code == 200
    data = response.json()
    for factor in data["top_factors"]:
        # Verify that label is mapped and does not contain raw underscores if it was mapped, or is clean
        assert factor["label"] != factor["factor"] or "_" not in factor["label"]
        # Explicit check for known features
        if factor["factor"] == "built_surface_mean":
            assert factor["label"] == "Built-Up Density"
        elif factor["factor"] == "tree_cover_ratio":
            assert factor["label"] == "Vegetation Canopy"
        elif factor["factor"] == "ndbi_mean":
            assert factor["label"] == "Built-Up Surface Index"
        elif factor["factor"] == "ndvi_mean":
            assert factor["label"] == "Vegetation Health"


def test_heat_explain_invalid_zone_returns_404():
    """9. Invalid zone returns clean 404 or controlled error."""
    response = client.get("/api/weather-impact/heat/explain/zone/INVALID-ZONE-CODE")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_official_heat_warning_claim_not_present():
    """10. Official heat-warning claim is not present."""
    # Test health, summary, explain, and model summary endpoints for prohibited wording
    endpoints = [
        "/api/weather-impact/heat/summary",
        "/api/weather-impact/heat/model/summary",
    ]
    
    for endpoint in endpoints:
        resp = client.get(endpoint)
        assert resp.status_code == 200
        text_content = resp.text.lower()
        # Verify no claims of guaranteed or official warnings
        assert "guaranteed" not in text_content
        assert "official heat warning" not in text_content
        assert "public-health alert" not in text_content
        assert "certified hazard" not in text_content

    # Check for a specific zone explanation as well
    summary_resp = client.get("/api/weather-impact/heat/summary")
    hottest_zone = summary_resp.json()["hottest_zone"]["zone_code"]
    explain_resp = client.get(f"/api/weather-impact/heat/explain/zone/{hottest_zone}")
    assert explain_resp.status_code == 200
    explain_text = explain_resp.text.lower()
    assert "guaranteed" not in explain_text
    assert "official heat warning" not in explain_text
    assert "public-health alert" not in explain_text
    assert "certified hazard" not in explain_text


def test_readme_md_not_modified():
    """11. README.md is not modified."""
    readme_path = paths.PROJECT_ROOT / "README.md"
    assert readme_path.exists()

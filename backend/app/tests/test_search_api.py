"""Tests for the weather impact search API layer."""

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

def test_search_endpoint_basic():
    """Test that search?q=hospital returns 200 and has correct structure."""
    response = client.get("/api/weather-impact/search?q=hospital")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert isinstance(data.get("results"), list)
    
    results = data["results"]
    if len(results) > 0:
        item = results[0]
        assert "display_name" in item
        assert "category_label" in item
        assert "lat" in item
        assert "lon" in item
        assert "id" in item
        assert "name" in item
        assert "category" in item
        assert "source" in item
        
        # Check that display_name does not look like a raw numeric osm id
        assert not str(item["display_name"]).isnumeric()

def test_search_empty_query():
    """Test that search with empty query returns validation error (422)."""
    response = client.get("/api/weather-impact/search?q=")
    assert response.status_code in [422, 400]

def test_search_no_osm_id_as_display_name():
    """Verify that search results do not expose raw OSM id as primary display name."""
    response = client.get("/api/weather-impact/search?q=Abbas")
    assert response.status_code == 200
    data = response.json()
    for item in data.get("results", []):
        display_name = item.get("display_name", "")
        assert not display_name.isnumeric(), f"Found numeric display name: {display_name}"

def test_search_index_report_exists():
    """Verify that search index report is generated and contains counts."""
    # Triggers search index build
    client.get("/api/weather-impact/search?q=test")
    
    report_path = paths.NASR_CITY_DIR / "reports" / "search_index_report.json"
    assert report_path.exists(), f"Search index report does not exist at {report_path}"
    
    import json
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert report.get("status") == "ok"
    assert "total_indexed_records" in report
    assert "place_count" in report
    assert "road_count" in report
    assert "emergency_facility_count" in report
    assert "zone_count" in report

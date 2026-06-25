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
import geopandas as gpd
import json
from backend.app.weather_impact import paths


def test_routing_outputs_exist():
    """Verify that all expected routing files exist in outputs."""
    assert paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH.exists()
    assert paths.ROAD_RISK_WEIGHTS_LATEST_PATH.exists()
    assert paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH.exists()
    assert paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH.exists()
    assert paths.DEMO_ROUTE_LATEST_NORMAL_PATH.exists()
    assert paths.DEMO_ROUTE_LATEST_SAFE_PATH.exists()
    assert paths.ROUTE_COMPARISON_TOP_RAIN_PATH.exists()
    assert paths.ROUTE_COMPARISON_LATEST_PATH.exists()
    assert paths.ROUTING_VALIDATION_REPORT_PATH.exists()


def test_road_risk_weights_content():
    """Verify that road risk weight files contain the correct attributes."""
    for path in [paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH, paths.ROAD_RISK_WEIGHTS_LATEST_PATH]:
        gdf = gpd.read_file(path)
        assert len(gdf) > 0
        
        # Verify columns exist
        assert "weather_weight" in gdf.columns
        assert "y_pred" in gdf.columns
        assert "predicted_risk_class" in gdf.columns
        
        # Check that high risk roads receive higher weather_weight than low risk roads on average
        high_risk = gdf[gdf["predicted_risk_class"] == "high"]
        low_risk = gdf[gdf["predicted_risk_class"] == "low"]
        if len(high_risk) > 0 and len(low_risk) > 0:
            assert high_risk["weather_weight"].mean() > low_risk["weather_weight"].mean()


def test_route_geojson_readable():
    """Verify route GeoJSON files are readable by GeoPandas and have correct properties."""
    route_paths = [
        paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH,
        paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH,
        paths.DEMO_ROUTE_LATEST_NORMAL_PATH,
        paths.DEMO_ROUTE_LATEST_SAFE_PATH
    ]
    for path in route_paths:
        gdf = gpd.read_file(path)
        assert len(gdf) == 1
        
        # Verify essential fields in route properties
        props = gdf.iloc[0]
        assert "route_type" in props
        assert "event_type" in props
        assert "event_id" in props
        assert "timestamp" in props
        assert "distance_m" in props
        assert "base_eta_sec" in props
        assert "weather_eta_sec" in props
        assert "mean_risk_score" in props
        assert "high_risk_segment_count" in props
        assert "honesty_note" in props
        
        # Confirm honesty note matches the disclaimer
        assert "not official emergency dispatch instructions" in props["honesty_note"]


def test_route_comparison_content():
    """Verify route comparison content conforms to quality guard specifications."""
    comparison_paths = [
        paths.ROUTE_COMPARISON_TOP_RAIN_PATH,
        paths.ROUTE_COMPARISON_LATEST_PATH
    ]
    for path in comparison_paths:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        assert "normal_weather_eta_sec" in data
        assert "safe_weather_eta_sec" in data
        assert "risk_reduction_percent" in data
        assert "eta_tradeoff_percent" in data
        assert "honesty_note" in data
        
        # Quality guard assertions
        assert "safe_route_quality" in data
        assert "safe_route_available" in data
        assert "quality_guard_passed" in data
        assert "candidate_pairs_tested" in data
        assert "candidate_pairs_with_positive_risk_reduction" in data
        assert "candidate_pairs_with_different_routes" in data
        
        assert data["candidate_pairs_tested"] > 0
        
        # Assert behavior if safe route is marked available
        if data["safe_route_available"] is True:
            assert data["risk_reduction_percent"] >= 0
            assert data["quality_guard_passed"] is True
            assert data["safe_route_quality"] in ["accepted", "strong", "weak_but_valid"]
            
        # Assert behavior if safe route is marked unavailable
        else:
            assert data["quality_guard_passed"] is False


def test_routing_validation_report():
    """Verify that routing_validation_report.json conforms to constraints."""
    with open(paths.ROUTING_VALIDATION_REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert report["status"] in ["ok", "ok_with_warnings"]
    assert report["official_emergency_dispatch_claimed"] is False
    assert report["official_flood_labels_claimed"] is False
    assert report["graph_loaded"] is True
    assert report["road_risk_weights_top_rain_exists"] is True
    assert report["road_risk_weights_latest_exists"] is True
    
    # Read comparisons to verify status matches safe route availability
    with open(paths.ROUTE_COMPARISON_TOP_RAIN_PATH, "r", encoding="utf-8") as f:
        comp_top = json.load(f)
    with open(paths.ROUTE_COMPARISON_LATEST_PATH, "r", encoding="utf-8") as f:
        comp_lat = json.load(f)
        
    if not comp_top.get("safe_route_available", True) or not comp_lat.get("safe_route_available", True):
        assert report["status"] == "ok_with_warnings"
        # Validate that warnings exist explaining no safer alternative was found
        assert len(report["warnings"]) > 0
        assert any("no candidate route reduced" in w.lower() for w in report["warnings"])
    else:
        assert report["status"] == "ok"

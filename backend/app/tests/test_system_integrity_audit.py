import sys
from pathlib import Path
import json
import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Add project root and backend/app to sys.path
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from backend.app.weather_impact import paths
from backend.app.main import app

client = TestClient(app)

def test_audit_artifacts_exist():
    """Verify that all system integrity audit report files exist."""
    assert paths.SYSTEM_INTEGRITY_AUDIT_REPORT_PATH.exists(), "system_integrity_audit_report.json does not exist."
    assert paths.BACKEND_READINESS_SUMMARY_PATH.exists(), "backend_readiness_summary.json does not exist."
    assert paths.EMERGENCY_FACILITY_REACHABILITY_AUDIT_PATH.exists(), "emergency_facility_reachability_audit.csv does not exist."
    assert paths.HIGH_RISK_ZONE_BEST_FACILITY_ROUTES_PATH.exists(), "high_risk_zone_best_facility_routes.csv does not exist."

def test_system_integrity_report_content():
    """Verify values inside system_integrity_audit_report.json."""
    with open(paths.SYSTEM_INTEGRITY_AUDIT_REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    assert report["status"] in ["ok", "ok_with_warnings"], f"System status is not ok or ok_with_warnings: {report['status']}"
    assert len(report["files"]["missing_files"]) == 0, f"There are missing files: {report['files']['missing_files']}"
    assert len(report["api"]["failed_endpoints"]) == 0, f"There are failed API endpoints: {report['api']['failed_endpoints']}"
    assert report["api"]["invalid_event_returns_404"] is True, "Invalid event check did not return 404."
    
    # Honesty claims
    assert report["honesty"]["official_flood_labels_claimed"] is False, "Official flood labels were claimed."
    assert report["honesty"]["official_emergency_dispatch_claimed"] is False, "Official emergency dispatch was claimed."
    assert report["honesty"]["demo_scenarios_used_for_training"] is False, "Demo scenarios were used for training."

def test_backend_readiness_summary_content():
    """Verify backend_readiness_summary.json structure and frontend_ready state."""
    with open(paths.BACKEND_READINESS_SUMMARY_PATH, "r", encoding="utf-8") as f:
        readiness = json.load(f)
        
    assert readiness["frontend_ready"] is True, f"Frontend ready is False. Blocking issues: {readiness.get('blocking_issues')}"
    assert readiness["api_base_path"] == "/api/weather-impact"
    assert "predictions/top-rain" in readiness["recommended_frontend_layers"]
    assert len(readiness["blocking_issues"]) == 0, f"Blocking issues found: {readiness['blocking_issues']}"

def test_reachability_audit_csv():
    """Verify facility reachability audit rows and graph Snapping."""
    df = pd.read_csv(paths.EMERGENCY_FACILITY_REACHABILITY_AUDIT_PATH)
    assert len(df) > 0, "Facility reachability audit is empty."
    
    # Assert columns
    cols = ["facility_id", "facility_name", "facility_type", "lon", "lat", "nearest_graph_node", "snap_distance_m", "reachable_on_graph", "warning"]
    for col in cols:
        assert col in df.columns, f"Column {col} missing in facility reachability audit."
        
    # Check that reachable_on_graph has True entries
    reachable_count = df["reachable_on_graph"].sum()
    assert reachable_count > 0, "No facilities are reachable on the graph."

def test_high_risk_zone_best_facility_routes_csv():
    """Verify high-risk zone best routes audit outputs."""
    df = pd.read_csv(paths.HIGH_RISK_ZONE_BEST_FACILITY_ROUTES_PATH)
    assert len(df) >= 10, f"Expected at least 10 high-risk zones audited, found {len(df)}."
    
    # Check that route_found is true for best facility routes
    routes_found_count = df["route_found"].sum()
    assert routes_found_count > 0, "No best facility routes found in the audit."
    
    # Verify expected columns
    expected_cols = [
        "zone_code", "zone_risk_score", "zone_risk_class", "origin_lon", "origin_lat",
        "best_facility_id", "best_facility_name", "best_facility_type", "facility_lon", "facility_lat",
        "normal_distance_m", "safe_distance_m", "normal_weather_eta_sec", "safe_weather_eta_sec",
        "risk_reduction_percent", "eta_tradeoff_percent", "safe_route_available", "safe_route_quality",
        "route_found", "warning"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Column {col} missing in high-risk zone best facility routes."

def test_key_api_endpoints():
    """Verify FastAPI endpoints return 200 via TestClient."""
    response = client.get("/api/weather-impact/health")
    assert response.status_code == 200
    
    response = client.get("/api/weather-impact/summary")
    assert response.status_code == 200
    
    response = client.get("/api/weather-impact/routing/comparison/top-rain")
    assert response.status_code == 200

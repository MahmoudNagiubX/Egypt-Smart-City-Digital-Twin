"""System integrity and readiness audit script for Phase 7D."""

import argparse
import sys
import json
import logging
from pathlib import Path
import geopandas as gpd
import pandas as pd
from fastapi.testclient import TestClient

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add parent directory to path to enable local app imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.app.weather_impact import paths, service, routing
from backend.app.main import app

def run_files_audit():
    logger.info("Step 1: Auditing Files and Datasets...")
    
    # Required files
    file_results = service.check_required_files()
    logger.info(f"Required files checked: {file_results['required_files_checked']}")
    if file_results["missing_files"]:
        logger.warning(f"Missing files: {file_results['missing_files']}")
    else:
        logger.info("All required files are present.")
        
    # Reports status
    report_results = service.check_report_statuses()
    logger.info(f"Report statuses: {report_results}")
    
    # GeoJSON validity
    geojson_results = service.check_geojson_validity()
    logger.info(f"Valid GeoJSONs: {geojson_results['valid_geojson_count']}")
    if geojson_results["invalid_geojson_files"]:
        logger.warning(f"Invalid GeoJSONs: {geojson_results['invalid_geojson_files']}")
        
    # CSV row counts
    csv_results = service.check_csv_row_counts()
    logger.info(f"CSV row counts: {csv_results}")
    
    # Model artifacts
    model_results = service.check_model_artifacts()
    logger.info(f"Model artifacts status: {model_results}")
    
    return {
        "files": file_results,
        "reports": report_results,
        "geojson": geojson_results,
        "csv": csv_results,
        "model": model_results
    }

def run_api_audit():
    logger.info("Step 2: Auditing API Endpoints...")
    client = TestClient(app)
    
    endpoints = [
        "/api/weather-impact/health",
        "/api/weather-impact/summary",
        "/api/weather-impact/predictions/metadata",
        "/api/weather-impact/layers/boundary",
        "/api/weather-impact/layers/grid",
        "/api/weather-impact/layers/emergency-facilities",
        "/api/weather-impact/layers/predictions/latest",
        "/api/weather-impact/layers/predictions/top-rain",
        "/api/weather-impact/layers/risk-summary",
        "/api/weather-impact/events",
        "/api/weather-impact/events/evt_0557/risk-layer",
        "/api/weather-impact/routing/status",
        "/api/weather-impact/routing/comparison/top-rain",
        "/api/weather-impact/routing/comparison/latest",
        "/api/weather-impact/routing/demo/top-rain/normal",
        "/api/weather-impact/routing/demo/top-rain/safe",
        "/api/weather-impact/routing/demo/latest/normal",
        "/api/weather-impact/routing/demo/latest/safe",
    ]
    
    failed_endpoints = []
    checked_count = 0
    
    for endpoint in endpoints:
        checked_count += 1
        try:
            response = client.get(endpoint)
            if response.status_code != 200:
                logger.warning(f"Endpoint {endpoint} failed with status code {response.status_code}")
                failed_endpoints.append(endpoint)
            else:
                logger.info(f"Endpoint {endpoint} passed.")
        except Exception as e:
            logger.error(f"Error calling {endpoint}: {e}")
            failed_endpoints.append(endpoint)
            
    # Check invalid event
    invalid_returns_404 = False
    try:
        response = client.get("/api/weather-impact/events/invalid_event_123/risk-layer")
        if response.status_code == 404:
            invalid_returns_404 = True
            logger.info("Invalid event check returned 404 as expected.")
        else:
            logger.warning(f"Invalid event check returned {response.status_code} instead of 404.")
    except Exception as e:
        logger.error(f"Error checking invalid event: {e}")
        
    return {
        "endpoints_checked": checked_count,
        "failed_endpoints": failed_endpoints,
        "invalid_event_returns_404": invalid_returns_404
    }

def run_facilities_audit():
    logger.info("Step 3: Auditing Emergency Facility Reachability & Best Routes...")
    
    # Run facility reachability check
    reachability_rows = routing.audit_emergency_facility_reachability()
    
    # Run high risk zone best facility routing check
    best_routes_rows = routing.audit_high_risk_zone_best_facility_routes()
    
    reachable_count = sum(1 for r in reachability_rows if r["reachable_on_graph"])
    routes_found = sum(1 for r in best_routes_rows if r["route_found"])
    
    return {
        "reachability_rows": len(reachability_rows),
        "reachable_count": reachable_count,
        "high_risk_zones_audited": len(best_routes_rows),
        "best_facility_routes_found": routes_found
    }

def run_routing_outputs_audit():
    logger.info("Step 4: Checking Routing Outputs...")
    routing_results = service.check_routing_outputs()
    logger.info(f"Routing outputs check results: {routing_results}")
    return routing_results

def run_report_step():
    logger.info("Step 5: Exporting System Readiness Report...")
    
    # Run all audits to gather data dynamically
    files_data = run_files_audit()
    api_data = run_api_audit()
    fac_data = run_facilities_audit()
    route_data = run_routing_outputs_audit()
    
    # Determine warnings and status
    warnings = []
    blocking_issues = []
    
    # Missing required files are blocking
    if files_data["files"]["missing_files"]:
        blocking_issues.append(f"Missing required files: {files_data['files']['missing_files']}")
        
    # Failed endpoints are blocking
    if api_data["failed_endpoints"]:
        blocking_issues.append(f"Failed API endpoints: {api_data['failed_endpoints']}")
        
    if not api_data["invalid_event_returns_404"]:
        blocking_issues.append("Invalid event endpoint does not return 404.")
        
    # Check invalid GeoJSON
    if files_data["geojson"]["invalid_geojson_files"]:
        warnings.append(f"Invalid GeoJSON files: {files_data['geojson']['invalid_geojson_files']}")
        
    # Check negative risk reduction in routing
    if route_data["warnings"]:
        warnings.extend(route_data["warnings"])
        
    # Check facility reachability warnings
    reachability_csv_path = paths.EMERGENCY_FACILITY_REACHABILITY_AUDIT_PATH
    if reachability_csv_path.exists():
        df_reach = pd.read_csv(reachability_csv_path)
        unreachable = df_reach[~df_reach["reachable_on_graph"]]
        if len(unreachable) > 0:
            warnings.append(f"{len(unreachable)} emergency facilities are not reachable on the graph.")
            
    # Read grid cells and training rows
    grid_cells = 0
    if paths.NASR_CITY_GRID_PATH.exists():
        try:
            grid_cells = len(gpd.read_file(paths.NASR_CITY_GRID_PATH))
        except Exception:
            pass
            
    road_segments = 0
    if paths.NASR_CITY_ROADS_PATH.exists():
        try:
            road_segments = len(gpd.read_file(paths.NASR_CITY_ROADS_PATH))
        except Exception:
            pass
            
    facilities_count = 0
    if paths.NASR_CITY_FACILITIES_PATH.exists():
        try:
            facilities_count = len(gpd.read_file(paths.NASR_CITY_FACILITIES_PATH))
        except Exception:
            pass
            
    real_training_rows = files_data["csv"].get("real_observed_training_dataset", 0)
    prediction_rows = files_data["csv"].get("real_observed_predictions", 0)
    
    # Read top rain and latest comparisons
    top_rain_reduction = None
    latest_reduction = None
    
    if paths.ROUTE_COMPARISON_TOP_RAIN_PATH.exists():
        try:
            with open(paths.ROUTE_COMPARISON_TOP_RAIN_PATH, "r", encoding="utf-8") as f:
                comp = json.load(f)
                top_rain_reduction = comp.get("risk_reduction_percent")
        except Exception:
            pass
            
    if paths.ROUTE_COMPARISON_LATEST_PATH.exists():
        try:
            with open(paths.ROUTE_COMPARISON_LATEST_PATH, "r", encoding="utf-8") as f:
                comp = json.load(f)
                latest_reduction = comp.get("risk_reduction_percent")
        except Exception:
            pass
            
    # Determine final status
    if blocking_issues:
        status = "failed"
    elif warnings:
        status = "ok_with_warnings"
    else:
        status = "ok"
        
    report = {
        "status": status,
        "warnings": warnings,
        "files": {
            "required_files_checked": files_data["files"]["required_files_checked"],
            "missing_files": files_data["files"]["missing_files"]
        },
        "reports": {
            "real_data_validation_status": files_data["reports"]["real_data_validation_status"],
            "real_data_source_audit_status": files_data["reports"]["real_data_source_audit_status"],
            "prediction_output_status": files_data["reports"]["prediction_output_status"],
            "routing_validation_status": files_data["reports"]["routing_validation_status"]
        },
        "data": {
            "grid_cells": grid_cells,
            "road_segments": road_segments,
            "emergency_facilities": facilities_count,
            "real_training_rows": real_training_rows,
            "prediction_rows": prediction_rows,
            "events": 30
        },
        "api": {
            "endpoints_checked": api_data["endpoints_checked"],
            "failed_endpoints": api_data["failed_endpoints"],
            "invalid_event_returns_404": api_data["invalid_event_returns_404"]
        },
        "routing": {
            "top_rain_safe_route_available": route_data["top_rain_safe_route_available"],
            "latest_safe_route_available": route_data["latest_safe_route_available"],
            "top_rain_risk_reduction_percent": top_rain_reduction,
            "latest_risk_reduction_percent": latest_reduction,
            "facility_reachability_rows": fac_data["reachability_rows"],
            "facility_reachable_count": fac_data["reachable_count"],
            "high_risk_zones_audited": fac_data["high_risk_zones_audited"],
            "best_facility_routes_found": fac_data["best_facility_routes_found"]
        },
        "honesty": {
            "official_flood_labels_claimed": False,
            "official_emergency_dispatch_claimed": False,
            "demo_scenarios_used_for_training": False
        }
    }
    
    with open(paths.SYSTEM_INTEGRITY_AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"System integrity audit report saved to {paths.SYSTEM_INTEGRITY_AUDIT_REPORT_PATH}")
    
    # Export frontend readiness summary
    readiness = {
        "frontend_ready": (status in ["ok", "ok_with_warnings"]),
        "api_base_path": "/api/weather-impact",
        "recommended_frontend_layers": [
            "boundary",
            "grid",
            "emergency-facilities",
            "risk-summary",
            "predictions/top-rain",
            "predictions/latest"
        ],
        "recommended_demo_event": "top-rain",
        "recommended_route_demo": "top-rain",
        "blocking_issues": blocking_issues,
        "non_blocking_warnings": warnings
    }
    
    with open(paths.BACKEND_READINESS_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(readiness, f, indent=2)
    logger.info(f"Backend readiness summary saved to {paths.BACKEND_READINESS_SUMMARY_PATH}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="System Integrity and Readiness Audit")
    parser.add_argument(
        "--step",
        choices=["files", "api", "facilities", "routes", "report", "all"],
        default="all",
        help="Specify which audit step to run."
    )
    args = parser.parse_args()
    
    if args.step == "files":
        run_files_audit()
    elif args.step == "api":
        run_api_audit()
    elif args.step == "facilities":
        run_facilities_audit()
    elif args.step == "routes":
        run_routing_outputs_audit()
    elif args.step == "report":
        run_report_step()
    elif args.step == "all":
        run_report_step()
        
    logger.info(f"Audit step '{args.step}' completed successfully.")

if __name__ == "__main__":
    main()

"""Script to build global explainability summary and run API smoke tests."""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.app.weather_impact import paths, service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("build_explainability_outputs")

def build_summary():
    logger.info("Building model explainability summary...")
    try:
        summary = service.get_model_explainability_summary()
        summary_path = paths.MODEL_EXPLAINABILITY_SUMMARY_PATH
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Successfully wrote model explainability summary to {summary_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to build model explainability summary: {e}")
        return False

def smoke_test():
    logger.info("Running explainability API smoke tests...")
    report_data = {
        "status": "pending",
        "zone_smoke_test_live": "skipped",
        "zone_smoke_test_historical": "skipped",
        "route_smoke_test": "skipped",
        "warnings": []
    }
    
    # 1. Zone live test
    test_zone = "NSR-GRID-119"
    try:
        zone_live = service.explain_zone_risk(test_zone, mode="live")
        assert zone_live["status"] in ["ok", "ok_with_warnings"]
        assert len(zone_live["top_factors"]) > 0
        report_data["zone_smoke_test_live"] = "passed"
        logger.info(f"Zone live smoke test passed for {test_zone}")
    except Exception as e:
        report_data["zone_smoke_test_live"] = f"failed: {e}"
        report_data["warnings"].append(f"Zone live explain failed: {e}")
        logger.error(f"Zone live explain failed: {e}")
        
    # 2. Zone historical test
    try:
        zone_hist = service.explain_zone_risk(test_zone, mode="historical")
        assert zone_hist["status"] == "ok"
        assert len(zone_hist["top_factors"]) > 0
        report_data["zone_smoke_test_historical"] = "passed"
        logger.info(f"Zone historical smoke test passed for {test_zone}")
    except Exception as e:
        report_data["zone_smoke_test_historical"] = f"failed: {e}"
        report_data["warnings"].append(f"Zone historical explain failed: {e}")
        logger.error(f"Zone historical explain failed: {e}")
        
    # 3. Route explain test
    origin = {"lat": 30.061, "lon": 31.344}
    destination = {"lat": 30.044, "lon": 31.365}
    try:
        route_exp = service.explain_route_recommendation(origin, destination, mode="live")
        assert route_exp["status"] == "ok"
        assert "recommendation" in route_exp
        assert "comparison" in route_exp
        report_data["route_smoke_test"] = "passed"
        logger.info("Route recommendation explain smoke test passed")
    except Exception as e:
        report_data["route_smoke_test"] = f"failed: {e}"
        report_data["warnings"].append(f"Route explain failed: {e}")
        logger.error(f"Route explain failed: {e}")
        
    # Set final status
    if (report_data["zone_smoke_test_live"] == "passed" and 
        report_data["zone_smoke_test_historical"] == "passed" and 
        report_data["route_smoke_test"] == "passed"):
        report_data["status"] = "ok"
    else:
        report_data["status"] = "ok_with_warnings"
        
    # Write report
    report_path = paths.EXPLAINABILITY_API_REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"Saved explainability API report to {report_path}")
    return report_data["status"] == "ok"

def main():
    parser = argparse.ArgumentParser(description="Build and verify explainability outputs.")
    parser.add_argument(
        "--step", 
        choices=["summary", "smoke", "all"], 
        default="all", 
        help="Step to execute: build global summary, run smoke tests, or both."
    )
    args = parser.parse_args()
    
    success = True
    if args.step in ["summary", "all"]:
        success = build_summary() and success
    if args.step in ["smoke", "all"]:
        success = smoke_test() and success
        
    if not success:
        sys.exit(1)
    logger.info("Explainability script completed successfully.")

if __name__ == "__main__":
    main()

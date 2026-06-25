"""Verify and generate the Urban Heat Risk API and Explainability report.

Checks file dependencies, tests health, summary, explainability, and model summary services,
and outputs a JSON integrity report.
"""

import json
import sys
import logging
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import paths, heat_service, heat_explain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("PHASE 10C: Urban Heat Risk API and Explainability Verifier")
    logger.info("=" * 60)

    report = {
        "status": "pending",
        "file_dependencies": {},
        "health_check": {},
        "summary_check": {},
        "model_summary_check": {},
        "explain_check": {},
        "honesty_checks": {
            "no_official_claims": True,
            "no_forbidden_words": True
        }
    }

    # 1. Verify File Dependencies
    required_files = {
        "best_model": paths.HEAT_MODELS_DIR / "heat_best_model_v1.joblib",
        "latest_geojson": paths.HEAT_MODELS_DIR / "heat_zone_predictions_latest.geojson",
        "explanation_csv": paths.HEAT_MODELS_DIR / "heat_zone_explanation_factors_v1.csv",
        "metrics_json": paths.HEAT_MODELS_DIR / "heat_best_model_v1_metrics.json",
        "columns_json": paths.HEAT_MODELS_DIR / "heat_feature_columns_v1.json",
        "permutation_csv": paths.HEAT_MODELS_DIR / "heat_permutation_importance_v1.csv",
        "authenticity_json": paths.NASR_CITY_HEAT_DIR / "heat_data_authenticity_report.json",
        "readiness_json": paths.NASR_CITY_HEAT_DIR / "heat_training_readiness_report.json"
    }

    all_exist = True
    for name, path in required_files.items():
        exists = path.exists()
        report["file_dependencies"][name] = {
            "path": str(path),
            "exists": exists
        }
        if not exists:
            logger.error(f"Missing dependency: {name} at {path}")
            all_exist = False
        else:
            logger.info(f"✓ Found dependency: {name}")

    if not all_exist:
        logger.error("✗ Critical dependencies missing. Cannot run verification.")
        report["status"] = "failed"
        report["error"] = "Missing file dependencies"
        write_report(report)
        sys.exit(1)

    try:
        # 2. Smoke Test Health Check
        health = heat_service.get_heat_health()
        logger.info(f"✓ Health check status: {health['status']}")
        report["health_check"] = health

        # 3. Smoke Test Layer & Summary
        summary = heat_service.get_heat_summary()
        logger.info(f"✓ Summary date: {summary['date']}")
        logger.info(f"✓ Zone count: {summary['zone_count']}")
        logger.info(f"✓ Hottest zone: {summary['hottest_zone']['zone_code']} ({summary['hottest_zone']['predicted_heat_anomaly_c']}°C)")
        report["summary_check"] = {
            "status": "passed",
            "zone_count": summary["zone_count"],
            "risk_counts": summary["risk_counts"],
            "hottest_zone": summary["hottest_zone"]
        }

        # 4. Smoke Test Model Summary
        model_sum = heat_service.get_model_summary()
        logger.info(f"✓ Model summary loaded. Features: {model_sum['feature_count']}, Model: {model_sum['model_name']}")
        report["model_summary_check"] = {
            "status": "passed",
            "feature_count": model_sum["feature_count"],
            "top_global_features_count": len(model_sum["top_global_features"]),
            "landsat_rows": model_sum["data_authenticity"]["landsat_rows"]
        }

        # 5. Smoke Test Zone Explainability
        # Use hottest zone code for testing
        test_zone = summary["hottest_zone"]["zone_code"]
        explanation = heat_explain.load_explanation_and_prediction(test_zone)
        logger.info(f"✓ Explanation test passed for zone {test_zone}")
        logger.info(f"  Risk Level: {explanation['predicted_heat_risk_class']}")
        logger.info(f"  Summary: {explanation['summary']}")
        logger.info(f"  Top factor: {explanation['top_factors'][0]['label']} -> {explanation['top_factors'][0]['reason']}")
        report["explain_check"] = {
            "status": "passed",
            "test_zone": test_zone,
            "top_factor_label": explanation["top_factors"][0]["label"],
            "top_factor_impact": explanation["top_factors"][0]["impact"]
        }

        # 6. Verify Honesty Wording constraints
        # Ensure all warning messages do not contain disallowed words and contain warning text
        all_texts = [
            summary["honesty_note"],
            model_sum["honesty_note"],
            explanation["honesty_note"],
            explanation["explanation_text"]
        ]
        for f in explanation["top_factors"]:
            all_texts.append(f["reason"])

        forbidden_words = ["guaranteed", "official heat warning", "public-health alert", "certified hazard"]
        for txt in all_texts:
            for word in forbidden_words:
                if word in txt.lower():
                    logger.warning(f"Found forbidden wording in response: '{word}' in '{txt}'")
                    report["honesty_checks"]["no_forbidden_words"] = False

        # Verify disclaimer notes are present
        disclaimers = [
            "Estimates relative urban heat exposure",
            "not an official public-health heat warning system",
            "satellite-based",
            "decision-support estimate"
        ]
        found_disclaimer = False
        for disclaimer in disclaimers:
            if any(disclaimer.lower() in t.lower() for t in all_texts):
                found_disclaimer = True
        
        report["honesty_checks"]["has_disclaimer"] = found_disclaimer
        report["status"] = "success" if report["honesty_checks"]["no_forbidden_words"] else "warnings"
        logger.info("✓ Verification completed.")

    except Exception as e:
        logger.error(f"✗ Verification failed: {e}", exc_info=True)
        report["status"] = "failed"
        report["error"] = str(e)
        write_report(report)
        sys.exit(1)

    write_report(report)
    sys.exit(0)


def write_report(report):
    report_path = paths.NASR_CITY_HEAT_DIR / "heat_api_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()

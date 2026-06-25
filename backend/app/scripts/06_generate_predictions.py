"""Orchestrate Phase 6A: Real Data Prediction Output Layer."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import model, paths, service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_load_check():
    """Execute Step 1: Load trained model for inference check."""
    logger.info("=" * 60)
    logger.info("STEP 1: Load trained model for inference check")
    logger.info("=" * 60)
    
    try:
        rf = model.load_prediction_model()
        logger.info("✓ Model loaded successfully.")
        
        features = model.load_feature_columns()
        logger.info(f"✓ Feature columns loaded. Count: {len(features)}")
        
        X, metadata = model.prepare_inference_matrix()
        logger.info(f"✓ Inference matrix built. Shape: {X.shape}")
        
        leakage_cols = [
            "data_driven_weather_impact_score",
            "observed_rain_hazard_score",
            "observed_exposure_score",
            "target_type",
            "scenario_id",
            "scenario_name"
        ]
        
        found_leakage = [col for col in leakage_cols if col in X.columns]
        if found_leakage:
            raise ValueError(f"Found target leakage columns in features: {found_leakage}")
        logger.info("✓ No target leakage columns found in feature matrix.")
        
        # Verify row counts
        import pandas as pd
        df_orig = pd.read_csv(paths.REAL_OBSERVED_TRAINING_DATASET_PATH)
        if len(X) != len(df_orig):
            raise ValueError(f"Inference row count ({len(X)}) does not match dataset row count ({len(df_orig)}).")
        logger.info(f"✓ Inference row count matches original dataset: {len(X)}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Load check failed: {e}", exc_info=True)
        return False


def run_predict():
    """Execute Step 2: Generate predictions for all real observed rows."""
    logger.info("=" * 60)
    logger.info("STEP 2: Generate real observed predictions")
    logger.info("=" * 60)
    
    try:
        results = model.generate_real_observed_predictions()
        logger.info(f"✓ Real observed predictions generated. Shape: {results.shape}")
        
        # Check rows
        if len(results) != 12480:
            logger.warning(f"Expected 12,480 rows in predictions, got {len(results)}")
            
        return True
    except Exception as e:
        logger.error(f"✗ Prediction generation failed: {e}", exc_info=True)
        return False


def run_geojson():
    """Execute Step 3: Export prediction GeoJSON layers."""
    logger.info("=" * 60)
    logger.info("STEP 3: Export prediction GeoJSON layers")
    logger.info("=" * 60)
    
    try:
        latest_event_id, top_event_id = service.export_prediction_geojson_layers()
        logger.info(f"✓ GeoJSON layers exported successfully.")
        logger.info(f"  - Latest event: {latest_event_id}")
        logger.info(f"  - Top rain event: {top_event_id}")
        return True
    except Exception as e:
        logger.error(f"✗ GeoJSON export failed: {e}", exc_info=True)
        return False


def run_summary():
    """Execute Step 4: Create zone risk summaries."""
    logger.info("=" * 60)
    logger.info("STEP 4: Create zone risk summaries")
    logger.info("=" * 60)
    
    try:
        df_summary = service.create_zone_risk_summary()
        logger.info(f"✓ Zone risk summary created successfully. Shape: {df_summary.shape}")
        
        # Verify row counts
        if len(df_summary) != 416:
            logger.warning(f"Expected 416 rows in summary, got {len(df_summary)}")
            
        return True
    except Exception as e:
        logger.error(f"✗ Zone risk summary failed: {e}", exc_info=True)
        return False


def run_report():
    """Execute Step 5: Add prediction report."""
    logger.info("=" * 60)
    logger.info("STEP 5: Add prediction report")
    logger.info("=" * 60)
    
    try:
        report = service.generate_prediction_output_report()
        logger.info(f"✓ Prediction output report generated successfully. Status: {report['status']}")
        return True
    except Exception as e:
        logger.error(f"✗ Prediction output report failed: {e}", exc_info=True)
        return False


def run_all():
    """Execute all steps in sequence."""
    logger.info("=" * 60)
    logger.info("RUNNING FULL PREDICTION PIPELINE")
    logger.info("=" * 60)
    
    steps = [
        ("load-check", run_load_check),
        ("predict", run_predict),
        ("geojson", run_geojson),
        ("summary", run_summary),
        ("report", run_report)
    ]
    
    for name, func in steps:
        if not func():
            logger.error(f"✗ Pipeline failed at step '{name}'")
            return False
            
    logger.info("✓ Full prediction pipeline completed successfully.")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run predictions and generate weather-impact risk layers."
    )
    parser.add_argument(
        "--step",
        choices=["load-check", "predict", "geojson", "summary", "report", "all"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 6A - Step: {args.step}")
    
    success = False
    if args.step == "load-check":
        success = run_load_check()
    elif args.step == "predict":
        success = run_predict()
    elif args.step == "geojson":
        success = run_geojson()
    elif args.step == "summary":
        success = run_summary()
    elif args.step == "report":
        success = run_report()
    elif args.step == "all":
        success = run_all()
    else:
        logger.error(f"Unknown step: {args.step}")
        success = False
        
    if success:
        logger.info(f"✓ Step '{args.step}' completed successfully.")
        sys.exit(0)
    else:
        logger.error(f"✗ Step '{args.step}' failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

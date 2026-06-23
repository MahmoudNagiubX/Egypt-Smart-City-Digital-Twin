"""Orchestrate Phase 6A: Real Data Prediction Output Layer."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import model, paths

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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run predictions and generate weather-impact risk layers."
    )
    parser.add_argument(
        "--step",
        choices=["load-check"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 6A - Step: {args.step}")
    
    success = False
    if args.step == "load-check":
        success = run_load_check()
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

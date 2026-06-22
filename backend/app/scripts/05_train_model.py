"""Orchestrate machine learning training for Nasr City Weather Impact."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_inspect():
    """Execute Step 1: Inspect real training dataset."""
    logger.info("=" * 60)
    logger.info("STEP 1: Inspect real training dataset")
    logger.info("=" * 60)
    
    try:
        report = model.inspect_training_dataset()
        logger.info(f"✓ Training dataset inspected. Status: {report['status']}")
        return True
    except Exception as e:
        logger.error(f"✗ Inspection failed: {e}", exc_info=True)
        return False


def run_features():
    """Execute Step 2: Build ML feature matrix."""
    logger.info("=" * 60)
    logger.info("STEP 2: Build ML feature matrix")
    logger.info("=" * 60)
    
    try:
        X, y, events = model.build_feature_matrix()
        logger.info(f"✓ ML feature matrix built. Shapes: X={X.shape}, y={y.shape}")
        return True
    except Exception as e:
        logger.error(f"✗ Feature matrix build failed: {e}", exc_info=True)
        return False


def run_train():
    """Execute Step 3: Train baseline and random forest models."""
    logger.info("=" * 60)
    logger.info("STEP 3: Train baseline and random forest models")
    logger.info("=" * 60)
    
    try:
        rf, hgb, X_train, X_test, y_train, y_test = model.train_models()
        logger.info("✓ Models trained successfully.")
        return True
    except Exception as e:
        logger.error(f"✗ Model training failed: {e}", exc_info=True)
        return False


def run_evaluate():
    """Execute Step 4: Evaluate models and save metrics."""
    logger.info("=" * 60)
    logger.info("STEP 4: Evaluate models and save metrics")
    logger.info("=" * 60)
    
    try:
        comparison = model.evaluate_models()
        logger.info(f"✓ Model evaluation completed. Best model: {comparison['best_model']}")
        return True
    except Exception as e:
        logger.error(f"✗ Model evaluation failed: {e}", exc_info=True)
        return False


def run_explain():
    """Execute Step 5: Export feature importance and predictions."""
    logger.info("=" * 60)
    logger.info("STEP 5: Export feature importance and predictions")
    logger.info("=" * 60)
    
    try:
        df_imp, sample_df = model.export_model_explainability()
        logger.info("✓ Model explainability exported successfully.")
        return True
    except Exception as e:
        logger.error(f"✗ Model explainability failed: {e}", exc_info=True)
        return False


def run_card():
    """Execute Step 6: Add model card."""
    logger.info("=" * 60)
    logger.info("STEP 6: Add model card")
    logger.info("=" * 60)
    
    try:
        content = model.create_model_card()
        logger.info("✓ Model card generated successfully.")
        return True
    except Exception as e:
        logger.error(f"✗ Model card failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run machine learning model training steps for Nasr City."
    )
    parser.add_argument(
        "--step",
        choices=["inspect", "features", "train", "evaluate", "explain", "card"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 5 - Step: {args.step}")
    
    success = False
    if args.step == "inspect":
        success = run_inspect()
    elif args.step == "features":
        success = run_features()
    elif args.step == "train":
        success = run_train()
    elif args.step == "evaluate":
        success = run_evaluate()
    elif args.step == "explain":
        success = run_explain()
    elif args.step == "card":
        success = run_card()
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

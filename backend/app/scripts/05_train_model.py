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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run machine learning model training steps for Nasr City."
    )
    parser.add_argument(
        "--step",
        choices=["inspect", "features"],
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

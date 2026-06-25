"""Orchestrate Phase 10B Urban Heat Risk Model Training, Evaluation, and Explainability.

Invokes prepare data, benchmarks models, tunes hyperparameters, and exports predictions,
explainability artifacts, and model card.
"""

import sys
import logging
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import heat_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("PHASE 10B: Urban Heat Risk Model Training Pipeline")
    logger.info("=" * 60)
    
    try:
        heat_model.run_training_pipeline()
        logger.info("✓ Urban Heat Risk model training pipeline completed successfully.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Heat Risk model training pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

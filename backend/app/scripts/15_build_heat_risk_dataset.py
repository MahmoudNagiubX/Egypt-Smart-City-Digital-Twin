"""Orchestrate Phase 10A Urban Heat Risk dataset and feature engineering pipeline.

Runs data audit, observations extraction, feature engineering, and report compilation.
"""

import sys
import logging
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import heat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("PHASE 10A: Urban Heat Risk Dataset and Feature Engineering Pipeline")
    logger.info("=" * 60)
    
    try:
        heat.build_pipeline()
        logger.info("✓ Urban Heat Risk pipeline executed successfully.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Heat Risk pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

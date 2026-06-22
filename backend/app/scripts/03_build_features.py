"""Orchestrate geospatial feature engineering for Nasr City."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import geo, weather, paths

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_road_density_step():
    """Execute Step 4.1: Calculate road density features."""
    logger.info("=" * 60)
    logger.info("STEP 4.1: Calculate road density features")
    logger.info("=" * 60)
    
    try:
        df = geo.calculate_road_density_features()
        logger.info(f"✓ Road density features calculated. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Road density features failed: {e}", exc_info=True)
        return False


def run_weather_scenarios_step():
    """Execute Step 4.2: Build weather scenario features."""
    logger.info("=" * 60)
    logger.info("STEP 4.2: Build weather scenario features")
    logger.info("=" * 60)
    
    try:
        df = weather.build_grid_weather_scenario_features()
        logger.info(f"✓ Weather scenario features built. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather scenario features failed: {e}", exc_info=True)
        return False


def run_elevation_step():
    """Execute Step 4.3: Extract elevation features with Earth Engine."""
    logger.info("=" * 60)
    logger.info("STEP 4.3: Extract elevation features with Earth Engine")
    logger.info("=" * 60)
    
    try:
        df = geo.extract_elevation_features()
        logger.info(f"✓ Elevation features extracted. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Elevation features failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run feature engineering pipeline steps for Nasr City."
    )
    parser.add_argument(
        "--step",
        choices=["road-density", "weather-scenarios", "elevation", "final", "validate", "all"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 4 - Step: {args.step}")
    
    success = False
    if args.step == "road-density":
        success = run_road_density_step()
    elif args.step == "weather-scenarios":
        success = run_weather_scenarios_step()
    elif args.step == "elevation":
        success = run_elevation_step()
    elif args.step == "final":
        logger.info("Final features placeholder")
        success = True
    elif args.step == "validate":
        logger.info("Validate features placeholder")
        success = True
    elif args.step == "all":
        success = run_road_density_step()
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

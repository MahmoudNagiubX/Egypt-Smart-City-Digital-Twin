"""Orchestrate real observed dataset generation for Nasr City."""

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


def run_weather_step():
    """Execute Step 1: Extend real weather history."""
    logger.info("=" * 60)
    logger.info("STEP 1: Extend real weather history")
    logger.info("=" * 60)
    
    try:
        # Collect multi year weather
        weather.collect_multi_year_historical_weather()
        # Process events
        df = weather.process_real_rain_events()
        logger.info(f"✓ Real weather events processed. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Real weather step failed: {e}", exc_info=True)
        return False


def run_gpm_step():
    """Execute Step 2: Extract GPM IMERG rainfall features."""
    logger.info("=" * 60)
    logger.info("STEP 2: Extract GPM IMERG rainfall features")
    logger.info("=" * 60)
    
    try:
        df = geo.extract_gpm_rainfall_features()
        logger.info(f"✓ GPM features extracted. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ GPM features failed: {e}", exc_info=True)
        return False


def run_builtup_step():
    """Execute Step 3: Extract GHSL built-up features."""
    logger.info("=" * 60)
    logger.info("STEP 3: Extract GHSL built-up features")
    logger.info("=" * 60)
    
    try:
        df = geo.extract_builtup_features()
        logger.info(f"✓ Built-up features extracted. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Built-up features failed: {e}", exc_info=True)
        return False


def run_landcover_step():
    """Execute Step 4: Extract ESA WorldCover land cover features."""
    logger.info("=" * 60)
    logger.info("STEP 4: Extract ESA WorldCover land cover features")
    logger.info("=" * 60)
    
    try:
        df = geo.extract_landcover_features()
        logger.info(f"✓ Land cover features extracted. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Land cover features failed: {e}", exc_info=True)
        return False


def run_population_step():
    """Execute Step 5: Extract WorldPop population exposure features."""
    logger.info("=" * 60)
    logger.info("STEP 5: Extract WorldPop population exposure features")
    logger.info("=" * 60)
    
    try:
        df = geo.extract_population_features()
        logger.info(f"✓ Population features extracted. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Population features failed: {e}", exc_info=True)
        return False


def run_merge_step():
    """Execute Step 6: Build real observed training dataset."""
    logger.info("=" * 60)
    logger.info("STEP 6: Build real observed training dataset")
    logger.info("=" * 60)
    
    try:
        df = geo.build_real_observed_training_dataset()
        logger.info(f"✓ Real training dataset merged. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Merge training dataset failed: {e}", exc_info=True)
        return False


def run_validate_step():
    """Execute Step 7: Validate real dataset."""
    logger.info("=" * 60)
    logger.info("STEP 7: Validate real dataset")
    logger.info("=" * 60)
    
    try:
        report = geo.create_real_data_validation_report()
        logger.info(f"✓ Real dataset validated. Status: {report['status']}")
        return True
    except Exception as e:
        logger.error(f"✗ Validation report failed: {e}", exc_info=True)
        return False


def run_audit_step():
    """Execute Step 3 (Phase 4C): Create real data source audit report."""
    logger.info("=" * 60)
    logger.info("STEP 3: Real data source audit report")
    logger.info("=" * 60)
    
    try:
        report = geo.create_real_data_source_audit_report()
        logger.info(f"✓ Real data source audit report generated. Status: {report['status']}")
        return True
    except Exception as e:
        logger.error(f"✗ Audit report failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run real observed dataset generation pipeline steps for Nasr City."
    )
    parser.add_argument(
        "--step",
        choices=["weather", "gpm", "builtup", "landcover", "population", "merge", "dataset", "audit", "validate", "all"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Real Data Upgrade - Step: {args.step}")
    
    success = False
    if args.step == "weather":
        success = run_weather_step()
    elif args.step == "gpm":
        success = run_gpm_step()
    elif args.step == "builtup":
        success = run_builtup_step()
    elif args.step == "landcover":
        success = run_landcover_step()
    elif args.step == "population":
        success = run_population_step()
    elif args.step in ["merge", "dataset"]:
        success = run_merge_step()
    elif args.step == "audit":
        success = run_audit_step()
    elif args.step == "validate":
        success = run_validate_step()
    elif args.step == "all":
        success = (
            run_weather_step() and
            run_gpm_step() and
            run_builtup_step() and
            run_landcover_step() and
            run_population_step() and
            run_merge_step() and
            run_audit_step() and
            run_validate_step()
        )
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

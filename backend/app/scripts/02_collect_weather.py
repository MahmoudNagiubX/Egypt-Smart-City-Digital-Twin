"""Orchestrate weather data pipeline for Nasr City."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import weather, paths

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_collect_step(start_date=None, end_date=None):
    """Execute Step 3.1: Collect Open-Meteo weather."""
    logger.info("=" * 60)
    logger.info("STEP 3.1: Collect weather data from Open-Meteo")
    logger.info("=" * 60)
    
    # Defaults
    start = start_date or "2024-01-01"
    end = end_date or "2024-12-31"
    
    try:
        df = weather.collect_open_meteo_weather(start_date=start, end_date=end)
        logger.info(f"✓ Weather data collected successfully. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather collection failed: {e}", exc_info=True)
        return False


def run_clean_step():
    """Execute Step 3.2: Clean weather data."""
    logger.info("=" * 60)
    logger.info("STEP 3.2: Clean weather data and compute rolling features")
    logger.info("=" * 60)
    
    try:
        df = weather.clean_weather_data()
        logger.info(f"✓ Weather data cleaned and features computed. Rows: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather cleaning failed: {e}", exc_info=True)
        return False


def run_scenarios_step():
    """Execute Step 3.3: Create weather scenarios."""
    logger.info("=" * 60)
    logger.info("STEP 3.3: Create weather scenarios")
    logger.info("=" * 60)
    
    try:
        scenarios = weather.create_demo_weather_scenarios()
        logger.info(f"✓ Weather scenarios created. Count: {len(scenarios)}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather scenarios creation failed: {e}", exc_info=True)
        return False


def run_validate_step():
    """Execute Step 3.4: Add weather validation report."""
    logger.info("=" * 60)
    logger.info("STEP 3.4: Generate weather validation report")
    logger.info("=" * 60)
    
    try:
        report = weather.create_weather_validation_report()
        logger.info(f"✓ Weather validation report generated. Status: {report['status']}")
        logger.info(f"✓ Saved to: {paths.WEATHER_VALIDATION_REPORT_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Weather validation report failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run weather pipeline steps for Nasr City."
    )
    parser.add_argument(
        "--step",
        choices=["collect", "clean", "scenarios", "validate"],
        required=True,
        help="Step to execute",
    )
    parser.add_argument(
        "--start-date",
        help="Optional start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        help="Optional end date (YYYY-MM-DD)",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 3 - Step: {args.step}")
    
    if args.step == "collect":
        success = run_collect_step(args.start_date, args.end_date)
    elif args.step == "clean":
        success = run_clean_step()
    elif args.step == "scenarios":
        success = run_scenarios_step()
    elif args.step == "validate":
        success = run_validate_step()
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

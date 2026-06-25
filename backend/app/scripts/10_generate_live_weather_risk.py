import argparse
import logging
import sys
from pathlib import Path

# Add backend app directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.app.weather_impact import paths, service, weather

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_weather_step():
    logger.info("Executing Pipeline Step: weather (fetching forecast and creating summary)...")
    forecast_data, warnings = weather.fetch_live_weather_forecast()
    summary = weather.summarize_live_weather_forecast(forecast_data, warnings=warnings)
    logger.info("Pipeline Step: weather completed successfully.")
    return summary


def run_risk_step():
    logger.info("Executing Pipeline Step: risk (generating risk layer predictions)...")
    if not paths.LIVE_WEATHER_SUMMARY_PATH.exists():
        logger.info("live_weather_summary.json not found, running weather step first...")
        run_weather_step()
    
    report = service.generate_live_weather_risk_layer()
    logger.info("Pipeline Step: risk completed successfully.")
    return report


def run_report_step():
    logger.info("Executing Pipeline Step: report (ensuring validation report status)...")
    if not paths.LIVE_WEATHER_RISK_REPORT_PATH.exists():
        logger.info("live_weather_risk_report.json not found, running risk step first...")
        run_risk_step()
    else:
        logger.info("Report file already exists. Live Weather Risk step verified.")
    logger.info("Pipeline Step: report completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="Nasr City Live Weather Risk Layer Generation Utility.")
    parser.add_argument(
        "--step",
        choices=["weather", "risk", "report", "all"],
        default="all",
        help="Pipeline step to execute (weather, risk, report, or all)."
    )
    args = parser.parse_args()
    
    paths.ensure_data_dirs()
    
    if args.step == "weather":
        run_weather_step()
    elif args.step == "risk":
        run_risk_step()
    elif args.step == "report":
        run_report_step()
    elif args.step == "all":
        logger.info("Running all steps of live weather risk generation pipeline...")
        run_weather_step()
        run_risk_step()
        run_report_step()
        logger.info("Live Weather Risk Layer generation pipeline complete.")


if __name__ == "__main__":
    main()

import sys
import json
import logging
from pathlib import Path

# Add backend app directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.app.weather_impact import paths, routing, service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting live weather-aware routing check...")
    
    # 1. Check status first
    status = service.get_live_routing_status()
    logger.info(f"Live Routing Status: {json.dumps(status, indent=2)}")
    
    # Example valid coordinates inside Nasr City:
    origin = {"lat": 30.061, "lon": 31.344}
    destination = {"lat": 30.044, "lon": 31.365}
    
    logger.info(f"Computing route from origin {origin} to destination {destination}...")
    
    try:
        result = routing.compute_live_custom_route(
            origin=origin,
            destination=destination,
            route_preference="both",
            refresh_live_weather=False
        )
        
        # Log comparison summary
        comparison = result["comparison"]
        logger.info("Route computation completed successfully!")
        logger.info(f"Recommendation: {result['recommendation']}")
        logger.info(f"Safe route quality: {comparison['safe_route_quality']}")
        logger.info(f"Safe route available: {comparison['safe_route_available']}")
        logger.info(f"Risk reduction: {comparison['risk_reduction_percent']:.2f}%")
        logger.info(f"ETA tradeoff: {comparison['eta_tradeoff_percent']:.2f}%")
        logger.info(f"Normal route distance: {comparison['normal_distance_m']:.1f} m")
        logger.info(f"Safe route distance: {comparison['safe_distance_m']:.1f} m")
        logger.info(f"Normal mean live risk score: {comparison['normal_mean_live_risk_score']:.4f}")
        logger.info(f"Safe mean live risk score: {comparison['safe_mean_live_risk_score']:.4f}")
        
    except Exception as e:
        logger.error(f"Failed to compute live custom route: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

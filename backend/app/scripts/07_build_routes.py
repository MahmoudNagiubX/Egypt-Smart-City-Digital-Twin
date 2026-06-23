"""Orchestrate Phase 7: Emergency Weather-Safe Routing."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import routing, paths

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_weights():
    """Execute Step 1: Prepare routing graph and road risk weights."""
    logger.info("=" * 60)
    logger.info("STEP 1: Prepare routing graph and risk weights")
    logger.info("=" * 60)
    
    try:
        # Build for top-rain
        top_rain_weights = routing.build_road_risk_weights("top-rain")
        logger.info(f"✓ Top rain road risk weights built. Shape: {top_rain_weights.shape}")
        
        # Build for latest
        latest_weights = routing.build_road_risk_weights("latest")
        logger.info(f"✓ Latest road risk weights built. Shape: {latest_weights.shape}")
        
        # Verify average weight differences
        # High risk roads should receive higher weight on average
        for name, df in [("top-rain", top_rain_weights), ("latest", latest_weights)]:
            high_risk = df[df["predicted_risk_class"] == "high"]
            low_risk = df[df["predicted_risk_class"] == "low"]
            
            if len(high_risk) > 0 and len(low_risk) > 0:
                mean_high = high_risk["weather_weight"].mean()
                mean_low = low_risk["weather_weight"].mean()
                logger.info(f"  - [{name}] Mean weight: High risk = {mean_high:.2f}s, Low risk = {mean_low:.2f}s")
                if mean_high <= mean_low:
                    logger.warning(f"  - [{name}] Warning: high risk roads do not have higher average weight than low risk.")
            else:
                logger.info(f"  - [{name}] High risk segments: {len(high_risk)}, Low risk segments: {len(low_risk)}")
                
        # Graph load check
        G = routing.load_routing_graph()
        logger.info(f"✓ Routing graph loaded successfully. Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")
        
        # Test apply
        G = routing.apply_risk_weights_to_graph(G, top_rain_weights)
        logger.info("✓ Graph weights updated successfully.")
        
        return True
    except Exception as e:
        logger.error(f"✗ Graph weights step failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build emergency weather-safe routes for Nasr City."
    )
    parser.add_argument(
        "--step",
        choices=["weights"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 7 - Step: {args.step}")
    
    success = False
    if args.step == "weights":
        success = run_weights()
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

"""Orchestrate spatial data preparation for Nasr City."""

import argparse
import logging
import sys
from pathlib import Path

# Add backend/app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_impact import geo, paths

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_boundary_step():
    """Execute Step 2.1: Prepare Nasr City boundary."""
    logger.info("=" * 60)
    logger.info("STEP 2.1: Prepare Nasr City boundary")
    logger.info("=" * 60)
    
    try:
        boundary_gdf = geo.prepare_nasr_city_boundary()
        logger.info(f"✓ Boundary prepared. Shape: {boundary_gdf.shape}")
        logger.info(f"✓ CRS: {boundary_gdf.crs}")
        logger.info(f"✓ Saved to: {paths.NASR_CITY_BOUNDARY_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Boundary step failed: {e}", exc_info=True)
        return False


def run_roads_step():
    """Execute Step 2.2: Download road network."""
    logger.info("=" * 60)
    logger.info("STEP 2.2: Download road network")
    logger.info("=" * 60)
    
    try:
        G, nodes_gdf, roads_gdf = geo.download_road_network()
        logger.info(f"✓ Network downloaded. Nodes: {len(nodes_gdf)}, Edges: {len(roads_gdf)}")
        logger.info(f"✓ Graph saved to: {paths.NASR_CITY_GRAPH_PATH}")
        logger.info(f"✓ Nodes saved to: {paths.NASR_CITY_NODES_PATH}")
        logger.info(f"✓ Roads saved to: {paths.NASR_CITY_ROADS_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Roads step failed: {e}", exc_info=True)
        return False


def run_facilities_step():
    """Execute Step 2.3: Extract emergency facilities."""
    logger.info("=" * 60)
    logger.info("STEP 2.3: Extract emergency facilities")
    logger.info("=" * 60)
    
    try:
        facilities_gdf = geo.extract_emergency_facilities()
        logger.info(f"✓ Facilities extracted. Count: {len(facilities_gdf)}")
        logger.info(f"✓ Saved to: {paths.NASR_CITY_FACILITIES_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Facilities step failed: {e}", exc_info=True)
        return False


def run_validate_step():
    """Execute Step 2.4: Validate road network and spatial data."""
    logger.info("=" * 60)
    logger.info("STEP 2.4: Validate spatial data")
    logger.info("=" * 60)
    
    try:
        report = geo.validate_spatial_data()
        logger.info(f"✓ Validation complete. Status: {report['status']}")
        logger.info(f"✓ Report saved to: {paths.SPATIAL_VALIDATION_REPORT_PATH}")
        
        # Print summary
        logger.info(f"  Roads: {report['roads_count']}")
        logger.info(f"  Nodes: {report['nodes_count']}")
        logger.info(f"  Facilities: {report['facilities_count']}")
        
        if report["fallbacks_used"]:
            logger.info(f"  Fallbacks used: {', '.join(report['fallbacks_used'])}")
        
        if report["warnings"]:
            logger.info("  Warnings:")
            for warning in report["warnings"]:
                logger.info(f"    - {warning}")
        
        return report["status"] in ["ok", "ok_with_warnings"]
    except Exception as e:
        logger.error(f"✗ Validation step failed: {e}", exc_info=True)
        return False


def run_grid_step():
    """Execute Step 2.5: Generate 500m grid cells."""
    logger.info("=" * 60)
    logger.info("STEP 2.5: Generate 500m grid cells")
    logger.info("=" * 60)
    
    try:
        grid_gdf = geo.generate_grid_cells()
        logger.info(f"✓ Grid generated. Count: {len(grid_gdf)}")
        logger.info(f"✓ Saved to: {paths.NASR_CITY_GRID_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Grid step failed: {e}", exc_info=True)
        return False


def run_join_step():
    """Execute Step 2.6: Spatial join roads to grid."""
    logger.info("=" * 60)
    logger.info("STEP 2.6: Spatial join roads to grid")
    logger.info("=" * 60)
    
    try:
        roads_gdf = geo.join_roads_to_grid()
        logger.info(f"✓ Spatial join complete. Roads processed: {len(roads_gdf)}")
        logger.info(f"✓ Saved to: {paths.ROADS_WITH_ZONE_IDS_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Join step failed: {e}", exc_info=True)
        return False


def run_postgis_step():
    """Execute Step 2.7: Check PostGIS optional status."""
    logger.info("=" * 60)
    logger.info("STEP 2.7: Check PostGIS optional status")
    logger.info("=" * 60)
    
    try:
        geo.check_postgis_optional_status()
        logger.info("✓ PostGIS optional status checked successfully.")
        return True
    except Exception as e:
        logger.error(f"✗ PostGIS step failed: {e}", exc_info=True)
        return False


def run_map_step():
    """Execute Step 2.8: Create static map screenshot."""
    logger.info("=" * 60)
    logger.info("STEP 2.8: Create static map screenshot")
    logger.info("=" * 60)
    
    try:
        map_path = geo.create_spatial_foundation_map()
        logger.info(f"✓ Static map screenshot created successfully at: {map_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Map step failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build spatial data for Nasr City Weather Impact module."
    )
    parser.add_argument(
        "--step",
        choices=["boundary", "roads", "facilities", "validate", "grid", "join", "postgis", "map"],
        required=True,
        help="Step to execute",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Phase 2 - Step: {args.step}")
    
    if args.step == "boundary":
        success = run_boundary_step()
    elif args.step == "roads":
        success = run_roads_step()
    elif args.step == "facilities":
        success = run_facilities_step()
    elif args.step == "validate":
        success = run_validate_step()
    elif args.step == "grid":
        success = run_grid_step()
    elif args.step == "join":
        success = run_join_step()
    elif args.step == "postgis":
        success = run_postgis_step()
    elif args.step == "map":
        success = run_map_step()
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

import os
from pathlib import Path
import json
import pytest
import geopandas as gpd

# Define paths relative to the test file to ensure compatibility
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
PROCESSED_DIR = NASR_CITY_DIR / "processed"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"
MAPS_DIR = NASR_CITY_DIR / "maps"

# Paths to verify
BOUNDARY_PATH = PROCESSED_DIR / "nasr_city_boundary.geojson"
GRAPH_PATH = PROCESSED_DIR / "nasr_city_graph.graphml"
NODES_PATH = PROCESSED_DIR / "nasr_city_nodes.geojson"
ROADS_PATH = PROCESSED_DIR / "nasr_city_roads.geojson"
FACILITIES_PATH = PROCESSED_DIR / "nasr_city_emergency_facilities.geojson"
GRID_PATH = PROCESSED_DIR / "nasr_city_grid_500m.geojson"
ROADS_WITH_ZONES_PATH = PROCESSED_DIR / "roads_with_zone_ids.geojson"
REPORT_PATH = OUTPUTS_DIR / "spatial_validation_report.json"
MAP_PATH = MAPS_DIR / "spatial_foundation_map.png"


def test_files_exist():
    """Verify that all spatial foundation files exist."""
    assert BOUNDARY_PATH.exists(), f"Boundary file not found: {BOUNDARY_PATH}"
    assert GRAPH_PATH.exists(), f"Graph file not found: {GRAPH_PATH}"
    assert NODES_PATH.exists(), f"Nodes file not found: {NODES_PATH}"
    assert ROADS_PATH.exists(), f"Roads file not found: {ROADS_PATH}"
    assert FACILITIES_PATH.exists(), f"Facilities file not found: {FACILITIES_PATH}"
    assert REPORT_PATH.exists(), f"Validation report not found: {REPORT_PATH}"
    assert GRID_PATH.exists(), f"Grid file not found: {GRID_PATH}"
    assert ROADS_WITH_ZONES_PATH.exists(), f"Roads with zones file not found: {ROADS_WITH_ZONES_PATH}"
    assert MAP_PATH.exists(), f"Static map PNG not found: {MAP_PATH}"


def test_boundary_read():
    """Verify boundary can be read with GeoPandas and is valid."""
    gdf = gpd.read_file(BOUNDARY_PATH)
    assert not gdf.empty
    assert gdf.crs is not None


def test_roads_read():
    """Verify roads can be read with GeoPandas and has valid CRS."""
    gdf = gpd.read_file(ROADS_PATH)
    assert not gdf.empty
    assert gdf.crs is not None


def test_facilities_read():
    """Verify emergency facilities can be read with GeoPandas."""
    gdf = gpd.read_file(FACILITIES_PATH)
    assert not gdf.empty
    assert gdf.crs is not None


def test_grid_read_and_attributes():
    """Verify grid can be read with GeoPandas and has expected columns."""
    gdf = gpd.read_file(GRID_PATH)
    assert not gdf.empty
    assert gdf.crs is not None
    assert "zone_code" in gdf.columns, "Missing zone_code in grid"
    assert "area_m2" in gdf.columns, "Missing area_m2 in grid"
    assert gdf["zone_code"].notna().all(), "Some grid cells have missing zone_code"
    assert (gdf["area_m2"] > 0).all(), "Some grid cells have zero or negative area"


def test_roads_with_zones_read_and_attributes():
    """Verify roads_with_zone_ids can be read with GeoPandas and has expected columns."""
    gdf = gpd.read_file(ROADS_WITH_ZONES_PATH)
    assert not gdf.empty
    assert gdf.crs is not None
    assert "zone_code" in gdf.columns, "Missing zone_code in joined roads"
    assert "road_id" in gdf.columns, "Missing road_id in joined roads"
    assert "base_travel_time_sec" in gdf.columns, "Missing base_travel_time_sec in joined roads"
    
    # Ensure at least some roads are assigned a zone_code
    assert gdf["zone_code"].notna().any(), "No roads were assigned a zone_code"
    
    # Ensure road_id is unique
    assert gdf["road_id"].is_unique, "road_id values are not unique"


def test_validation_report():
    """Verify validation report status is ok or ok_with_warnings."""
    with open(REPORT_PATH, "r") as f:
        report = json.load(f)
    
    assert "status" in report
    assert report["status"] in ["ok", "ok_with_warnings"], f"Validation status is: {report['status']}"

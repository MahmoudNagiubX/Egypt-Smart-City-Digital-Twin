"""Geospatial helper functions and data structures."""

import logging
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import Point, box

from . import data_loader, paths

logger = logging.getLogger(__name__)

# Constants
PLACE_NAME = "Nasr City, Cairo, Egypt"
FALLBACK_BBOX = (31.285, 30.015, 31.405, 30.095)  # (west, south, east, north)


def prepare_nasr_city_boundary():
    """Prepare Nasr City boundary GeoJSON.
    
    Returns:
        GeoDataFrame with boundary polygon(s) and source field.
    """
    paths.ensure_data_dirs()
    
    logger.info(f"Preparing Nasr City boundary for: {PLACE_NAME}")
    
    # Try OSMnx geocoding first
    try:
        logger.info("Attempting OSMnx place-based boundary...")
        boundary_gdf = ox.geocode_to_gdf(PLACE_NAME)
        if boundary_gdf is not None and not boundary_gdf.empty:
            boundary_gdf = boundary_gdf.to_crs("EPSG:4326")
            boundary_gdf["source"] = "osmnx_place"
            logger.info("Successfully retrieved boundary from OSMnx place.")
            data_loader.write_geojson(boundary_gdf, paths.NASR_CITY_BOUNDARY_PATH)
            return boundary_gdf
    except Exception as e:
        logger.warning(f"OSMnx place-based boundary failed: {e}")
    
    # Fallback: use bbox
    logger.info(f"Using fallback bbox: {FALLBACK_BBOX}")
    west, south, east, north = FALLBACK_BBOX
    geom = box(west, south, east, north)
    boundary_gdf = gpd.GeoDataFrame(
        {"source": ["fallback_bbox"]},
        geometry=[geom],
        crs="EPSG:4326",
    )
    data_loader.write_geojson(boundary_gdf, paths.NASR_CITY_BOUNDARY_PATH)
    return boundary_gdf


def download_road_network():
    """Download Nasr City drive road network.
    
    Returns:
        tuple: (networkx Graph, nodes GeoDataFrame, edges GeoDataFrame)
    """
    paths.ensure_data_dirs()
    
    logger.info("Downloading road network...")
    
    # Try place-based download
    try:
        logger.info(f"Attempting OSMnx place-based download for: {PLACE_NAME}")
        G = ox.graph_from_place(
            PLACE_NAME,
            network_type="drive",
            simplify=True,
        )
        logger.info("Successfully downloaded network from OSMnx place.")
    except Exception as e:
        logger.warning(f"OSMnx place-based download failed: {e}")
        logger.info("Using fallback bbox...")
        west, south, east, north = FALLBACK_BBOX
        bbox = (west, south, east, north)
        G = ox.graph_from_bbox(
            bbox,
            network_type="drive",
            simplify=True,
        )
        logger.info("Successfully downloaded network from bbox fallback.")
    
    # Add edge speeds and travel times
    logger.info("Adding edge speeds and travel times...")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    
    # Save graph
    logger.info(f"Saving graph to: {paths.NASR_CITY_GRAPH_PATH}")
    ox.save_graphml(G, paths.NASR_CITY_GRAPH_PATH)
    
    # Convert to GeoDataFrames
    nodes, edges = ox.graph_to_gdfs(G)
    
    # Clean up complex columns for GeoJSON export
    edges_clean = _clean_gdf_for_geojson(edges)
    nodes_clean = _clean_gdf_for_geojson(nodes)
    
    # Ensure CRS
    edges_clean = edges_clean.to_crs("EPSG:4326")
    nodes_clean = nodes_clean.to_crs("EPSG:4326")
    
    # Save GeoDataFrames
    logger.info(f"Saving nodes to: {paths.NASR_CITY_NODES_PATH}")
    data_loader.write_geojson(nodes_clean, paths.NASR_CITY_NODES_PATH)
    
    logger.info(f"Saving roads to: {paths.NASR_CITY_ROADS_PATH}")
    data_loader.write_geojson(edges_clean, paths.NASR_CITY_ROADS_PATH)
    
    return G, nodes_clean, edges_clean


def extract_emergency_facilities():
    """Extract medical and emergency facilities from OpenStreetMap.
    
    Returns:
        GeoDataFrame with facilities as points.
    """
    paths.ensure_data_dirs()
    
    logger.info("Extracting emergency facilities...")
    
    # Define amenity tags to search
    tags = {
        "amenity": ["hospital", "clinic", "doctors", "fire_station", "police"]
    }
    
    facilities_list = []
    
    # Try place-based extraction
    try:
        logger.info(f"Attempting OSMnx features extraction for: {PLACE_NAME}")
        features = ox.features_from_place(PLACE_NAME, tags)
        if features is not None and not features.empty:
            features_gdf = gpd.GeoDataFrame(features)
            facilities_list.append(features_gdf)
            logger.info(f"Retrieved {len(features_gdf)} facilities from OSMnx place.")
    except Exception as e:
        logger.warning(f"OSMnx place-based extraction failed: {e}")
    
    # Fallback: try bbox-based extraction
    if not facilities_list:
        try:
            logger.info("Using fallback bbox for features extraction...")
            west, south, east, north = FALLBACK_BBOX
            bbox = (west, south, east, north)
            features = ox.features_from_bbox(bbox, tags)
            if features is not None and not features.empty:
                features_gdf = gpd.GeoDataFrame(features)
                facilities_list.append(features_gdf)
                logger.info(f"Retrieved {len(features_gdf)} facilities from bbox.")
        except Exception as e:
            logger.warning(f"Bbox-based extraction failed: {e}")
    
    # If still no results, use demo fallback
    if not facilities_list:
        logger.warning("No facilities found. Using demo fallback.")
        demo_facilities = [
            {"name": "Nasr City Hospital", "amenity": "hospital", "facility_type": "hospital"},
            {"name": "Nasr City Fire Station", "amenity": "fire_station", "facility_type": "fire_station"},
            {"name": "Nasr City Police", "amenity": "police", "facility_type": "police"},
            {"name": "Nasr City Clinic", "amenity": "clinic", "facility_type": "clinic"},
            {"name": "Nasr City Medical Center", "amenity": "doctors", "facility_type": "doctors"},
        ]
        
        # Create demo geometries inside bbox
        west, south, east, north = FALLBACK_BBOX
        geometries = [
            Point(31.33, 30.035),
            Point(31.35, 30.045),
            Point(31.32, 30.065),
            Point(31.37, 30.055),
            Point(31.34, 30.075),
        ]
        
        for facility, geom in zip(demo_facilities, geometries):
            facility["geometry"] = geom
            facility["source"] = "demo_fallback"
        
        facilities_gdf = gpd.GeoDataFrame(demo_facilities, crs="EPSG:4326")
        facilities_list = [facilities_gdf]
    
    if facilities_list:
        # Combine all facilities
        facilities_gdf = gpd.GeoDataFrame(
            pd.concat(facilities_list, ignore_index=True),
            crs="EPSG:4326"
        )
    else:
        # Empty fallback
        facilities_gdf = gpd.GeoDataFrame(
            columns=["name", "amenity", "facility_type", "source", "geometry"],
            crs="EPSG:4326"
        )
    
    # Convert polygons to points
    facilities_gdf["geometry"] = facilities_gdf.geometry.apply(
        lambda geom: geom.representative_point() if geom.geom_type in ["Polygon", "MultiPolygon"] else geom
    )
    
    # Ensure required columns
    if "facility_type" not in facilities_gdf.columns:
        facilities_gdf["facility_type"] = facilities_gdf.get("amenity", "unknown")
    
    if "source" not in facilities_gdf.columns:
        facilities_gdf["source"] = "osmnx"
    
    # Keep only essential columns
    keep_cols = ["name", "amenity", "facility_type", "source", "geometry"]
    facilities_gdf = facilities_gdf[[c for c in keep_cols if c in facilities_gdf.columns or c == "geometry"]]
    
    # Ensure CRS
    facilities_gdf = facilities_gdf.to_crs("EPSG:4326")
    
    logger.info(f"Saving {len(facilities_gdf)} facilities to: {paths.NASR_CITY_FACILITIES_PATH}")
    data_loader.write_geojson(facilities_gdf, paths.NASR_CITY_FACILITIES_PATH)
    
    return facilities_gdf


def validate_spatial_data():
    """Validate spatial foundation files and create validation report.
    
    Returns:
        dict: Validation report.
    """
    report = {
        "boundary_exists": False,
        "roads_exists": False,
        "nodes_exists": False,
        "graph_exists": False,
        "facilities_exists": False,
        "roads_count": 0,
        "nodes_count": 0,
        "facilities_count": 0,
        "boundary_crs": None,
        "roads_crs": None,
        "nodes_crs": None,
        "facilities_crs": None,
        "missing_road_geometries": 0,
        "missing_road_lengths": 0,
        "missing_travel_time": 0,
        "missing_speed_kph": 0,
        "road_bounds": [],
        "fallbacks_used": [],
        "status": "pending",
        "warnings": [],
    }
    
    # Check boundary
    if paths.NASR_CITY_BOUNDARY_PATH.exists():
        try:
            boundary_gdf = data_loader.read_geojson(paths.NASR_CITY_BOUNDARY_PATH)
            report["boundary_exists"] = True
            report["boundary_crs"] = str(boundary_gdf.crs)
            if "source" in boundary_gdf.columns:
                source = boundary_gdf["source"].iloc[0]
                if source == "fallback_bbox":
                    report["fallbacks_used"].append("boundary_bbox")
        except Exception as e:
            report["warnings"].append(f"Boundary read error: {e}")
    
    # Check roads
    if paths.NASR_CITY_ROADS_PATH.exists():
        try:
            roads_gdf = data_loader.read_geojson(paths.NASR_CITY_ROADS_PATH)
            report["roads_exists"] = True
            report["roads_count"] = len(roads_gdf)
            report["roads_crs"] = str(roads_gdf.crs)
            
            # Check for missing geometries
            report["missing_road_geometries"] = int(roads_gdf.geometry.isna().sum())
            
            # Check for missing attributes
            if "length" in roads_gdf.columns:
                report["missing_road_lengths"] = int(roads_gdf["length"].isna().sum())
            
            if "travel_time" in roads_gdf.columns:
                report["missing_travel_time"] = int(roads_gdf["travel_time"].isna().sum())
            
            if "speed_kph" in roads_gdf.columns:
                report["missing_speed_kph"] = int(roads_gdf["speed_kph"].isna().sum())
            
            # Get bounds
            if len(roads_gdf) > 0 and roads_gdf.geometry.notna().any():
                bounds = roads_gdf.total_bounds.tolist()
                report["road_bounds"] = bounds
        except Exception as e:
            report["warnings"].append(f"Roads read error: {e}")
    
    # Check nodes
    if paths.NASR_CITY_NODES_PATH.exists():
        try:
            nodes_gdf = data_loader.read_geojson(paths.NASR_CITY_NODES_PATH)
            report["nodes_exists"] = True
            report["nodes_count"] = len(nodes_gdf)
            report["nodes_crs"] = str(nodes_gdf.crs)
        except Exception as e:
            report["warnings"].append(f"Nodes read error: {e}")
    
    # Check graph
    if paths.NASR_CITY_GRAPH_PATH.exists():
        report["graph_exists"] = True
    
    # Check facilities
    if paths.NASR_CITY_FACILITIES_PATH.exists():
        try:
            facilities_gdf = data_loader.read_geojson(paths.NASR_CITY_FACILITIES_PATH)
            report["facilities_exists"] = True
            report["facilities_count"] = len(facilities_gdf)
            report["facilities_crs"] = str(facilities_gdf.crs)
            if "source" in facilities_gdf.columns:
                if (facilities_gdf["source"] == "demo_fallback").any():
                    report["fallbacks_used"].append("facilities_demo")
        except Exception as e:
            report["warnings"].append(f"Facilities read error: {e}")
    
    # Determine status
    all_required_exist = (
        report["boundary_exists"]
        and report["roads_exists"]
        and report["nodes_exists"]
        and report["graph_exists"]
        and report["facilities_exists"]
    )
    
    counts_valid = (
        report["roads_count"] > 0
        and report["nodes_count"] > 0
        and report["facilities_count"] >= 3
    )
    
    if all_required_exist and counts_valid:
        if report["fallbacks_used"]:
            report["status"] = "ok_with_warnings"
        else:
            report["status"] = "ok"
    elif not all_required_exist:
        report["status"] = "failed"
        missing = []
        if not report["boundary_exists"]:
            missing.append("boundary")
        if not report["roads_exists"]:
            missing.append("roads")
        if not report["nodes_exists"]:
            missing.append("nodes")
        if not report["graph_exists"]:
            missing.append("graph")
        if not report["facilities_exists"]:
            missing.append("facilities")
        report["warnings"].append(f"Missing files: {', '.join(missing)}")
    else:
        report["status"] = "failed"
        if report["roads_count"] == 0:
            report["warnings"].append("No roads found")
        if report["nodes_count"] == 0:
            report["warnings"].append("No nodes found")
        if report["facilities_count"] < 3:
            report["warnings"].append(f"Only {report['facilities_count']} facilities found (need >= 3)")
    
    logger.info(f"Validation status: {report['status']}")
    if report["warnings"]:
        for warning in report["warnings"]:
            logger.warning(f"  - {warning}")
    
    # Save report
    paths.ensure_data_dirs()
    data_loader.save_json(report, paths.SPATIAL_VALIDATION_REPORT_PATH)
    
    return report


def _clean_gdf_for_geojson(gdf):
    """Convert complex columns to strings for GeoJSON export."""
    gdf_clean = gdf.copy()
    
    for col in gdf_clean.columns:
        if gdf_clean[col].dtype == "object":
            try:
                # Check if column contains complex types
                if gdf_clean[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    gdf_clean[col] = gdf_clean[col].astype(str)
            except Exception:
                pass
    
    return gdf_clean


# pandas already imported at top


def generate_grid_cells(cell_size_m: int = 500):
    """Generate analysis grid cells over Nasr City boundary.
    
    Args:
        cell_size_m: Size of square grid cells in meters (default 500).
        
    Returns:
        GeoDataFrame with grid cells, zone_code, and area_m2.
    """
    paths.ensure_data_dirs()
    logger.info(f"Generating {cell_size_m}m grid cells over Nasr City boundary...")
    
    # 1. Load boundary
    boundary_gdf = data_loader.read_geojson(paths.NASR_CITY_BOUNDARY_PATH)
    
    # 2. Ensure CRS is EPSG:4326
    boundary_gdf = boundary_gdf.to_crs("EPSG:4326")
    
    # 3. Reproject boundary to metric CRS (EPSG:3857)
    boundary_metric = boundary_gdf.to_crs("EPSG:3857")
    
    # 4. Get bounds of boundary in metric CRS
    minx, miny, maxx, maxy = boundary_metric.total_bounds
    
    # 5. Generate square grid cells
    grid_cells = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            grid_cells.append(box(x, y, x + cell_size_m, y + cell_size_m))
            y += cell_size_m
        x += cell_size_m
        
    grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs="EPSG:3857")
    
    # 6. Clip/intersect cells to the Nasr City boundary
    boundary_union = boundary_metric.geometry.unary_union
    grid_gdf["geometry"] = grid_gdf.geometry.intersection(boundary_union)
    
    # 7. Remove empty and non-polygon geometries
    grid_gdf = grid_gdf[~grid_gdf.geometry.is_empty]
    grid_gdf = grid_gdf[grid_gdf.geom_type.isin(["Polygon", "MultiPolygon"])]
    
    if grid_gdf.empty:
        raise ValueError("No grid cells intersected the boundary.")
        
    # Sort grid cells spatially (Y descending, X ascending)
    centroids = grid_gdf.geometry.centroid
    grid_gdf["centroid_x"] = centroids.x
    grid_gdf["centroid_y"] = centroids.y
    grid_gdf = grid_gdf.sort_values(by=["centroid_y", "centroid_x"], ascending=[False, True]).reset_index(drop=True)
    grid_gdf = grid_gdf.drop(columns=["centroid_x", "centroid_y"])
    
    # 8. Add zone_code and area_m2
    grid_gdf["area_m2"] = grid_gdf.geometry.area
    grid_gdf["zone_code"] = [f"NSR-GRID-{i+1:03d}" for i in range(len(grid_gdf))]
    
    # 9. Reproject to EPSG:4326
    grid_gdf = grid_gdf.to_crs("EPSG:4326")
    
    # 10. Save to file
    logger.info(f"Saving grid with {len(grid_gdf)} cells to: {paths.NASR_CITY_GRID_PATH}")
    data_loader.write_geojson(grid_gdf, paths.NASR_CITY_GRID_PATH)
    
    return grid_gdf


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


def join_roads_to_grid():
    """Assign each road segment to a grid zone based on largest intersection length.
    
    Returns:
        GeoDataFrame: Processed roads with zone_code, road_id, length_m,
                      base_speed_kph, and base_travel_time_sec.
    """
    paths.ensure_data_dirs()
    logger.info("Joining roads to grid zones...")
    
    # 1. Load roads and grid
    roads_gdf = data_loader.read_geojson(paths.NASR_CITY_ROADS_PATH)
    grid_gdf = data_loader.read_geojson(paths.NASR_CITY_GRID_PATH)
    
    # 2. Ensure both are in EPSG:4326
    roads_gdf = roads_gdf.to_crs("EPSG:4326")
    grid_gdf = grid_gdf.to_crs("EPSG:4326")
    
    # Create unique road_id
    roads_gdf["road_id"] = [f"NSR-ROAD-{i+1:05d}" for i in range(len(roads_gdf))]
    
    # Normalize road columns
    roads_gdf["length_m"] = roads_gdf["length"].astype(float)
    
    # Normalize speed_kph
    if "speed_kph" in roads_gdf.columns:
        def clean_speed(val):
            if pd.isna(val) or val is None:
                return 50.0
            if isinstance(val, list):
                val = val[0]
            try:
                return float(val)
            except (ValueError, TypeError):
                return 50.0
        roads_gdf["base_speed_kph"] = roads_gdf["speed_kph"].apply(clean_speed)
    else:
        roads_gdf["base_speed_kph"] = 50.0
        
    # Normalize travel_time
    if "travel_time" in roads_gdf.columns:
        def clean_travel_time(val):
            if pd.isna(val) or val is None:
                return None
            if isinstance(val, list):
                val = val[0]
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
        roads_gdf["base_travel_time_sec"] = roads_gdf["travel_time"].apply(clean_travel_time)
    else:
        roads_gdf["base_travel_time_sec"] = None
        
    # Fallback calculation if travel time is missing or None
    mask = roads_gdf["base_travel_time_sec"].isna()
    if mask.any():
        speeds = roads_gdf.loc[mask, "base_speed_kph"].astype(float)
        speeds = speeds.replace(0, 50.0)  # Avoid division by zero
        roads_gdf.loc[mask, "base_travel_time_sec"] = roads_gdf.loc[mask, "length_m"].astype(float) * 3.6 / speeds
        
    # 3. Reproject to EPSG:3857 for spatial operations
    roads_metric = roads_gdf.to_crs("EPSG:3857")
    grid_metric = grid_gdf.to_crs("EPSG:3857")
    
    # Perform intersection overlay
    intersected = gpd.overlay(roads_metric[["road_id", "geometry"]], grid_metric[["zone_code", "geometry"]], how="intersection")
    
    # Calculate intersection lengths
    intersected["inter_length"] = intersected.geometry.length
    
    # Sort and drop duplicates to keep the zone with the largest intersection length
    best_joins = intersected.sort_values(by="inter_length", ascending=False).drop_duplicates(subset=["road_id"])
    
    # Map back to roads
    zone_mapping = dict(zip(best_joins["road_id"], best_joins["zone_code"]))
    roads_gdf["zone_code"] = roads_gdf["road_id"].map(zone_mapping)
    
    # 9. Reproject back to EPSG:4326
    roads_gdf = roads_gdf.to_crs("EPSG:4326")
    
    # Filter and keep only required columns
    keep_cols = ["road_id", "zone_code", "length_m", "base_speed_kph", "base_travel_time_sec", "geometry"]
    roads_final = roads_gdf[keep_cols].copy()
    
    # 10. Save
    logger.info(f"Saving joined roads to: {paths.ROADS_WITH_ZONE_IDS_PATH}")
    data_loader.write_geojson(roads_final, paths.ROADS_WITH_ZONE_IDS_PATH)
    
    assigned_count = int(roads_final["zone_code"].notna().sum())
    pct = (assigned_count / len(roads_final)) * 100
    logger.info(f"Roads assigned to zones: {assigned_count}/{len(roads_final)} ({pct:.2f}%)")
    
    return roads_final


def check_postgis_optional_status():
    """Confirm PostGIS optional status based on configuration settings."""
    try:
        from config import settings
    except ImportError:
        try:
            from ..config import settings
        except ImportError:
            class FallbackSettings:
                use_postgis = False
            settings = FallbackSettings()
            
    if not settings.use_postgis:
        print("PostGIS load skipped because USE_POSTGIS=false. GeoJSON-first MVP remains ready.")
    else:
        print("PostGIS load is requested (USE_POSTGIS=true).")


def create_spatial_foundation_map():
    """Create a static map visualization of the spatial foundation layers."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    
    paths.ensure_data_dirs()
    logger.info("Generating static spatial foundation map...")
    
    # 1. Load datasets
    boundary_gdf = data_loader.read_geojson(paths.NASR_CITY_BOUNDARY_PATH)
    grid_gdf = data_loader.read_geojson(paths.NASR_CITY_GRID_PATH)
    roads_gdf = data_loader.read_geojson(paths.ROADS_WITH_ZONE_IDS_PATH)
    facilities_gdf = data_loader.read_geojson(paths.NASR_CITY_FACILITIES_PATH)
    
    # 2. Ensure they are in EPSG:4326 for coordinate plotting
    boundary_gdf = boundary_gdf.to_crs("EPSG:4326")
    grid_gdf = grid_gdf.to_crs("EPSG:4326")
    roads_gdf = roads_gdf.to_crs("EPSG:4326")
    facilities_gdf = facilities_gdf.to_crs("EPSG:4326")
    
    # 3. Create plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot boundary (filled with light color, thick outline)
    boundary_gdf.plot(ax=ax, color="#e6f2ff", edgecolor="#0066cc", linewidth=2.5, alpha=0.5)
    
    # Plot 500m grid (no fill, thin dashed gridlines)
    grid_gdf.plot(ax=ax, facecolor="none", edgecolor="#808080", linewidth=0.8, linestyle="--", alpha=0.7)
    
    # Plot roads (thin gray/black lines)
    roads_gdf.plot(ax=ax, color="#4d4d4d", linewidth=0.5, alpha=0.8)
    
    # Plot emergency facilities (red markers)
    if not facilities_gdf.empty:
        facilities_gdf.plot(ax=ax, color="#cc0000", markersize=35, marker="^", alpha=0.9)
    
    # 4. Styling
    ax.set_title("Nasr City Emergency Mobility - Spatial Foundation Map", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude", fontsize=10)
    ax.grid(True, linestyle=":", alpha=0.5)
    
    # Create a custom legend
    legend_elements = [
        Line2D([0], [0], color="#0066cc", lw=2.5, label="Nasr City Boundary"),
        Line2D([0], [0], color="#808080", lw=0.8, linestyle="--", label="500m Grid Cells"),
        Line2D([0], [0], color="#4d4d4d", lw=0.5, label="Roads Network"),
        Line2D([0], [0], marker="^", color="w", label="Emergency Facility", markerfacecolor="#cc0000", markersize=8)
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, facecolor="white", edgecolor="#e0e0e0")
    
    # Save the figure
    logger.info(f"Saving map screenshot to: {paths.SPATIAL_FOUNDATION_MAP_PATH}")
    paths.SPATIAL_FOUNDATION_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(paths.SPATIAL_FOUNDATION_MAP_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    return str(paths.SPATIAL_FOUNDATION_MAP_PATH)


def calculate_road_density_features():
    """Calculate road network density and type count features for each grid zone."""
    paths.ensure_data_dirs()
    logger.info("Calculating road density features per grid zone...")
    
    # 1. Load inputs
    grid = data_loader.read_geojson(paths.NASR_CITY_GRID_PATH)
    roads_joined = data_loader.read_geojson(paths.ROADS_WITH_ZONE_IDS_PATH)
    roads_orig = data_loader.read_geojson(paths.NASR_CITY_ROADS_PATH)
    
    # Ensure both are in EPSG:3857 for metric calculations
    grid_metric = grid.to_crs("EPSG:3857")
    
    # Map original highway type to roads_joined
    roads_orig["road_id"] = [f"NSR-ROAD-{i+1:05d}" for i in range(len(roads_orig))]
    highway_map = dict(zip(roads_orig["road_id"], roads_orig["highway"]))
    roads_joined["highway"] = roads_joined["road_id"].map(highway_map)
    
    # Try mapping u and v for intersection_proxy_count
    if "u" in roads_orig.columns and "v" in roads_orig.columns:
        u_map = dict(zip(roads_orig["road_id"], roads_orig["u"]))
        v_map = dict(zip(roads_orig["road_id"], roads_orig["v"]))
        roads_joined["u"] = roads_joined["road_id"].map(u_map)
        roads_joined["v"] = roads_joined["road_id"].map(v_map)
        has_nodes = True
    else:
        has_nodes = False

    def get_road_class(hw):
        if not isinstance(hw, str):
            if isinstance(hw, list):
                hw = hw[0]
            else:
                return "unknown"
        hw = str(hw).lower()
        if "primary" in hw:
            return "primary"
        elif "secondary" in hw:
            return "secondary"
        elif "tertiary" in hw:
            return "tertiary"
        elif "residential" in hw:
            return "residential"
        elif "service" in hw:
            return "service"
        else:
            return "unknown"
            
    roads_joined["road_class"] = roads_joined["highway"].apply(get_road_class)
    
    # Group roads by zone_code
    grouped = roads_joined.groupby("zone_code")
    
    road_counts = grouped.size().to_dict()
    road_lengths = grouped["length_m"].sum().to_dict()
    avg_speeds = grouped["base_speed_kph"].mean().to_dict()
    avg_travel_times = grouped["base_travel_time_sec"].mean().to_dict()
    
    # Class counts
    if not roads_joined.empty:
        class_counts = grouped["road_class"].value_counts().unstack(fill_value=0)
    else:
        class_counts = pd.DataFrame(columns=["primary", "secondary", "tertiary", "residential", "service", "unknown"])
        
    for cls in ["primary", "secondary", "tertiary", "residential", "service", "unknown"]:
        if cls not in class_counts.columns:
            class_counts[cls] = 0
            
    # Calculate intersection proxy count
    intersection_proxies = {}
    if has_nodes and not roads_joined.empty:
        for zc, group in grouped:
            nodes = set(group["u"].dropna().tolist() + group["v"].dropna().tolist())
            intersection_proxies[zc] = len(nodes)
    else:
        intersection_proxies = road_counts
        
    # Build feature rows for all grid cells
    rows = []
    for _, cell in grid_metric.iterrows():
        zc = cell["zone_code"]
        area_m2 = float(cell.geometry.area)
        area_km2 = area_m2 / 1_000_000.0
        
        length = float(road_lengths.get(zc, 0.0))
        density = length / area_km2 if area_km2 > 0 else 0.0
        
        p_count = int(class_counts.loc[zc, "primary"]) if zc in class_counts.index else 0
        sec_count = int(class_counts.loc[zc, "secondary"]) if zc in class_counts.index else 0
        tert_count = int(class_counts.loc[zc, "tertiary"]) if zc in class_counts.index else 0
        res_count = int(class_counts.loc[zc, "residential"]) if zc in class_counts.index else 0
        srv_count = int(class_counts.loc[zc, "service"]) if zc in class_counts.index else 0
        unk_count = int(class_counts.loc[zc, "unknown"]) if zc in class_counts.index else 0
        
        speed = avg_speeds.get(zc, 50.0)
        if pd.isna(speed):
            speed = 50.0
            
        tt = avg_travel_times.get(zc, 0.0)
        if pd.isna(tt):
            tt = 0.0
            
        rows.append({
            "zone_code": zc,
            "zone_area_m2": area_m2,
            "zone_area_km2": area_km2,
            "road_count": int(road_counts.get(zc, 0)),
            "road_length_m": length,
            "road_density_m_per_km2": density,
            "primary_road_count": p_count,
            "secondary_road_count": sec_count,
            "tertiary_road_count": tert_count,
            "residential_road_count": res_count,
            "service_road_count": srv_count,
            "unknown_road_count": unk_count,
            "avg_base_speed_kph": float(speed),
            "avg_base_travel_time_sec": float(tt),
            "intersection_proxy_count": int(intersection_proxies.get(zc, 0))
        })
        
    features_df = pd.DataFrame(rows)
    data_loader.write_csv(features_df, paths.GRID_ROAD_FEATURES_PATH)
    logger.info(f"Saved road features to {paths.GRID_ROAD_FEATURES_PATH}")
    return features_df


def extract_elevation_features(project_id: str = "smart-city-digital-twin"):
    """Extract SRTM elevation and slope features for each grid zone using Google Earth Engine.
    
    If Earth Engine is not available or fails, falls back to proxy features.
    """
    paths.ensure_data_dirs()
    logger.info("Extracting elevation features...")
    
    # Load grid zones
    grid = data_loader.read_geojson(paths.NASR_CITY_GRID_PATH)
    
    elevation_source = "srtm_earth_engine"
    elevation_warning = ""
    rows = []
    
    try:
        import ee
        import json
        
        logger.info(f"Initializing Earth Engine with project: {project_id}")
        ee.Initialize(project=project_id)
        
        # Load SRTM and calculate slope
        srtm = ee.Image("USGS/SRTMGL1_003")
        slope = ee.Terrain.slope(srtm)
        dem = srtm.select(["elevation"]).rename(["elevation"]).addBands(slope.select(["slope"]).rename(["slope"]))
        
        # Construct FeatureCollection
        logger.info("Converting grid geometries to Earth Engine geometries...")
        features = []
        for _, row in grid.iterrows():
            geom_dict = json.loads(gpd.GeoSeries([row.geometry]).to_json())["features"][0]["geometry"]
            ee_geom = ee.Geometry(geom_dict)
            features.append(ee.Feature(ee_geom, {"zone_code": row["zone_code"]}))
            
        fc = ee.FeatureCollection(features)
        
        # Define combined reducer
        reducer = ee.Reducer.mean() \
            .combine(ee.Reducer.min(), "", True) \
            .combine(ee.Reducer.max(), "", True) \
            .combine(ee.Reducer.stdDev(), "", True)
            
        logger.info("Reducing DEM bands over grid zones...")
        reduced = dem.reduceRegions(
            collection=fc,
            reducer=reducer,
            scale=30
        )
        
        # Fetch results excluding geometries for fast transfer
        properties_fc = reduced.select(
            ["zone_code", "elevation_mean", "elevation_min", "elevation_max", "elevation_stdDev",
             "slope_mean", "slope_min", "slope_max", "slope_stdDev"],
            retainGeometry=False
        )
        
        logger.info("Fetching results from Earth Engine server...")
        results = properties_fc.getInfo()["features"]
        
        for feat in results:
            props = feat["properties"]
            zc = props.get("zone_code")
            
            e_mean = props.get("elevation_mean", 0.0)
            e_min = props.get("elevation_min", 0.0)
            e_max = props.get("elevation_max", 0.0)
            
            # stdDev variants
            e_std = props.get("elevation_stdDev")
            if e_std is None:
                e_std = props.get("elevation_std_dev")
            if e_std is None:
                e_std = props.get("elevation_stddev", 0.0)
                
            s_mean = props.get("slope_mean", 0.0)
            s_min = props.get("slope_min", 0.0)
            s_max = props.get("slope_max", 0.0)
            
            rows.append({
                "zone_code": zc,
                "elevation_mean": float(e_mean),
                "elevation_min": float(e_min),
                "elevation_max": float(e_max),
                "elevation_std": float(e_std),
                "slope_mean": float(s_mean),
                "slope_min": float(s_min),
                "slope_max": float(s_max),
            })
            
        logger.info(f"Successfully processed {len(rows)} cells with Earth Engine.")
        
    except Exception as e:
        logger.warning(f"Earth Engine elevation extraction failed, using fallback proxy: {e}")
        elevation_source = "fallback_proxy"
        elevation_warning = str(e)
        
        # Create empty rows for fallback mapping
        rows = []
        for zc in grid["zone_code"]:
            rows.append({
                "zone_code": zc,
                "elevation_mean": 0.0,
                "elevation_min": 0.0,
                "elevation_max": 0.0,
                "elevation_std": 0.0,
                "slope_mean": 0.0,
                "slope_min": 0.0,
                "slope_max": 0.0,
            })
            
    df = pd.DataFrame(rows)
    df["elevation_source"] = elevation_source
    df["elevation_warning"] = elevation_warning
    
    # Calculate low_elevation_score and low_slope_score
    if elevation_source == "srtm_earth_engine" and len(df) > 1:
        # lower elevation = higher score
        emin = df["elevation_mean"].min()
        emax = df["elevation_mean"].max()
        if emax > emin:
            df["low_elevation_score"] = 1.0 - (df["elevation_mean"] - emin) / (emax - emin)
        else:
            df["low_elevation_score"] = 0.5
            
        # flatter slope = higher score
        smin = df["slope_mean"].min()
        smax = df["slope_mean"].max()
        if smax > smin:
            df["low_slope_score"] = 1.0 - (df["slope_mean"] - smin) / (smax - smin)
        else:
            df["low_slope_score"] = 0.5
    else:
        df["low_elevation_score"] = 0.5
        df["low_slope_score"] = 0.5
        
    # Clip scores to [0.0, 1.0]
    df["low_elevation_score"] = df["low_elevation_score"].clip(0.0, 1.0)
    df["low_slope_score"] = df["low_slope_score"].clip(0.0, 1.0)
    
    # Save CSV
    data_loader.write_csv(df, paths.GRID_ELEVATION_FEATURES_PATH)
    logger.info(f"Saved elevation features to {paths.GRID_ELEVATION_FEATURES_PATH}")
    return df







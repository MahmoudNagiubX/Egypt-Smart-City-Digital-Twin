"""Weather-aware route optimization module."""

import logging
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import osmnx as ox
from . import paths, data_loader

logger = logging.getLogger(__name__)


def load_routing_graph():
    """Load the OSMnx routing graph for Nasr City."""
    if not paths.NASR_CITY_GRAPH_PATH.exists():
        raise FileNotFoundError(f"Routing graph GraphML not found at: {paths.NASR_CITY_GRAPH_PATH}")
    logger.info(f"Loading routing graph from {paths.NASR_CITY_GRAPH_PATH}")
    return ox.load_graphml(paths.NASR_CITY_GRAPH_PATH)


def load_road_segments():
    """Load the road segments with zone IDs."""
    if not paths.ROADS_WITH_ZONE_IDS_PATH.exists():
        raise FileNotFoundError(f"Road segments GeoJSON not found at: {paths.ROADS_WITH_ZONE_IDS_PATH}")
    return gpd.read_file(paths.ROADS_WITH_ZONE_IDS_PATH)


def load_event_risk_layer(event_type: str):
    """Load the predictions risk layer GeoJSON for top-rain or latest event."""
    if event_type == "top-rain":
        path = paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH
    elif event_type == "latest":
        path = paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH
    else:
        raise ValueError(f"Unsupported event_type: {event_type}")
        
    if not path.exists():
        raise FileNotFoundError(f"Event risk layer GeoJSON not found at: {path}")
        
    logger.info(f"Loading {event_type} risk layer from {path}")
    return gpd.read_file(path)


def build_road_risk_weights(event_type: str):
    """Apply zone-level risk predictions to road segments and calculate routing weights."""
    logger.info(f"Building road risk weights for event type: {event_type}...")
    
    if not paths.NASR_CITY_ROADS_PATH.exists():
        raise FileNotFoundError(f"Nasr City roads GeoJSON not found at: {paths.NASR_CITY_ROADS_PATH}")
        
    # 1. Load road segments, roads mapping, and risk layer
    roads_gdf = gpd.read_file(paths.NASR_CITY_ROADS_PATH)
    roads_gdf["road_id"] = [f"NSR-ROAD-{i+1:05d}" for i in range(len(roads_gdf))]
    
    roads_zones = load_road_segments()
    risk_layer = load_event_risk_layer(event_type)
    
    # 2. Merge road segments with their zone assignments
    merged = roads_gdf.merge(roads_zones[["road_id", "zone_code"]], on="road_id", how="left")
    
    # 3. Merge with zone-level risk predictions
    road_risk = merged.merge(risk_layer[["zone_code", "y_pred", "predicted_risk_class"]], on="zone_code", how="left")
    
    # 4. Fill missing risk values safely (e.g. roads outside boundary)
    road_risk["y_pred"] = road_risk["y_pred"].fillna(0.0).astype(float)
    road_risk["predicted_risk_class"] = road_risk["predicted_risk_class"].fillna("low")
    
    # 5. Normal weight calculation:
    # Prefer travel_time if available, fallback to length / speed
    normal_weight = road_risk["travel_time"].copy()
    
    # Fallback to length / (speed_kph / 3.6)
    speed_denom = road_risk["speed_kph"].fillna(50.0).replace(0, 50.0)
    fallback_time = road_risk["length"] / (speed_denom / 3.6)
    
    normal_weight = normal_weight.fillna(fallback_time)
    
    # 6. Weather weight logic:
    risk_score = np.clip(road_risk["y_pred"], 0.0, 1.0)
    weather_penalty_factor = 1.0 + (2.5 * risk_score)
    
    # Apply extra penalty multiplier for high risk class
    high_risk_mask = (road_risk["predicted_risk_class"] == "high")
    weather_penalty_factor = np.where(high_risk_mask, weather_penalty_factor * 3.0, weather_penalty_factor)
    
    weather_travel_time_sec = normal_weight * weather_penalty_factor
    
    # 7. Add columns
    road_risk["base_travel_time_sec"] = normal_weight
    road_risk["weather_penalty_factor"] = weather_penalty_factor
    road_risk["weather_travel_time_sec"] = weather_travel_time_sec
    road_risk["weather_weight"] = weather_travel_time_sec
    
    # Select final columns to keep
    keep_cols = [
        "road_id", "u", "v", "key", "zone_code", "length", 
        "base_travel_time_sec", "speed_kph", "y_pred", 
        "predicted_risk_class", "weather_penalty_factor", 
        "weather_travel_time_sec", "weather_weight", "geometry"
    ]
    actual_cols = [c for c in keep_cols if c in road_risk.columns]
    
    result_gdf = gpd.GeoDataFrame(road_risk[actual_cols], geometry="geometry", crs="EPSG:4326")
    
    # 8. Save output
    paths.ensure_data_dirs()
    if event_type == "top-rain":
        out_path = paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH
    elif event_type == "latest":
        out_path = paths.ROAD_RISK_WEIGHTS_LATEST_PATH
    else:
        raise ValueError(f"Unsupported event_type: {event_type}")
        
    # pyogrio driver is faster and safe
    result_gdf.to_file(out_path, driver="GeoJSON")
    logger.info(f"Saved road risk weights for {event_type} to {out_path} (rows: {len(result_gdf)})")
    
    return result_gdf


def apply_risk_weights_to_graph(G, road_risk_df):
    """Update Graph G edge attributes with weights from road_risk_df."""
    logger.info("Applying risk weights to graph edges...")
    
    # Convert edge keys to integers
    u_vals = road_risk_df["u"].astype(int)
    v_vals = road_risk_df["v"].astype(int)
    key_vals = road_risk_df["key"].astype(int)
    
    weights_dict = {}
    for idx, row in road_risk_df.iterrows():
        edge_key = (int(row["u"]), int(row["v"]), int(row["key"]))
        weights_dict[edge_key] = {
            "base_travel_time_sec": float(row["base_travel_time_sec"]),
            "weather_weight": float(row["weather_weight"]),
            "predicted_risk_class": str(row["predicted_risk_class"]),
            "y_pred": float(row["y_pred"]),
            "length": float(row["length"])
        }
        
    for u, v, k, data in G.edges(keys=True, data=True):
        edge_key = (u, v, k)
        if edge_key in weights_dict:
            data.update(weights_dict[edge_key])
        else:
            # Safe fallback edge attributes if missing
            length = float(data.get("length", 10.0))
            speed = float(data.get("speed_kph", 50.0))
            travel_time = float(data.get("travel_time", length / (speed / 3.6)))
            data["base_travel_time_sec"] = travel_time
            data["weather_weight"] = travel_time
            data["predicted_risk_class"] = "low"
            data["y_pred"] = 0.0
            
    return G


def select_demo_route_points(event_type: str):
    """Select origin (highest risk zone centroid) and destination (nearest emergency facility)."""
    logger.info(f"Selecting demo route points for event type: {event_type}...")
    
    # 1. Load risk layer
    risk_layer = load_event_risk_layer(event_type)
    if len(risk_layer) == 0:
        raise ValueError(f"Risk layer for {event_type} is empty.")
        
    # Find zone with highest y_pred
    highest_risk_row = risk_layer.sort_values("y_pred", ascending=False).iloc[0]
    origin_zone_code = highest_risk_row["zone_code"]
    origin_geom = highest_risk_row["geometry"]
    
    # Calculate centroid
    origin_centroid = origin_geom.centroid
    origin_lon = origin_centroid.x
    origin_lat = origin_centroid.y
    
    # 2. Load emergency facilities
    if not paths.NASR_CITY_FACILITIES_PATH.exists():
        raise FileNotFoundError(f"Emergency facilities GeoJSON not found at: {paths.NASR_CITY_FACILITIES_PATH}")
    facilities = gpd.read_file(paths.NASR_CITY_FACILITIES_PATH)
    if len(facilities) == 0:
        raise ValueError("Emergency facilities GeoJSON is empty.")
        
    # Calculate distance to all facilities
    dists = facilities.geometry.distance(origin_centroid)
    nearest_idx = dists.idxmin()
    nearest_fac = facilities.loc[nearest_idx]
    
    fac_geom = nearest_fac["geometry"]
    fac_centroid = fac_geom.centroid
    dest_lon = fac_centroid.x
    dest_lat = fac_centroid.y
    
    fac_name = nearest_fac.get("name", "Unknown Emergency Facility")
    fac_type = nearest_fac.get("facility_type", "hospital")
    
    logger.info(f"Selected origin zone: {origin_zone_code} ({origin_lon:.5f}, {origin_lat:.5f})")
    logger.info(f"Selected destination: {fac_name} ({dest_lon:.5f}, {dest_lat:.5f})")
    
    return {
        "origin_lon": float(origin_lon),
        "origin_lat": float(origin_lat),
        "origin_zone_code": str(origin_zone_code),
        "dest_lon": float(dest_lon),
        "dest_lat": float(dest_lat),
        "destination_facility_name": str(fac_name),
        "destination_facility_type": str(fac_type)
    }


def find_nearest_graph_node(G, lon, lat):
    """Find the nearest graph node in Nasr City for given coordinates."""
    return ox.nearest_nodes(G, X=lon, Y=lat)


def compute_route(G, origin_node, destination_node, weight):
    """Compute shortest path between origin and destination nodes using NetworkX."""
    import networkx as nx
    try:
        route = nx.shortest_path(G, source=origin_node, target=destination_node, weight=weight)
        return route
    except nx.NetworkXNoPath:
        logger.warning(f"No path found between node {origin_node} and {destination_node} using weight {weight}")
        return None


def get_route_edge_data(G, route, weight_key):
    """Retrieve list of edge data dicts along a route list of nodes."""
    edges_data = []
    for u, v in zip(route[:-1], route[1:]):
        edge_options = G.get_edge_data(u, v)
        if not edge_options:
            continue
        # If there are multiple edges, pick the one with the smallest weight_key
        best_key = min(edge_options.keys(), key=lambda k: edge_options[k].get(weight_key, float('inf')))
        edges_data.append(edge_options[best_key])
    return edges_data


def sum_route_metric(edges_data, key, fallback=0.0):
    """Sum a numeric key across all edges in the route."""
    return sum(float(data.get(key, fallback)) for data in edges_data)


def count_route_high_risk(edges_data):
    """Count the number of high risk segments in the route."""
    return sum(1 for data in edges_data if data.get("predicted_risk_class") == "high")


def mean_route_risk(edges_data):
    """Calculate the average risk score across all edges in the route."""
    if not edges_data:
        return 0.0
    return sum(float(data.get("y_pred", 0.0)) for data in edges_data) / len(edges_data)


def compare_routes(normal_route, safe_route, G, event_type, points_info):
    """Compare normal vs weather-safe route metrics."""
    logger.info(f"Comparing normal and safe routes for event: {event_type}...")
    
    # Get edge data for both
    normal_edges = get_route_edge_data(G, normal_route, "base_travel_time_sec")
    safe_edges = get_route_edge_data(G, safe_route, "weather_weight")
    
    # 1. Sum up metrics
    normal_dist = sum_route_metric(normal_edges, "length")
    safe_dist = sum_route_metric(safe_edges, "length")
    
    normal_base_eta = sum_route_metric(normal_edges, "base_travel_time_sec")
    safe_base_eta = sum_route_metric(safe_edges, "base_travel_time_sec")
    
    normal_weather_eta = sum_route_metric(normal_edges, "weather_weight")
    safe_weather_eta = sum_route_metric(safe_edges, "weather_weight")
    
    # 2. Risk metrics
    normal_high_risk = count_route_high_risk(normal_edges)
    safe_high_risk = count_route_high_risk(safe_edges)
    avoided_high_risk = normal_high_risk - safe_high_risk
    
    normal_mean_risk = mean_route_risk(normal_edges)
    safe_mean_risk = mean_route_risk(safe_edges)
    
    risk_red = 0.0
    if normal_mean_risk > 0.0:
        risk_red = ((normal_mean_risk - safe_mean_risk) / normal_mean_risk) * 100.0
        
    eta_tradeoff = 0.0
    if normal_base_eta > 0.0:
        eta_tradeoff = ((safe_base_eta - normal_base_eta) / normal_base_eta) * 100.0
        
    event_id = "Unknown"
    timestamp = "Unknown"
    if paths.PREDICTION_OUTPUT_REPORT_PATH.exists():
        try:
            report = data_loader.load_json(paths.PREDICTION_OUTPUT_REPORT_PATH)
            if event_type == "top-rain":
                event_id = report.get("top_rain_event_id", "evt_0557")
            else:
                event_id = report.get("latest_event_id", "evt_dry_009")
        except Exception:
            pass
            
    if paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists() and event_id != "Unknown":
        try:
            df = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
            matching = df[df["event_id"] == event_id]
            if len(matching) > 0:
                timestamp = str(matching["timestamp"].iloc[0])
        except Exception:
            pass
            
    metrics = {
        "normal_distance_m": float(normal_dist),
        "safe_distance_m": float(safe_dist),
        "normal_base_eta_sec": float(normal_base_eta),
        "safe_base_eta_sec": float(safe_base_eta),
        "normal_weather_eta_sec": float(normal_weather_eta),
        "safe_weather_eta_sec": float(safe_weather_eta),
        "normal_high_risk_segment_count": int(normal_high_risk),
        "safe_high_risk_segment_count": int(safe_high_risk),
        "avoided_high_risk_segments": int(avoided_high_risk),
        "normal_mean_risk_score": float(normal_mean_risk),
        "safe_mean_risk_score": float(safe_mean_risk),
        "risk_reduction_percent": float(risk_red),
        "eta_tradeoff_percent": float(eta_tradeoff),
        "origin_zone_code": points_info["origin_zone_code"],
        "destination_facility_name": points_info["destination_facility_name"],
        "destination_facility_type": points_info["destination_facility_type"],
        "event_type": event_type,
        "event_id": event_id,
        "timestamp": timestamp
    }
    
    return metrics


def build_demo_routes(event_type: str):
    """Build and compute normal vs weather-safe demo routes for an event type."""
    if event_type == "top-rain":
        weights_path = paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH
    else:
        weights_path = paths.ROAD_RISK_WEIGHTS_LATEST_PATH
        
    if not weights_path.exists():
        build_road_risk_weights(event_type)
        
    road_risk_df = gpd.read_file(weights_path)
    G = load_routing_graph()
    G = apply_risk_weights_to_graph(G, road_risk_df)
    
    points_info = select_demo_route_points(event_type)
    
    origin_node = find_nearest_graph_node(G, points_info["origin_lon"], points_info["origin_lat"])
    dest_node = find_nearest_graph_node(G, points_info["dest_lon"], points_info["dest_lat"])
    
    normal_route = compute_route(G, origin_node, dest_node, "base_travel_time_sec")
    safe_route = compute_route(G, origin_node, dest_node, "weather_weight")
    
    if normal_route is None or safe_route is None:
        raise ValueError(f"Could not compute routes for event type: {event_type}")
        
    metrics = compare_routes(normal_route, safe_route, G, event_type, points_info)
    
    return normal_route, safe_route, G, metrics


def route_to_geojson(G, route_nodes, event_type, route_type, metrics, points_info):
    """Convert a route node list to a GeoJSON FeatureCollection."""
    from shapely.geometry import LineString
    
    if len(route_nodes) < 2:
        # fallback to empty LineString if not enough nodes
        line = LineString()
    else:
        coordinates = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route_nodes]
        line = LineString(coordinates)
        
    is_safe = (route_type == "weather_safe")
    prefix = "safe" if is_safe else "normal"
    
    properties = {
        "route_type": route_type,
        "event_type": event_type,
        "event_id": metrics.get("event_id", "Unknown"),
        "timestamp": metrics.get("timestamp", "Unknown"),
        "distance_m": float(metrics.get(f"{prefix}_distance_m", 0.0)),
        "base_eta_sec": float(metrics.get(f"{prefix}_base_eta_sec", 0.0)),
        "weather_eta_sec": float(metrics.get(f"{prefix}_weather_eta_sec", 0.0)),
        "mean_risk_score": float(metrics.get(f"{prefix}_mean_risk_score", 0.0)),
        "high_risk_segment_count": int(metrics.get(f"{prefix}_high_risk_segment_count", 0)),
        "origin_lon": float(points_info["origin_lon"]),
        "origin_lat": float(points_info["origin_lat"]),
        "destination_lon": float(points_info["dest_lon"]),
        "destination_lat": float(points_info["dest_lat"]),
        "destination_facility_name": points_info.get("destination_facility_name", "Unknown"),
        "honesty_note": "Routes are decision-support prototype outputs, not official emergency dispatch instructions."
    }
    
    gdf = gpd.GeoDataFrame([properties], geometry=[line], crs="EPSG:4326")
    return gdf


def export_demo_route_outputs():
    """Build, compare, and export all demo routes and comparisons."""
    logger.info("Exporting all demo route outputs...")
    warnings = []
    
    # 1. Top Rain
    n_route_top, s_route_top, G_top, metrics_top = build_demo_routes("top-rain")
    points_top = select_demo_route_points("top-rain")
    
    # Check if routes are identical
    if n_route_top == s_route_top:
        warnings.append("Top-rain: normal and safe routes are identical, no safer alternative path found.")
        
    gdf_top_normal = route_to_geojson(G_top, n_route_top, "top-rain", "normal", metrics_top, points_top)
    gdf_top_safe = route_to_geojson(G_top, s_route_top, "top-rain", "weather_safe", metrics_top, points_top)
    
    gdf_top_normal.to_file(paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH, driver="GeoJSON")
    gdf_top_safe.to_file(paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH, driver="GeoJSON")
    
    with open(paths.ROUTE_COMPARISON_TOP_RAIN_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_top, f, indent=2)
        
    # 2. Latest
    n_route_lat, s_route_lat, G_lat, metrics_lat = build_demo_routes("latest")
    points_lat = select_demo_route_points("latest")
    
    # Check if routes are identical
    if n_route_lat == s_route_lat:
        warnings.append("Latest: normal and safe routes are identical, no safer alternative path found.")
        
    gdf_lat_normal = route_to_geojson(G_lat, n_route_lat, "latest", "normal", metrics_lat, points_lat)
    gdf_lat_safe = route_to_geojson(G_lat, s_route_lat, "latest", "weather_safe", metrics_lat, points_lat)
    
    gdf_lat_normal.to_file(paths.DEMO_ROUTE_LATEST_NORMAL_PATH, driver="GeoJSON")
    gdf_lat_safe.to_file(paths.DEMO_ROUTE_LATEST_SAFE_PATH, driver="GeoJSON")
    
    with open(paths.ROUTE_COMPARISON_LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_lat, f, indent=2)
        
    # Create validation report
    create_routing_validation_report(warnings)
    logger.info("All demo route outputs exported successfully.")


def create_routing_validation_report(warnings=None):
    """Generate and write routing_validation_report.json."""
    if warnings is None:
        warnings = []
        
    # Check if files exist
    road_weights_top_rain_exists = paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH.exists()
    road_weights_latest_exists = paths.ROAD_RISK_WEIGHTS_LATEST_PATH.exists()
    
    top_rain_routes_created = (
        paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH.exists() and 
        paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH.exists()
    )
    latest_routes_created = (
        paths.DEMO_ROUTE_LATEST_NORMAL_PATH.exists() and 
        paths.DEMO_ROUTE_LATEST_SAFE_PATH.exists()
    )
    
    top_rain_comparison_exists = paths.ROUTE_COMPARISON_TOP_RAIN_PATH.exists()
    latest_comparison_exists = paths.ROUTE_COMPARISON_LATEST_PATH.exists()
    
    graph_loaded = False
    try:
        G = load_routing_graph()
        if len(G) > 0:
            graph_loaded = True
    except Exception as e:
        warnings.append(f"Failed to load graph: {e}")
        
    # Check output folder exists
    paths.ensure_data_dirs()
    
    status = "ok"
    if warnings:
        status = "ok_with_warnings"
    if not (top_rain_routes_created and latest_routes_created and graph_loaded):
        status = "failed"
        
    report = {
        "status": status,
        "warnings": warnings,
        "graph_loaded": graph_loaded,
        "road_risk_weights_top_rain_exists": road_weights_top_rain_exists,
        "road_risk_weights_latest_exists": road_weights_latest_exists,
        "top_rain_routes_created": top_rain_routes_created,
        "latest_routes_created": latest_routes_created,
        "top_rain_comparison_exists": top_rain_comparison_exists,
        "latest_comparison_exists": latest_comparison_exists,
        "official_emergency_dispatch_claimed": False,
        "official_flood_labels_claimed": False
    }
    
    with open(paths.ROUTING_VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Routing validation report written to {paths.ROUTING_VALIDATION_REPORT_PATH}")
    return report



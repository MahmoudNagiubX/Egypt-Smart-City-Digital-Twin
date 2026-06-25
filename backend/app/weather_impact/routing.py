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

ROUTE_HONESTY_NOTE = (
    "Routes are decision-support prototype outputs, not official emergency dispatch instructions."
)
MAX_ROUTE_SNAP_DISTANCE_M = 1500.0


class RoutingPointOutsideGraphError(ValueError):
    """Raised when a requested coordinate is too far from the routing graph."""


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
    weather_penalty_factor = 1.0 + 4.0 * (risk_score ** 2)
    
    # Apply multipliers for medium and high risk classes
    medium_risk_mask = (road_risk["predicted_risk_class"] == "medium")
    high_risk_mask = (road_risk["predicted_risk_class"] == "high")
    
    weather_penalty_factor = np.where(medium_risk_mask, weather_penalty_factor * 1.25, weather_penalty_factor)
    weather_penalty_factor = np.where(high_risk_mask, weather_penalty_factor * 1.75, weather_penalty_factor)
    
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


def _haversine_distance_m(lon1, lat1, lon2, lat2):
    """Return the great-circle distance between two WGS84 points in metres."""
    from math import asin, cos, radians, sin, sqrt

    lon1_rad, lat1_rad, lon2_rad, lat2_rad = map(
        radians, (lon1, lat1, lon2, lat2)
    )
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    return 6371008.8 * 2 * asin(sqrt(a))


def snap_coordinate_to_graph(G, lon, lat, max_distance_m=MAX_ROUTE_SNAP_DISTANCE_M):
    """Snap a coordinate to the graph and reject points outside the service area."""
    node = find_nearest_graph_node(G, lon, lat)
    node_lon = float(G.nodes[node]["x"])
    node_lat = float(G.nodes[node]["y"])
    distance_m = _haversine_distance_m(lon, lat, node_lon, node_lat)
    if distance_m > max_distance_m:
        raise RoutingPointOutsideGraphError(
            f"Coordinate ({lat:.6f}, {lon:.6f}) is outside the Nasr City routing graph "
            f"(nearest road node is {distance_m:.0f} m away)."
        )
    return node, distance_m


def build_custom_routes(origin, destination, event_type):
    """Compute normal and weather-weighted routes for arbitrary map coordinates."""
    if event_type not in ["top-rain", "latest"]:
        raise ValueError(f"Unsupported event_type: {event_type}")

    G = load_routing_graph()
    weights_path = (
        paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH
        if event_type == "top-rain"
        else paths.ROAD_RISK_WEIGHTS_LATEST_PATH
    )
    if not weights_path.exists():
        build_road_risk_weights(event_type)
    G = apply_risk_weights_to_graph(G, gpd.read_file(weights_path))

    origin_node, origin_snap_m = snap_coordinate_to_graph(
        G, origin["lon"], origin["lat"]
    )
    destination_node, destination_snap_m = snap_coordinate_to_graph(
        G, destination["lon"], destination["lat"]
    )
    if origin_node == destination_node:
        raise ValueError("Origin and destination snap to the same routing node.")

    normal_route = compute_route(
        G, origin_node, destination_node, "base_travel_time_sec"
    )
    safe_route = compute_route(G, origin_node, destination_node, "weather_weight")
    if normal_route is None or safe_route is None:
        raise ValueError(
            "No traversable route is available between the requested coordinates."
        )

    points_info = {
        "origin_lon": float(origin["lon"]),
        "origin_lat": float(origin["lat"]),
        "origin_zone_code": "custom",
        "dest_lon": float(destination["lon"]),
        "dest_lat": float(destination["lat"]),
        "destination_facility_name": "Custom destination",
        "destination_facility_type": "custom",
    }
    metrics = compare_routes(normal_route, safe_route, G, event_type, points_info)
    metrics["routes_identical"] = normal_route == safe_route
    quality, available = evaluate_safe_route_quality(metrics)
    metrics["safe_route_quality"] = quality
    metrics["safe_route_available"] = available
    metrics["quality_guard_passed"] = available

    normal_geojson = json.loads(
        route_to_geojson(
            G, normal_route, event_type, "normal", metrics, points_info
        ).to_json()
    )
    safe_geojson = json.loads(
        route_to_geojson(
            G, safe_route, event_type, "weather_safe", metrics, points_info
        ).to_json()
    )

    warnings = []
    if not available:
        warnings.append(
            "No distinct lower-risk alternative was found; the weather-safe route must not be "
            "presented as safer than the normal route."
        )

    comparison_keys = [
        "safe_route_available",
        "safe_route_quality",
        "risk_reduction_percent",
        "eta_tradeoff_percent",
        "avoided_high_risk_segments",
        "normal_distance_m",
        "safe_distance_m",
        "normal_weather_eta_sec",
        "safe_weather_eta_sec",
        "normal_mean_risk_score",
        "safe_mean_risk_score",
    ]
    comparison = {key: metrics[key] for key in comparison_keys}
    comparison["honesty_note"] = ROUTE_HONESTY_NOTE

    return {
        "status": "ok" if not warnings else "ok_with_warnings",
        "event_type": event_type,
        "origin": {
            "lat": float(origin["lat"]),
            "lon": float(origin["lon"]),
            "nearest_node": origin_node,
            "snap_distance_m": float(origin_snap_m),
        },
        "destination": {
            "lat": float(destination["lat"]),
            "lon": float(destination["lon"]),
            "nearest_node": destination_node,
            "snap_distance_m": float(destination_snap_m),
        },
        "normal_route": normal_geojson,
        "weather_safe_route": safe_geojson,
        "comparison": comparison,
        "warnings": warnings,
        "honesty_note": ROUTE_HONESTY_NOTE,
    }


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
        "timestamp": timestamp,
        "honesty_note": ROUTE_HONESTY_NOTE
    }
    
    return metrics


def find_candidate_origins(risk_layer, top_n=10):
    """Find top N high-risk zone centroids as candidate origins."""
    high_risk_zones = risk_layer[risk_layer["predicted_risk_class"] == "high"]
    if len(high_risk_zones) == 0:
        sorted_zones = risk_layer.sort_values("y_pred", ascending=False)
    else:
        sorted_zones = high_risk_zones.sort_values("y_pred", ascending=False)
        
    top_zones = sorted_zones.head(top_n)
    candidates = []
    for _, row in top_zones.iterrows():
        centroid = row["geometry"].centroid
        candidates.append({
            "zone_code": str(row["zone_code"]),
            "lon": float(centroid.x),
            "lat": float(centroid.y),
            "y_pred": float(row["y_pred"]),
            "predicted_risk_class": str(row["predicted_risk_class"])
        })
    return candidates


def find_candidate_destinations(facilities, origin_centroid, top_n=5):
    """Find top N closest/medium distance emergency facilities for an origin centroid."""
    dists = facilities.geometry.distance(origin_centroid)
    sorted_facs = facilities.copy()
    sorted_facs["distance"] = dists
    sorted_facs = sorted_facs.sort_values("distance")
    
    candidates = []
    for _, row in sorted_facs.head(top_n).iterrows():
        centroid = row["geometry"].centroid
        name = row.get("name")
        if pd.isna(name) or name is None or str(name).strip() == "" or str(name).lower() == "nan":
            # Fallback to facility type if name is missing
            fac_type = row.get("facility_type", "emergency_facility")
            name = f"Nasr City Emergency {str(fac_type).capitalize()}"
        candidates.append({
            "name": str(name),
            "facility_type": str(row.get("facility_type", "hospital")),
            "lon": float(centroid.x),
            "lat": float(centroid.y)
        })
    return candidates


def evaluate_candidate_route_pair(G, origin, destination, event_type):
    """Compute and evaluate a single candidate route pair."""
    origin_node = find_nearest_graph_node(G, origin["lon"], origin["lat"])
    dest_node = find_nearest_graph_node(G, destination["lon"], destination["lat"])
    
    normal_route = compute_route(G, origin_node, dest_node, "base_travel_time_sec")
    safe_route = compute_route(G, origin_node, dest_node, "weather_weight")
    
    if normal_route is None or safe_route is None:
        return None
        
    points_info = {
        "origin_lon": origin["lon"],
        "origin_lat": origin["lat"],
        "origin_zone_code": origin["zone_code"],
        "dest_lon": destination["lon"],
        "dest_lat": destination["lat"],
        "destination_facility_name": destination["name"],
        "destination_facility_type": destination["facility_type"]
    }
    
    metrics = compare_routes(normal_route, safe_route, G, event_type, points_info)
    routes_identical = (normal_route == safe_route)
    metrics["routes_identical"] = routes_identical
    
    dist_km = metrics["normal_distance_m"] / 1000.0
    
    return {
        "normal_route": normal_route,
        "safe_route": safe_route,
        "metrics": metrics,
        "points_info": points_info,
        "routes_identical": routes_identical,
        "distance_km": dist_km
    }


def evaluate_safe_route_quality(comparison):
    """Evaluate quality of the computed safe route compared to normal."""
    routes_identical = comparison.get("routes_identical", False)
    risk_red = comparison.get("risk_reduction_percent", 0.0)
    normal_risk = comparison.get("normal_mean_risk_score", 0.0)
    safe_risk = comparison.get("safe_mean_risk_score", 0.0)
    avoided_segments = comparison.get("avoided_high_risk_segments", 0)
    
    if routes_identical:
        return "rejected_identical_routes", False
        
    if risk_red < 0.0 or safe_risk > normal_risk:
        return "rejected_negative_risk_reduction", False
        
    if risk_red >= 5.0 and avoided_segments > 0:
        return "strong", True
    elif 0.0 <= risk_red < 5.0:
        return "weak_but_valid", True
    else:
        return "accepted", True


def select_best_quality_route_pair(event_type: str):
    """Search candidates and select the best demo route pair using the quality guard."""
    logger.info(f"Selecting best quality demo route pair for event type: {event_type}...")
    
    risk_layer = load_event_risk_layer(event_type)
    if len(risk_layer) == 0:
        raise ValueError(f"Risk layer for {event_type} is empty.")
        
    if not paths.NASR_CITY_FACILITIES_PATH.exists():
        raise FileNotFoundError(f"Emergency facilities GeoJSON not found at: {paths.NASR_CITY_FACILITIES_PATH}")
    facilities = gpd.read_file(paths.NASR_CITY_FACILITIES_PATH)
    if len(facilities) == 0:
        raise ValueError("Emergency facilities GeoJSON is empty.")
        
    G = load_routing_graph()
    
    if event_type == "top-rain":
        weights_path = paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH
    else:
        weights_path = paths.ROAD_RISK_WEIGHTS_LATEST_PATH
        
    if not weights_path.exists():
        build_road_risk_weights(event_type)
    road_risk_df = gpd.read_file(weights_path)
    G = apply_risk_weights_to_graph(G, road_risk_df)
    
    origins = find_candidate_origins(risk_layer, top_n=15)
    candidates_evaluated = []
    
    for origin in origins:
        origin_geom = risk_layer[risk_layer["zone_code"] == origin["zone_code"]].iloc[0]["geometry"]
        origin_centroid = origin_geom.centroid
        destinations = find_candidate_destinations(facilities, origin_centroid, top_n=15)
        
        for destination in destinations:
            res = evaluate_candidate_route_pair(G, origin, destination, event_type)
            if res is not None:
                metrics = res["metrics"]
                quality, available = evaluate_safe_route_quality(metrics)
                
                score = 0.0
                if available:
                    score += 1000.0
                    score += metrics["risk_reduction_percent"] * 50.0
                    if metrics["avoided_high_risk_segments"] > 0:
                        score += metrics["avoided_high_risk_segments"] * 20.0
                    score -= metrics["eta_tradeoff_percent"] * 1.5
                else:
                    score += metrics["risk_reduction_percent"] * 50.0
                    score -= metrics["eta_tradeoff_percent"] * 1.5
                    
                dist_km = res["distance_km"]
                if 2.0 <= dist_km <= 10.0:
                    score += 200.0
                elif dist_km < 1.0:
                    score -= 500.0
                elif dist_km > 12.0:
                    score -= 100.0
                    
                res["score"] = score
                res["safe_route_quality"] = quality
                res["safe_route_available"] = available
                res["quality_guard_passed"] = available
                candidates_evaluated.append(res)
                
    if not candidates_evaluated:
        raise ValueError(f"No candidate route pairs could be computed for event: {event_type}")
        
    pos_risk_count = sum(1 for c in candidates_evaluated if c["safe_route_available"])
    diff_routes_count = sum(1 for c in candidates_evaluated if not c["routes_identical"])
    
    candidates_evaluated = sorted(candidates_evaluated, key=lambda x: x["score"], reverse=True)
    best_candidate = candidates_evaluated[0]
    
    logger.info(f"Best candidate selected with score: {best_candidate['score']:.2f}")
    logger.info(f"Origin: {best_candidate['points_info']['origin_zone_code']}, Destination: {best_candidate['points_info']['destination_facility_name']}")
    logger.info(f"Distance: {best_candidate['distance_km']:.2f} km, Quality: {best_candidate['safe_route_quality']}, Available: {best_candidate['safe_route_available']}")
    
    best_candidate["candidate_pairs_tested"] = len(candidates_evaluated)
    best_candidate["candidate_pairs_with_positive_risk_reduction"] = pos_risk_count
    best_candidate["candidate_pairs_with_different_routes"] = diff_routes_count
    
    return best_candidate


def build_demo_routes(event_type: str):
    """Build and compute normal vs weather-safe demo routes for an event type using quality-guarded candidate search."""
    best_candidate = select_best_quality_route_pair(event_type)
    
    G = load_routing_graph()
    if event_type == "top-rain":
        weights_path = paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH
    else:
        weights_path = paths.ROAD_RISK_WEIGHTS_LATEST_PATH
    road_risk_df = gpd.read_file(weights_path)
    G = apply_risk_weights_to_graph(G, road_risk_df)
    
    normal_route = best_candidate["normal_route"]
    safe_route = best_candidate["safe_route"]
    metrics = best_candidate["metrics"]
    points_info = best_candidate["points_info"]
    
    metrics["safe_route_quality"] = best_candidate["safe_route_quality"]
    metrics["safe_route_available"] = best_candidate["safe_route_available"]
    metrics["quality_guard_passed"] = best_candidate["quality_guard_passed"]
    
    metrics["candidate_search_used"] = True
    metrics["candidate_pairs_tested"] = best_candidate["candidate_pairs_tested"]
    metrics["candidate_pairs_with_positive_risk_reduction"] = best_candidate["candidate_pairs_with_positive_risk_reduction"]
    metrics["candidate_pairs_with_different_routes"] = best_candidate["candidate_pairs_with_different_routes"]
    
    metrics["selected_origin_zone_code"] = points_info["origin_zone_code"]
    metrics["selected_destination_facility_name"] = points_info["destination_facility_name"]
    
    if best_candidate["safe_route_available"]:
        metrics["selected_reason"] = (
            f"Best quality candidate found. Quality: {best_candidate['safe_route_quality']}. "
            f"Risk reduction: {metrics['risk_reduction_percent']:.2f}%. Distance: {best_candidate['distance_km']:.2f} km."
        )
    else:
        metrics["selected_reason"] = (
            "Least bad candidate selected. Warning: No candidate route reduced model-estimated risk; "
            f"safe route should not be presented as safer for this event. Distance: {best_candidate['distance_km']:.2f} km."
        )
        
    metrics["routes_identical"] = best_candidate["routes_identical"]
    
    metrics["origin_lon"] = points_info["origin_lon"]
    metrics["origin_lat"] = points_info["origin_lat"]
    metrics["dest_lon"] = points_info["dest_lon"]
    metrics["dest_lat"] = points_info["dest_lat"]
    
    return normal_route, safe_route, G, metrics


def route_to_geojson(G, route_nodes, event_type, route_type, metrics, points_info=None):
    """Convert a route node list to a GeoJSON FeatureCollection."""
    from shapely.geometry import LineString
    
    if len(route_nodes) < 2:
        line = LineString()
    else:
        coordinates = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route_nodes]
        line = LineString(coordinates)
        
    is_safe = (route_type == "weather_safe")
    prefix = "safe" if is_safe else "normal"
    
    p_info = points_info if points_info is not None else metrics
    
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
        "origin_lon": float(p_info.get("origin_lon", 0.0)),
        "origin_lat": float(p_info.get("origin_lat", 0.0)),
        "destination_lon": float(p_info.get("dest_lon", p_info.get("destination_lon", 0.0))),
        "destination_lat": float(p_info.get("dest_lat", p_info.get("destination_lat", 0.0))),
        "destination_facility_name": p_info.get("destination_facility_name", "Unknown"),
        "honesty_note": ROUTE_HONESTY_NOTE
    }
    
    gdf = gpd.GeoDataFrame([properties], geometry=[line], crs="EPSG:4326")
    return gdf


def export_demo_route_outputs():
    """Build, compare, and export all demo routes and comparisons using candidate search and quality guard."""
    logger.info("Exporting all demo route outputs...")
    warnings = []
    
    n_route_top, s_route_top, G_top, metrics_top = build_demo_routes("top-rain")
    
    if not metrics_top.get("safe_route_available", True):
        warnings.append("Top-rain: No candidate route reduced model-estimated risk; safe route should not be presented as safer for this event.")
    elif metrics_top.get("routes_identical", n_route_top == s_route_top):
        warnings.append("Top-rain: normal and safe routes are identical, no safer alternative path found.")
        
    gdf_top_normal = route_to_geojson(G_top, n_route_top, "top-rain", "normal", metrics_top, metrics_top)
    gdf_top_safe = route_to_geojson(G_top, s_route_top, "top-rain", "weather_safe", metrics_top, metrics_top)
    
    gdf_top_normal.to_file(paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH, driver="GeoJSON")
    gdf_top_safe.to_file(paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH, driver="GeoJSON")
    
    with open(paths.ROUTE_COMPARISON_TOP_RAIN_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_top, f, indent=2)
        
    n_route_lat, s_route_lat, G_lat, metrics_lat = build_demo_routes("latest")
    
    if not metrics_lat.get("safe_route_available", True):
        warnings.append("Latest: No candidate route reduced model-estimated risk; safe route should not be presented as safer for this event.")
    elif metrics_lat.get("routes_identical", n_route_lat == s_route_lat):
        warnings.append("Latest: normal and safe routes are identical, no safer alternative path found.")
        
    gdf_lat_normal = route_to_geojson(G_lat, n_route_lat, "latest", "normal", metrics_lat, metrics_lat)
    gdf_lat_safe = route_to_geojson(G_lat, s_route_lat, "latest", "weather_safe", metrics_lat, metrics_lat)
    
    gdf_lat_normal.to_file(paths.DEMO_ROUTE_LATEST_NORMAL_PATH, driver="GeoJSON")
    gdf_lat_safe.to_file(paths.DEMO_ROUTE_LATEST_SAFE_PATH, driver="GeoJSON")
    
    with open(paths.ROUTE_COMPARISON_LATEST_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_lat, f, indent=2)
        
    create_routing_validation_report(warnings)
    logger.info("All demo route outputs exported successfully.")


def create_routing_validation_report(warnings=None):
    """Generate and write routing_validation_report.json."""
    if warnings is None:
        warnings = []
        
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
        
    safe_top_available = True
    safe_lat_available = True
    
    if top_rain_comparison_exists:
        try:
            with open(paths.ROUTE_COMPARISON_TOP_RAIN_PATH, "r", encoding="utf-8") as f:
                comp_top = json.load(f)
                safe_top_available = comp_top.get("safe_route_available", True)
        except Exception:
            pass
            
    if latest_comparison_exists:
        try:
            with open(paths.ROUTE_COMPARISON_LATEST_PATH, "r", encoding="utf-8") as f:
                comp_lat = json.load(f)
                safe_lat_available = comp_lat.get("safe_route_available", True)
        except Exception:
            pass
            
    paths.ensure_data_dirs()
    
    if not (top_rain_routes_created and latest_routes_created and graph_loaded):
        status = "failed"
    elif not safe_top_available or not safe_lat_available:
        status = "ok_with_warnings"
    else:
        status = "ok"
        
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


def audit_emergency_facility_reachability(G=None):
    """
    Perform a reachability and snap distance audit for all emergency facilities.
    """
    import math
    import networkx as nx
    import pandas as pd
    import geopandas as gpd
    from . import paths
    
    logger.info("Running emergency facility reachability audit...")
    
    if G is None:
        G = load_routing_graph()
        
    if not paths.NASR_CITY_FACILITIES_PATH.exists():
        raise FileNotFoundError(f"Emergency facilities GeoJSON not found at: {paths.NASR_CITY_FACILITIES_PATH}")
    facilities = gpd.read_file(paths.NASR_CITY_FACILITIES_PATH)
    
    # Snapping origin: NSR-GRID-119 centroid
    origin_node = None
    if paths.NASR_CITY_GRID_PATH.exists():
        try:
            grid_gdf = gpd.read_file(paths.NASR_CITY_GRID_PATH)
            cell_119 = grid_gdf[grid_gdf["zone_code"] == "NSR-GRID-119"]
            if len(cell_119) > 0:
                c = cell_119.geometry.centroid.iloc[0]
                origin_node = find_nearest_graph_node(G, c.x, c.y)
                logger.info(f"Using NSR-GRID-119 centroid nearest node {origin_node} as reachability reference.")
            else:
                logger.warning("NSR-GRID-119 not found in grid GeoJSON. Falling back to first grid cell.")
                c = grid_gdf.geometry.centroid.iloc[0]
                origin_node = find_nearest_graph_node(G, c.x, c.y)
        except Exception as e:
            logger.warning(f"Error finding reference origin node: {e}")
            
    if origin_node is None:
        # Fallback to any node in the graph
        origin_node = list(G.nodes)[0]
        logger.warning(f"Using fallback origin node {origin_node}")
        
    audit_rows = []
    
    for idx, row in facilities.iterrows():
        # Get or generate ID
        fac_id = row.get("id")
        if pd.isna(fac_id) or fac_id is None:
            fac_id = row.get("facility_id")
        if pd.isna(fac_id) or fac_id is None:
            fac_id = f"FAC-{idx+1:03d}"
            
        name = row.get("name")
        if pd.isna(name) or name is None or str(name).strip() == "" or str(name).lower() == "nan":
            fac_type = row.get("facility_type", "emergency_facility")
            name = f"Nasr City Emergency {str(fac_type).capitalize()}"
            
        fac_type = row.get("facility_type")
        if pd.isna(fac_type) or fac_type is None:
            fac_type = row.get("amenity", "emergency_facility")
            
        geom = row["geometry"]
        lon = float(geom.x)
        lat = float(geom.y)
        
        # Snap to graph
        nearest_node = find_nearest_graph_node(G, lon, lat)
        
        # Calculate snap distance using degrees to meters approximation
        node_x = G.nodes[nearest_node]['x']
        node_y = G.nodes[nearest_node]['y']
        
        avg_lat = math.radians((lat + node_y) / 2.0)
        dy = (lat - node_y) * 111320.0
        dx = (lon - node_x) * 111320.0 * math.cos(avg_lat)
        snap_distance_m = float(math.sqrt(dx*dx + dy*dy))
        
        # Check reachability on graph
        reachable = False
        warning = ""
        try:
            reachable = nx.has_path(G, origin_node, nearest_node)
        except Exception as e:
            warning = f"Reachability check failed: {e}"
            
        if not reachable and not warning:
            warning = f"No path from reference node {origin_node} to snapped node {nearest_node}"
            
        if snap_distance_m > 500.0:
            if warning:
                warning += "; "
            warning += f"Large snapping distance: {snap_distance_m:.1f}m"
            
        audit_rows.append({
            "facility_id": str(fac_id),
            "facility_name": str(name),
            "facility_type": str(fac_type),
            "lon": lon,
            "lat": lat,
            "nearest_graph_node": int(nearest_node),
            "snap_distance_m": snap_distance_m,
            "reachable_on_graph": bool(reachable),
            "warning": warning
        })
        
    df = pd.DataFrame(audit_rows)
    paths.ensure_data_dirs()
    df.to_csv(paths.EMERGENCY_FACILITY_REACHABILITY_AUDIT_PATH, index=False, encoding="utf-8")
    logger.info(f"Facility reachability audit written to {paths.EMERGENCY_FACILITY_REACHABILITY_AUDIT_PATH}")
    return audit_rows


def audit_high_risk_zone_best_facility_routes(G=None):
    """
    Audit high-risk zones to find the best emergency facility route under weather risk.
    """
    import pandas as pd
    import geopandas as gpd
    import networkx as nx
    from . import paths
    
    logger.info("Running high-risk zone best facility routing audit...")
    
    if G is None:
        G = load_routing_graph()
        
    # Load top-rain risk layer
    if not paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH.exists():
        raise FileNotFoundError(f"Top-rain risk layer GeoJSON not found at: {paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH}")
    risk_layer = gpd.read_file(paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH)
    
    # Select high-risk zones
    high_risk_zones = risk_layer[risk_layer["predicted_risk_class"] == "high"]
    if len(high_risk_zones) > 50:
        high_risk_zones = risk_layer.sort_values(by="y_pred", ascending=False).head(50)
    elif len(high_risk_zones) < 10:
        high_risk_zones = risk_layer.sort_values(by="y_pred", ascending=False).head(10)
        
    logger.info(f"Selected {len(high_risk_zones)} zones for best facility audit.")
    
    # Apply top-rain risk weights to graph
    if not paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH.exists():
        logger.warning("Road risk weights top rain not found. Building them...")
        build_road_risk_weights("top-rain")
    road_risk_df = gpd.read_file(paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH)
    G = apply_risk_weights_to_graph(G, road_risk_df)
    
    # Load facilities
    if not paths.NASR_CITY_FACILITIES_PATH.exists():
        raise FileNotFoundError(f"Emergency facilities GeoJSON not found at: {paths.NASR_CITY_FACILITIES_PATH}")
    facilities = gpd.read_file(paths.NASR_CITY_FACILITIES_PATH)
    
    # Identify hospitals
    hospitals = facilities[
        facilities["facility_type"].str.lower().str.contains("hospital|clinic|medical|health", na=False) |
        facilities["amenity"].str.lower().str.contains("hospital|clinic|medical|health", na=False) |
        facilities["name"].str.lower().str.contains("hospital|clinic|medical|health|مستشفى|عيادة", na=False)
    ]
    if len(hospitals) == 0:
        logger.warning("No hospitals/clinics identified. Using all emergency facilities as candidates.")
        hospitals = facilities
        
    best_routes_rows = []
    
    for _, zone_row in high_risk_zones.iterrows():
        zone_code = zone_row["zone_code"]
        zone_risk_score = zone_row["y_pred"]
        zone_risk_class = zone_row["predicted_risk_class"]
        
        centroid = zone_row["geometry"].centroid
        origin_lon = float(centroid.x)
        origin_lat = float(centroid.y)
        
        origin_node = find_nearest_graph_node(G, origin_lon, origin_lat)
        
        candidate_results = []
        for idx, fac_row in hospitals.iterrows():
            fac_id = fac_row.get("id")
            if pd.isna(fac_id) or fac_id is None:
                fac_id = fac_row.get("facility_id")
            if pd.isna(fac_id) or fac_id is None:
                fac_id = f"FAC-{idx+1:03d}"
                
            fac_name = fac_row.get("name")
            if pd.isna(fac_name) or fac_name is None or str(fac_name).strip() == "" or str(fac_name).lower() == "nan":
                fac_type = fac_row.get("facility_type", "hospital")
                fac_name = f"Nasr City Emergency {str(fac_type).capitalize()}"
                
            fac_type = fac_row.get("facility_type")
            if pd.isna(fac_type) or fac_type is None:
                fac_type = fac_row.get("amenity", "hospital")
                
            fac_geom = fac_row["geometry"]
            fac_lon = float(fac_geom.x)
            fac_lat = float(fac_geom.y)
            
            dest_node = find_nearest_graph_node(G, fac_lon, fac_lat)
            
            normal_route = compute_route(G, origin_node, dest_node, "base_travel_time_sec")
            safe_route = compute_route(G, origin_node, dest_node, "weather_weight")
            
            if normal_route is None or safe_route is None:
                continue
                
            points_info = {
                "origin_lon": origin_lon,
                "origin_lat": origin_lat,
                "origin_zone_code": zone_code,
                "dest_lon": fac_lon,
                "dest_lat": fac_lat,
                "destination_facility_name": fac_name,
                "destination_facility_type": fac_type
            }
            
            metrics = compare_routes(normal_route, safe_route, G, "top-rain", points_info)
            quality, available = evaluate_safe_route_quality(metrics)
            
            candidate_results.append({
                "facility_id": fac_id,
                "facility_name": fac_name,
                "facility_type": fac_type,
                "fac_lon": fac_lon,
                "fac_lat": fac_lat,
                "metrics": metrics,
                "safe_route_available": available,
                "safe_route_quality": quality,
                "route_found": True,
                "warning": ""
            })
            
        if not candidate_results:
            # No routes found to any candidate hospitals
            best_routes_rows.append({
                "zone_code": str(zone_code),
                "zone_risk_score": float(zone_risk_score),
                "zone_risk_class": str(zone_risk_class),
                "origin_lon": origin_lon,
                "origin_lat": origin_lat,
                "best_facility_id": "None",
                "best_facility_name": "None",
                "best_facility_type": "None",
                "facility_lon": 0.0,
                "facility_lat": 0.0,
                "normal_distance_m": 0.0,
                "safe_distance_m": 0.0,
                "normal_weather_eta_sec": 0.0,
                "safe_weather_eta_sec": 0.0,
                "risk_reduction_percent": 0.0,
                "eta_tradeoff_percent": 0.0,
                "safe_route_available": False,
                "safe_route_quality": "none",
                "route_found": False,
                "warning": "No route found to any candidate hospitals/clinics."
            })
        else:
            # Sort candidates by:
            # 1. safe_route_available (True first)
            # 2. safe_weather_eta_sec (lowest first)
            # 3. safe_mean_risk_score (lower first)
            # 4. safe_distance_m (lowest first)
            
            def sort_key(item):
                metrics = item["metrics"]
                safe_eta = metrics.get("safe_weather_eta_sec", float('inf'))
                safe_risk = metrics.get("safe_mean_risk_score", float('inf'))
                safe_dist = metrics.get("safe_distance_m", float('inf'))
                return (
                    item["safe_route_available"],
                    -safe_eta,
                    -safe_risk,
                    -safe_dist
                )
                
            candidate_results.sort(key=sort_key, reverse=True)
            best_item = candidate_results[0]
            best_metrics = best_item["metrics"]
            
            best_routes_rows.append({
                "zone_code": str(zone_code),
                "zone_risk_score": float(zone_risk_score),
                "zone_risk_class": str(zone_risk_class),
                "origin_lon": origin_lon,
                "origin_lat": origin_lat,
                "best_facility_id": str(best_item["facility_id"]),
                "best_facility_name": str(best_item["facility_name"]),
                "best_facility_type": str(best_item["facility_type"]),
                "facility_lon": float(best_item["fac_lon"]),
                "facility_lat": float(best_item["fac_lat"]),
                "normal_distance_m": float(best_metrics.get("normal_distance_m", 0.0)),
                "safe_distance_m": float(best_metrics.get("safe_distance_m", 0.0)),
                "normal_weather_eta_sec": float(best_metrics.get("normal_weather_eta_sec", 0.0)),
                "safe_weather_eta_sec": float(best_metrics.get("safe_weather_eta_sec", 0.0)),
                "risk_reduction_percent": float(best_metrics.get("risk_reduction_percent", 0.0)),
                "eta_tradeoff_percent": float(best_metrics.get("eta_tradeoff_percent", 0.0)),
                "safe_route_available": bool(best_item["safe_route_available"]),
                "safe_route_quality": str(best_item["safe_route_quality"]),
                "route_found": True,
                "warning": best_item["warning"]
            })
            
    df = pd.DataFrame(best_routes_rows)
    paths.ensure_data_dirs()
    df.to_csv(paths.HIGH_RISK_ZONE_BEST_FACILITY_ROUTES_PATH, index=False, encoding="utf-8")
    logger.info(f"High-risk zone best facility routes written to {paths.HIGH_RISK_ZONE_BEST_FACILITY_ROUTES_PATH}")
    return best_routes_rows


def load_live_weather_risk_layer():
    """Load the live weather risk layer GeoJSON, generating it if it doesn't exist."""
    path = paths.LIVE_WEATHER_RISK_GEOJSON_PATH
    if not path.exists():
        logger.info("Live weather risk layer not found. Generating it now...")
        from . import service
        service.generate_live_weather_risk_layer()
        
    if not path.exists():
        raise FileNotFoundError(f"Live weather risk layer GeoJSON not found at: {path}")
        
    logger.info(f"Loading live weather risk layer from {path}")
    return gpd.read_file(path)


def build_live_road_risk_weights():
    """Apply live weather zone-level risk predictions to road segments and calculate routing weights."""
    logger.info("Building live road risk weights...")
    
    if not paths.NASR_CITY_ROADS_PATH.exists():
        raise FileNotFoundError(f"Nasr City roads GeoJSON not found at: {paths.NASR_CITY_ROADS_PATH}")
        
    # 1. Load road segments, roads mapping, and live risk layer
    roads_gdf = gpd.read_file(paths.NASR_CITY_ROADS_PATH)
    roads_gdf["road_id"] = [f"NSR-ROAD-{i+1:05d}" for i in range(len(roads_gdf))]
    
    roads_zones = load_road_segments()
    risk_layer = load_live_weather_risk_layer()
    
    # 2. Merge road segments with their zone assignments
    merged = roads_gdf.merge(roads_zones[["road_id", "zone_code"]], on="road_id", how="left")
    
    # 3. Merge with zone-level live risk predictions
    road_risk = merged.merge(
        risk_layer[[
            "zone_code", "live_predicted_score", "live_risk_class", 
            "rain_24h_mm", "max_precipitation_probability"
        ]], 
        on="zone_code", 
        how="left"
    )
    
    # Load live weather summary to check rain_risk_expected
    rain_risk_expected = False
    if paths.LIVE_WEATHER_SUMMARY_PATH.exists():
        try:
            with open(paths.LIVE_WEATHER_SUMMARY_PATH, "r", encoding="utf-8") as f:
                summary = json.load(f)
                rain_risk_expected = bool(summary.get("rain_risk_expected", False))
        except Exception as e:
            logger.warning(f"Failed to read live weather summary: {e}")
            
    # 4. Fill missing values safely
    road_risk["live_predicted_score"] = road_risk["live_predicted_score"].fillna(0.0).astype(float)
    road_risk["live_risk_class"] = road_risk["live_risk_class"].fillna("low")
    
    # If live_weather_risk did not have rain_24h_mm, fill with fallback from summary
    if "rain_24h_mm" in road_risk.columns:
        road_risk["rain_24h_mm"] = road_risk["rain_24h_mm"].fillna(0.0).astype(float)
    else:
        road_risk["rain_24h_mm"] = 0.0
        
    if "max_precipitation_probability" in road_risk.columns:
        road_risk["max_precipitation_probability"] = road_risk["max_precipitation_probability"].fillna(0.0).astype(float)
    else:
        road_risk["max_precipitation_probability"] = 0.0
        
    # 5. Normal weight calculation
    normal_weight = road_risk["travel_time"].copy()
    speed_denom = road_risk["speed_kph"].fillna(50.0).replace(0, 50.0)
    fallback_time = road_risk["length"] / (speed_denom / 3.6)
    normal_weight = normal_weight.fillna(fallback_time)
    
    # 6. Penalty Logic
    risk_score = np.clip(road_risk["live_predicted_score"], 0.0, 1.0)
    
    if rain_risk_expected:
        weather_penalty_factor = 1.0 + 4.0 * (risk_score ** 2)
        medium_risk_mask = (road_risk["live_risk_class"] == "medium")
        high_risk_mask = (road_risk["live_risk_class"] == "high")
        weather_penalty_factor = np.where(medium_risk_mask, weather_penalty_factor * 1.20, weather_penalty_factor)
        weather_penalty_factor = np.where(high_risk_mask, weather_penalty_factor * 1.75, weather_penalty_factor)
    else:
        weather_penalty_factor = 1.0 + 1.25 * (risk_score ** 2)
        
    live_weather_weight = normal_weight * weather_penalty_factor
    
    # Add columns
    road_risk["base_travel_time_sec"] = normal_weight
    road_risk["live_weather_penalty_factor"] = weather_penalty_factor
    road_risk["live_weather_weight"] = live_weather_weight
    
    # Select columns to keep
    keep_cols = [
        "u", "v", "key", "zone_code", "length", 
        "base_travel_time_sec", "live_predicted_score", 
        "live_risk_class", "live_weather_penalty_factor", 
        "live_weather_weight", "rain_24h_mm", "max_precipitation_probability", "geometry"
    ]
    actual_cols = [c for c in keep_cols if c in road_risk.columns]
    
    result_gdf = gpd.GeoDataFrame(road_risk[actual_cols], geometry="geometry", crs="EPSG:4326")
    
    # Export
    out_path = paths.LIVE_ROAD_RISK_WEIGHTS_GEOJSON_PATH
    result_gdf.to_file(out_path, driver="GeoJSON")
    logger.info(f"Saved live road risk weights to {out_path} (rows: {len(result_gdf)})")
    
    return result_gdf


def apply_live_risk_weights_to_graph(G, road_risk_df):
    """Update Graph G edge attributes with weights from road_risk_df for live weather routing."""
    logger.info("Applying live risk weights to graph edges...")
    
    weights_dict = {}
    for idx, row in road_risk_df.iterrows():
        edge_key = (int(row["u"]), int(row["v"]), int(row["key"]))
        weights_dict[edge_key] = {
            "base_travel_time_sec": float(row["base_travel_time_sec"]),
            "live_weather_weight": float(row["live_weather_weight"]),
            "live_risk_class": str(row["live_risk_class"]),
            "live_predicted_score": float(row["live_predicted_score"]),
            "length": float(row["length"])
        }
        
    for u, v, k, data in G.edges(keys=True, data=True):
        edge_key = (u, v, k)
        if edge_key in weights_dict:
            data.update(weights_dict[edge_key])
        else:
            length = float(data.get("length", 10.0))
            speed = float(data.get("speed_kph", 50.0))
            travel_time = float(data.get("travel_time", length / (speed / 3.6)))
            data["base_travel_time_sec"] = travel_time
            data["live_weather_weight"] = travel_time
            data["live_risk_class"] = "low"
            data["live_predicted_score"] = 0.0
            
    return G


def compare_live_routes(normal_route, safe_route, G):
    """Compare normal vs live weather-safe route metrics using live risk scores."""
    logger.info("Comparing live normal and weather-safe routes...")
    
    normal_edges = get_route_edge_data(G, normal_route, "base_travel_time_sec")
    safe_edges = get_route_edge_data(G, safe_route, "live_weather_weight")
    
    normal_dist = sum_route_metric(normal_edges, "length")
    safe_dist = sum_route_metric(safe_edges, "length")
    
    normal_base_eta = sum_route_metric(normal_edges, "base_travel_time_sec")
    safe_base_eta = sum_route_metric(safe_edges, "base_travel_time_sec")
    
    normal_weather_eta = sum_route_metric(normal_edges, "live_weather_weight")
    safe_weather_eta = sum_route_metric(safe_edges, "live_weather_weight")
    
    normal_high_risk = sum(1 for data in normal_edges if data.get("live_risk_class") == "high")
    safe_high_risk = sum(1 for data in safe_edges if data.get("live_risk_class") == "high")
    avoided_high_risk = normal_high_risk - safe_high_risk
    
    normal_mean_risk = sum(float(data.get("live_predicted_score", 0.0)) for data in normal_edges) / len(normal_edges) if normal_edges else 0.0
    safe_mean_risk = sum(float(data.get("live_predicted_score", 0.0)) for data in safe_edges) / len(safe_edges) if safe_edges else 0.0
    
    risk_red = 0.0
    if normal_mean_risk > 0.0:
        risk_red = ((normal_mean_risk - safe_mean_risk) / normal_mean_risk) * 100.0
        
    eta_tradeoff = 0.0
    if normal_base_eta > 0.0:
        eta_tradeoff = ((safe_base_eta - normal_base_eta) / normal_base_eta) * 100.0
        
    routes_identical = (normal_route == safe_route)
    
    safe_route_available = (
        (not routes_identical) and 
        (safe_mean_risk <= normal_mean_risk) and 
        (risk_red >= 0.0)
    )
    
    if routes_identical or risk_red <= 0.0:
        safe_route_quality = "no_distinct_safer_alternative"
    elif risk_red >= 5.0:
        safe_route_quality = "strong"
    else:
        safe_route_quality = "weak_but_valid"
        
    metrics = {
        "normal_distance_m": float(normal_dist),
        "safe_distance_m": float(safe_dist),
        "normal_weather_eta_sec": float(normal_weather_eta),
        "safe_weather_eta_sec": float(safe_weather_eta),
        "normal_mean_live_risk_score": float(normal_mean_risk),
        "safe_mean_live_risk_score": float(safe_mean_risk),
        "live_high_risk_segment_count_normal": int(normal_high_risk),
        "live_high_risk_segment_count_safe": int(safe_high_risk),
        "avoided_high_risk_segments": int(avoided_high_risk),
        "risk_reduction_percent": float(risk_red),
        "eta_tradeoff_percent": float(eta_tradeoff),
        "routes_identical": bool(routes_identical),
        "safe_route_available": bool(safe_route_available),
        "safe_route_quality": safe_route_quality,
        "honesty_note": "Routes are decision-support prototype outputs based on model-estimated live weather-impact risk, not official emergency dispatch instructions."
    }
    
    return metrics


def live_route_to_geojson(G, route_nodes, route_type, metrics, points_info):
    """Convert a live route node list to a GeoJSON FeatureCollection."""
    from shapely.geometry import LineString
    
    if len(route_nodes) < 2:
        line = LineString()
    else:
        coordinates = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route_nodes]
        line = LineString(coordinates)
        
    is_safe = (route_type == "weather_safe")
    prefix = "safe" if is_safe else "normal"
    
    properties = {
        "route_type": route_type,
        "mode": "live_weather",
        "distance_m": float(metrics.get(f"{prefix}_distance_m", 0.0)),
        "base_eta_sec": float(metrics.get(f"{prefix}_weather_eta_sec", 0.0)),
        "weather_eta_sec": float(metrics.get(f"{prefix}_weather_eta_sec", 0.0)),
        "mean_risk_score": float(metrics.get(f"{prefix}_mean_live_risk_score", 0.0)),
        "high_risk_segment_count": int(metrics.get(f"live_high_risk_segment_count_{prefix}", 0)),
        "origin_lon": float(points_info["origin"]["lon"]),
        "origin_lat": float(points_info["origin"]["lat"]),
        "destination_lon": float(points_info["destination"]["lon"]),
        "destination_lat": float(points_info["destination"]["lat"]),
        "honesty_note": "Live predictions are model-estimated weather-impact risk scores, not verified flood incident labels."
    }
    
    gdf = gpd.GeoDataFrame([properties], geometry=[line], crs="EPSG:4326")
    return gdf


def compute_live_custom_route(origin, destination, route_preference="both", refresh_live_weather=False):
    """Compute live weather-aware routes and return comparison metrics and GeoJSON overlays."""
    if refresh_live_weather:
        logger.info("Refreshing live weather risk layer as requested...")
        from . import service
        service.generate_live_weather_risk_layer()
        
    G = load_routing_graph()
    
    weights_path = paths.LIVE_ROAD_RISK_WEIGHTS_GEOJSON_PATH
    if not weights_path.exists():
        build_live_road_risk_weights()
    road_risk_df = gpd.read_file(weights_path)
    G = apply_live_risk_weights_to_graph(G, road_risk_df)
    
    origin_node, origin_snap_m = snap_coordinate_to_graph(G, origin["lon"], origin["lat"])
    destination_node, destination_snap_m = snap_coordinate_to_graph(G, destination["lon"], destination["lat"])
    
    if origin_node == destination_node:
        raise ValueError("Origin and destination snap to the same routing node.")
        
    normal_route = compute_route(G, origin_node, destination_node, "base_travel_time_sec")
    safe_route = compute_route(G, origin_node, destination_node, "live_weather_weight")
    
    if normal_route is None or safe_route is None:
        raise ValueError("No traversable route is available between the requested coordinates.")
        
    rain_risk_expected = False
    live_weather_summary = {
        "rain_1h_mm": 0.0,
        "rain_3h_mm": 0.0,
        "rain_6h_mm": 0.0,
        "rain_24h_mm": 0.0,
        "max_precipitation_probability": 0.0
    }
    if paths.LIVE_WEATHER_SUMMARY_PATH.exists():
        try:
            with open(paths.LIVE_WEATHER_SUMMARY_PATH, "r", encoding="utf-8") as f:
                summary = json.load(f)
                rain_risk_expected = bool(summary.get("rain_risk_expected", False))
                forecast = summary.get("forecast_window", {})
                for key in live_weather_summary:
                    live_weather_summary[key] = float(forecast.get(key, 0.0))
        except Exception as e:
            logger.warning(f"Failed to read live weather summary: {e}")
            
    metrics = compare_live_routes(normal_route, safe_route, G)
    
    if not rain_risk_expected and metrics["risk_reduction_percent"] < 5.0:
        metrics["safe_route_quality"] = "normal_route_preferred"
        
    if not rain_risk_expected:
        recommendation = "normal_route_acceptable"
        metrics["honesty_note"] = (
            "Live route recommendations are decision-support prototype outputs. "
            "No meaningful rain risk is expected, so the normal route is acceptable."
        )
    elif metrics["safe_route_available"]:
        recommendation = "weather_safe_route_recommended"
    else:
        recommendation = "no_distinct_safer_alternative"
        
    points_info = {"origin": origin, "destination": destination}
    normal_geojson = json.loads(live_route_to_geojson(G, normal_route, "normal", metrics, points_info).to_json())
    safe_geojson = json.loads(live_route_to_geojson(G, safe_route, "weather_safe", metrics, points_info).to_json())
    
    return {
        "status": "ok" if not (metrics["safe_route_quality"] in ["no_distinct_safer_alternative", "normal_route_preferred"]) else "ok_with_warnings",
        "mode": "live_weather",
        "rain_risk_expected": rain_risk_expected,
        "recommendation": recommendation,
        "origin": {
            "lat": float(origin["lat"]),
            "lon": float(origin["lon"]),
            "nearest_node": origin_node,
            "snap_distance_m": float(origin_snap_m),
        },
        "destination": {
            "lat": float(destination["lat"]),
            "lon": float(destination["lon"]),
            "nearest_node": destination_node,
            "snap_distance_m": float(destination_snap_m),
        },
        "normal_route": normal_geojson,
        "weather_safe_route": safe_geojson,
        "comparison": metrics,
        "live_weather_summary": live_weather_summary,
        "honesty_note": "Routes are decision-support prototype outputs based on model-estimated live weather-impact risk, not official emergency dispatch instructions."
    }





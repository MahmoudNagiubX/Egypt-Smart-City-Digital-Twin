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

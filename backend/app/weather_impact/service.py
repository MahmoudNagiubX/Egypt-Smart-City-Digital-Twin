"""High-level backend services for weather-impact assessment."""

import logging
import pandas as pd
import geopandas as gpd
from . import paths

logger = logging.getLogger(__name__)


def export_prediction_geojson_layers():
    """Convert prediction outputs into map-ready GeoJSON layers by joining with spatial grid.
    
    Returns:
        latest_event_id (str): ID of the latest selected event
        top_event_id (str): ID of the top rain event
    """
    logger.info("Exporting prediction GeoJSON layers...")
    
    if not paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists():
        raise FileNotFoundError(f"Predictions CSV not found at: {paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH}")
        
    if not paths.NASR_CITY_GRID_PATH.exists():
        raise FileNotFoundError(f"Grid GeoJSON not found at: {paths.NASR_CITY_GRID_PATH}")
        
    # 1. Load predictions and grid
    df_pred = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
    grid = gpd.read_file(paths.NASR_CITY_GRID_PATH)
    
    # Check grid CRS
    if grid.crs is None or grid.crs.to_string() != "EPSG:4326":
        logger.info(f"Re-projecting grid from {grid.crs} to EPSG:4326")
        grid = grid.to_crs("EPSG:4326")
        
    # We only need zone_code and geometry from grid
    grid_slim = grid[["zone_code", "geometry"]].copy()
    
    # 2. Join predictions to grid geometry by zone_code
    gdf_all = grid_slim.merge(df_pred, on="zone_code", how="inner")
    
    # Filter columns to keep it clean and performant
    keep_cols = [
        "zone_code", "event_id", "timestamp", "y_pred", "predicted_risk_class",
        "rain_24h_mm", "gpm_precipitation_sum", "built_surface_mean", "population_sum",
        "geometry"
    ]
    
    # Ensure all columns exist before filtering
    actual_keep_cols = [col for col in keep_cols if col in gdf_all.columns]
    gdf_all = gdf_all[actual_keep_cols].copy()
    
    # 3. Export all predictions GeoJSON
    paths.ensure_data_dirs()
    logger.info(f"Saving all predictions GeoJSON (rows: {len(gdf_all)})...")
    gdf_all.to_file(paths.REAL_OBSERVED_PREDICTIONS_GEOJSON_PATH, driver="GeoJSON")
    logger.info(f"Saved real_observed_predictions.geojson to {paths.REAL_OBSERVED_PREDICTIONS_GEOJSON_PATH}")
    
    # 4. Identify latest selected event:
    latest_row = df_pred.sort_values("timestamp", ascending=False).iloc[0]
    latest_event_id = latest_row["event_id"]
    latest_timestamp = latest_row["timestamp"]
    logger.info(f"Latest event identified: {latest_event_id} at {latest_timestamp}")
    
    gdf_latest = gdf_all[gdf_all["event_id"] == latest_event_id].copy()
    gdf_latest.to_file(paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH, driver="GeoJSON")
    logger.info(f"Saved latest_selected_event_risk.geojson to {paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH} (rows: {len(gdf_latest)})")
    
    # 5. Identify top rain event:
    event_rain = df_pred.groupby("event_id")["rain_24h_mm"].mean().reset_index()
    top_event_row = event_rain.sort_values("rain_24h_mm", ascending=False).iloc[0]
    top_event_id = top_event_row["event_id"]
    logger.info(f"Top rain event identified: {top_event_id} with mean 24h rain: {top_event_row['rain_24h_mm']:.2f} mm")
    
    gdf_top = gdf_all[gdf_all["event_id"] == top_event_id].copy()
    gdf_top.to_file(paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH, driver="GeoJSON")
    logger.info(f"Saved top_rain_event_risk.geojson to {paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH} (rows: {len(gdf_top)})")
    
    return latest_event_id, top_event_id

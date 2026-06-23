"""High-level backend services for weather-impact assessment."""

import logging
import pandas as pd
import geopandas as gpd
from . import paths, data_loader

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


def create_zone_risk_summary():
    """Create zone-level aggregated summaries across selected real observed events and join with grid geometry.
    
    Returns:
        df_summary (pd.DataFrame): aggregated zone risk summary
    """
    logger.info("Creating zone risk summaries...")
    
    if not paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists():
        raise FileNotFoundError(f"Predictions CSV not found at: {paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH}")
        
    df_pred = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
    
    grouped = df_pred.groupby("zone_code")
    
    summary_rows = []
    for zone_code, group in grouped:
        event_count = len(group)
        mean_pred = float(group["y_pred"].mean())
        max_pred = float(group["y_pred"].max())
        min_pred = float(group["y_pred"].min())
        
        high_cnt = int((group["predicted_risk_class"] == "high").sum())
        med_cnt = int((group["predicted_risk_class"] == "medium").sum())
        low_cnt = int((group["predicted_risk_class"] == "low").sum())
        
        high_ratio = high_cnt / event_count if event_count > 0 else 0.0
        
        mean_ae = float(group["absolute_error"].mean()) if "absolute_error" in group.columns else 0.0
        mean_rain = float(group["rain_24h_mm"].mean()) if "rain_24h_mm" in group.columns else 0.0
        max_rain = float(group["rain_24h_mm"].max()) if "rain_24h_mm" in group.columns else 0.0
        mean_gpm = float(group["gpm_precipitation_sum"].mean()) if "gpm_precipitation_sum" in group.columns else 0.0
        mean_built = float(group["built_surface_mean"].mean()) if "built_surface_mean" in group.columns else 0.0
        mean_pop = float(group["population_sum"].mean()) if "population_sum" in group.columns else 0.0
        
        # dominant_risk_class rules:
        # * high if high_risk_event_ratio >= 0.33
        # * medium if mean_predicted_score >= 0.33
        # * else low
        if high_ratio >= 0.33:
            dominant_class = "high"
        elif mean_pred >= 0.33:
            dominant_class = "medium"
        else:
            dominant_class = "low"
            
        summary_rows.append({
            "zone_code": zone_code,
            "event_count": event_count,
            "mean_predicted_score": mean_pred,
            "max_predicted_score": max_pred,
            "min_predicted_score": min_pred,
            "high_risk_event_count": high_cnt,
            "medium_risk_event_count": med_cnt,
            "low_risk_event_count": low_cnt,
            "high_risk_event_ratio": high_ratio,
            "mean_absolute_error": mean_ae,
            "mean_rain_24h_mm": mean_rain,
            "max_rain_24h_mm": max_rain,
            "mean_gpm_precipitation_sum": mean_gpm,
            "mean_built_surface_mean": mean_built,
            "mean_population_sum": mean_pop,
            "dominant_risk_class": dominant_class
        })
        
    df_summary = pd.DataFrame(summary_rows)
    
    # Save CSV
    paths.ensure_data_dirs()
    data_loader.write_csv(df_summary, paths.ZONE_RISK_SUMMARY_CSV_PATH)
    logger.info(f"Saved zone risk summary CSV to {paths.ZONE_RISK_SUMMARY_CSV_PATH} (rows: {len(df_summary)})")
    
    # Create GeoJSON by joining with grid
    if not paths.NASR_CITY_GRID_PATH.exists():
        raise FileNotFoundError(f"Grid GeoJSON not found at: {paths.NASR_CITY_GRID_PATH}")
        
    grid = gpd.read_file(paths.NASR_CITY_GRID_PATH)
    if grid.crs is None or grid.crs.to_string() != "EPSG:4326":
        grid = grid.to_crs("EPSG:4326")
        
    grid_slim = grid[["zone_code", "geometry"]].copy()
    gdf_summary = grid_slim.merge(df_summary, on="zone_code", how="inner")
    
    gdf_summary.to_file(paths.ZONE_RISK_SUMMARY_GEOJSON_PATH, driver="GeoJSON")
    logger.info(f"Saved zone risk summary GeoJSON to {paths.ZONE_RISK_SUMMARY_GEOJSON_PATH} (rows: {len(gdf_summary)})")
    
    return df_summary


def generate_prediction_output_report():
    """Analyze predictions and export prediction_output_report.json.
    
    Returns:
        report (dict): analyzed prediction report
    """
    logger.info("Generating prediction output report...")
    
    if not paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists():
        raise FileNotFoundError(f"Predictions CSV not found at: {paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH}")
        
    df_pred = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
    
    # 1. Row/event counts
    prediction_rows = len(df_pred)
    zone_count = int(df_pred["zone_code"].nunique())
    event_count = int(df_pred["event_id"].nunique())
    
    # 2. Risk class counts
    counts = df_pred["predicted_risk_class"].value_counts().to_dict()
    risk_class_counts = {
        "low": int(counts.get("low", 0)),
        "medium": int(counts.get("medium", 0)),
        "high": int(counts.get("high", 0))
    }
    
    # 3. Identify latest and top rain events
    latest_row = df_pred.sort_values("timestamp", ascending=False).iloc[0]
    latest_event_id = latest_row["event_id"]
    
    event_rain = df_pred.groupby("event_id")["rain_24h_mm"].mean().reset_index()
    top_event_row = event_rain.sort_values("rain_24h_mm", ascending=False).iloc[0]
    top_event_id = top_event_row["event_id"]
    
    # 4. Check outputs existence
    outputs_status = {
        "real_observed_predictions_csv": paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists(),
        "real_observed_predictions_geojson": paths.REAL_OBSERVED_PREDICTIONS_GEOJSON_PATH.exists(),
        "latest_selected_event_risk_geojson": paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH.exists(),
        "top_rain_event_risk_geojson": paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH.exists(),
        "zone_risk_summary_csv": paths.ZONE_RISK_SUMMARY_CSV_PATH.exists(),
        "zone_risk_summary_geojson": paths.ZONE_RISK_SUMMARY_GEOJSON_PATH.exists()
    }
    
    warnings = []
    # If any output is missing, add warning
    for out, exists in outputs_status.items():
        if not exists:
            warnings.append(f"Missing output file: {out}")
            
    report = {
        "training_dataset": "real_observed_training_dataset.csv",
        "model_used": "weather_impact_rf_model.joblib",
        "target_predicted": "data_driven_weather_impact_score",
        "official_flood_labels_claimed": False,
        "demo_scenarios_used_for_training": False,
        "prediction_rows": prediction_rows,
        "zone_count": zone_count,
        "event_count": event_count,
        "risk_class_counts": risk_class_counts,
        "latest_event_id": latest_event_id,
        "top_rain_event_id": top_event_id,
        "outputs": outputs_status,
        "honesty_note": (
            "Predictions represent model-estimated weather-impact risk scores derived from engineered real-observation targets. "
            "They are not verified street-level flood incident predictions."
        ),
        "status": "ok" if len(warnings) == 0 else "ok_with_warnings",
        "warnings": warnings
    }
    
    paths.ensure_data_dirs()
    data_loader.save_json(report, paths.PREDICTION_OUTPUT_REPORT_PATH)
    logger.info(f"Saved prediction output report to {paths.PREDICTION_OUTPUT_REPORT_PATH}")
    return report



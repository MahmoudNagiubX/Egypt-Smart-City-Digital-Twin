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


def load_json_file(path):
    """Load and parse a JSON file safely."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found at: {path}")
    with open(path_obj, "r", encoding="utf-8") as f:
        return json.load(f)


def load_geojson_layer(path):
    """Load a GeoJSON layer directly as a dictionary (fast)."""
    return load_json_file(path)


def load_csv_records(path, limit=None):
    """Load a CSV file into list of dictionaries."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found at: {path}")
    df = pd.read_csv(path_obj)
    if limit is not None:
        df = df.head(limit)
    return df.to_dict(orient="records")


def get_module_status():
    """Retrieve module health and availability status."""
    outputs = {
        "boundary": paths.NASR_CITY_BOUNDARY_PATH.exists(),
        "grid": paths.NASR_CITY_GRID_PATH.exists(),
        "roads": paths.NASR_CITY_ROADS_PATH.exists(),
        "roads_zones": paths.ROADS_WITH_ZONE_IDS_PATH.exists(),
        "emergency_facilities": paths.NASR_CITY_FACILITIES_PATH.exists(),
        "predictions": paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists(),
        "predictions_geojson": paths.REAL_OBSERVED_PREDICTIONS_GEOJSON_PATH.exists(),
        "latest_event_risk_geojson": paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH.exists(),
        "top_rain_event_risk_geojson": paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH.exists(),
        "zone_risk_summary_csv": paths.ZONE_RISK_SUMMARY_CSV_PATH.exists(),
        "zone_risk_summary_geojson": paths.ZONE_RISK_SUMMARY_GEOJSON_PATH.exists(),
        "prediction_report": paths.PREDICTION_OUTPUT_REPORT_PATH.exists()
    }
    
    report_status = None
    if paths.PREDICTION_OUTPUT_REPORT_PATH.exists():
        try:
            report = load_json_file(paths.PREDICTION_OUTPUT_REPORT_PATH)
            report_status = report.get("status")
        except Exception:
            pass
            
    # Check if predictions are ready
    predictions_ready = outputs["predictions"] and outputs["prediction_report"]
    status = "healthy" if predictions_ready else "partial"
    
    return {
        "module_name": "Nasr City Weather-Impact Emergency Mobility Module",
        "status": status,
        "outputs_available": outputs,
        "prediction_report_status": report_status,
        "official_flood_labels_claimed": False,
        "demo_scenarios_used_for_training": False
    }


def get_prediction_metadata():
    """Retrieve metadata about the predictions from the report."""
    if not paths.PREDICTION_OUTPUT_REPORT_PATH.exists():
        raise FileNotFoundError(f"Prediction output report not found at: {paths.PREDICTION_OUTPUT_REPORT_PATH}")
        
    report = load_json_file(paths.PREDICTION_OUTPUT_REPORT_PATH)
    latest_event_id = report.get("latest_event_id", "")
    latest_event_timestamp = ""
    
    if paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists() and latest_event_id:
        try:
            df = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
            latest_row = df[df["event_id"] == latest_event_id]
            if len(latest_row) > 0:
                latest_event_timestamp = str(latest_row["timestamp"].iloc[0])
        except Exception:
            pass
            
    if not latest_event_timestamp:
        latest_event_timestamp = "2024-02-20T00:00"  # fallback
        
    return {
        "model_used": report.get("model_used", "weather_impact_rf_model.joblib"),
        "dataset_used": report.get("training_dataset", "real_observed_training_dataset.csv"),
        "prediction_rows": report.get("prediction_rows", 12480),
        "zone_count": report.get("zone_count", 416),
        "event_count": report.get("event_count", 30),
        "risk_class_counts": report.get("risk_class_counts", {}),
        "latest_event_id": latest_event_id,
        "latest_event_timestamp": latest_event_timestamp,
        "top_rain_event_id": report.get("top_rain_event_id", ""),
        "official_flood_labels_claimed": False,
        "demo_scenarios_used_for_training": False,
        "status": report.get("status", "ok")
    }


def list_prediction_events():
    """List unique events from real observed predictions with summary metrics."""
    if not paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists():
        raise FileNotFoundError(f"Predictions CSV not found at: {paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH}")
        
    df = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
    
    events = []
    grouped = df.groupby("event_id")
    for event_id, group in grouped:
        timestamp = group["timestamp"].iloc[0]
        mean_rain = float(group["rain_24h_mm"].mean())
        max_rain = float(group["rain_24h_mm"].max())
        mean_score = float(group["y_pred"].mean())
        high_risk_zones = int((group["predicted_risk_class"] == "high").sum())
        
        events.append({
            "event_id": event_id,
            "timestamp": str(timestamp),
            "mean_rain_24h_mm": mean_rain,
            "max_rain_24h_mm": max_rain,
            "mean_predicted_score": mean_score,
            "high_risk_zone_count": high_risk_zones
        })
        
    # Sort events by timestamp
    events = sorted(events, key=lambda x: x["timestamp"])
    return events


def get_event_risk_layer(event_id):
    """Filter real observed predictions by event_id and merge with grid geometry."""
    if not paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists():
        raise FileNotFoundError(f"Predictions CSV not found at: {paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH}")
        
    df = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
    df_event = df[df["event_id"] == event_id].copy()
    if len(df_event) == 0:
        raise ValueError(f"Event ID '{event_id}' not found in predictions.")
        
    if not paths.NASR_CITY_GRID_PATH.exists():
        raise FileNotFoundError(f"Grid GeoJSON not found at: {paths.NASR_CITY_GRID_PATH}")
        
    grid = gpd.read_file(paths.NASR_CITY_GRID_PATH)
    if grid.crs is None or grid.crs.to_string() != "EPSG:4326":
        grid = grid.to_crs("EPSG:4326")
        
    grid_slim = grid[["zone_code", "geometry"]].copy()
    gdf = grid_slim.merge(df_event, on="zone_code", how="inner")
    
    keep_cols = [
        "zone_code", "event_id", "timestamp", "y_pred", "predicted_risk_class",
        "rain_24h_mm", "gpm_precipitation_sum", "built_surface_mean", "population_sum",
        "geometry"
    ]
    actual_cols = [c for c in keep_cols if c in gdf.columns]
    gdf = gdf[actual_cols].copy()
    
    return json.loads(gdf.to_json())




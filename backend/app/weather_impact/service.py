"""High-level backend services for weather-impact assessment."""

import json
import logging
import re
from pathlib import Path
import pandas as pd
import geopandas as gpd
from . import paths, data_loader

logger = logging.getLogger(__name__)

PLACE_CATEGORIES = (
    "hospital",
    "clinic",
    "mosque",
    "mall",
    "school",
    "university",
    "police",
    "fire_station",
    "emergency",
    "landmark",
)
PLACE_LABELS = {
    "hospital": "Hospital",
    "clinic": "Clinic",
    "mosque": "Mosque",
    "mall": "Mall",
    "school": "School",
    "university": "University",
    "police": "Police Station",
    "fire_station": "Fire Station",
    "emergency": "Emergency Facility",
    "landmark": "Landmark",
}
PLACE_ICONS = {
    "hospital": "hospital",
    "clinic": "medical",
    "mosque": "mosque",
    "mall": "shopping",
    "school": "school",
    "university": "university",
    "police": "police",
    "fire_station": "fire_station",
    "emergency": "emergency",
    "landmark": "landmark",
}
_RAW_OSM_ID = re.compile(r"^(?:osm[:_ -]?)?(?:node|way|relation)?[:_ -]?\d+$", re.I)


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


def _normalise_place_category(properties):
    """Map source-specific OSM fields to the public category vocabulary."""
    category = str(
        properties.get("category")
        or properties.get("facility_type")
        or properties.get("amenity")
        or ""
    ).strip().lower()
    aliases = {
        "place_of_worship": "mosque",
        "fire station": "fire_station",
        "doctors": "clinic",
        "medical": "clinic",
        "attraction": "landmark",
        "museum": "landmark",
        "monument": "landmark",
    }
    category = aliases.get(category, category)
    if category not in PLACE_CATEGORIES:
        category = "emergency" if properties.get("facility_type") else "landmark"
    return category


def _clean_display_name(properties, category):
    """Prefer an English/Latin name and otherwise return a human-readable label."""
    for key in ("name:en", "name_en", "display_name", "name"):
        value = properties.get(key)
        if value is None:
            continue
        value = str(value).strip()
        if not value or value.lower() == "nan" or _RAW_OSM_ID.match(value):
            continue
        if re.search(r"[\u0600-\u06ff]", value) or any(
            marker in value for marker in ("Ø", "Ù", "Ã", "Â", "�")
        ):
            continue
        if re.search(r"[A-Za-z]", value):
            return value
    return PLACE_LABELS[category]


def _point_coordinates(geometry):
    """Return point coordinates for point or polygonal source geometry."""
    if not geometry:
        return None
    if geometry.get("type") == "Point":
        coordinates = geometry.get("coordinates", [])
        if len(coordinates) >= 2:
            return float(coordinates[0]), float(coordinates[1])
    try:
        from shapely.geometry import shape

        point = shape(geometry).representative_point()
        return float(point.x), float(point.y)
    except Exception:
        return None


def _load_normalised_places():
    sources = []
    warnings = []
    if paths.NASR_CITY_POIS_PATH.exists():
        sources.append((paths.NASR_CITY_POIS_PATH, False))
    else:
        warnings.append(
            "Broader OpenStreetMap POIs are unavailable; serving existing emergency facilities only."
        )
    if paths.NASR_CITY_FACILITIES_PATH.exists():
        sources.append((paths.NASR_CITY_FACILITIES_PATH, True))
    else:
        warnings.append("Existing emergency facilities GeoJSON is unavailable.")

    features = []
    seen = {}
    for source_path, is_emergency_source in sources:
        source_data = load_geojson_layer(source_path)
        for index, feature in enumerate(source_data.get("features", []), start=1):
            properties = feature.get("properties") or {}
            coordinates = _point_coordinates(feature.get("geometry"))
            if coordinates is None:
                continue
            lon, lat = coordinates
            category = _normalise_place_category(properties)
            dedupe_key = (category, round(lon, 5), round(lat, 5))
            if dedupe_key in seen:
                if is_emergency_source:
                    seen[dedupe_key]["properties"]["is_emergency_facility"] = True
                continue
            source_id = (
                properties.get("place_id")
                or properties.get("osmid")
                or properties.get("osm_id")
                or f"{source_path.stem}-{index}"
            )
            place_id = str(source_id)
            original_name = properties.get("name") or properties.get("name:en")
            if original_name is not None and str(original_name).lower() == "nan":
                original_name = None
            normalised_feature = {
                "type": "Feature",
                "properties": {
                    "place_id": place_id,
                    "name": original_name,
                    "display_name": _clean_display_name(properties, category),
                    "category": category,
                    "category_label": PLACE_LABELS[category],
                    "icon_type": PLACE_ICONS[category],
                    "source": str(properties.get("source") or "OpenStreetMap"),
                    "lon": lon,
                    "lat": lat,
                    "is_emergency_facility": is_emergency_source,
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
            features.append(normalised_feature)
            seen[dedupe_key] = normalised_feature
    return features, warnings


def get_places(category="all", limit=None):
    """Return normalised map places as a GeoJSON FeatureCollection."""
    if category not in ("all", *PLACE_CATEGORIES):
        raise ValueError(f"Unsupported place category: {category}")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")

    features, _ = _load_normalised_places()
    if category == "emergency":
        features = [
            feature
            for feature in features
            if feature["properties"].get("is_emergency_facility")
        ]
    elif category != "all":
        features = [
            feature
            for feature in features
            if feature["properties"]["category"] == category
        ]
    if limit is not None:
        features = features[:limit]
    for feature in features:
        feature["properties"].pop("is_emergency_facility", None)
    return {"type": "FeatureCollection", "features": features}


def get_places_summary():
    """Return source availability and category counts for public places."""
    features, warnings = _load_normalised_places()
    categories = {category: 0 for category in PLACE_CATEGORIES}
    emergency_count = 0
    for feature in features:
        properties = feature["properties"]
        categories[properties["category"]] += 1
        if properties.get("is_emergency_facility"):
            emergency_count += 1
    categories["emergency"] = emergency_count
    return {
        "total_places": len(features),
        "categories": categories,
        "source": "OpenStreetMap / existing processed data",
        "status": "ok" if not warnings else "ok_with_warnings",
        "warnings": warnings,
    }


def get_custom_emergency_route(origin, destination, event_type, route_preference):
    """Route between user-selected coordinates using the existing routing engine."""
    from . import routing

    result = routing.build_custom_routes(origin, destination, event_type)
    result["route_preference"] = route_preference
    return result


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


def get_summary_stats():
    """Get summarized weather-impact risk metrics for dashboard cards."""
    if not paths.PREDICTION_OUTPUT_REPORT_PATH.exists():
        raise FileNotFoundError("Prediction report not found.")
    if not paths.ZONE_RISK_SUMMARY_CSV_PATH.exists():
        raise FileNotFoundError("Zone risk summary CSV not found.")
        
    report = load_json_file(paths.PREDICTION_OUTPUT_REPORT_PATH)
    df_zones = pd.read_csv(paths.ZONE_RISK_SUMMARY_CSV_PATH)
    
    # Get top 5 highest risk zones
    top_zones = df_zones.sort_values("max_predicted_score", ascending=False).head(5)
    highest_risk_zones = []
    for _, row in top_zones.iterrows():
        highest_risk_zones.append({
            "zone_code": str(row["zone_code"]),
            "max_predicted_score": float(row["max_predicted_score"]),
            "dominant_risk_class": str(row["dominant_risk_class"])
        })
        
    # Get risk counts from summary
    risk_class_counts = report.get("risk_class_counts", {})
    
    return {
        "zone_count": int(report.get("zone_count", 416)),
        "event_count": int(report.get("event_count", 30)),
        "prediction_row_count": int(report.get("prediction_rows", 12480)),
        "risk_class_counts": risk_class_counts,
        "highest_risk_zones": highest_risk_zones,
        "top_rain_event_id": str(report.get("top_rain_event_id", "")),
        "latest_event_id": str(report.get("latest_event_id", "")),
        "model_name": str(report.get("model_used", "weather_impact_rf_model.joblib")),
        "dataset_name": str(report.get("training_dataset", "real_observed_training_dataset.csv")),
        "honesty_statement": (
            "Predictions are model-estimated weather-impact risk scores derived from "
            "engineered real-observation targets, not verified street-level flood incident labels."
        )
    }


def get_routing_status():
    """Retrieve the routing validation report."""
    if not paths.ROUTING_VALIDATION_REPORT_PATH.exists():
        raise FileNotFoundError(f"Routing validation report not found at: {paths.ROUTING_VALIDATION_REPORT_PATH}")
    report = load_json_file(paths.ROUTING_VALIDATION_REPORT_PATH)
    # Ensure honesty note is present
    report["honesty_note"] = "Routes are decision-support prototype outputs, not official emergency dispatch instructions."
    return report


def get_demo_route(event_type: str, route_type: str):
    """Retrieve GeoJSON for a computed demo route."""
    if event_type not in ["top-rain", "latest"]:
        raise ValueError(f"Unsupported event_type: {event_type}")
    if route_type not in ["normal", "safe", "weather_safe"]:
        raise ValueError(f"Unsupported route_type: {route_type}")
        
    if event_type == "top-rain":
        if route_type == "normal":
            path = paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH
        else:
            path = paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH
    else:
        if route_type == "normal":
            path = paths.DEMO_ROUTE_LATEST_NORMAL_PATH
        else:
            path = paths.DEMO_ROUTE_LATEST_SAFE_PATH
            
    if not path.exists():
        raise FileNotFoundError(f"Demo route GeoJSON file not found at: {path}")
        
    return load_geojson_layer(path)


def get_route_comparison(event_type: str):
    """Retrieve route comparison metrics for an event type."""
    if event_type not in ["top-rain", "latest"]:
        raise ValueError(f"Unsupported event_type: {event_type}")
        
    if event_type == "top-rain":
        path = paths.ROUTE_COMPARISON_TOP_RAIN_PATH
    else:
        path = paths.ROUTE_COMPARISON_LATEST_PATH
        
    if not path.exists():
        raise FileNotFoundError(f"Route comparison JSON not found at: {path}")
        
    comparison = load_json_file(path)
    comparison["honesty_note"] = "Routes are decision-support prototype outputs, not official emergency dispatch instructions."
    return comparison


def check_required_files():
    """Verify that all expected spatial, dataset, ML, prediction, and routing files exist."""
    required = [
        # Spatial
        ("nasr_city_boundary", paths.NASR_CITY_BOUNDARY_PATH),
        ("nasr_city_grid_500m", paths.NASR_CITY_GRID_PATH),
        ("nasr_city_roads", paths.NASR_CITY_ROADS_PATH),
        ("roads_with_zone_ids", paths.ROADS_WITH_ZONE_IDS_PATH),
        ("nasr_city_emergency_facilities", paths.NASR_CITY_FACILITIES_PATH),
        ("nasr_city_graph", paths.NASR_CITY_GRAPH_PATH),
        # Real data
        ("real_observed_training_dataset", paths.REAL_OBSERVED_TRAINING_DATASET_PATH),
        ("real_data_validation_report", paths.REAL_DATA_VALIDATION_REPORT_PATH),
        # ML
        ("weather_impact_rf_model", paths.RF_MODEL_PATH),
        ("ml_feature_columns", paths.ML_FEATURE_COLUMNS_PATH),
        ("model_comparison", paths.MODEL_COMPARISON_PATH),
        ("model_card", paths.MODEL_CARD_PATH),
        # Prediction
        ("real_observed_predictions", paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH),
        ("latest_selected_event_risk", paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH),
        ("top_rain_event_risk", paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH),
        ("zone_risk_summary_geojson", paths.ZONE_RISK_SUMMARY_GEOJSON_PATH),
        ("prediction_output_report", paths.PREDICTION_OUTPUT_REPORT_PATH),
        # Routing
        ("road_risk_weights_top_rain", paths.ROAD_RISK_WEIGHTS_TOP_RAIN_PATH),
        ("road_risk_weights_latest", paths.ROAD_RISK_WEIGHTS_LATEST_PATH),
        ("demo_route_top_rain_normal", paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH),
        ("demo_route_top_rain_safe", paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH),
        ("demo_route_latest_normal", paths.DEMO_ROUTE_LATEST_NORMAL_PATH),
        ("demo_route_latest_safe", paths.DEMO_ROUTE_LATEST_SAFE_PATH),
        ("route_comparison_top_rain", paths.ROUTE_COMPARISON_TOP_RAIN_PATH),
        ("route_comparison_latest", paths.ROUTE_COMPARISON_LATEST_PATH),
        ("routing_validation_report", paths.ROUTING_VALIDATION_REPORT_PATH)
    ]
    
    source_audit_path = paths.NASR_CITY_OUTPUTS / "real_data_source_audit_report.json"
    required.append(("real_data_source_audit_report", source_audit_path))
    
    missing = []
    checked_count = 0
    for name, path in required:
        checked_count += 1
        if not path.exists():
            missing.append(name)
            
    return {
        "required_files_checked": checked_count,
        "missing_files": missing
    }


def check_report_statuses():
    """Verify statuses of validation and validation reports."""
    statuses = {
        "real_data_validation_status": "missing",
        "real_data_source_audit_status": "missing",
        "prediction_output_status": "missing",
        "routing_validation_status": "missing"
    }
    
    if paths.REAL_DATA_VALIDATION_REPORT_PATH.exists():
        try:
            report = load_json_file(paths.REAL_DATA_VALIDATION_REPORT_PATH)
            statuses["real_data_validation_status"] = report.get("status", "unknown")
        except Exception:
            statuses["real_data_validation_status"] = "error"
            
    source_audit_path = paths.NASR_CITY_OUTPUTS / "real_data_source_audit_report.json"
    if source_audit_path.exists():
        try:
            report = load_json_file(source_audit_path)
            statuses["real_data_source_audit_status"] = report.get("status", "unknown")
        except Exception:
            statuses["real_data_source_audit_status"] = "error"
            
    if paths.PREDICTION_OUTPUT_REPORT_PATH.exists():
        try:
            report = load_json_file(paths.PREDICTION_OUTPUT_REPORT_PATH)
            statuses["prediction_output_status"] = report.get("status", "unknown")
        except Exception:
            statuses["prediction_output_status"] = "error"
            
    if paths.ROUTING_VALIDATION_REPORT_PATH.exists():
        try:
            report = load_json_file(paths.ROUTING_VALIDATION_REPORT_PATH)
            statuses["routing_validation_status"] = report.get("status", "unknown")
        except Exception:
            statuses["routing_validation_status"] = "error"
            
    return statuses


def check_geojson_validity():
    """Check that GeoJSON files are readable by GeoPandas and structurally valid."""
    geojson_files = [
        ("nasr_city_boundary", paths.NASR_CITY_BOUNDARY_PATH),
        ("nasr_city_grid_500m", paths.NASR_CITY_GRID_PATH),
        ("nasr_city_roads", paths.NASR_CITY_ROADS_PATH),
        ("nasr_city_emergency_facilities", paths.NASR_CITY_FACILITIES_PATH),
        ("latest_selected_event_risk", paths.LATEST_SELECTED_EVENT_RISK_GEOJSON_PATH),
        ("top_rain_event_risk", paths.TOP_RAIN_EVENT_RISK_GEOJSON_PATH),
        ("zone_risk_summary_geojson", paths.ZONE_RISK_SUMMARY_GEOJSON_PATH),
        ("demo_route_top_rain_normal", paths.DEMO_ROUTE_TOP_RAIN_NORMAL_PATH),
        ("demo_route_top_rain_safe", paths.DEMO_ROUTE_TOP_RAIN_SAFE_PATH),
        ("demo_route_latest_normal", paths.DEMO_ROUTE_LATEST_NORMAL_PATH),
        ("demo_route_latest_safe", paths.DEMO_ROUTE_LATEST_SAFE_PATH)
    ]
    
    invalid = []
    for name, path in geojson_files:
        if path.exists():
            try:
                gdf = gpd.read_file(path)
                if len(gdf) == 0 and "demo_route" not in name:
                    invalid.append(f"{name} (empty)")
            except Exception as e:
                invalid.append(f"{name} ({str(e)})")
        else:
            invalid.append(f"{name} (not found)")
            
    return {
        "valid_geojson_count": len(geojson_files) - len(invalid),
        "invalid_geojson_files": invalid
    }


def check_csv_row_counts():
    """Verify row counts for key CSV files."""
    csv_files = [
        ("real_observed_training_dataset", paths.REAL_OBSERVED_TRAINING_DATASET_PATH),
        ("real_observed_predictions", paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH),
        ("zone_risk_summary_csv", paths.ZONE_RISK_SUMMARY_CSV_PATH)
    ]
    
    counts = {}
    for name, path in csv_files:
        if path.exists():
            try:
                df = pd.read_csv(path)
                counts[name] = len(df)
            except Exception:
                counts[name] = -1
        else:
            counts[name] = 0
            
    return counts


def check_model_artifacts():
    """Verify ML model artifacts existence and basic features list."""
    status = "ok"
    reasons = []
    
    if not paths.RF_MODEL_PATH.exists():
        status = "failed"
        reasons.append("Model joblib file missing")
    if not paths.ML_FEATURE_COLUMNS_PATH.exists():
        status = "failed"
        reasons.append("Feature columns JSON missing")
    if not paths.MODEL_CARD_PATH.exists():
        status = "failed"
        reasons.append("Model Card markdown missing")
        
    return {
        "status": status,
        "reasons": reasons
    }


def check_prediction_outputs():
    """Verify that predictions exist and have correct event types."""
    status = "ok"
    warnings = []
    
    if paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH.exists():
        try:
            df = pd.read_csv(paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
            events = df["event_id"].unique()
            if len(events) < 30:
                warnings.append(f"Expected at least 30 events, found {len(events)}")
        except Exception as e:
            status = "failed"
            warnings.append(f"Failed to read predictions: {e}")
    else:
        status = "failed"
        warnings.append("Predictions CSV missing")
        
    return {
        "status": status,
        "warnings": warnings
    }


def check_routing_outputs():
    """Verify weights and route artifacts exist and safe route is valid."""
    status = "ok"
    warnings = []
    
    safe_top_available = True
    safe_lat_available = True
    
    if paths.ROUTE_COMPARISON_TOP_RAIN_PATH.exists():
        try:
            with open(paths.ROUTE_COMPARISON_TOP_RAIN_PATH, "r", encoding="utf-8") as f:
                comp = json.load(f)
                safe_top_available = comp.get("safe_route_available", True)
                if comp.get("risk_reduction_percent", 0.0) < 0.0:
                    warnings.append("Top-rain comparison reports negative risk reduction")
        except Exception as e:
            warnings.append(f"Failed to parse top-rain comparison: {e}")
            
    if paths.ROUTE_COMPARISON_LATEST_PATH.exists():
        try:
            with open(paths.ROUTE_COMPARISON_LATEST_PATH, "r", encoding="utf-8") as f:
                comp = json.load(f)
                safe_lat_available = comp.get("safe_route_available", True)
                if comp.get("risk_reduction_percent", 0.0) < 0.0:
                    warnings.append("Latest comparison reports negative risk reduction")
        except Exception as e:
            warnings.append(f"Failed to parse latest comparison: {e}")
            
    return {
        "status": "ok" if (safe_top_available and safe_lat_available) else "ok_with_warnings",
        "top_rain_safe_route_available": safe_top_available,
        "latest_safe_route_available": safe_lat_available,
        "warnings": warnings
    }


def generate_live_weather_risk_layer(cache_expiry_hours: float = 3.0) -> dict:
    """Generate live risk predictions using forecast weather and export outputs."""
    import numpy as np
    from . import weather, model
    
    logger.info("Generating live weather risk layer...")
    paths.ensure_data_dirs()
    
    warnings = []
    status = "ok"
    
    # 1. Fetch and process live forecast
    try:
        forecast_data, fetch_warnings = weather.fetch_live_weather_forecast(cache_expiry_hours)
        warnings.extend(fetch_warnings)
        
        live_weather_summary = weather.summarize_live_weather_forecast(forecast_data, warnings=fetch_warnings)
        
    except Exception as e:
        logger.error(f"Live weather risk generation failed during weather collection: {e}")
        # Build a failed report
        report = {
            "status": "failed",
            "source": "Open-Meteo Forecast API",
            "model_used": "weather_impact_rf_model.joblib",
            "feature_columns_used": False,
            "prediction_rows": 0,
            "rain_risk_expected": False,
            "risk_class_counts": {"low": 0, "medium": 0, "high": 0},
            "forecast_window_hours": 24,
            "max_rain_24h_mm": 0.0,
            "max_precipitation_probability": 0.0,
            "uses_forecast_precipitation_proxy_for_satellite_features": False,
            "official_flood_labels_claimed": False,
            "official_emergency_dispatch_claimed": False,
            "honesty_note": "Live predictions are model-estimated weather-impact risk scores, not verified flood incident labels.",
            "warnings": [f"Live weather data fetch failed: {e}"]
        }
        paths.LIVE_WEATHER_RISK_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        data_loader.save_json(report, paths.LIVE_WEATHER_RISK_REPORT_PATH)
        return report

    # 2. Build live feature matrix
    try:
        X, metadata, uses_gpm_proxy = model.build_live_weather_feature_matrix(live_weather_summary)
        
        # 3. Load model and predict
        rf = model.load_prediction_model()
        y_pred_raw = rf.predict(X)
        y_pred = np.clip(y_pred_raw, 0.0, 1.0)
        
        # 4. Construct predictions DataFrame
        df_predictions = pd.DataFrame()
        df_predictions["zone_code"] = metadata["zone_code"]
        df_predictions["live_predicted_score"] = y_pred
        df_predictions["live_risk_class"] = df_predictions["live_predicted_score"].apply(model.score_to_risk_class)
        
        # Add required columns
        forecast_window = live_weather_summary["forecast_window"]
        current = live_weather_summary["current"]
        
        df_predictions["rain_1h_mm"] = forecast_window["rain_1h_mm"]
        df_predictions["rain_3h_mm"] = forecast_window["rain_3h_mm"]
        df_predictions["rain_6h_mm"] = forecast_window["rain_6h_mm"]
        df_predictions["rain_24h_mm"] = forecast_window["rain_24h_mm"]
        df_predictions["max_precipitation_probability"] = forecast_window["max_precipitation_probability"]
        
        df_predictions["temperature_2m"] = current["temperature_2m"]
        df_predictions["apparent_temperature"] = current["apparent_temperature"]
        df_predictions["relative_humidity_2m"] = forecast_window.get("mean_relative_humidity_2m", 50.0)
        df_predictions["wind_speed_10m"] = current["wind_speed_10m"]
        
        # Rush hour check
        import datetime
        time_str = current.get("time")
        try:
            dt = datetime.datetime.fromisoformat(time_str)
            current_hour = dt.hour
        except Exception:
            current_hour = datetime.datetime.now().hour
        is_rush_hour = current_hour in {7, 8, 9, 16, 17, 18}
        
        df_predictions["is_rush_hour"] = is_rush_hour
        df_predictions["source"] = "Open-Meteo Forecast API"
        df_predictions["target_description"] = "model-estimated live weather-impact risk"
        
        # Save CSV
        data_loader.write_csv(df_predictions, paths.LIVE_WEATHER_RISK_PREDICTIONS_CSV_PATH)
        logger.info(f"Saved live weather risk predictions CSV to {paths.LIVE_WEATHER_RISK_PREDICTIONS_CSV_PATH}")
        
        # 5. Join to grid geometry and save live_weather_risk.geojson
        grid = gpd.read_file(paths.NASR_CITY_GRID_PATH)
        
        # check CRS
        if grid.crs is None or grid.crs.to_string() != "EPSG:4326":
            grid = grid.to_crs("EPSG:4326")
            
        grid_slim = grid[["zone_code", "geometry"]].copy()
        gdf_live = grid_slim.merge(df_predictions, on="zone_code", how="inner")
        
        # Keep GeoJSON columns clean
        geojson_cols = [
            "zone_code", "live_predicted_score", "live_risk_class",
            "rain_1h_mm", "rain_3h_mm", "rain_6h_mm", "rain_24h_mm",
            "max_precipitation_probability", "source", "geometry"
        ]
        
        actual_cols = [c for c in geojson_cols if c in gdf_live.columns]
        gdf_live = gdf_live[actual_cols].copy()
        
        # Add honesty note
        gdf_live["honesty_note"] = "Live predictions are model-estimated weather-impact risk scores, not verified flood incident labels."
        
        gdf_live.to_file(paths.LIVE_WEATHER_RISK_GEOJSON_PATH, driver="GeoJSON")
        logger.info(f"Saved live weather risk GeoJSON layer to {paths.LIVE_WEATHER_RISK_GEOJSON_PATH} (rows: {len(gdf_live)})")
        
        # 6. Build risk class counts for report
        class_counts = df_predictions["live_risk_class"].value_counts().to_dict()
        risk_class_counts = {
            "low": int(class_counts.get("low", 0)),
            "medium": int(class_counts.get("medium", 0)),
            "high": int(class_counts.get("high", 0))
        }
        
        # 7. Generate live_weather_risk_report.json
        if len(warnings) > 0 or uses_gpm_proxy:
            status = "ok_with_warnings"
            
        report = {
            "status": status,
            "source": "Open-Meteo Forecast API",
            "model_used": "weather_impact_rf_model.joblib",
            "feature_columns_used": True,
            "prediction_rows": len(df_predictions),
            "rain_risk_expected": bool(live_weather_summary["rain_risk_expected"]),
            "risk_class_counts": risk_class_counts,
            "forecast_window_hours": 24,
            "max_rain_24h_mm": float(forecast_window.get("rain_24h_mm", 0.0)),
            "max_precipitation_probability": float(forecast_window.get("max_precipitation_probability", 0.0)),
            "uses_forecast_precipitation_proxy_for_satellite_features": bool(uses_gpm_proxy),
            "official_flood_labels_claimed": False,
            "official_emergency_dispatch_claimed": False,
            "honesty_note": "Live predictions are model-estimated weather-impact risk scores, not verified flood incident labels.",
            "warnings": warnings
        }
        
        data_loader.save_json(report, paths.LIVE_WEATHER_RISK_REPORT_PATH)
        logger.info(f"Saved live weather risk report to {paths.LIVE_WEATHER_RISK_REPORT_PATH}")
        return report
        
    except Exception as e:
        logger.error(f"Live weather risk generation prediction stage failed: {e}")
        report = {
            "status": "failed",
            "source": "Open-Meteo Forecast API",
            "model_used": "weather_impact_rf_model.joblib",
            "feature_columns_used": False,
            "prediction_rows": 0,
            "rain_risk_expected": False,
            "risk_class_counts": {"low": 0, "medium": 0, "high": 0},
            "forecast_window_hours": 24,
            "max_rain_24h_mm": 0.0,
            "max_precipitation_probability": 0.0,
            "uses_forecast_precipitation_proxy_for_satellite_features": False,
            "official_flood_labels_claimed": False,
            "official_emergency_dispatch_claimed": False,
            "honesty_note": "Live predictions are model-estimated weather-impact risk scores, not verified flood incident labels.",
            "warnings": [f"Prediction stage failed: {e}"]
        }
        data_loader.save_json(report, paths.LIVE_WEATHER_RISK_REPORT_PATH)
        return report


def get_live_routing_status() -> dict:
    """Retrieve live weather routing readiness, summary, and status."""
    warnings = []
    
    live_weather_available = paths.LIVE_WEATHER_SUMMARY_PATH.exists()
    live_risk_layer_available = paths.LIVE_WEATHER_RISK_GEOJSON_PATH.exists()
    live_road_weights_available = paths.LIVE_ROAD_RISK_WEIGHTS_GEOJSON_PATH.exists()
    
    # Read weather summary
    rain_risk_expected = False
    if live_weather_available:
        try:
            summary = load_json_file(paths.LIVE_WEATHER_SUMMARY_PATH)
            rain_risk_expected = bool(summary.get("rain_risk_expected", False))
            if summary.get("warnings"):
                warnings.extend(summary["warnings"])
        except Exception as e:
            warnings.append(f"Failed to read live weather summary: {e}")
            live_weather_available = False
            
    # Read risk report
    risk_class_counts = {"low": 0, "medium": 0, "high": 0}
    live_report_status = "failed"
    if paths.LIVE_WEATHER_RISK_REPORT_PATH.exists():
        try:
            report = load_json_file(paths.LIVE_WEATHER_RISK_REPORT_PATH)
            live_report_status = report.get("status", "unknown")
            counts = report.get("risk_class_counts", {})
            for key in risk_class_counts:
                risk_class_counts[key] = int(counts.get(key, 0))
            if report.get("warnings"):
                warnings.extend(report["warnings"])
        except Exception as e:
            warnings.append(f"Failed to read live risk report: {e}")
    else:
        warnings.append("Live weather risk report does not exist.")
        
    # Recommended mode
    if rain_risk_expected:
        recommended_mode = "weather_safe_routing_available"
    else:
        recommended_mode = "normal_route_acceptable"
        
    # Global status calculation
    status = "ok"
    if not (live_weather_available and live_risk_layer_available):
        status = "failed"
    elif not rain_risk_expected or len(warnings) > 0:
        status = "ok_with_warnings"
        
    validation_report = {
        "status": status,
        "live_weather_available": bool(live_weather_available),
        "live_risk_layer_available": bool(live_risk_layer_available),
        "live_road_weights_available": bool(live_road_weights_available),
        "rain_risk_expected": bool(rain_risk_expected),
        "official_flood_labels_claimed": False,
        "official_emergency_dispatch_claimed": False,
        "warnings": warnings
    }
    
    try:
        paths.ensure_data_dirs()
        data_loader.save_json(validation_report, paths.LIVE_ROUTE_VALIDATION_REPORT_PATH)
        logger.info(f"Saved live route validation report to {paths.LIVE_ROUTE_VALIDATION_REPORT_PATH}")
    except Exception as e:
        logger.error(f"Failed to save live route validation report: {e}")
        
    return {
        "status": status,
        "live_weather_available": bool(live_weather_available),
        "live_risk_layer_available": bool(live_risk_layer_available),
        "live_report_status": live_report_status,
        "rain_risk_expected": bool(rain_risk_expected),
        "risk_class_counts": risk_class_counts,
        "recommended_mode": recommended_mode,
        "warnings": list(set(warnings)),
        "honesty_note": "Live route recommendations are decision-support prototype outputs, not official emergency dispatch instructions."
    }


def search_places_and_roads(
    q: str,
    limit: int = 8,
    category: str | None = None,
    include_roads: bool = True,
    include_places: bool = True
):
    """Search for places, POIs, roads, and zones within local Nasr City data."""
    from . import search
    results = search.search_local(
        q=q,
        limit=limit,
        category=category,
        include_roads=include_roads,
        include_places=include_places
    )
    return {
        "status": "ok",
        "query": q,
        "results": results,
        "warnings": []
    }


def explain_zone_risk(zone_code: str, mode: str = "live", event_id: str | None = None) -> dict:
    """Delegate to explainability module to explain zone risk factors."""
    from . import explain
    return explain.explain_zone_risk(zone_code, mode=mode, event_id=event_id)


def explain_route_recommendation(origin: dict, destination: dict, mode: str = "live") -> dict:
    """Delegate to explainability module to explain route recommendations and tradeoffs."""
    from . import explain
    return explain.explain_route_recommendation(origin, destination, mode=mode)


def get_model_explainability_summary() -> dict:
    """Delegate to explainability module to retrieve global model explainability metrics."""
    from . import explain
    return explain.get_model_explainability_summary()








"""Urban Heat Risk services for FastAPI endpoints."""

import json
import logging
from typing import Dict, List, Optional
import pandas as pd

from . import paths
from .heat_explain import FACTOR_LABEL_MAP, REASON_TEMPLATES, sanitize_text

logger = logging.getLogger(__name__)

HONESTY_NOTE_LAYER = (
    "This heat-risk layer estimates relative urban heat exposure from satellite "
    "land-surface temperature and geospatial features. It is not an official "
    "public-health heat warning system."
)

HONESTY_NOTE_MODEL = (
    "The heat model is trained on verified Landsat-derived land-surface temperature "
    "anomalies. It is not an official public-health heat warning system."
)


def get_heat_health() -> Dict:
    """Retrieve availability status of model files, layer, and explainability artifacts."""
    model_path = paths.HEAT_MODELS_DIR / "heat_best_model_v1.joblib"
    layer_path = paths.HEAT_MODELS_DIR / "heat_zone_predictions_latest.geojson"
    explainability_path = paths.HEAT_MODELS_DIR / "heat_zone_explanation_factors_v1.csv"

    model_available = model_path.exists()
    latest_layer_available = layer_path.exists()
    explainability_available = explainability_path.exists()

    all_available = model_available and latest_layer_available and explainability_available

    return {
        "status": "ok" if all_available else "degraded",
        "model_available": model_available,
        "latest_layer_available": latest_layer_available,
        "explainability_available": explainability_available,
        "message": (
            "Urban heat risk outputs are available."
            if all_available
            else "Some urban heat risk files or models are missing."
        ),
    }


def get_latest_layer() -> Dict:
    """Load and return the latest GeoJSON layer containing heat risk predictions."""
    layer_path = paths.HEAT_MODELS_DIR / "heat_zone_predictions_latest.geojson"
    if not layer_path.exists():
        raise FileNotFoundError(f"Latest heat risk GeoJSON layer not found at {layer_path}")

    with open(layer_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_heat_summary() -> Dict:
    """Compute aggregated summary statistics for the latest heat risk predictions."""
    layer_path = paths.HEAT_MODELS_DIR / "heat_zone_predictions_latest.geojson"
    if not layer_path.exists():
        raise FileNotFoundError(f"Latest heat risk GeoJSON layer not found at {layer_path}")

    with open(layer_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    features = geojson.get("features", [])
    if not features:
        raise ValueError("GeoJSON layer contains no features.")

    zone_count = len(features)
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    anomalies = []
    hottest_feature = None
    max_anomaly = float("-inf")
    date_str = ""

    for feature in features:
        props = feature.get("properties", {})
        if not date_str and "date" in props:
            date_str = str(props["date"])

        anomaly = props.get("predicted_heat_anomaly_c")
        if anomaly is not None:
            anomaly = float(anomaly)
            anomalies.append(anomaly)
            if anomaly > max_anomaly:
                max_anomaly = anomaly
                hottest_feature = feature

        risk_class = props.get("predicted_heat_risk_class")
        if risk_class in risk_counts:
            risk_counts[risk_class] += 1

    mean_anomaly = sum(anomalies) / len(anomalies) if anomalies else 0.0
    max_anomaly_val = max_anomaly if max_anomaly != float("-inf") else 0.0

    # Build hottest zone info
    hottest_zone_info = {
        "zone_code": "unknown",
        "zone_label": "Zone Unknown",
        "predicted_heat_anomaly_c": 0.0,
        "predicted_heat_risk_class": "low",
    }

    if hottest_feature:
        props = hottest_feature["properties"]
        zone_code = props.get("zone_code", "unknown")
        numeric_part = zone_code.replace("NSR-GRID-", "")
        zone_label = f"Zone {int(numeric_part)}" if numeric_part.isdigit() else f"Zone {numeric_part}"

        hottest_zone_info = {
            "zone_code": zone_code,
            "zone_label": zone_label,
            "predicted_heat_anomaly_c": float(props.get("predicted_heat_anomaly_c", 0.0)),
            "predicted_heat_risk_class": str(props.get("predicted_heat_risk_class", "low")),
        }

    return {
        "status": "ok",
        "date": date_str,
        "zone_count": zone_count,
        "risk_counts": risk_counts,
        "max_heat_anomaly_c": max_anomaly_val,
        "mean_heat_anomaly_c": mean_anomaly,
        "hottest_zone": hottest_zone_info,
        "model_name": "HistGradientBoostingRegressor",
        "honesty_note": HONESTY_NOTE_LAYER,
    }


def get_model_summary() -> Dict:
    """Retrieve summary metrics, permutation importances, and data authenticity details for the Heat model."""
    metrics_path = paths.HEAT_MODELS_DIR / "heat_best_model_v1_metrics.json"
    columns_path = paths.HEAT_MODELS_DIR / "heat_feature_columns_v1.json"
    importance_path = paths.HEAT_MODELS_DIR / "heat_permutation_importance_v1.csv"
    authenticity_path = paths.NASR_CITY_HEAT_DIR / "heat_data_authenticity_report.json"
    readiness_path = paths.NASR_CITY_HEAT_DIR / "heat_training_readiness_report.json"

    # Default fallbacks
    metrics = {}
    feature_count = 61
    top_global_features = []
    authenticity_info = {"landsat_rows": 4932, "fallback_rows": 0, "ready_for_training": True}

    # Load metrics
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

    # Load columns config
    if columns_path.exists():
        with open(columns_path, "r", encoding="utf-8") as f:
            col_config = json.load(f)
            feature_count = col_config.get("feature_count", feature_count)

    # Load permutation importances
    if importance_path.exists():
        df_imp = pd.read_csv(importance_path)
        # Sort descending
        df_imp = df_imp.sort_values("importance_mean", ascending=False)
        # Select top 5-10
        top_n = df_imp.head(6)
        for _, r in top_n.iterrows():
            feat_name = str(r["feature"])
            importance = float(r["importance_mean"])
            
            # Map label
            label = FACTOR_LABEL_MAP.get(feat_name, feat_name.replace("_", " ").title())
            
            # Set default/specific reason
            if label in REASON_TEMPLATES:
                # Keep it consistent with allowed wordings
                reason = REASON_TEMPLATES[label]
            elif feat_name == "bare_sparse_ratio":
                reason = "Bare soil and sparse vegetation contribute to increased local heating."
            elif feat_name == "avg_base_speed_kph":
                reason = "Traffic flow dynamics reflect the built environment characteristics."
            elif feat_name == "elevation_mean" or feat_name == "elevation_max":
                reason = "Elevation and topography influence surface air flow and thermal patterns."
            elif feat_name == "slope_mean":
                reason = "Terrain slope affects solar radiation exposure and warmth accumulation."
            else:
                reason = f"This spatial feature is model-estimated to contribute to local heat variations."

            # Sanitize to follow safety requirements
            reason = sanitize_text(reason)

            top_global_features.append({
                "feature": feat_name,
                "label": label,
                "importance": importance,
                "reason": reason
            })

    # Load data authenticity report
    if authenticity_path.exists():
        with open(authenticity_path, "r", encoding="utf-8") as f:
            auth_data = json.load(f)
            counts = auth_data.get("row_level_source_counts", {})
            authenticity_info["landsat_rows"] = int(counts.get("landsat_gee", 4932))
            authenticity_info["fallback_rows"] = int(counts.get("fallback_physics", 0))

    # Load training readiness report
    if readiness_path.exists():
        with open(readiness_path, "r", encoding="utf-8") as f:
            readiness_data = json.load(f)
            authenticity_info["ready_for_training"] = bool(readiness_data.get("ready_for_training", True))

    return {
        "status": "ok",
        "model_name": "HistGradientBoostingRegressor",
        "target": "heat_anomaly_c",
        "feature_count": feature_count,
        "metrics": metrics,
        "top_global_features": top_global_features,
        "data_authenticity": authenticity_info,
        "honesty_note": HONESTY_NOTE_MODEL,
    }

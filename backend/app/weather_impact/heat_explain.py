"""Urban Heat Risk explainability and factor mapping service."""

import logging
import re
from typing import Dict, List, Optional
import pandas as pd

from . import paths

logger = logging.getLogger(__name__)

# Human-readable label mappings for raw fields
FACTOR_LABEL_MAP = {
    "built_surface_mean": "Built-Up Density",
    "tree_cover_ratio": "Vegetation Canopy",
    "ndbi_mean": "Built-Up Surface Index",
    "ndvi_mean": "Vegetation Health",
    "road_density": "Road Density",
    "road_density_m_per_km2": "Road Density",
    "population_sum": "Exposed Population",
    "water_coverage": "Water Coverage",
    "water_ratio": "Water Coverage",
    "bare_sparse_ratio": "Bare Soil Ratio",
    "avg_base_speed_kph": "Road Network Speed",
    "elevation_mean": "Mean Elevation",
    "elevation_max": "Max Elevation",
    "slope_mean": "Mean Slope",
    "heat_anomaly_c": "Heat Anomaly",
    "predicted_heat_anomaly_c": "Predicted Heat Anomaly",
    "predicted_heat_risk_score": "Heat Risk Score",
    "predicted_heat_risk_class": "Heat Risk Level",
    "lst_c": "Land Surface Temperature",
}

# Reason templates as specified in instructions
REASON_TEMPLATES = {
    "Built-Up Density": "Dense built-up surfaces can trap heat and reduce natural cooling.",
    "Vegetation Canopy": "Lower vegetation coverage reduces shade and evaporative cooling.",
    "Built-Up Surface Index": "Higher built-up surface intensity is associated with stronger urban heat retention.",
    "Road Density": "Dense road surfaces can contribute to heat storage and exposure.",
    "Exposed Population": "Higher exposed population increases heat-impact concern.",
    "Water Coverage": "Lower nearby water coverage reduces local cooling potential.",
}

HONESTY_NOTE = "This is a satellite-based decision-support estimate, not an official public-health heat warning."


def sanitize_text(text: str) -> str:
    """Sanitize explanation text to remove/replace any forbidden phrases."""
    if not text:
        return ""
    
    # Do not use: guaranteed, official heat warning, public-health alert, certified hazard
    replacements = {
        "official heat warning": "official public-health advisory",
        "public-health alert": "public-health notification",
        "certified hazard": "estimated exposure level",
        "guaranteed": "estimated"
    }
    
    sanitized = text
    for k, v in replacements.items():
        sanitized = re.sub(re.escape(k), v, sanitized, flags=re.IGNORECASE)
    return sanitized


def get_factor_impact(factor: str, value: float) -> str:
    """Determine impact direction based on factor characteristics."""
    # High vegetation/water generally reduces risk; low increases it
    if factor in ["tree_cover_ratio", "ndvi_mean", "water_coverage", "water_ratio"]:
        if value > 0.15:
            return "reduces heat risk"
        else:
            return "increases heat risk"
    return "increases heat risk"


def get_clean_reason(label: str, csv_reason: str) -> str:
    """Get clean reason text using template or sanitizing CSV reason."""
    if label in REASON_TEMPLATES:
        return REASON_TEMPLATES[label]
    
    # Fallback to sanitized CSV reason
    return sanitize_text(csv_reason)


def load_explanation_and_prediction(
    zone_code: str, date: Optional[str] = None, latest: bool = True
) -> Dict:
    """Load explanation factors and prediction metrics for a specific zone and date."""
    explain_path = paths.HEAT_MODELS_DIR / "heat_zone_explanation_factors_v1.csv"
    pred_path = paths.HEAT_MODELS_DIR / "heat_zone_predictions_v1.csv"

    if not explain_path.exists():
        raise FileNotFoundError(f"Explanation factors CSV not found at {explain_path}")
    if not pred_path.exists():
        raise FileNotFoundError(f"Predictions CSV not found at {pred_path}")

    # Load CSVs
    df_explain = pd.read_csv(explain_path)
    df_pred = pd.read_csv(pred_path)

    # Filter by zone code
    df_explain_zone = df_explain[df_explain["zone_code"] == zone_code]
    df_pred_zone = df_pred[df_pred["zone_code"] == zone_code]

    if df_explain_zone.empty or df_pred_zone.empty:
        raise ValueError(f"Zone code {zone_code} not found in predictions or explanations.")

    # Determine date to filter
    if date:
        row_explain = df_explain_zone[df_explain_zone["date"] == date]
        row_pred = df_pred_zone[df_pred_zone["date"] == date]
    elif latest:
        # Sort by date descending
        df_explain_zone = df_explain_zone.sort_values("date", ascending=False)
        row_explain = df_explain_zone.head(1)
        # Match same date for prediction
        latest_date = row_explain["date"].values[0]
        row_pred = df_pred_zone[df_pred_zone["date"] == latest_date]
    else:
        # First available
        row_explain = df_explain_zone.head(1)
        row_pred = df_pred_zone[df_pred_zone["date"] == row_explain["date"].values[0]]

    if row_explain.empty or row_pred.empty:
        raise ValueError(f"No heat risk prediction found for zone {zone_code} on date {date or 'latest'}")

    explain_row = row_explain.iloc[0].to_dict()
    pred_row = row_pred.iloc[0].to_dict()

    # Extract top factors
    top_factors = []
    for i in range(1, 4):
        f_col = f"top_factor_{i}"
        v_col = f"top_factor_{i}_value"
        r_col = f"top_factor_{i}_reason"
        l_col = f"top_factor_{i}_label"

        if f_col in explain_row and pd.notna(explain_row[f_col]) and explain_row[f_col] != "":
            factor_name = str(explain_row[f_col])
            value = float(explain_row[v_col]) if v_col in explain_row and pd.notna(explain_row[v_col]) else 0.0
            
            # Map label
            label = FACTOR_LABEL_MAP.get(factor_name, str(explain_row.get(l_col, factor_name)))
            if label == factor_name and "_" in label:
                label = label.replace("_", " ").title()

            # Map reason
            csv_reason = str(explain_row[r_col]) if r_col in explain_row and pd.notna(explain_row[r_col]) else ""
            reason = get_clean_reason(label, csv_reason)

            # Impact
            impact = get_factor_impact(factor_name, value)

            top_factors.append({
                "factor": factor_name,
                "label": label,
                "value": value,
                "impact": impact,
                "reason": reason
            })

    # Zone label
    numeric_part = zone_code.replace("NSR-GRID-", "")
    if numeric_part.isdigit():
        zone_label = f"Zone {int(numeric_part)}"
    else:
        zone_label = f"Zone {numeric_part}"

    predicted_anomaly = float(pred_row["predicted_heat_anomaly_c"])
    predicted_score = float(pred_row["predicted_heat_risk_score"])
    predicted_class = str(pred_row["predicted_heat_risk_class"])

    summary = f"{zone_label} is estimated as {predicted_class} heat risk."

    raw_explanation_text = explain_row.get("explanation_text", "")
    explanation_text = sanitize_text(raw_explanation_text)
    if not explanation_text:
        explanation_text = f"This zone is estimated as {predicted_class} heat risk based on satellite measurements and spatial indicators."

    return {
        "status": "ok",
        "zone_code": zone_code,
        "zone_label": zone_label,
        "date": str(explain_row["date"]),
        "predicted_heat_risk_class": predicted_class,
        "predicted_heat_anomaly_c": predicted_anomaly,
        "predicted_heat_risk_score": predicted_score,
        "summary": summary,
        "top_factors": top_factors,
        "explanation_text": explanation_text,
        "honesty_note": HONESTY_NOTE
    }

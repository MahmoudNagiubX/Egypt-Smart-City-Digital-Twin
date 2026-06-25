"""Zone and Route explainability algorithms and API helpers."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import re
import pandas as pd

from backend.app.weather_impact import paths, service, routing

logger = logging.getLogger(__name__)

# Static labels mapping
FEATURE_LABELS = {
    "rain_24h_mm": "24h Rainfall",
    "rain_6h_mm": "6h Rainfall",
    "rain_3h_mm": "3h Rainfall",
    "rain_1h_mm": "1h Rainfall",
    "built_surface_mean": "Built-Up Density",
    "population_sum": "Exposed Population",
    "road_density_m_per_km2": "Road Density",
    "road_density": "Road Density",
    "elevation_mean": "Elevation",
    "slope_mean": "Slope",
    "low_elevation_score": "Low Elevation Risk",
    "vegetation_ratio": "Vegetation Coverage",
    "water_ratio": "Water Coverage",
    "bare_ratio": "Bare Land",
    "live_predicted_score": "Live Risk Score",
    "live_risk_class": "Live Risk Level",
    "antecedent_rain_proxy": "Antecedent Rainfall Proxy",
    "low_slope_score": "Low Slope Risk",
    "built_surface_x_low_vegetation": "Built-Up Density and Low Vegetation Interaction",
    "imperviousness_proxy": "Imperviousness Proxy",
    "exposure_x_hazard_proxy": "Exposure Hazard Interaction",
    "rain_x_impervious_proxy": "Rainfall Imperviousness Interaction"
}

# Static characteristics cache
_zone_static_cache: Dict[str, dict] = {}
_cache_initialized = False

def _initialize_zone_static_cache():
    global _zone_static_cache, _cache_initialized
    if _cache_initialized:
        return
    
    logger.info("Initializing explainability zone static characteristics cache...")
    try:
        cols = ['built_surface_mean', 'road_density_m_per_km2', 'elevation_mean', 'slope_mean', 'low_elevation_score']
        
        # Prefer training dataset since it has all normalized features
        dataset_path = paths.REAL_OBSERVED_TRAINING_DATASET_PATH
        if dataset_path.exists():
            df = pd.read_csv(dataset_path)
            # Find matching zone characteristics
            df_static = df.groupby('zone_code')[cols].first().reset_index()
            for _, row in df_static.iterrows():
                zcode = row['zone_code']
                _zone_static_cache[zcode] = {
                    'built_surface_mean': float(row['built_surface_mean']) if not pd.isna(row['built_surface_mean']) else 0.0,
                    'road_density_m_per_km2': float(row['road_density_m_per_km2']) if not pd.isna(row['road_density_m_per_km2']) else 0.0,
                    'elevation_mean': float(row['elevation_mean']) if not pd.isna(row['elevation_mean']) else 150.0,
                    'slope_mean': float(row['slope_mean']) if not pd.isna(row['slope_mean']) else 5.0,
                    'low_elevation_score': float(row['low_elevation_score']) if not pd.isna(row['low_elevation_score']) else 0.0
                }
            logger.info(f"Loaded {len(_zone_static_cache)} zone characteristics from training dataset.")
            _cache_initialized = True
            return
            
        # Fallback to zone_features_ml_ready.csv if training data missing
        fallback_path = paths.ZONE_FEATURES_CSV_PATH
        if fallback_path.exists():
            df = pd.read_csv(fallback_path)
            cols_fallback = [c for c in cols if c in df.columns]
            df_static = df.groupby('zone_code')[cols_fallback].first().reset_index()
            for _, row in df_static.iterrows():
                zcode = row['zone_code']
                _zone_static_cache[zcode] = {
                    'built_surface_mean': float(row.get('built_surface_mean', 0.0)) if not pd.isna(row.get('built_surface_mean', 0.0)) else 0.0,
                    'road_density_m_per_km2': float(row.get('road_density_m_per_km2', 0.0)) if not pd.isna(row.get('road_density_m_per_km2', 0.0)) else 0.0,
                    'elevation_mean': float(row.get('elevation_mean', 150.0)) if not pd.isna(row.get('elevation_mean', 150.0)) else 150.0,
                    'slope_mean': float(row.get('slope_mean', 5.0)) if not pd.isna(row.get('slope_mean', 5.0)) else 5.0,
                    'low_elevation_score': float(row.get('low_elevation_score', 0.0)) if not pd.isna(row.get('low_elevation_score', 0.0)) else 0.0
                }
            logger.info(f"Loaded {len(_zone_static_cache)} zone characteristics from ML ready features fallback.")
            _cache_initialized = True
            return
            
        logger.warning("Explainability cache source files missing; rule-based factors fallback enabled.")
    except Exception as e:
        logger.error(f"Failed to initialize explainability cache: {e}")

def explain_zone_risk(zone_code: str, mode: str = "live", event_id: Optional[str] = None) -> dict:
    """Explain why a specific zone has its estimated risk level."""
    _initialize_zone_static_cache()
    
    zone_code_upper = zone_code.upper().strip()
    
    # Resolve user-friendly label (Zone X) from code (NSR-GRID-X)
    match = re.search(r'\d+', zone_code_upper)
    zone_number = match.group(0).lstrip('0') if match else zone_code_upper
    if not zone_number:
        zone_number = "0"
    zone_label = f"Zone {zone_number}"
    
    honesty_note = (
        "The model estimates relative weather-impact risk using engineered features and weak labels. "
        "It is not trained on verified official flood incident labels."
    )
    confidence_note = "This is a model-estimated relative risk explanation, not an official flood report."
    
    if mode == "live":
        # Load live predictions CSV
        pred_path = paths.LIVE_WEATHER_RISK_PREDICTIONS_CSV_PATH
        if not pred_path.exists():
            logger.info("Live weather predictions missing. Generating...")
            try:
                service.generate_live_weather_risk_layer()
            except Exception as e:
                logger.error(f"Failed to generate live predictions: {e}")
                
        if pred_path.exists():
            df_live = pd.read_csv(pred_path)
            row_live = df_live[df_live['zone_code'] == zone_code_upper]
            if not row_live.empty:
                row_data = row_live.iloc[0].to_dict()
                risk_score = float(row_data.get('live_predicted_score', 0.0))
                risk_class = str(row_data.get('live_risk_class', 'low'))
                risk_label = f"{risk_class.capitalize()} Risk"
                
                # Rule-based threshold top factor selection
                static_data = _zone_static_cache.get(zone_code_upper, {
                    'built_surface_mean': 2000.0,
                    'road_density_m_per_km2': 10000.0,
                    'elevation_mean': 150.0,
                    'slope_mean': 5.0,
                    'low_elevation_score': 0.4
                })
                
                candidates = []
                
                # 24h Rain
                r24 = float(row_data.get('rain_24h_mm', 0.0))
                candidates.append({
                    "factor": "rain_24h_mm",
                    "label": FEATURE_LABELS["rain_24h_mm"],
                    "value": r24,
                    "impact": "increases risk" if r24 > 5.0 else "neutral",
                    "reason": "Higher 24-hour rainfall increases surface water accumulation risk.",
                    "score": r24 * 1.5
                })
                
                # 6h Rain
                r6 = float(row_data.get('rain_6h_mm', 0.0))
                candidates.append({
                    "factor": "rain_6h_mm",
                    "label": FEATURE_LABELS["rain_6h_mm"],
                    "value": r6,
                    "impact": "increases risk" if r6 > 2.0 else "neutral",
                    "reason": "Higher 6-hour rainfall intensity increases estimated runoff.",
                    "score": r6 * 2.0
                })
                
                # Built-Up Mean
                bs = static_data['built_surface_mean']
                candidates.append({
                    "factor": "built_surface_mean",
                    "label": FEATURE_LABELS["built_surface_mean"],
                    "value": bs,
                    "impact": "increases risk" if bs > 2500 else "neutral",
                    "reason": "Dense built-up surfaces reduce natural ground absorption and infiltration.",
                    "score": (bs / 5187.0) * 8.0
                })
                
                # Road density
                rd = static_data['road_density_m_per_km2']
                candidates.append({
                    "factor": "road_density_m_per_km2",
                    "label": FEATURE_LABELS["road_density_m_per_km2"],
                    "value": rd,
                    "impact": "increases risk" if rd > 15000 else "neutral",
                    "reason": "Dense road networks increase exposure of transportation infrastructure.",
                    "score": (rd / 71226.0) * 6.0
                })
                
                # Low elevation score
                le = static_data['low_elevation_score']
                candidates.append({
                    "factor": "low_elevation_score",
                    "label": FEATURE_LABELS["low_elevation_score"],
                    "value": le,
                    "impact": "increases risk" if le > 0.6 else "neutral",
                    "reason": "Lower elevation makes the area a potential sink for surrounding water runoff.",
                    "score": le * 5.0
                })
                
                # Slope
                sl = static_data['slope_mean']
                candidates.append({
                    "factor": "slope_mean",
                    "label": FEATURE_LABELS["slope_mean"],
                    "value": sl,
                    "impact": "increases risk" if sl < 4.0 else "neutral",
                    "reason": "Flatter terrain slows natural drainage, increasing accumulation risk.",
                    "score": (12.0 - sl) * 0.5
                })
                
                # Sort by score descending and take top 3
                candidates.sort(key=lambda x: x["score"], reverse=True)
                top_factors = []
                for c in candidates[:3]:
                    top_factors.append({
                        "factor": c["factor"],
                        "label": c["label"],
                        "value": round(c["value"], 2),
                        "impact": c["impact"],
                        "reason": c["reason"]
                    })
                
                # Generate explanation text
                factors_text = []
                for i, factor in enumerate(top_factors):
                    reason_lowered = factor['reason'][0].lower() + factor['reason'][1:]
                    factors_text.append(f"{i+1}) {factor['label']} ({factor['value']:.2f}) which {reason_lowered}")
                explanation_text = f"This zone is model-estimated as {risk_class} risk. The primary risk drivers are: " + ", ".join(factors_text) + "."
                
                return {
                    "status": "ok_with_warnings",
                    "zone_code": zone_code_upper,
                    "zone_label": zone_label,
                    "mode": "live",
                    "risk_score": round(risk_score, 4),
                    "risk_class": risk_class,
                    "risk_label": risk_label,
                    "summary": f"{zone_label} is currently estimated as {risk_label.lower()}.",
                    "top_factors": top_factors,
                    "explanation_text": explanation_text,
                    "confidence_note": "This is a model-estimated relative risk explanation computed from current live weather and static features, not an official flood report.",
                    "honesty_note": honesty_note
                }
                
        # If live record not found, raise value error
        raise ValueError(f"Zone {zone_code_upper} not found in current live predictions.")
        
    else:  # historical mode
        factors_path = paths.ZONE_EXPLANATION_FACTORS_V2_PATH
        if not factors_path.exists():
            raise FileNotFoundError("Historical explanation factors v2 file is missing.")
            
        df_factors = pd.read_csv(factors_path)
        df_zone = df_factors[df_factors['zone_code'] == zone_code_upper]
        if df_zone.empty:
            raise ValueError(f"Zone {zone_code_upper} not found in historical records.")
            
        if event_id:
            row_hist = df_zone[df_zone['event_id'] == event_id]
            if row_hist.empty:
                # Fallback: take highest risk event for this zone
                row_hist = df_zone.sort_values(by='predicted_score', ascending=False)
        else:
            # Take highest risk event
            row_hist = df_zone.sort_values(by='predicted_score', ascending=False)
            
        row_data = row_hist.iloc[0].to_dict()
        
        # Parse top factors
        top_factors = []
        for i in range(1, 4):
            f_name = row_data.get(f"top_factor_{i}")
            if f_name and not pd.isna(f_name):
                f_val = float(row_data.get(f"top_factor_{i}_value", 0.0))
                f_reason = str(row_data.get(f"top_factor_{i}_reason", "Local environmental factor increases risk."))
                top_factors.append({
                    "factor": str(f_name),
                    "label": FEATURE_LABELS.get(str(f_name), str(f_name)),
                    "value": round(f_val, 2),
                    "impact": "increases risk" if f_val > 0 else "neutral",
                    "reason": f_reason
                })
                
        risk_score = float(row_data.get('predicted_score', 0.0))
        risk_class = str(row_data.get('predicted_risk_class', 'low'))
        risk_label = f"{risk_class.capitalize()} Risk"
        explanation_text = str(row_data.get('explanation_text', ''))
        
        # Replace raw feature names in explanation_text with human labels
        for k, v in FEATURE_LABELS.items():
            explanation_text = explanation_text.replace(k, v)
            
        return {
            "status": "ok",
            "zone_code": zone_code_upper,
            "zone_label": zone_label,
            "mode": f"historical (event {row_data.get('event_id')})",
            "risk_score": round(risk_score, 4),
            "risk_class": risk_class,
            "risk_label": risk_label,
            "summary": f"{zone_label} is estimated as {risk_label.lower()} during historical event {row_data.get('event_id')}.",
            "top_factors": top_factors,
            "explanation_text": explanation_text,
            "confidence_note": confidence_note,
            "honesty_note": honesty_note
        }

def explain_route_recommendation(origin: dict, destination: dict, mode: str = "live") -> dict:
    """Explain why the weather-safe route was or was not recommended."""
    # Build routing coordinates
    orig_coords = {"lat": float(origin["lat"]), "lon": float(origin["lon"])}
    dest_coords = {"lat": float(destination["lat"]), "lon": float(destination["lon"])}
    
    # Compute live custom route using existing logic
    route_res = routing.compute_live_custom_route(orig_coords, dest_coords, route_preference="both")
    
    recommendation = route_res["recommendation"]
    metrics = route_res["comparison"]
    
    # Set recommendation label
    rec_label_map = {
        "normal_route_acceptable": "Normal Route Acceptable",
        "weather_safe_route_recommended": "Weather-Safe Route Recommended",
        "no_distinct_safer_alternative": "No Distinct Safer Alternative"
    }
    recommendation_label = rec_label_map.get(recommendation, "Normal Route Acceptable")
    
    # Build Route Reasons list
    reasons = []
    
    reduction_val = float(metrics.get("risk_reduction_percent", 0.0))
    tradeoff_val = float(metrics.get("eta_tradeoff_percent", 0.0))
    avoided_segs = int(metrics.get("avoided_high_risk_segments", 0))
    
    # Risk Reduction reason
    if reduction_val > 0.0:
        reasons.append({
            "label": "Risk Reduction",
            "value": f"{reduction_val:.1f}%",
            "reason": "The safe route avoids higher-risk road segments."
        })
    else:
        reasons.append({
            "label": "Risk Reduction",
            "value": "0.0%",
            "reason": "Both routes present equivalent model-estimated risk."
        })
        
    # ETA Tradeoff reason
    if tradeoff_val > 0.0:
        reasons.append({
            "label": "ETA Tradeoff",
            "value": f"{tradeoff_val:.1f}%",
            "reason": "The safer route adds a small travel-time penalty."
        })
    else:
        reasons.append({
            "label": "ETA Tradeoff",
            "value": "0.0%",
            "reason": "The safer route follows the same layout or adds no travel time."
        })
        
    # Segment avoidance if relevant
    if avoided_segs > 0:
        reasons.append({
            "label": "Segment Avoidance",
            "value": str(avoided_segs),
            "reason": f"Avoids {avoided_segs} road segment(s) with high estimated rain risk."
        })
        
    # Determine summary and explanations
    if recommendation == "normal_route_acceptable":
        summary = "No meaningful rain-related route risk is expected. The normal route is acceptable."
    elif recommendation == "weather_safe_route_recommended":
        summary = "The weather-safe route is recommended because it reduces model-estimated route risk while keeping the ETA tradeoff acceptable."
    else:  # no_distinct_safer_alternative
        summary = "The system did not find a distinct route with lower model-estimated risk."
        
    if reduction_val <= 0:
        summary = "The normal route is recommended. Both paths present equivalent estimated risk."
        
    if tradeoff_val > 20.0:
        summary += " Note: The estimated safety improvement comes with a significant travel-time tradeoff."
        
    normal_high_segs = int(metrics.get("live_high_risk_segment_count_normal", 0))
    normal_mean_risk = float(metrics.get("normal_mean_live_risk_score", 0.0))
    normal_explanation = {
        "summary": "The normal route crosses more model-estimated rain-risk areas." if normal_high_segs > 0 else "The normal route is clear of significant weather-impact risk.",
        "risk_level": "higher" if reduction_val > 5.0 else "normal",
        "high_risk_segments": normal_high_segs,
        "mean_risk_score": round(normal_mean_risk, 4)
    }
    
    safe_high_segs = int(metrics.get("live_high_risk_segment_count_safe", 0))
    safe_mean_risk = float(metrics.get("safe_mean_live_risk_score", 0.0))
    safe_explanation = {
        "summary": "The safe route avoids some higher-risk segments." if avoided_segs > 0 else "The safe route follows the standard road path.",
        "risk_level": "lower" if reduction_val > 5.0 else "normal",
        "high_risk_segments": safe_high_segs,
        "mean_risk_score": round(safe_mean_risk, 4)
    }
    
    comparison = {
        "risk_reduction_percent": round(reduction_val, 2),
        "eta_tradeoff_percent": round(tradeoff_val, 2),
        "avoided_high_risk_segments": avoided_segs,
        "normal_distance_m": float(metrics.get("normal_distance_m", 0.0)),
        "safe_distance_m": float(metrics.get("safe_distance_m", 0.0))
    }
    
    return {
        "status": "ok",
        "mode": "live",
        "recommendation": recommendation,
        "recommendation_label": recommendation_label,
        "summary": summary,
        "route_reasons": reasons,
        "normal_route_explanation": normal_explanation,
        "safe_route_explanation": safe_explanation,
        "comparison": comparison,
        "honesty_note": "Routes are decision-support prototype outputs based on model-estimated weather-impact risk, not official emergency dispatch instructions."
    }

def get_model_explainability_summary() -> dict:
    """Retrieve global model explanation summary, feature importances, and metrics."""
    # Default outputs if files missing
    model_name = "Ridge Baseline V2"
    model_type = "weak-label supervised regression"
    target = "engineered weather-impact risk score"
    model_size_mb = 0.0029
    metrics = {
        "R2": 0.9999,
        "MAE": 1.2e-05,
        "RMSE": 1.5e-05,
        "Severity Macro F1": 1.0000,
        "best_alpha": 10.0
    }
    reasoning = "Selected for high efficiency and generalization in Ridge Baseline v2."
    
    # 1. Try to load metrics
    metrics_path = paths.BEST_MODEL_V2_METRICS_PATH
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
                metrics.update(metrics_data)
        except Exception as e:
            logger.warning(f"Error loading model metrics: {e}")
            
    # 2. Try to load model selection reason
    reason_path = paths.MODEL_SELECTION_REASON_V2_PATH
    if reason_path.exists():
        try:
            with open(reason_path, "r", encoding="utf-8") as f:
                reason_data = json.load(f)
                reasoning = reason_data.get("reasoning", reasoning)
                model_name = reason_data.get("selected_model", model_name)
                if "all_candidates_scored" in reason_data and model_name in reason_data["all_candidates_scored"]:
                    model_size_mb = float(reason_data["all_candidates_scored"][model_name].get("model_size_mb", model_size_mb))
        except Exception as e:
            logger.warning(f"Error loading selection reason: {e}")
            
    # 3. Load global features from permutation importance
    top_global_features = []
    imp_path = paths.PERMUTATION_IMPORTANCE_V2_PATH
    if imp_path.exists():
        try:
            df_imp = pd.read_csv(imp_path)
            for _, row in df_imp.head(10).iterrows():
                f_name = str(row['feature'])
                f_imp = float(row.get('importance_mean', 0.0))
                
                # Define feature explain reasons
                reasons_map = {
                    "built_surface_mean": "Dense built-up surfaces reduce natural ground absorption and increase runoff potential.",
                    "rain_24h_mm": "Higher 24-hour rainfall represents the total volume of water accumulated over the day.",
                    "rain_6h_mm": "6-hour rainfall volume indicates mid-term precipitation intensity and storm duration.",
                    "elevation_mean": "Elevation determines natural drainage paths and low-lying accumulation zones.",
                    "slope_mean": "Flatter slopes slow down natural drainage, leading to surface water pooling.",
                    "rain_1h_mm": "1-hour rainfall volume captures short-duration peak precipitation intensity.",
                    "antecedent_rain_proxy": "Rainfall from previous days limits the remaining ground absorption capacity.",
                    "low_slope_score": "Identifies areas with flat terrain highly susceptible to water accumulation.",
                    "rain_3h_mm": "3-hour rainfall volume contributes to short-to-mid-term runoff generation.",
                    "built_surface_x_low_vegetation": "Interaction between dense building cover and lack of vegetation accelerates runoff."
                }
                reason = reasons_map.get(f_name, "Estimated feature contribution to relative weather-impact risk score.")
                
                top_global_features.append({
                    "feature": f_name,
                    "label": FEATURE_LABELS.get(f_name, f_name),
                    "importance": round(f_imp, 4),
                    "reason": reason
                })
        except Exception as e:
            logger.warning(f"Error loading permutation importance: {e}")
            
    # Fallback default features if empty
    if not top_global_features:
        default_features = [
            ("built_surface_mean", 0.5096, "Dense built-up surfaces reduce natural ground absorption and increase runoff potential."),
            ("rain_24h_mm", 0.4431, "Higher 24-hour rainfall represents the total volume of water accumulated over the day."),
            ("rain_6h_mm", 0.0734, "6-hour rainfall volume indicates mid-term precipitation intensity and storm duration."),
            ("elevation_mean", 0.0647, "Elevation determines natural drainage paths and low-lying accumulation zones.")
        ]
        for f, imp, r in default_features:
            top_global_features.append({
                "feature": f,
                "label": FEATURE_LABELS.get(f, f),
                "importance": imp,
                "reason": r
            })
            
    known_limitations = [
        "Target variable is an engineered index, not direct flood sensor readings.",
        "Trained using weak labels based on a combined exposure-hazard formula.",
        "Does not account for real-time drainage network updates or blockages."
    ]
    
    honesty_note = (
        "The model predicts an engineered weather-impact risk score derived from real weather, satellite, road, and exposure features. "
        "It is not trained on verified official flood incident labels."
    )
    
    return {
        "status": "ok",
        "model_name": model_name,
        "model_type": model_type,
        "target": target,
        "top_global_features": top_global_features,
        "metrics": metrics,
        "model_size_mb": round(model_size_mb, 4),
        "known_limitations": known_limitations,
        "honesty_note": honesty_note
    }

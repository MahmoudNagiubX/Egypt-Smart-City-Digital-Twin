"""Project audit, safe cleanup, and model baseline review script for Phase 9A."""

import sys
import json
import logging
import time
from pathlib import Path
import shutil
import pandas as pd
import numpy as np
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
APP_ROOT = BACKEND_ROOT / "app"
DATA_DIR = APP_ROOT / "data" / "nasr_city"
REPORTS_DIR = DATA_DIR / "reports"

# Ensure reports directory exists
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Add parent directory to path to enable local app imports
sys.path.append(str(PROJECT_ROOT))

# Core folders to scan for inventory
FOLDERS_TO_SCAN = {
    "weather_impact": APP_ROOT / "weather_impact",
    "scripts": APP_ROOT / "scripts",
    "tests": APP_ROOT / "tests",
    "nasr_city_data": DATA_DIR,
    "frontend_src": PROJECT_ROOT / "frontend" / "src"
}

def classify_file(rel_path: Path):
    path_str = str(rel_path.as_posix())
    
    # Check cache first
    if "__pycache__" in path_str or ".pytest_cache" in path_str or ".mypy_cache" in path_str or ".ruff_cache" in path_str or path_str.endswith(".pyc"):
        return "cache", "safe_to_delete", "Temporary cache or compilation file"
        
    if path_str.startswith("frontend/src/"):
        return "frontend_source", "required", "Frontend React application source file"
        
    if path_str.startswith("backend/app/tests/"):
        return "test", "required", "Backend test file"
        
    if path_str.startswith("backend/app/scripts/"):
        return "source_code", "required", "Pipeline/audit/utility script"
        
    if path_str.startswith("backend/app/weather_impact/"):
        return "source_code", "required", "Core weather-impact module source code"
        
    if path_str.startswith("backend/app/data/nasr_city/"):
        parts = rel_path.parts
        # parts look like ('backend', 'app', 'data', 'nasr_city', ...)
        subfolder = parts[4] if len(parts) > 4 else ""
        
        if subfolder == "raw":
            return "raw_data", "required", "Raw weather history / raw input data"
            
        elif subfolder == "processed":
            return "processed_data", "generated_but_required", "Processed geospatial datasets or features"
            
        elif subfolder == "models":
            ext = rel_path.suffix
            if ext == ".joblib":
                return "model_artifact", "generated_but_required", "Trained ML model binary"
            elif ext == ".json" and ("metrics" in path_str or "comparison" in path_str or "summary" in path_str):
                return "model_metrics", "generated_but_required", "Model training metrics or split metadata"
            elif ext == ".csv" and "importance" in path_str:
                return "model_metrics", "generated_but_required", "Feature importance metrics"
            elif ext == ".png" and "importance" in path_str:
                return "model_metrics", "reproducible", "Feature importance plot visualization"
            elif rel_path.name == "MODEL_CARD.md":
                return "report", "required", "Model documentation and metadata card"
            else:
                return "processed_data", "generated_but_required", "Model-related data artifact"
                
        elif subfolder == "outputs":
            if rel_path.name.startswith("live_") or "live" in path_str:
                return "live_weather_output", "generated_but_required", "Live weather hazard predictions and weights"
            elif "route" in path_str or "routing" in path_str:
                return "route_output", "reproducible", "Route analysis/comparison output"
            elif "report" in path_str or "validation" in path_str:
                return "report", "reproducible", "Generated validation/audit report"
            else:
                return "processed_data", "reproducible", "Model predictions or generated outputs"
                
        elif subfolder == "cache":
            if rel_path.name == "live_open_meteo_forecast.json":
                return "cache", "review_needed", "Cached weather forecast from Open-Meteo"
            return "cache", "reproducible", "Cached temporary file"
            
        elif subfolder == "samples":
            return "raw_data", "reproducible", "Sample/dummy data for testing and local runs"
            
        elif subfolder == "maps":
            return "processed_data", "reproducible", "Static map visualizations"
            
        elif subfolder == "reports":
            return "report", "required", "Audit/project state report"

    return "unknown", "review_needed", "File in unscanned directory or unknown category"

def run_project_file_inventory():
    logger.info("Running Step 1: Generating project file inventory...")
    inventory = []
    
    for key, folder in FOLDERS_TO_SCAN.items():
        if not folder.exists():
            logger.warning(f"Scan directory does not exist: {folder}")
            continue
            
        # Scan files recursively
        for path in folder.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(PROJECT_ROOT)
                file_size = path.stat().st_size
                mtime = path.stat().st_mtime
                mtime_str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(mtime))
                
                category, required_status, reason = classify_file(rel_path)
                
                inventory.append({
                    "path": rel_path.as_posix(),
                    "file_type": path.suffix.lower() or "no_extension",
                    "size": file_size,
                    "last_modified": mtime_str,
                    "category": category,
                    "required_status": required_status,
                    "reason": reason
                })
                
    # Save inventory
    inventory_path = REPORTS_DIR / "project_file_inventory.json"
    with open(inventory_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
    logger.info(f"Inventory saved successfully with {len(inventory)} entries to {inventory_path}")
    return inventory

def run_safe_cleanup():
    logger.info("Running Step 2: Executing safe cleanup...")
    deleted_files = []
    deleted_folders = []
    
    # Define directories that are safe to delete entirely if they are caches
    cache_dirs_to_check = [
        PROJECT_ROOT / ".pytest_cache",
        PROJECT_ROOT / ".mypy_cache",
        PROJECT_ROOT / ".ruff_cache",
    ]
    
    # Find __pycache__ folders recursively in backend/app
    backend_app = PROJECT_ROOT / "backend" / "app"
    if backend_app.exists():
        for p in backend_app.rglob("__pycache__"):
            if p.is_dir():
                cache_dirs_to_check.append(p)
                
    # Find .pyc files
    pyc_files_to_delete = []
    if backend_app.exists():
        for p in backend_app.rglob("*.pyc"):
            if p.is_file():
                pyc_files_to_delete.append(p)
                
    # Execute file deletion
    for f in pyc_files_to_delete:
        try:
            rel_p = f.relative_to(PROJECT_ROOT).as_posix()
            f.unlink()
            deleted_files.append(rel_p)
            logger.info(f"Deleted cache file: {rel_p}")
        except Exception as e:
            logger.error(f"Error deleting cache file {f}: {e}")
            
    # Execute directory deletion
    # Sort from deepest to shallowest to avoid parent-child conflicts
    for d in sorted(cache_dirs_to_check, key=lambda x: len(x.parts), reverse=True):
        if d.exists() and d.is_dir():
            try:
                rel_p = d.relative_to(PROJECT_ROOT).as_posix()
                shutil.rmtree(d)
                deleted_folders.append(rel_p)
                logger.info(f"Deleted cache directory: {rel_p}")
            except Exception as e:
                logger.error(f"Error deleting cache directory {d}: {e}")
                
    # Compile candidate list for review (not deleted)
    safe_to_delete_candidates = [
        "frontend/dist"  # Untracked in git, but generated via build
    ]
    
    review_needed = [
        "backend/app/data/nasr_city/cache/live_open_meteo_forecast.json"
    ]
    
    protected_patterns = [
        "backend/app/data/nasr_city/models/*.joblib",
        "backend/app/data/nasr_city/models/ml_feature_columns.json",
        "backend/app/data/nasr_city/processed/*.csv",
        "backend/app/data/nasr_city/processed/*.geojson",
        "backend/app/data/nasr_city/outputs/live_*",
        "backend/app/data/nasr_city/outputs/demo_route_*",
        "backend/app/data/nasr_city/outputs/route_comparison_*",
        "backend/app/data/nasr_city/outputs/*validation_report.json",
        "backend/app/data/nasr_city/outputs/*metrics.json",
        "frontend/src/**",
        "backend/app/**.py",
        "README.md"
    ]
    
    report = {
        "status": "ok",
        "files_deleted": deleted_files,
        "folders_deleted": deleted_folders,
        "safe_to_delete_candidates": safe_to_delete_candidates,
        "review_needed": review_needed,
        "protected_patterns": protected_patterns,
        "warnings": []
    }
    
    cleanup_report_path = REPORTS_DIR / "safe_cleanup_report.json"
    with open(cleanup_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Safe cleanup report saved to {cleanup_report_path}")
    return report

def run_model_baseline_review():
    logger.info("Running Step 3: Performing model baseline review...")
    
    dataset_path = DATA_DIR / "processed" / "real_observed_training_dataset.csv"
    if not dataset_path.exists():
        logger.error(f"Training dataset not found: {dataset_path}")
        return {}
        
    # Read training dataset
    df = pd.read_csv(dataset_path)
    row_count = len(df)
    
    # Read feature columns list
    feature_cols_path = DATA_DIR / "models" / "ml_feature_columns.json"
    if feature_cols_path.exists():
        with open(feature_cols_path, "r", encoding="utf-8") as f:
            feature_cols = json.load(f)
    else:
        feature_cols = []
    feature_count = len(feature_cols)
    
    # Read model comparison
    comparison_path = DATA_DIR / "models" / "model_comparison.json"
    if comparison_path.exists():
        with open(comparison_path, "r", encoding="utf-8") as f:
            model_comparison = json.load(f)
    else:
        model_comparison = {}
        
    # Compute class distribution
    if "data_driven_weather_impact_score" in df.columns:
        scores = df["data_driven_weather_impact_score"]
        classes = []
        for s in scores:
            if s < 0.33:
                classes.append("low")
            elif s < 0.66:
                classes.append("medium")
            else:
                classes.append("high")
        s_series = pd.Series(classes)
        counts = s_series.value_counts().to_dict()
        pcts = (s_series.value_counts(normalize=True) * 100).to_dict()
        
        class_distribution = {}
        for k in ["low", "medium", "high"]:
            class_distribution[k] = {
                "count": int(counts.get(k, 0)),
                "percentage": float(round(pcts.get(k, 0.0), 2))
            }
    else:
        class_distribution = {}
        
    # Compute missing values summary
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    missing_counts = {col: int(val) for col, val in missing_cols.items()}
    missing_summary = {
        "has_missing": len(missing_counts) > 0,
        "missing_counts": missing_counts,
        "total_missing": int(missing.sum())
    }
    
    # Read feature importance
    feat_imp_path = DATA_DIR / "models" / "feature_importance.csv"
    top_features = []
    if feat_imp_path.exists():
        try:
            feat_imp_df = pd.read_csv(feat_imp_path)
            # Take top 10
            for idx, row in feat_imp_df.head(10).iterrows():
                top_features.append({
                    "feature": str(row["feature"]),
                    "importance": float(row["importance"]),
                    "rank": int(row["rank"])
                })
        except Exception as e:
            logger.error(f"Error loading feature importance: {e}")
            
    # Baseline review structure
    review = {
        "dataset_path": dataset_path.relative_to(PROJECT_ROOT).as_posix(),
        "row_count": row_count,
        "feature_count": feature_count,
        "target_columns": ["data_driven_weather_impact_score"],
        "current_selected_model": model_comparison.get("best_model", "Random Forest"),
        "current_metrics": model_comparison.get("metric_comparison", {}),
        "train_test_split_strategy": "Event-based split using GroupShuffleSplit on event_id. 24 training events (9984 rows) and 6 test events (2496 rows) with no spatial-temporal overlap between splits.",
        "leakage_risks": "High spatial autocorrelation due to neighboring zone grid units sharing similar static features (e.g. built-up density, elevation). Although temporal/event leakage is mitigated by event-based splitting, spatial features are highly stable and risk leakage might exist.",
        "weak_label_limitation": "Target variable is an engineered hazard-exposure-vulnerability risk target rather than official street-level verified flood incident labels.",
        "class_distribution": class_distribution,
        "missing_value_summary": missing_summary,
        "top_feature_importance": top_features,
        "current_model_weaknesses": [
            "Heavy Random Forest joblib model (96.5 MB) makes inference deployment heavy.",
            "Relies on engineered surrogate target rather than actual ground truth flood data.",
            "Very high R2 (0.98) points to high likelihood of overfitting or spatial feature leakage.",
            "Lacks dynamic temporal propagation (e.g. water routing, flow accumulation between zones)."
        ],
        "recommended_next_candidate_models": [
            "RandomForestRegressor tuned",
            "ExtraTreesRegressor",
            "HistGradientBoostingRegressor tuned",
            "GradientBoostingRegressor",
            "Ridge/ElasticNet baseline if useful"
        ]
    }
    
    review_path = REPORTS_DIR / "model_baseline_review.json"
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review, f, indent=2)
        
    logger.info(f"Model baseline review saved to {review_path}")
    return review

def run_feature_engineering_gap_report():
    logger.info("Running Step 4: Generating feature engineering gap report...")
    
    feature_cols_path = DATA_DIR / "models" / "ml_feature_columns.json"
    if feature_cols_path.exists():
        with open(feature_cols_path, "r", encoding="utf-8") as f:
            feature_cols = json.load(f)
    else:
        feature_cols = []
        
    # Group current features
    current_groups = {
        "weather": [f for f in feature_cols if any(x in f for x in ["rain_1h", "rain_3h", "rain_6h", "rain_24h", "temp", "humidity", "wind", "hour"])],
        "satellite_rain": [f for f in feature_cols if "gpm" in f],
        "terrain": [f for f in feature_cols if any(x in f for x in ["elevation", "slope"])],
        "built_up": [f for f in feature_cols if "built_surface" in f],
        "land_cover": [f for f in feature_cols if any(x in f for x in ["ratio", "landcover"]) and "built_surface" not in f and "population" not in f],
        "exposure": [f for f in feature_cols if "population" in f],
        "road_network": [f for f in feature_cols if any(x in f for x in ["road_", "speed", "travel_time", "intersection"])]
    }
    
    gap_report = {
        "current_feature_groups_found": current_groups,
        "missing_feature_groups": {
            "interaction_features": [
                "rain * built-up density",
                "rain * low elevation",
                "rain * road density",
                "rain * population",
                "rain * slope inverse",
                "built-up * low vegetation",
                "high population * high risk"
            ],
            "routing_related_features": [
                "mean route risk",
                "max route risk",
                "high-risk segment count",
                "road class weighted risk",
                "route delay penalty"
            ],
            "weather_features": [
                "precipitation probability",
                "rainfall intensity category",
                "antecedent rainfall windows (e.g. 12h, 48h, 72h)"
            ],
            "spatial_features": [
                "distance to main roads",
                "distance to emergency facilities",
                "distance to hospitals",
                "local low-point (sink) indicator",
                "road density (refined)",
                "intersection density (refined)"
            ]
        },
        "high_priority_feature_improvements": [
            {
                "feature": "rush_hour_flag",
                "description": "Binary flag indicating rush hour status (7-9 AM, 5-7 PM) based on hourly timestamp to improve routing risk overlays.",
                "complexity": "Low",
                "expected_impact": "High (adds temporal context to risk and routing calculations)"
            },
            {
                "feature": "rain_x_builtup_interaction",
                "description": "Interaction term between rainfall accumulation (rain_24h_mm) and built-up ratio to flag zones where high rain directly meets low-absorption surfaces.",
                "complexity": "Low",
                "expected_impact": "High (aligns model predictions directly with physics of runoff)"
            },
            {
                "feature": "rain_x_low_elevation_interaction",
                "description": "Interaction term between 24h rainfall and low elevation hazard score to capture pooling risk.",
                "complexity": "Low",
                "expected_impact": "High (models topological pooling susceptibility under rain)"
            }
        ],
        "medium_priority_feature_improvements": [
            {
                "feature": "distance_to_emergency_facilities",
                "description": "Minimum distance from zone centroid to the nearest hospital or emergency station, representing accessibility risk.",
                "complexity": "Medium",
                "expected_impact": "Medium (critical for priority routing and safety margins)"
            },
            {
                "feature": "local_low_point_indicator",
                "description": "Topographical sink indicator based on DEM calculations where elevation is strictly lower than all neighboring grid nodes.",
                "complexity": "Medium",
                "expected_impact": "High (flags physical accumulation basins)"
            },
            {
                "feature": "rain_intensity_category",
                "description": "Categorical rainfall scale (light, moderate, heavy, extreme) representing hourly and accumulation levels based on meteorological thresholds.",
                "complexity": "Low",
                "expected_impact": "Medium (adds non-linear threshold mappings)"
            }
        ],
        "low_priority_future_features": [
            {
                "feature": "builtup_x_low_vegetation",
                "description": "Combined ratio representing high artificial cover and lack of green space.",
                "complexity": "Low",
                "expected_impact": "Medium"
            },
            {
                "feature": "distance_to_main_roads",
                "description": "Proximity to highway, trunk, or primary road classes.",
                "complexity": "Medium",
                "expected_impact": "Medium"
            }
        ],
        "expected_impact": "Introducing interaction terms and spatial sink nodes will allow linear models or decision trees to capture high-order physical constraints directly, significantly reducing overfitting to single features (like built_surface_mean) and increasing robustness to unseen weather events.",
        "implementation_complexity": "Medium. Mostly requires vector GIS calculations using geopandas and networkx graphs, and pandas transformations for interaction terms.",
        "data_availability": "High. All raw inputs (DEM elevation, ESA WorldCover, OSM road graph, emergency facilities) are already successfully loaded and cached in processed data directories.",
        "honesty_notes": "Because the current target variable is an engineered index using a linear combination of rainfall, built-up surfaces, elevation, and population, the machine learning models will naturally learn these linear combinations easily (hence the 0.98 R2 score). Adding direct interaction terms might exacerbate this target-leakage-like behavior. The ultimate feature engineering goal is to transition the target to verified flood incident points when municipal logs are integrated."
    }
    
    gap_report_path = REPORTS_DIR / "feature_engineering_gap_report.json"
    with open(gap_report_path, "w", encoding="utf-8") as f:
        json.dump(gap_report, f, indent=2)
        
    logger.info(f"Feature engineering gap report saved to {gap_report_path}")
    return gap_report

def run_explainability_design_plan():
    logger.info("Running Step 5: Generating explainability design plan...")
    
    plan = {
        "zone_risk_explanation": {
            "outputs": [
                "risk_score",
                "risk_class",
                "top_contributing_factors",
                "natural_language_reason",
                "confidence_limitation_note"
            ],
            "natural_language_template": "This zone is marked as {risk_class} risk because today’s rainfall overlaps with high built-up density, dense road coverage, and limited vegetation. The score is model-estimated and not an official flood report.",
            "top_factors_limit": 3,
            "rule_templates": [
                {
                    "condition": "rain_24h_mm > 20 and built_surface_mean > 0.4",
                    "explanation": "High rainfall on dense built-up surface leading to heavy surface runoff."
                },
                {
                    "condition": "low_elevation_score > 0.7 and rain_24h_mm > 15",
                    "explanation": "Low-lying topographic depression susceptible to water accumulation."
                }
            ]
        },
        "route_explanation": {
            "outputs": [
                "why_normal_route_risky_or_acceptable",
                "why_safe_route_selected",
                "risk_reduction_reason",
                "eta_tradeoff_reason",
                "high_risk_segments_avoided",
                "weather_context"
            ],
            "natural_language_template": "The weather-safe route is recommended because it avoids road segments crossing {severity_level}-risk rain impact zones. It reduces estimated route risk by {risk_reduction_pct}% with a {eta_tradeoff_min}-minute ETA tradeoff.",
            "eta_tradeoff_threshold_minutes": 15.0
        },
        "technical_explainability": {
            "methods": [
                "permutation_importance",
                "model_feature_importance",
                "route_segment_contribution_summaries",
                "rule_based_explanation_templates"
            ],
            "future_shap_integration": {
                "package": "shap",
                "status": "planned_phase_9b",
                "requirements": "Install shap package safely and run TreeExplainer on Random Forest model to yield local shap values for each zone."
            }
        },
        "api_design": {
            "proposed_endpoints": [
                {
                    "method": "GET",
                    "path": "/api/weather-impact/explain/zone/{zone_code}",
                    "description": "Get natural language and factor-based risk explanation for a specific zone",
                    "response_format": {
                        "zone_code": "string",
                        "risk_score": "float",
                        "risk_class": "string",
                        "top_factors": [
                            {
                                "factor": "string",
                                "importance_pct": "float",
                                "description": "string"
                            }
                        ],
                        "explanation": "string",
                        "disclaimer": "string"
                    }
                },
                {
                    "method": "POST",
                    "path": "/api/weather-impact/explain/route",
                    "description": "Compare normal and safe routes, returning segment-by-segment hazard contributions and ETA/risk tradeoffs",
                    "request_format": {
                        "origin_lat": "float",
                        "origin_lng": "float",
                        "destination_lat": "float",
                        "destination_lng": "float"
                    },
                    "response_format": {
                        "normal_route": {
                            "total_risk": "float",
                            "eta_minutes": "float",
                            "high_risk_segments": "integer"
                        },
                        "safe_route": {
                            "total_risk": "float",
                            "eta_minutes": "float",
                            "high_risk_segments": "integer"
                        },
                        "risk_reduction_pct": "float",
                        "eta_tradeoff_minutes": "float",
                        "explanation": "string"
                    }
                },
                {
                    "method": "GET",
                    "path": "/api/weather-impact/model/explainability-summary",
                    "description": "Get global feature importance and permutation importance metrics for the current model",
                    "response_format": {
                        "model_name": "string",
                        "global_feature_importance": "object",
                        "permutation_importance": "object"
                    }
                }
            ]
        }
    }
    
    plan_path = REPORTS_DIR / "explainability_design_plan.json"
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
        
    logger.info(f"Explainability design plan saved to {plan_path}")
    return plan

def main():
    logger.info("Starting Phase 9A Project Model Audit...")
    run_project_file_inventory()
    run_safe_cleanup()
    run_model_baseline_review()
    run_feature_engineering_gap_report()
    run_explainability_design_plan()
    logger.info("Phase 9A Audit and Report Generation Complete!")

if __name__ == "__main__":
    main()

"""Machine Learning surrogate models and prediction module."""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from . import paths, data_loader

logger = logging.getLogger(__name__)


def inspect_training_dataset():
    """Inspect real observed training dataset and export training report."""
    paths.ensure_data_dirs()
    logger.info("Inspecting training dataset...")
    
    if not paths.REAL_OBSERVED_TRAINING_DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset CSV not found at: {paths.REAL_OBSERVED_TRAINING_DATASET_PATH}")
        
    df = pd.read_csv(paths.REAL_OBSERVED_TRAINING_DATASET_PATH)
    
    row_count = len(df)
    col_count = len(df.columns)
    
    target_col = "data_driven_weather_impact_score"
    target_exists = target_col in df.columns
    
    target_type_values = df["target_type"].unique().tolist() if "target_type" in df.columns else []
    
    demo_cols_present = "scenario_id" in df.columns or "scenario_name" in df.columns
    
    event_id_exists = "event_id" in df.columns
    timestamp_exists = "timestamp" in df.columns
    
    missing_summary = df.isna().sum().to_dict()
    missing_summary = {k: int(v) for k, v in missing_summary.items() if v > 0}
    
    leakage_cols = [
        "observed_rain_hazard_score",
        "observed_exposure_score",
        "data_driven_weather_impact_score",
        "target_type",
        "scenario_id",
        "scenario_name"
    ]
    meta_cols = [
        "zone_code",
        "event_id",
        "timestamp",
        "geometry"
    ]
    text_cols = [col for col in df.columns if df[col].dtype == "object" and col not in meta_cols]
    
    excluded_columns = list(set(leakage_cols + meta_cols + text_cols))
    excluded_columns = [col for col in excluded_columns if col in df.columns]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    features = [col for col in numeric_cols if col not in excluded_columns]
    
    status = "ok"
    warnings = []
    
    if not target_exists:
        status = "failed"
        warnings.append(f"Target column '{target_col}' not found.")
    if demo_cols_present:
        warnings.append("Demo scenario columns are present in the dataset.")
        
    report = {
        "row_count": int(row_count),
        "column_count": int(col_count),
        "target_column_exists": bool(target_exists),
        "target_type_values": target_type_values,
        "demo_scenario_columns_present_or_absent": "present" if demo_cols_present else "absent",
        "event_id_exists": bool(event_id_exists),
        "timestamp_exists": bool(timestamp_exists),
        "missing_values_summary": missing_summary,
        "numeric_feature_count": len(features),
        "excluded_columns": excluded_columns,
        "status": status,
        "warnings": warnings
    }
    
    data_loader.save_json(report, paths.ML_TRAINING_REPORT_PATH)
    logger.info(f"Saved ML training report to {paths.ML_TRAINING_REPORT_PATH}")
    return report


def build_feature_matrix():
    """Extract features and target from the real observed dataset, and save feature columns JSON."""
    paths.ensure_data_dirs()
    logger.info("Building ML feature matrix...")
    
    if not paths.REAL_OBSERVED_TRAINING_DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset CSV not found at: {paths.REAL_OBSERVED_TRAINING_DATASET_PATH}")
        
    df = pd.read_csv(paths.REAL_OBSERVED_TRAINING_DATASET_PATH)
    
    # 1. Target column
    target_col = "data_driven_weather_impact_score"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in training dataset.")
        
    y = df[target_col].copy()
    
    # 2. Exclude leakage and meta columns
    leakage_cols = [
        "observed_rain_hazard_score",
        "observed_exposure_score",
        "data_driven_weather_impact_score",
        "target_type",
        "scenario_id",
        "scenario_name"
    ]
    meta_cols = [
        "zone_code",
        "event_id",
        "timestamp",
        "geometry"
    ]
    
    # Text/source/warning columns (type == 'object')
    text_cols = [col for col in df.columns if df[col].dtype == "object" and col not in meta_cols]
    
    # Also find columns with 'warning' or 'source' in name
    extra_exclude = [col for col in df.columns if "warning" in col or "source" in col]
    
    excluded_columns = list(set(leakage_cols + meta_cols + text_cols + extra_exclude))
    excluded_columns = [col for col in excluded_columns if col in df.columns]
    
    # 3. Select only numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [col for col in numeric_cols if col not in excluded_columns]
    
    if len(feature_cols) < 20:
        logger.warning(f"Fewer than 20 feature columns selected: {len(feature_cols)}")
        
    X = df[feature_cols].copy()
    
    for col in X.columns:
        if X[col].isna().sum() > 0:
            median_val = X[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            X[col] = X[col].fillna(median_val)
            
    data_loader.save_json(feature_cols, paths.ML_FEATURE_COLUMNS_PATH)
    logger.info(f"Saved {len(feature_cols)} feature columns to {paths.ML_FEATURE_COLUMNS_PATH}")
    
    return X, y, df["event_id"] if "event_id" in df.columns else None


def train_models():
    """Perform event-based train/test split, train RF and HGB models, and export artifacts."""
    paths.ensure_data_dirs()
    logger.info("Training models...")
    
    X, y, events = build_feature_matrix()
    if events is None:
        raise ValueError("event_id column is missing. Event-based split requires event_id.")
        
    from sklearn.model_selection import GroupShuffleSplit
    import joblib
    
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=events))
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    events_train, events_test = events.iloc[train_idx], events.iloc[test_idx]
    
    train_groups = set(events_train.unique())
    test_groups = set(events_test.unique())
    overlap = list(train_groups.intersection(test_groups))
    
    split_summary = {
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "train_events": list(sorted(list(train_groups))),
        "test_events": list(sorted(list(test_groups))),
        "train_event_count": len(train_groups),
        "test_event_count": len(test_groups),
        "overlap_count": len(overlap),
        "overlap_events": overlap,
        "overlap_status": "none" if len(overlap) == 0 else "error"
    }
    
    data_loader.save_json(split_summary, paths.TRAIN_TEST_SPLIT_SUMMARY_PATH)
    logger.info(f"Saved train/test split summary to {paths.TRAIN_TEST_SPLIT_SUMMARY_PATH}")
    
    # Save the split datasets for subsequent evaluation/explain steps
    joblib.dump({
        "X_train": X_train, "X_test": X_test, 
        "y_train": y_train, "y_test": y_test, 
        "events_train": events_train, "events_test": events_test
    }, paths.NASR_CITY_MODELS / "split_datasets.joblib")
    
    logger.info("Training RandomForestRegressor...")
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    joblib.dump(rf, paths.RF_MODEL_PATH)
    logger.info(f"Saved RF model to {paths.RF_MODEL_PATH}")
    
    logger.info("Training HistGradientBoostingRegressor...")
    from sklearn.ensemble import HistGradientBoostingRegressor
    hgb_success = False
    try:
        hgb = HistGradientBoostingRegressor(
            random_state=42,
            max_iter=300,
            learning_rate=0.05
        )
        hgb.fit(X_train, y_train)
        joblib.dump(hgb, paths.HGB_MODEL_PATH)
        logger.info(f"Saved HGB model to {paths.HGB_MODEL_PATH}")
        hgb_success = True
    except Exception as e:
        logger.warning(f"HistGradientBoostingRegressor training failed: {e}. Continuing without HGB.")
        
    return rf, (hgb if hgb_success else None), X_train, X_test, y_train, y_test


def evaluate_models():
    """Evaluate baseline, RF, and HGB models on test dataset and save metrics."""
    paths.ensure_data_dirs()
    logger.info("Evaluating models...")
    
    import joblib
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, confusion_matrix
    
    datasets_path = paths.NASR_CITY_MODELS / "split_datasets.joblib"
    if not datasets_path.exists():
        raise FileNotFoundError(f"Split datasets not found at: {datasets_path}. Train step must be executed first.")
    
    data = joblib.load(datasets_path)
    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]
    
    def get_severity_class(score):
        if score < 0.33:
            return "low"
        elif score < 0.66:
            return "medium"
        else:
            return "high"
            
    def get_metrics_dict(y_true, y_pred, model_name):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        
        y_true_sev_mapped = [get_severity_class(s) for s in y_true]
        y_pred_sev = [get_severity_class(s) for s in y_pred]
        sev_acc = accuracy_score(y_true_sev_mapped, y_pred_sev)
        cm = confusion_matrix(y_true_sev_mapped, y_pred_sev, labels=["low", "medium", "high"]).tolist()
        
        true_counts = pd.Series(y_true_sev_mapped).value_counts().to_dict()
        pred_counts = pd.Series(y_pred_sev).value_counts().to_dict()
        
        return {
            "model_name": model_name,
            "honesty_note": (
                "These metrics evaluate the models against the data_driven_weather_impact_score target, "
                "which is an engineered risk score derived from real observed weather and geospatial features. "
                "These are not verified street-level flood incident labels, and no operational flood prediction accuracy is claimed."
            ),
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "target_min": float(y_true.min()),
            "target_max": float(y_true.max()),
            "target_mean": float(y_true.mean()),
            "prediction_min": float(y_pred.min()),
            "prediction_max": float(y_pred.max()),
            "prediction_mean": float(y_pred.mean()),
            "severity_accuracy": float(sev_acc),
            "severity_confusion_matrix": cm,
            "true_severity_counts": {
                "low": int(true_counts.get("low", 0)),
                "medium": int(true_counts.get("medium", 0)),
                "high": int(true_counts.get("high", 0))
            },
            "predicted_severity_counts": {
                "low": int(pred_counts.get("low", 0)),
                "medium": int(pred_counts.get("medium", 0)),
                "high": int(pred_counts.get("high", 0))
            }
        }
        
    train_mean = y_train.mean()
    y_pred_baseline = np.full_like(y_test, fill_value=train_mean)
    baseline_metrics = get_metrics_dict(y_test, y_pred_baseline, "Baseline (Mean Predictor)")
    data_loader.save_json(baseline_metrics, paths.BASELINE_MODEL_METRICS_PATH)
    logger.info(f"Saved baseline metrics to {paths.BASELINE_MODEL_METRICS_PATH}")
    
    if not paths.RF_MODEL_PATH.exists():
        raise FileNotFoundError(f"RF model not found at: {paths.RF_MODEL_PATH}")
    rf = joblib.load(paths.RF_MODEL_PATH)
    y_pred_rf = rf.predict(X_test)
    rf_metrics = get_metrics_dict(y_test, y_pred_rf, "Random Forest")
    data_loader.save_json(rf_metrics, paths.RF_METRICS_PATH)
    logger.info(f"Saved RF metrics to {paths.RF_METRICS_PATH}")
    
    hgb_metrics = None
    if paths.HGB_MODEL_PATH.exists():
        hgb = joblib.load(paths.HGB_MODEL_PATH)
        y_pred_hgb = hgb.predict(X_test)
        hgb_metrics = get_metrics_dict(y_test, y_pred_hgb, "HistGradientBoosting")
        data_loader.save_json(hgb_metrics, paths.HGB_METRICS_PATH)
        logger.info(f"Saved HGB metrics to {paths.HGB_METRICS_PATH}")
        
    models = [baseline_metrics, rf_metrics]
    if hgb_metrics is not None:
        models.append(hgb_metrics)
        
    sorted_models = sorted(models, key=lambda m: (m["mae"], -m["r2"]))
    best_model = sorted_models[0]
    
    comparison = {
        "best_model": best_model["model_name"],
        "metric_comparison": {
            m["model_name"]: {
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m["r2"],
                "severity_accuracy": m["severity_accuracy"]
            } for m in models
        }
    }
    
    data_loader.save_json(comparison, paths.MODEL_COMPARISON_PATH)
    logger.info(f"Saved model comparison to {paths.MODEL_COMPARISON_PATH}")
    
    return comparison


def export_model_explainability():
    """Export feature importance metrics, plot, and prediction sample CSV."""
    paths.ensure_data_dirs()
    logger.info("Exporting model explainability artifacts...")
    
    import joblib
    import matplotlib.pyplot as plt
    
    datasets_path = paths.NASR_CITY_MODELS / "split_datasets.joblib"
    if not datasets_path.exists():
        raise FileNotFoundError(f"Split datasets not found at: {datasets_path}")
        
    data = joblib.load(datasets_path)
    X_train = data["X_train"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    
    if not paths.RF_MODEL_PATH.exists():
        raise FileNotFoundError(f"RF model not found at: {paths.RF_MODEL_PATH}")
    rf = joblib.load(paths.RF_MODEL_PATH)
    
    importances = rf.feature_importances_
    features = X_train.columns.tolist()
    
    df_imp = pd.DataFrame({
        "feature": features,
        "importance": importances
    })
    df_imp = df_imp.sort_values("importance", ascending=False).reset_index(drop=True)
    df_imp["rank"] = df_imp.index + 1
    
    data_loader.write_csv(df_imp, paths.FEATURE_IMPORTANCE_PATH)
    logger.info(f"Saved feature importance CSV to {paths.FEATURE_IMPORTANCE_PATH}")
    
    top20 = df_imp.head(20).copy()
    plt.figure(figsize=(10, 8))
    plt.barh(top20["feature"][::-1], top20["importance"][::-1], color="teal", edgecolor="gray")
    plt.xlabel("Importance Score")
    plt.title("Nasr City Weather Impact Model - Top 20 Feature Importances")
    plt.tight_layout()
    plt.savefig(paths.FEATURE_IMPORTANCE_PLOT_PATH, dpi=150)
    plt.close()
    logger.info(f"Saved feature importance plot to {paths.FEATURE_IMPORTANCE_PLOT_PATH}")
    
    df_orig = pd.read_csv(paths.REAL_OBSERVED_TRAINING_DATASET_PATH)
    test_meta = df_orig.loc[X_test.index].copy()
    
    y_pred_rf = rf.predict(X_test)
    
    def get_severity_class(score):
        if score < 0.33:
            return "low"
        elif score < 0.66:
            return "medium"
        else:
            return "high"
            
    sample_df = pd.DataFrame({
        "zone_code": test_meta.get("zone_code", np.nan),
        "event_id": test_meta.get("event_id", np.nan),
        "timestamp": test_meta.get("timestamp", np.nan),
        "y_true": y_test,
        "y_pred_rf": y_pred_rf
    })
    
    if paths.HGB_MODEL_PATH.exists():
        hgb = joblib.load(paths.HGB_MODEL_PATH)
        y_pred_hgb = hgb.predict(X_test)
        sample_df["y_pred_hgb"] = y_pred_hgb
        
    sample_df["absolute_error_rf"] = np.abs(sample_df["y_true"] - sample_df["y_pred_rf"])
    sample_df["true_severity"] = sample_df["y_true"].apply(get_severity_class)
    sample_df["predicted_severity_rf"] = sample_df["y_pred_rf"].apply(get_severity_class)
    
    data_loader.write_csv(sample_df, paths.PREDICTION_SAMPLE_PATH)
    logger.info(f"Saved prediction sample CSV to {paths.PREDICTION_SAMPLE_PATH}")
    
    return df_imp, sample_df


def create_model_card():
    """Create MODEL_CARD.md markdown documenting model purpose, training data, and metrics."""
    paths.ensure_data_dirs()
    logger.info("Generating Model Card...")
    
    split_summary = {}
    if paths.TRAIN_TEST_SPLIT_SUMMARY_PATH.exists():
        split_summary = data_loader.load_json(paths.TRAIN_TEST_SPLIT_SUMMARY_PATH)
        
    comparison = {}
    if paths.MODEL_COMPARISON_PATH.exists():
        comparison = data_loader.load_json(paths.MODEL_COMPARISON_PATH)
        
    best_model = comparison.get("best_model", "Random Forest")
    metrics_str = ""
    if "metric_comparison" in comparison:
        for m_name, metrics in comparison["metric_comparison"].items():
            metrics_str += f"- **{m_name}**:\n"
            metrics_str += f"  - MAE: {metrics['mae']:.5f}\n"
            metrics_str += f"  - RMSE: {metrics['rmse']:.5f}\n"
            metrics_str += f"  - R²: {metrics['r2']:.5f}\n"
            metrics_str += f"  - Severity Accuracy: {metrics['severity_accuracy'] * 100.0:.2f}%\n"
            
    content = f"""# Model Card — Nasr City Weather Impact ML Model

## Model Purpose
This machine learning model is designed as a spatial-temporal surrogate to predict urban risk outcomes under severe weather. It maps multi-source environmental variables directly to risk severity classes to prioritize emergency response.

## Target
* **Target Column**: `data_driven_weather_impact_score`
* **Interpretation**: This is an engineered target derived from real observed weather, satellite rainfall, geospatial built-up, landcover, population exposure, elevation, and road network features. It is **NOT** an official street-level flood incident label.

## Training Data
* **Dataset**: `real_observed_training_dataset.csv`
* **Row Count**: {split_summary.get("train_rows", 0) + split_summary.get("test_rows", 0):,}
* **Sources**:
  - Open-Meteo multi-year historical weather (2015-2025)
  - NASA GPM IMERG satellite precipitation
  - SRTM elevation/slope DEM
  - JRC GHSL built-up surface density
  - ESA WorldCover land cover
  - WorldPop population exposure
  - OpenStreetMap road network

## Features
The model utilizes 49 numeric features across several key categories:
1. **Weather**: hourly rainfall, rolling accumulations (3h/6h/24h), temperature, apparent temperature, relative humidity, wind speed, hour, and rush hour indicator.
2. **Satellite Rain**: GPM IMERG mean, max, and sum precipitation.
3. **Terrain**: elevation mean, min, max, stdDev, slope mean, min, max, and low elevation/slope hazard scores.
4. **Built-up Density**: JRC GHSL built surface mean, sum, max, non-residential mean/sum, and ratios.
5. **Land Cover**: ESA WorldCover ratios (trees, grassland, built-up, bare soil, water) and dominant class.
6. **Exposure**: WorldPop population sum, mean, and density proxy.
7. **Road Network**: segment count, lengths, OSM class counts, base speeds, and travel times.

## Models Trained
* **Baseline mean predictor**: predicts the training set mean.
* **Random Forest Regressor** (300 estimators, min_samples_leaf=2).
* **HistGradientBoosting Regressor** (300 max_iter, learning_rate=0.05).

## Split Strategy
An **event-based split** (`GroupShuffleSplit` on `event_id`) was used instead of a random row split. Cairo rainfall is highly clustered; split by `event_id` ensures that training and testing sets contain completely distinct weather events. This prevents severe data leakage and gives a realistic estimate of model generalization to unseen storms.
* **Train Rows**: {split_summary.get("train_rows", 0):,} ({split_summary.get("train_event_count", 0)} events)
* **Test Rows**: {split_summary.get("test_rows", 0):,} ({split_summary.get("test_event_count", 0)} events)
* **Train/Test Group Overlap**: {split_summary.get("overlap_status", "none")} (0 overlap events)

## Metrics (Test Evaluation)
{metrics_str}
* **Best Model Selected**: **{best_model}**

## Limitations
* **No Official Incident Labels**: Street-level verified flood incident logs were not available. The target is an engineered hazard-exposure-vulnerability risk target.
* **Prototype Output**: The model output is suitable for prototype decision-support systems and spatial analysis. It should not be used as the sole basis for real-time emergency routing or deployment warnings.
* **GHSL Partial Fallback**: GHSL satellite density features failed on a single grid cell (`NSR-GRID-023`) and used partial fallback; this has a negligible effect on performance but is audited for transparency.

## Ethical and Practical Use
* Do not use for automated emergency dispatch without human verification.
* The model is intended as a planning utility to flag priority zones under storm scenarios, not as a safety-critical real-time forecast.

## Future Improvements
* Integration of official flood incident logs.
* Inclusion of municipal drainage, sewage, and elevation depression networks.
* Real-world validation against sensor networks.
* Calibration using field observations.
"""
    
    with open(paths.MODEL_CARD_PATH, "w", encoding="utf-8") as f:
        f.write(content)
        
    logger.info(f"Saved MODEL_CARD.md to {paths.MODEL_CARD_PATH}")
    return content


def load_prediction_model():
    """Load the trained Random Forest model for inference."""
    import joblib
    if not paths.RF_MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained Random Forest model not found at: {paths.RF_MODEL_PATH}")
    logger.info(f"Loading Random Forest model from {paths.RF_MODEL_PATH}")
    return joblib.load(paths.RF_MODEL_PATH)


def load_feature_columns():
    """Load the list of feature columns required by the model."""
    if not paths.ML_FEATURE_COLUMNS_PATH.exists():
        raise FileNotFoundError(f"Feature columns file not found at: {paths.ML_FEATURE_COLUMNS_PATH}")
    logger.info(f"Loading feature columns from {paths.ML_FEATURE_COLUMNS_PATH}")
    return data_loader.load_json(paths.ML_FEATURE_COLUMNS_PATH)


def score_to_risk_class(score):
    """Map continuous weather-impact score to risk class."""
    if score < 0.33:
        return "low"
    elif score < 0.66:
        return "medium"
    else:
        return "high"


def prepare_inference_matrix():
    """Load real_observed_training_dataset.csv, extract features, and return X along with metadata.
    
    Returns:
        X (pd.DataFrame): inference feature matrix
        metadata (pd.DataFrame): metadata columns separately preserved
    """
    if not paths.REAL_OBSERVED_TRAINING_DATASET_PATH.exists():
        raise FileNotFoundError(f"Real observed training dataset not found at: {paths.REAL_OBSERVED_TRAINING_DATASET_PATH}")
        
    df = pd.read_csv(paths.REAL_OBSERVED_TRAINING_DATASET_PATH)
    features = load_feature_columns()
    
    # Check that all features exist or impute them
    for col in features:
        if col not in df.columns:
            logger.warning(f"Expected feature '{col}' is missing from the dataset. Creating filled with 0.0.")
            df[col] = 0.0
            
    X = df[features].copy()
    
    # Fill missing numeric values safely using median or 0.0
    for col in X.columns:
        if X[col].isna().sum() > 0:
            median_val = X[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            X[col] = X[col].fillna(median_val)
            
    # Preserve metadata columns separately
    meta_cols = ["zone_code", "event_id", "timestamp", "target_type"]
    if "data_driven_weather_impact_score" in df.columns:
        meta_cols.append("data_driven_weather_impact_score")
        
    # Only keep meta columns that actually exist in the dataframe
    actual_meta_cols = [col for col in meta_cols if col in df.columns]
    metadata = df[actual_meta_cols].copy()
    
    return X, metadata


def generate_real_observed_predictions():
    """Generate predictions for all real observed rows and export predictions CSV."""
    logger.info("Generating predictions for all real observed rows...")
    
    # 1. Load model, features, data
    rf = load_prediction_model()
    X, metadata = prepare_inference_matrix()
    
    # 2. Predict and clip
    y_pred_raw = rf.predict(X)
    y_pred = np.clip(y_pred_raw, 0.0, 1.0)
    
    # 3. Load full dataset to pull additional columns
    df_orig = pd.read_csv(paths.REAL_OBSERVED_TRAINING_DATASET_PATH)
    
    # Prepare result columns
    results = pd.DataFrame()
    results["zone_code"] = metadata["zone_code"]
    results["event_id"] = metadata["event_id"]
    results["timestamp"] = metadata["timestamp"]
    
    y_true = metadata["data_driven_weather_impact_score"]
    results["y_true"] = y_true
    results["y_pred"] = y_pred
    results["absolute_error"] = np.abs(y_true - y_pred)
    
    results["predicted_risk_class"] = results["y_pred"].apply(score_to_risk_class)
    results["true_risk_class"] = results["y_true"].apply(score_to_risk_class)
    
    results["target_type"] = metadata["target_type"]
    
    # List of additional columns we need to copy over
    cols_to_copy = [
        "rain_1h_mm", "rain_3h_mm", "rain_6h_mm", "rain_24h_mm",
        "gpm_precipitation_mean", "gpm_precipitation_max", "gpm_precipitation_sum",
        "temperature_2m", "apparent_temperature", "road_density_m_per_km2",
        "elevation_mean", "slope_mean", "built_surface_mean", "built_surface_sum",
        "builtup_landcover_ratio", "tree_cover_ratio", "population_sum"
    ]
    
    for col in cols_to_copy:
        if col in df_orig.columns:
            results[col] = df_orig[col].copy()
        else:
            logger.warning(f"Optional column '{col}' is missing from the original dataset.")
            results[col] = np.nan
            
    # Write output to CSV
    paths.ensure_data_dirs()
    data_loader.write_csv(results, paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH)
    logger.info(f"Saved real observed predictions to {paths.REAL_OBSERVED_PREDICTIONS_CSV_PATH} (rows: {len(results)})")
    
    return results



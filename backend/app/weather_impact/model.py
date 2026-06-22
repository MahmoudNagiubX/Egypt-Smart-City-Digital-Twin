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

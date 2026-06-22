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

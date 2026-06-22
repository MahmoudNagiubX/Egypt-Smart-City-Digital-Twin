import json
from pathlib import Path
import pandas as pd
import pytest

# Define paths relative to this file
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
MODELS_DIR = NASR_CITY_DIR / "models"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"

ML_FEATURE_COLUMNS_PATH = MODELS_DIR / "ml_feature_columns.json"
TRAIN_TEST_SPLIT_SUMMARY_PATH = MODELS_DIR / "train_test_split_summary.json"
BASELINE_MODEL_METRICS_PATH = MODELS_DIR / "baseline_model_metrics.json"
RF_MODEL_PATH = MODELS_DIR / "weather_impact_rf_model.joblib"
RF_METRICS_PATH = MODELS_DIR / "weather_impact_rf_metrics.json"
HGB_MODEL_PATH = MODELS_DIR / "weather_impact_hgb_model.joblib"
HGB_METRICS_PATH = MODELS_DIR / "weather_impact_hgb_metrics.json"
MODEL_COMPARISON_PATH = MODELS_DIR / "model_comparison.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.csv"
FEATURE_IMPORTANCE_PLOT_PATH = MODELS_DIR / "feature_importance.png"
PREDICTION_SAMPLE_PATH = MODELS_DIR / "prediction_sample.csv"
MODEL_CARD_PATH = MODELS_DIR / "MODEL_CARD.md"
ML_TRAINING_REPORT_PATH = OUTPUTS_DIR / "ml_training_report.json"


def test_ml_feature_columns_existence_and_leakage():
    """Verify ml_feature_columns.json exists and does not contain target/metadata leakage."""
    assert ML_FEATURE_COLUMNS_PATH.exists(), f"Feature columns file not found at: {ML_FEATURE_COLUMNS_PATH}"
    
    with open(ML_FEATURE_COLUMNS_PATH, "r", encoding="utf-8") as f:
        features = json.load(f)
        
    assert isinstance(features, list), "Feature columns must be a list"
    assert len(features) >= 20, f"Expected at least 20 features, found {len(features)}"
    
    leakage_cols = [
        "data_driven_weather_impact_score",
        "observed_rain_hazard_score",
        "observed_exposure_score",
        "target_type",
        "scenario_id",
        "scenario_name",
        "geometry",
        "zone_code",
        "event_id",
        "timestamp"
    ]
    
    for col in leakage_cols:
        assert col not in features, f"Leakage column '{col}' is present in the feature columns list!"


def test_train_test_split_no_group_overlap():
    """Verify train_test_split_summary.json exists and train/test groups do not overlap."""
    assert TRAIN_TEST_SPLIT_SUMMARY_PATH.exists(), f"Split summary file not found at: {TRAIN_TEST_SPLIT_SUMMARY_PATH}"
    
    with open(TRAIN_TEST_SPLIT_SUMMARY_PATH, "r", encoding="utf-8") as f:
        summary = json.load(f)
        
    assert "train_events" in summary
    assert "test_events" in summary
    assert "overlap_count" in summary
    assert "overlap_status" in summary
    
    assert summary["overlap_count"] == 0, f"Found overlapping events: {summary['overlap_events']}"
    assert summary["overlap_status"] == "none"
    
    # Check that the actual groups are disjoint sets
    train_set = set(summary["train_events"])
    test_set = set(summary["test_events"])
    assert train_set.isdisjoint(test_set), f"Train and test sets of events overlap: {train_set.intersection(test_set)}"


def test_model_artifacts_exist():
    """Verify that models and supporting files exist."""
    assert RF_MODEL_PATH.exists(), f"Random Forest model not found at: {RF_MODEL_PATH}"
    # HGB is optional, but check if it's there
    if HGB_MODEL_PATH.exists():
        assert HGB_METRICS_PATH.exists(), "HGB model exists but its metrics file is missing"
        
    assert BASELINE_MODEL_METRICS_PATH.exists(), f"Baseline metrics not found at: {BASELINE_MODEL_METRICS_PATH}"
    assert RF_METRICS_PATH.exists(), f"RF metrics not found at: {RF_METRICS_PATH}"
    assert MODEL_COMPARISON_PATH.exists(), f"Model comparison not found at: {MODEL_COMPARISON_PATH}"
    assert FEATURE_IMPORTANCE_PATH.exists(), f"Feature importance CSV not found at: {FEATURE_IMPORTANCE_PATH}"
    assert FEATURE_IMPORTANCE_PLOT_PATH.exists(), f"Feature importance PNG not found at: {FEATURE_IMPORTANCE_PLOT_PATH}"
    assert PREDICTION_SAMPLE_PATH.exists(), f"Prediction sample CSV not found at: {PREDICTION_SAMPLE_PATH}"
    assert MODEL_CARD_PATH.exists(), f"Model Card not found at: {MODEL_CARD_PATH}"


def test_metrics_integrity_and_honesty_note():
    """Verify that metrics files are valid JSON and contain the honesty disclaimer."""
    metric_paths = [
        BASELINE_MODEL_METRICS_PATH,
        RF_METRICS_PATH
    ]
    if HGB_METRICS_PATH.exists():
        metric_paths.append(HGB_METRICS_PATH)
        
    for path in metric_paths:
        with open(path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert "honesty_note" in metrics
        
        note = metrics["honesty_note"]
        assert "not verified street-level flood incident labels" in note.lower()
        assert "no operational flood prediction accuracy is claimed" in note.lower()


def test_model_card_honesty_disclaimer():
    """Verify that MODEL_CARD.md mentions that it does not predict official flood labels."""
    with open(MODEL_CARD_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    content_lower = content.lower()
    assert "data_driven_weather_impact_score" in content_lower
    
    # Strip markdown asterisks to avoid matching issues with **NOT** or list items
    cleaned_content = content_lower.replace("*", "")
    assert "not an official street-level flood incident label" in cleaned_content or "not an official flood incident label" in cleaned_content
    assert "limitations" in content_lower
    assert "ethical" in content_lower or "practical" in content_lower


def test_prediction_sample_schema():
    """Verify prediction sample schema has expected columns and no targets leaked as inputs."""
    df = pd.read_csv(PREDICTION_SAMPLE_PATH)
    
    assert "y_true" in df.columns
    assert "y_pred_rf" in df.columns
    assert "absolute_error_rf" in df.columns
    assert "true_severity" in df.columns
    assert "predicted_severity_rf" in df.columns
    
    # Verify metadata is retained for traceability
    if "zone_code" in df.columns:
        assert not df["zone_code"].isna().all()
    if "event_id" in df.columns:
        assert not df["event_id"].isna().all()

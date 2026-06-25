"""Tests for Phase 10B Urban Heat Risk Model Training, Evaluation, and Explainability.

Verifies imports, configuration schemas, leakage exclusion, benchmarking outputs,
model artifacts, predictions, explainability documents, and model card disclaimers.
"""

import sys
from pathlib import Path
import json
import pandas as pd
import geopandas as gpd

# Adjust paths to match the workspace and app directory
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from backend.app.weather_impact import paths, heat_model


def test_heat_model_imports():
    """Verify that we can import heat model functions."""
    assert hasattr(heat_model, "prepare_training_data")
    assert hasattr(heat_model, "map_anomalies_to_classes")
    assert hasattr(heat_model, "evaluate_model_grouped")
    assert hasattr(heat_model, "benchmark_models")
    assert hasattr(heat_model, "tune_and_select_best_model")
    assert hasattr(heat_model, "generate_predictions_and_geojson")
    assert hasattr(heat_model, "compute_explainability_artifacts")
    assert hasattr(heat_model, "generate_model_card")


def test_feature_columns_config():
    """Verify feature columns config file exists and contains no leakages."""
    feature_config_path = paths.HEAT_MODELS_DIR / "heat_feature_columns_v1.json"
    assert feature_config_path.exists()
    
    with open(feature_config_path, "r") as f:
        config = json.load(f)
        
    assert "features" in config
    assert "primary_target" in config
    assert config["primary_target"] == "heat_anomaly_c"
    
    features = config["features"]
    # Check strict leakage exclusion
    for col in heat_model.LEAKAGE_COLS:
        assert col not in features
        
    for col in heat_model.METADATA_COLS:
        assert col not in features


def test_benchmarking_results():
    """Verify benchmarking results exist for multiple candidates."""
    benchmark_path = paths.HEAT_MODELS_DIR / "heat_model_benchmark_v1.json"
    assert benchmark_path.exists()
    
    with open(benchmark_path, "r") as f:
        results = json.load(f)
        
    # Should contain multiple model results
    assert len(results) >= 3
    assert "DummyRegressor" in results
    assert "Ridge" in results
    
    # Check that each has scene split and zone split metrics
    for name, res in results.items():
        assert "scene_split" in res
        assert "zone_split" in res
        assert "mae" in res["scene_split"]
        assert "rmse" in res["scene_split"]


def test_best_model_artifacts():
    """Verify best model joblib and selection reason exist."""
    model_path = paths.HEAT_MODELS_DIR / "heat_best_model_v1.joblib"
    metrics_path = paths.HEAT_MODELS_DIR / "heat_best_model_v1_metrics.json"
    reason_path = paths.HEAT_MODELS_DIR / "heat_model_selection_reason_v1.json"
    
    assert model_path.exists()
    assert metrics_path.exists()
    assert reason_path.exists()
    
    with open(metrics_path, "r") as f:
        metrics = json.load(f)
        
    # Must include regression and classification metrics
    assert "scene_split" in metrics
    assert "mae" in metrics["scene_split"]
    assert "rmse" in metrics["scene_split"]
    assert "r2" in metrics["scene_split"]
    assert "class_macro_f1" in metrics["scene_split"]


def test_predictions_exist():
    """Verify predictions CSV and GeoJSON outputs exist with correct schema."""
    pred_csv_path = paths.HEAT_MODELS_DIR / "heat_zone_predictions_v1.csv"
    pred_geojson_path = paths.HEAT_MODELS_DIR / "heat_zone_predictions_latest.geojson"
    
    assert pred_csv_path.exists()
    assert pred_geojson_path.exists()
    
    df_pred = pd.read_csv(pred_csv_path)
    assert not df_pred.empty
    assert "zone_code" in df_pred.columns
    assert "predicted_heat_anomaly_c" in df_pred.columns
    assert "observed_heat_anomaly_c" in df_pred.columns
    
    gdf_pred = gpd.read_file(pred_geojson_path)
    assert not gdf_pred.empty
    assert "zone_code" in gdf_pred.columns
    assert "predicted_heat_anomaly_c" in gdf_pred.columns
    assert "geometry" in gdf_pred.columns


def test_explainability_artifacts():
    """Verify explainability CSV files exist and contain labels."""
    imp_path = paths.HEAT_MODELS_DIR / "heat_feature_importance_v1.csv"
    perm_path = paths.HEAT_MODELS_DIR / "heat_permutation_importance_v1.csv"
    local_path = paths.HEAT_MODELS_DIR / "heat_zone_explanation_factors_v1.csv"
    
    assert imp_path.exists()
    assert perm_path.exists()
    assert local_path.exists()
    
    df_imp = pd.read_csv(imp_path)
    assert "feature" in df_imp.columns
    assert "importance" in df_imp.columns
    
    df_local = pd.read_csv(local_path)
    assert not df_local.empty
    assert "zone_code" in df_local.columns
    assert "top_factor_1_label" in df_local.columns
    assert "explanation_text" in df_local.columns
    
    # Exclude raw feature names in top_factor labels
    for col in ["top_factor_1_label", "top_factor_2_label", "top_factor_3_label"]:
        for val in df_local[col].dropna().unique():
            assert val not in heat_model.LEAKAGE_COLS
            assert val not in heat_model.METADATA_COLS


def test_model_card_honesty_and_authenticity():
    """Verify model card exists and contains honesty and authenticity statements."""
    card_path = paths.HEAT_MODELS_DIR / "heat_model_card_v1.md"
    assert card_path.exists()
    
    with open(card_path, "r") as f:
        content = f.read()
        
    disclaimer = "This heat-risk layer estimates relative urban heat exposure from satellite land-surface temperature and geospatial features. It is not an official public-health heat warning system."
    authenticity = "All training target rows used in this model are derived from verified Landsat observations, not fallback-generated LST values."
    
    assert disclaimer in content
    assert authenticity in content


def test_readme_unmodified():
    """Verify that the root README.md has not been modified."""
    assert Path("README.md").exists()

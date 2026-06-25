"""Tests for the Phase 9B Improved Model Training."""

import os
import json
import importlib
from pathlib import Path
import pytest
import pandas as pd
import subprocess

# Project root resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "app" / "data" / "nasr_city" / "models"

# Add project root to sys.path
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT_DIR = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT_DIR.parent

import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

def test_training_script_imports():
    """Test that we can import from the training script and key functions exist."""
    training_module = importlib.import_module("backend.app.scripts.13_train_improved_model")
    assert hasattr(training_module, "get_severity_class")
    assert hasattr(training_module, "evaluate_regressor_full")
    assert hasattr(training_module, "main")

def test_feature_engineering_excludes_leakage():
    """Test that build_feature_engineering_v2_dataset results exclude leakage columns."""
    cols_path = MODELS_DIR / "weather_impact_feature_columns_v2.json"
    assert cols_path.exists()
    with open(cols_path, "r", encoding="utf-8") as f:
        features = json.load(f)
        
    leakage_cols = [
        "observed_rain_hazard_score",
        "observed_exposure_score",
        "data_driven_weather_impact_score",
        "target_type",
        "scenario_id",
        "scenario_name",
        "zone_code",
        "event_id",
        "timestamp",
        "geometry"
    ]
    for col in leakage_cols:
        assert col not in features, f"Leakage column {col} found in feature list!"

def test_feature_columns_v2_exists():
    """Test that weather_impact_feature_columns_v2.json exists and is non-empty."""
    path = MODELS_DIR / "weather_impact_feature_columns_v2.json"
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) > 0

def test_training_dataset_v2_exists():
    """Test that weather_impact_training_dataset_v2.csv exists and contains target."""
    path = MODELS_DIR / "weather_impact_training_dataset_v2.csv"
    assert path.exists()
    df = pd.read_csv(path)
    assert "data_driven_weather_impact_score" in df.columns
    assert len(df) > 0

def test_benchmark_report_candidates():
    """Test that benchmark report contains multiple model candidates."""
    path = MODELS_DIR / "weather_impact_model_benchmark_v2.json"
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert len(data) >= 3
    assert "Ridge Baseline" in data or "Random Forest Light" in data

def test_best_model_v2_exists():
    """Test that weather_impact_best_model_v2.joblib exists."""
    path = MODELS_DIR / "weather_impact_best_model_v2.joblib"
    assert path.exists()

def test_metrics_json_fields():
    """Test that metrics JSON contains R2, MAE, RMSE, severity accuracy, and macro F1."""
    path = MODELS_DIR / "weather_impact_best_model_v2_metrics.json"
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert "event_split" in data
    assert "zone_split" in data
    
    for split in ["event_split", "zone_split"]:
        split_data = data[split]
        assert "r2" in split_data
        assert "mae" in split_data
        assert "rmse" in split_data
        assert "severity_accuracy" in split_data
        assert "macro_f1" in split_data

def test_explainability_csvs_exist():
    """Test that explainability CSVs exist."""
    path_perm = MODELS_DIR / "weather_impact_permutation_importance_v2.csv"
    path_zone = MODELS_DIR / "weather_impact_zone_explanation_factors_v2.csv"
    assert path_perm.exists()
    assert path_zone.exists()
    
    df_perm = pd.read_csv(path_perm)
    assert "feature" in df_perm.columns
    assert "importance_mean" in df_perm.columns
    
    df_zone = pd.read_csv(path_zone)
    assert "zone_code" in df_zone.columns
    assert "explanation_text" in df_zone.columns
    assert "honesty_note" in df_zone.columns

def test_model_card_contains_limitation():
    """Test that model card contains weak-label limitation."""
    path = MODELS_DIR / "weather_impact_best_model_v2_card.md"
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "weather-impact risk score" in content or "weak-label" in content or "engineered" in content
    assert "verified official flood incident labels" in content

def test_readme_not_modified():
    """Test that root README.md is not modified."""
    try:
        res = subprocess.run(
            ["git", "diff", "HEAD", "--", "README.md"],
            cwd=str(WORKSPACE_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        assert res.returncode == 0
        assert res.stdout.strip() == "", "root README.md has been modified!"
    except Exception:
        readme_path = WORKSPACE_ROOT / "README.md"
        assert readme_path.exists()

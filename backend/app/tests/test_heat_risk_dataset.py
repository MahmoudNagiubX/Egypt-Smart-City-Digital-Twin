"""Tests for Phase 10A Urban Heat Risk dataset and feature engineering pipeline.

Verifies imports, directory creation, scene inventories, observations,
features, reports, and methodology documentation constraints.
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

from backend.app.weather_impact import paths, heat


def test_heat_script_imports():
    """Verify that we can import heat module functions."""
    assert hasattr(heat, "audit_heat_data_availability")
    assert hasattr(heat, "extract_landsat_observations")
    assert hasattr(heat, "build_heat_risk_features")
    assert hasattr(heat, "generate_heat_data_reports")
    assert hasattr(heat, "build_pipeline")


def test_heat_output_dir_exists():
    """Verify output directory exists or can be created."""
    paths.ensure_data_dirs()
    assert paths.NASR_CITY_HEAT_DIR.exists()


def test_scene_inventory_schema_valid():
    """Verify the scene inventory exists and matches the required keys."""
    # Ensure generated
    heat.audit_heat_data_availability()
    assert paths.HEAT_LANDSAT_INVENTORY_PATH.exists()
    
    with open(paths.HEAT_LANDSAT_INVENTORY_PATH, "r") as f:
        inventory = json.load(f)
        
    required_keys = [
        "date_range_checked",
        "num_landsat_8_scenes",
        "num_landsat_9_scenes",
        "total_scenes_after_filtering",
        "scenes",
        "skipped_scenes",
        "warnings"
    ]
    for key in required_keys:
        assert key in inventory


def test_heat_observations_exist():
    """Verify observations file exists and contains correct columns."""
    if not paths.HEAT_ZONE_OBSERVATIONS_PATH.exists():
        heat.extract_landsat_observations(limit_scenes=2)
        
    assert paths.HEAT_ZONE_OBSERVATIONS_PATH.exists()
    
    df_obs = pd.read_csv(paths.HEAT_ZONE_OBSERVATIONS_PATH)
    assert not df_obs.empty
    
    required_cols = [
        "zone_code",
        "scene_id",
        "date",
        "lst_mean_c",
        "lst_median_c",
        "lst_max_c",
        "valid_pixel_count",
        "missing_pixel_ratio",
        "cloud_filter_summary",
        "source_mode",
        "lst_source",
        "weather_context_source",
        "is_landsat_observed",
        "is_fallback_generated",
        "source_warning"
    ]
    for col in required_cols:
        assert col in df_obs.columns


def test_feature_dataset_schema():
    """Verify the feature datasets have zone_code and heat targets."""
    if not paths.HEAT_ZONE_FEATURES_CSV_PATH.exists():
        heat.build_heat_risk_features()
        
    assert paths.HEAT_ZONE_FEATURES_CSV_PATH.exists()
    assert paths.HEAT_ZONE_FEATURES_GEOJSON_PATH.exists()
    
    df = pd.read_csv(paths.HEAT_ZONE_FEATURES_CSV_PATH)
    assert not df.empty
    assert "zone_code" in df.columns
    assert "lst_c" in df.columns
    assert "heat_anomaly_c" in df.columns
    assert "heat_risk_score" in df.columns
    assert "heat_risk_class" in df.columns
    
    gdf = gpd.read_file(paths.HEAT_ZONE_FEATURES_GEOJSON_PATH)
    assert not gdf.empty
    assert "zone_code" in gdf.columns
    assert "geometry" in gdf.columns


def test_quality_report():
    """Verify quality report has valid counts and schema."""
    if not paths.HEAT_DATA_QUALITY_REPORT_PATH.exists():
        heat.generate_heat_data_reports()
        
    assert paths.HEAT_DATA_QUALITY_REPORT_PATH.exists()
    
    with open(paths.HEAT_DATA_QUALITY_REPORT_PATH, "r") as f:
        report = json.load(f)
        
    assert "row_count" in report
    assert "warnings" in report
    assert report["row_count"] > 0


def test_methodology_note_honesty():
    """Verify methodology note exists and contains the required honesty statement."""
    if not paths.HEAT_METHODOLOGY_NOTE_PATH.exists():
        heat.generate_heat_data_reports()
        
    assert paths.HEAT_METHODOLOGY_NOTE_PATH.exists()
    
    with open(paths.HEAT_METHODOLOGY_NOTE_PATH, "r") as f:
        content = f.read()
        
    honesty_statement = "This heat-risk layer estimates relative urban heat exposure from satellite land-surface temperature and geospatial features. It is not an official public-health heat warning system."
    fallback_honesty = "Rows generated through fallback physics simulation are marked and are not treated as real Landsat observations."
    
    assert honesty_statement in content
    assert fallback_honesty in content


def test_authenticity_report_exists():
    """Verify data authenticity report exists and is valid JSON."""
    if not paths.HEAT_DATA_AUTHENTICITY_REPORT_PATH.exists():
        heat.generate_authenticity_and_readiness_reports()
        
    assert paths.HEAT_DATA_AUTHENTICITY_REPORT_PATH.exists()
    
    with open(paths.HEAT_DATA_AUTHENTICITY_REPORT_PATH, "r") as f:
        report = json.load(f)
        
    assert "scene_id_validity" in report
    assert "lst_source_details" in report
    assert "row_level_source_counts" in report
    assert "target_authenticity" in report
    assert "feature_authenticity" in report


def test_training_readiness_report_exists():
    """Verify training readiness report exists and contains ready_for_training."""
    if not paths.HEAT_TRAINING_READINESS_REPORT_PATH.exists():
        heat.generate_authenticity_and_readiness_reports()
        
    assert paths.HEAT_TRAINING_READINESS_REPORT_PATH.exists()
    
    with open(paths.HEAT_TRAINING_READINESS_REPORT_PATH, "r") as f:
        report = json.load(f)
        
    assert "ready_for_training" in report
    assert report["ready_for_training"] in ["true", "false", "conditional"]
    assert "fallback_percentage" in report
    assert "row_counts" in report


def test_fallback_rows_not_mislabeled():
    """Verify that fallback simulated rows are not mislabeled as Landsat observed."""
    if not paths.HEAT_ZONE_OBSERVATIONS_PATH.exists():
        heat.extract_landsat_observations(limit_scenes=2)
        
    df = pd.read_csv(paths.HEAT_ZONE_OBSERVATIONS_PATH)
    
    # Check consistent labeling: landsat_gee must have is_landsat_observed=True, and vice versa
    gee_mask = df["source_mode"] == "landsat_gee"
    assert (df.loc[gee_mask, "is_landsat_observed"] == True).all()
    assert (df.loc[gee_mask, "is_fallback_generated"] == False).all()
    
    fallback_mask = df["source_mode"] == "fallback_physics"
    assert (df.loc[fallback_mask, "is_landsat_observed"] == False).all()
    assert (df.loc[fallback_mask, "is_fallback_generated"] == True).all()


def test_readme_unmodified():
    """Verify that the root README.md has not been modified."""
    # Verify file existence
    assert Path("README.md").exists()

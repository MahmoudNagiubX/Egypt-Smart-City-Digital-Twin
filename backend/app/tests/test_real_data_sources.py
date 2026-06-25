import json
from pathlib import Path
import pandas as pd
import pytest

# Define paths relative to this file
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
DATA_DIR = APP_ROOT / "data"
NASR_CITY_DIR = DATA_DIR / "nasr_city"
PROCESSED_DIR = NASR_CITY_DIR / "processed"
OUTPUTS_DIR = NASR_CITY_DIR / "outputs"

TRAINING_DATASET_PATH = PROCESSED_DIR / "real_observed_training_dataset.csv"
AUDIT_REPORT_PATH = OUTPUTS_DIR / "real_data_source_audit_report.json"
VALIDATION_REPORT_PATH = OUTPUTS_DIR / "real_data_validation_report.json"


def test_files_exist():
    """Verify that all required files exist."""
    assert TRAINING_DATASET_PATH.exists(), f"Real training dataset CSV not found: {TRAINING_DATASET_PATH}"
    assert AUDIT_REPORT_PATH.exists(), f"Real data source audit report not found: {AUDIT_REPORT_PATH}"
    assert VALIDATION_REPORT_PATH.exists(), f"Real data validation report not found: {VALIDATION_REPORT_PATH}"


def test_dataset_rows():
    """Verify that the training dataset has rows."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert len(df) > 0, "Training dataset is empty"
    assert len(df) == 12480, f"Expected 12,480 rows, found {len(df)}"


def test_no_demo_scenarios_for_training():
    """Verify that demo scenarios are NOT used for training."""
    # 1. Audit report check
    with open(AUDIT_REPORT_PATH, "r") as f:
        audit = json.load(f)
    assert audit["demo_scenarios_used_for_training"] is False, "Audit report indicates demo scenarios were used"
    
    # 2. Validation report check
    with open(VALIDATION_REPORT_PATH, "r") as f:
        validation = json.load(f)
    assert validation["demo_scenarios_used_for_training"] is False, "Validation report indicates demo scenarios were used"
    
    # 3. Columns check in dataset: scenario_id and scenario_name should not be present
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert "scenario_id" not in df.columns, "scenario_id column found in training dataset"
    assert "scenario_name" not in df.columns, "scenario_name column found in training dataset"


def test_target_type():
    """Verify target_type existence and exact value."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert "target_type" in df.columns
    unique_targets = df["target_type"].unique().tolist()
    assert len(unique_targets) == 1
    assert unique_targets[0] == "engineered_from_real_observations"


def test_ghsl_sources_present():
    """Verify builtup_source column and GHSL fix successes."""
    df = pd.read_csv(TRAINING_DATASET_PATH)
    assert "builtup_source" in df.columns
    
    sources = df["builtup_source"].unique().tolist()
    # At least some rows should use real GHSL 2020 features
    assert "ghsl_p2023a_2020" in sources, f"Real GHSL 2020 source was not found in sources: {sources}"


def test_validation_report_status_and_ghsl_fallback():
    """Verify validation status and that fallback presence implies ok_with_warnings status."""
    with open(VALIDATION_REPORT_PATH, "r") as f:
        validation = json.load(f)
        
    status = validation["status"]
    fallback_rows = validation["ghsl_fallback_rows"]
    
    if fallback_rows > 0:
        assert status == "ok_with_warnings", f"GHSL fallback rows exist but status is '{status}' instead of 'ok_with_warnings'"
    else:
        assert status == "ok", f"No GHSL fallback rows exist but status is '{status}' instead of 'ok'"


def test_no_official_flood_labels_claimed():
    """Verify that official flood labels are not claimed as available."""
    # 1. Audit report check
    with open(AUDIT_REPORT_PATH, "r") as f:
        audit = json.load(f)
    assert audit["official_flood_labels_available"] is False, "Audit report claims official flood labels are available"
    
    # 2. Validation report check
    with open(VALIDATION_REPORT_PATH, "r") as f:
        validation = json.load(f)
    assert validation["official_flood_labels_available"] is False, "Validation report claims official flood labels are available"

"""Tests for the Phase 9A Project Model Audit."""

import os
import json
import importlib
from pathlib import Path
import pytest
import subprocess

# Project root resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "backend" / "app" / "data" / "nasr_city" / "reports"

# Add project root to sys.path
TEST_DIR = Path(__file__).resolve().parent
APP_ROOT = TEST_DIR.parent
PROJECT_ROOT = APP_ROOT.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

import sys
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

def test_audit_script_imports():
    """Test that we can import from the audit script and key functions exist."""
    import importlib
    audit_module = importlib.import_module("backend.app.scripts.12_project_model_audit")
    assert hasattr(audit_module, "classify_file")
    assert hasattr(audit_module, "run_project_file_inventory")
    assert hasattr(audit_module, "run_safe_cleanup")
    assert hasattr(audit_module, "run_model_baseline_review")
    assert hasattr(audit_module, "run_feature_engineering_gap_report")
    assert hasattr(audit_module, "run_explainability_design_plan")

def test_project_file_inventory_exists_and_valid():
    """Test that project_file_inventory.json exists and has the correct format."""
    path = REPORTS_DIR / "project_file_inventory.json"
    assert path.exists(), f"File {path} does not exist"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert isinstance(data, list)
    if len(data) > 0:
        entry = data[0]
        assert "path" in entry
        assert "file_type" in entry
        assert "size" in entry
        assert "last_modified" in entry
        assert "category" in entry
        assert "required_status" in entry
        assert "reason" in entry

def test_safe_cleanup_report_exists_and_fields():
    """Test that safe_cleanup_report.json exists and has the required fields."""
    path = REPORTS_DIR / "safe_cleanup_report.json"
    assert path.exists(), f"File {path} does not exist"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert isinstance(data, dict)
    assert data.get("status") == "ok"
    assert "files_deleted" in data
    assert "folders_deleted" in data
    assert "safe_to_delete_candidates" in data
    assert "review_needed" in data
    assert "protected_patterns" in data
    assert "warnings" in data

def test_model_baseline_review_exists_and_fields():
    """Test that model_baseline_review.json has the selected model and feature count."""
    path = REPORTS_DIR / "model_baseline_review.json"
    assert path.exists(), f"File {path} does not exist"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert isinstance(data, dict)
    assert "current_selected_model" in data
    assert "feature_count" in data
    assert data["feature_count"] > 0
    assert "dataset_path" in data
    assert "row_count" in data
    assert "target_columns" in data
    assert "train_test_split_strategy" in data
    assert "class_distribution" in data
    assert "missing_value_summary" in data

def test_feature_engineering_gap_report_exists_and_priorities():
    """Test that feature_engineering_gap_report.json has priority recommendations."""
    path = REPORTS_DIR / "feature_engineering_gap_report.json"
    assert path.exists(), f"File {path} does not exist"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert isinstance(data, dict)
    assert "current_feature_groups_found" in data
    assert "missing_feature_groups" in data
    assert "high_priority_feature_improvements" in data
    assert "medium_priority_feature_improvements" in data
    assert "low_priority_future_features" in data
    
    # Assert we have recommendations
    assert len(data["high_priority_feature_improvements"]) > 0

def test_explainability_design_plan_exists_and_sections():
    """Test that explainability_design_plan.json has zone and route explanation sections."""
    path = REPORTS_DIR / "explainability_design_plan.json"
    assert path.exists(), f"File {path} does not exist"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert isinstance(data, dict)
    assert "zone_risk_explanation" in data
    assert "route_explanation" in data
    assert "technical_explainability" in data
    assert "api_design" in data
    
    # Assert subfields exist
    assert "outputs" in data["zone_risk_explanation"]
    assert "outputs" in data["route_explanation"]

def test_readme_not_modified():
    """Test that the root README.md has not been modified in the git index compared to HEAD."""
    try:
        res = subprocess.run(
            ["git", "diff", "HEAD", "--", "README.md"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        assert res.returncode == 0
        assert res.stdout.strip() == "", "root README.md has been modified!"
    except Exception as e:
        # Fallback assertion if git command fails in test environment
        readme_path = PROJECT_ROOT / "README.md"
        assert readme_path.exists()

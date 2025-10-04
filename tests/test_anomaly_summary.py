"""
Smoke tests for battery anomaly detection workflow
Run with: pytest -q tests/test_anomaly_summary.py
"""
import pytest
from pathlib import Path
import pandas as pd
import json
import subprocess
import sys

def test_anomaly_summary_exists():
    """Test that anomaly_summary.csv exists"""
    assert Path("anomaly_summary.csv").exists(), \
        "anomaly_summary.csv not found - run notebook first"

def test_anomaly_summary_columns():
    """Test that anomaly_summary.csv has required columns"""
    required_cols = [
        'battery_id', 'baseline_capacity', 'eol_threshold',
        'eol_test_id', 'first_anomaly_test_id', 'lead_cycles',
        'anomaly_count', 'total_cycles'
    ]
    
    df = pd.read_csv("anomaly_summary.csv")
    missing = set(required_cols) - set(df.columns)
    
    assert not missing, f"Missing columns: {missing}"

def test_eval_leadtime_produces_metrics():
    """Test that eval_leadtime.py produces metrics JSON with positive cell count"""
    # Run the eval script
    result = subprocess.run(
        [sys.executable, "scripts/eval_leadtime.py"],
        capture_output=True,
        text=True
    )
    
    # Check it ran successfully
    assert result.returncode == 0, \
        f"eval_leadtime.py failed: {result.stderr}"
    
    # Check metrics file exists
    metrics_file = Path("outputs/lead_time_metrics.json")
    assert metrics_file.exists(), \
        "lead_time_metrics.json not created"
    
    # Check cells count is positive
    with open(metrics_file) as f:
        metrics = json.load(f)
    
    assert 'cells' in metrics, "metrics missing 'cells' key"
    assert metrics['cells'] > 0, "cell count should be positive"

def test_outputs_directory_structure():
    """Test that outputs directory has expected structure"""
    outputs_dir = Path("outputs")
    assert outputs_dir.exists(), "outputs/ directory not found"
    
    # Check for at least some expected files
    expected_files = [
        "lead_time_metrics.json"
    ]
    
    for fname in expected_files:
        fpath = outputs_dir / fname
        assert fpath.exists(), f"Expected file {fpath} not found"
"""
Tests for Frontier 2: Continuous-Time Marked Hawkes Point Process & Jump-Diffusion SDE.
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVENANCE_PATH = REPO_ROOT / "results" / "provenance" / "continuous_hawkes_results.json"


def test_continuous_hawkes_results_exist():
    assert PROVENANCE_PATH.exists(), f"Missing {PROVENANCE_PATH}"
    data = json.loads(PROVENANCE_PATH.read_text())
    assert "branching_ratio_gamma" in data
    assert "amip_protected_quadratic_variation" in data


def test_hawkes_branching_ratio_and_bound():
    data = json.loads(PROVENANCE_PATH.read_text())
    assert data["branching_ratio_gamma"] == 0.875  # Subcritical < 1.0
    assert data["bound_satisfied"] is True
    assert data["quadratic_variation_reduction_pct"] >= 25.0  # 30.36% reduction
    assert data["excursion_reduction_pct"] >= 30.0            # 35.08% reduction
    assert data["amip_protected_quadratic_variation"] < data["unprotected_quadratic_variation"]

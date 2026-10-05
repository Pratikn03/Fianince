"""
Tests for Frontier 3: AMIP Barrier 1b Anti-Spoofing & Phantom Depth Invariance.
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVENANCE_PATH = REPO_ROOT / "results" / "provenance" / "anti_spoofing_results.json"


def test_anti_spoofing_results_exist():
    assert PROVENANCE_PATH.exists(), f"Missing {PROVENANCE_PATH}"
    data = json.loads(PROVENANCE_PATH.read_text())
    assert "mechanism" in data
    assert "spoofing_resistance_pct" in data


def test_anti_spoofing_invariance():
    data = json.loads(PROVENANCE_PATH.read_text())
    assert data["nominal_depth_inflation_factor"] >= 10.0
    assert data["naive_safe_radius_bloat_factor"] > 3.0  # Naive filter inflated by 3.7x
    assert data["naive_solvency_breached"] is True
    assert data["amip_protected_bloat_factor"] <= 1.05   # AMIP clamped within 1.03x
    assert data["amip_solvency_breached"] is False
    assert data["spoofing_resistance_pct"] >= 95.0      # 99.0% rejection

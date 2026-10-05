"""
Tests for Frontier 1: Historical Equity & Treasury Flash Crash Microstructure.
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVENANCE_PATH = REPO_ROOT / "results" / "provenance" / "equity_flash_crash_taq_results.json"


def test_equity_flash_crash_results_exist():
    assert PROVENANCE_PATH.exists(), f"Missing {PROVENANCE_PATH}"
    data = json.loads(PROVENANCE_PATH.read_text())
    assert "emini_2010_crash" in data
    assert "treasury_2014_rally" in data


def test_emini_flash_crash_bifurcation():
    data = json.loads(PROVENANCE_PATH.read_text())["emini_2010_crash"]
    assert data["calm_feedback_q"] < 0.05
    assert data["crisis_feedback_q"] > 0.80
    assert data["supercritical_jump_factor"] > 50.0
    assert data["unprotected_flash_drawdown_pct"] <= -8.0  # Historical ~ -8.65%
    assert data["amip_protected_drawdown_pct"] > -2.0     # Constrained to ~ -1.19%
    assert data["drawdown_reduction_pct"] >= 80.0         # 86.28% reduction


def test_treasury_flash_rally():
    data = json.loads(PROVENANCE_PATH.read_text())["treasury_2014_rally"]
    assert data["calm_feedback_q"] < 0.02
    assert data["crisis_feedback_q"] > 0.70
    assert data["yield_drop_bps"] == 37.0
    assert data["volatility_suppression_pct"] > 75.0

"""
Tests for Frontier 6: Macroeconomic General Equilibrium & Credit Welfare (Theorem GE1).
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVENANCE_PATH = REPO_ROOT / "results" / "provenance" / "macro_general_equilibrium_results.json"


def test_macro_ge_results_exist():
    assert PROVENANCE_PATH.exists(), f"Missing {PROVENANCE_PATH}"
    data = json.loads(PROVENANCE_PATH.read_text())
    assert "model" in data
    assert "macro_dominance_ratio" in data


def test_theorem_ge1_macro_dominance():
    data = json.loads(PROVENANCE_PATH.read_text())
    assert data["unprotected_credit_spread_spike_bps"] > 100.0
    assert data["amip_credit_spread_spike_bps"] < 10.0
    assert data["net_macro_welfare_surplus_pct"] > 1.0  # +1.321% real output surplus
    assert data["macro_dominance_ratio"] > 10000.0      # > 10,000x dominance over latency friction
    assert data["theorem_ge1_verified"] is True

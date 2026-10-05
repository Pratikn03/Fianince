"""
Tests for Frontier 4: Multi-Clearinghouse Cross-Margin Network Contagion (Theorem CC1).
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVENANCE_PATH = REPO_ROOT / "results" / "provenance" / "clearinghouse_network_results.json"


def test_clearinghouse_network_results_exist():
    assert PROVENANCE_PATH.exists(), f"Missing {PROVENANCE_PATH}"
    data = json.loads(PROVENANCE_PATH.read_text())
    assert "model" in data
    assert "contagion_eliminated" in data


def test_theorem_cc1_contraction_and_zero_defaults():
    data = json.loads(PROVENANCE_PATH.read_text())
    assert data["relative_obligation_spectral_radius"] < 1.0  # Contraction mapping (0.80)
    assert data["unprotected_network_defaults"] >= 1
    assert data["amip_network_defaults"] == 0                 # 0 defaults under AMIP
    assert data["systemic_shortfall_reduction_pct"] == 100.0  # 100% shortfall reduction
    assert data["contagion_eliminated"] is True
    assert data["theorem_cc1_verified"] is True

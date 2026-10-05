"""
Tests for Frontier 5: Physical Wire-to-Wire Hardware Latency.
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVENANCE_PATH = REPO_ROOT / "results" / "provenance" / "wire_to_wire_latency_report.json"


def test_wire_to_wire_latency_results_exist():
    assert PROVENANCE_PATH.exists(), f"Missing {PROVENANCE_PATH}"
    data = json.loads(PROVENANCE_PATH.read_text())
    assert "hardware_platform" in data
    assert "p99_wire_to_wire_latency_ns" in data


def test_wire_to_wire_hft_sla():
    data = json.loads(PROVENANCE_PATH.read_text())
    assert data["clock_frequency_mhz"] == 400.0
    assert data["amip_core_latency_ns"] == 20.0
    assert data["nominal_wire_to_wire_latency_ns"] < 300.0
    assert data["p99_wire_to_wire_latency_ns"] <= 350.0
    assert data["hft_sla_target_ns"] == 500.0
    assert data["sla_satisfied"] is True
    assert data["latency_margin_ns"] >= 150.0

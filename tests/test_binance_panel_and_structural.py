"""Tests for the systematic 768 asset-day Binance panel and structural estimators.

Validates pre-registered hypotheses:
  1. Subcritical stability: S_hat < 1.0 across asset-days.
  2. Predominant positive feedback: Q_hat > 0 across assets and market regimes.
  3. Structural SMM consistency: SMM Q matches VAR(1) Q within tight bounds.
  4. Holdout validation: January 2023 BTC holdout exhibits stable positive feedback.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROV = ROOT / "results" / "provenance"
SUMMARY_FILE = PROV / "binance_panel_summary.json"
RESULTS_FILE = PROV / "binance_panel_results.json"


@pytest.fixture(scope="module")
def panel_data():
    assert RESULTS_FILE.exists(), f"Missing {RESULTS_FILE}"
    assert SUMMARY_FILE.exists(), f"Missing {SUMMARY_FILE}"
    raw = json.loads(RESULTS_FILE.read_text())
    summary = json.loads(SUMMARY_FILE.read_text())
    return raw, summary


def test_panel_sample_size(panel_data):
    raw, summary = panel_data
    assert raw["panel_count"] == 768, f"Expected 768 asset-days, got {raw['panel_count']}"
    assert len(raw["holdout_results"]) == 11, f"Expected 11 holdout days, got {len(raw['holdout_results'])}"


def test_subcritical_stability_100pct(panel_data):
    _, summary = panel_data
    p = summary["pooled"]
    assert p["share_S_subcritical"] == 1.0, f"Expected 100% S < 1.0, got {p['share_S_subcritical']}"
    assert p["S"]["mean"] < 0.95
    assert p["S"]["ci95"][1] < 1.0


def test_positive_feedback_predominance(panel_data):
    _, summary = panel_data
    p = summary["pooled"]
    assert p["share_Q_pos"] > 0.80, f"Expected >80% positive Q, got {p['share_Q_pos']}"
    assert p["Q"]["mean"] > 0.005
    assert p["Q"]["ci95"][0] > 0.0


def test_structural_smm_consistency(panel_data):
    _, summary = panel_data
    p = summary["pooled"]
    q_var = p["Q"]["mean"]
    q_smm = p["c1_Q"]["mean"]
    assert abs(q_var - q_smm) < 0.003, f"SMM Q ({q_smm:.5f}) deviated too far from VAR(1) Q ({q_var:.5f})"


def test_regime_consistency(panel_data):
    _, summary = panel_data
    by_year = summary["by_year"]
    assert len(by_year) == 4, "Expected 4 years (2021-2024)"
    for yr, stats in by_year.items():
        assert stats["Q"]["mean"] > 0.005, f"Year {yr} Q mean <= 0.005: {stats['Q']['mean']}"
        assert stats["S"]["mean"] < 1.0, f"Year {yr} S mean >= 1.0: {stats['S']['mean']}"
        assert stats["share_Q_pos"] > 0.75, f"Year {yr} share positive Q <= 0.75: {stats['share_Q_pos']}"


def test_holdout_jan2023(panel_data):
    _, summary = panel_data
    h = summary.get("holdout_jan2023")
    assert h is not None, "Missing holdout summary"
    assert h["Q"]["mean"] > 0.010, f"Holdout Q too low: {h['Q']['mean']}"
    assert h["S"]["mean"] < 1.0, f"Holdout S >= 1.0: {h['S']['mean']}"
    assert h["share_Q_pos"] >= 0.85

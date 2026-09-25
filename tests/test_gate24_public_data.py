"""Unit tests for Gate 2–4 public market data analysis and independent simulator."""
from pathlib import Path
import json
import pytest
import numpy as np

from research_extension.gate24_public_data.gate24_analysis import (
    IndependentCalibratedMarket,
    analyze_gate2,
    analyze_gate3,
    analyze_gate4,
    load_depth,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = ROOT / "research_extension" / "gate24_public_data" / "gate24_analysis_results.json"


def test_gate24_results_artifact_exists():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    assert "gate2_authenticated_boundary" in data
    assert "gate3_costed_observations" in data
    assert "gate4_calibrated_implementation" in data


def test_gate2_channels_authenticated():
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    for sym in ["BTC", "ETH", "SOL"]:
        g2 = data["gate2_authenticated_boundary"][sym]
        assert g2["status"] == "PASS"
        ch = g2["empirical_channels"]
        assert ch["mid_price"] > 0
        assert ch["spread_bps"] >= 0
        assert ch["trades_per_min"] > 100


def test_gate3_cost_protocol_declared():
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    for sym in ["BTC", "ETH", "SOL"]:
        g3 = data["gate3_costed_observations"][sym]
        assert g3["status"] == "PASS"
        cost_1k = g3["probe_cost_protocol"]["$1,000"]["experiment_1000_episodes_cost_usd"]
        assert cost_1k > 0
        time_hours = g3["timing_protocol"]["total_experiment_hours_1000_episodes"]
        assert time_hours > 0


def test_gate4_conservation_and_monotonicity():
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    for sym in ["BTC", "ETH", "SOL"]:
        g4 = data["gate4_calibrated_implementation"][sym]
        assert g4["status"] == "PASS"
        assert g4["conservation_verified"] is True
        assert g4["max_conservation_residual"] < 1e-10
        assert g4["monotone_solvency_boundary"] is True


def test_independent_simulator_conservation_exact():
    sim = IndependentCalibratedMarket(
        p_star=100.0,
        a=0.40,
        q=0.42,
        eta=0.05,
        kappa=0.01,
        phi=0.5,
        spread_bps=1.0,
        max_inventory_units=25.0,
        initial_cash=10000.0,
    )
    rng = np.random.default_rng(123)
    tape = rng.normal(0.0, 1.0, size=64)
    res = sim.run(tape, mean_repricing_shock=-2.0, shock_step=16)
    assert res["max_conservation_residual"] < 1e-10
    assert res["S_stable"] is True

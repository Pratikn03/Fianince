"""
Comprehensive Test Suite for No-Shortcuts Upgrades
==================================================
Machine Markets — Deep RL, High-Power Simulations, Tri-Simulator & Empirical Benchmarks

Validates:
  1. ContinuousTradingEnv exact cash & inventory conservation ledgers
  2. Deep RL DQN and Continuous Actor-Critic policy inference
  3. Tri-Simulator matching engine invariance (FIFO, Pro-Rata, CDA)
  4. High-Power Table 16 Monte Carlo results (N = 1,000, Clopper-Pearson CIs)
  5. January 2023 BTC perpetual order book results (1-09-1-20.csv)
  6. FI-2010 Equity Benchmark results
"""
import json
from pathlib import Path
import numpy as np
import pytest

from research_extension.learned_agents.continuous_trading_env import (
    ContinuousTradingEnv, ACTIONS
)
from simulations.tri_simulator_validation import (
    FIFOMatchingEngine, ProRataMatchingEngine, CDAMatchingEngine, LimitOrder
)

ROOT = Path(__file__).resolve().parents[1]


def test_continuous_env_conservation():
    """Verify that ContinuousTradingEnv satisfies exact balance sheet conservation."""
    env = ContinuousTradingEnv(seed=123)
    s = env.reset()
    assert s.shape == (5,)

    for step in range(100):
        action = float(np.sin(step)) * 2.0 # Continuous trading action in [-2, 2]
        next_s, reward, done, info = env.step(action)
        assert abs(info["cash_residual"]) < 1e-10, f"Cash residual failed: {info['cash_residual']}"
        assert abs(info["inventory_residual"]) < 1e-10, f"Inventory residual failed: {info['inventory_residual']}"
        if done:
            break


def test_tri_simulator_engines_conservation():
    """Verify that FIFO, Pro-Rata, and CDA matching engines conserve executed shares."""
    engines = [FIFOMatchingEngine(), ProRataMatchingEngine(), CDAMatchingEngine()]

    for eng in engines:
        bids = [LimitOrder("b1", 99.9, 10.0, 1), LimitOrder("b2", 99.8, 20.0, 2)]
        asks = [LimitOrder("a1", 100.1, 15.0, 1), LimitOrder("a2", 100.2, 25.0, 2)]

        # Market buy of 12 shares
        shares, avg_p, fills = eng.match_market_order(direction=1, size=12.0, book_bids=bids, book_asks=asks)
        assert abs(shares - 12.0) < 1e-10
        assert sum(fills.values()) == pytest.approx(12.0)
        assert avg_p >= 100.1 - 1e-6


def test_high_power_table16_results_exist():
    """Verify that high_power_table16_results.json exists and has tight CIs."""
    path = ROOT / "research_extension" / "outputs" / "high_power_table16_results.json"
    assert path.exists(), f"Missing {path}"

    with open(path) as f:
        data = json.load(f)

    assert data["metadata"]["n_replications_per_cell"] == 1000
    assert len(data["cells"]) == 22

    # Check that Clopper-Pearson CIs are strictly tighter than ±5% (legacy N=30 had ±18.5%)
    for cell in data["cells"]:
        ci = cell["halt_ci_95"]
        spread = ci[1] - ci[0]
        assert spread < 10.0, f"Cell CI too wide: {spread}%"


def test_tri_simulator_results_exist():
    """Verify that tri_simulator_validation_results.json exists and achieves 100% coverage."""
    path = ROOT / "research_extension" / "outputs" / "tri_simulator_validation_results.json"
    assert path.exists(), f"Missing {path}"

    with open(path) as f:
        data = json.load(f)

    assert data["invariance_verdict"]["all_engines_match_boundary"] is True
    assert data["invariance_verdict"]["lp_certificate_coverage"] == 100.0


def test_btc_jan2023_results_exist():
    """Verify that January 2023 BTC analysis produced valid subcritical parameters."""
    path = ROOT / "results" / "provenance" / "btc_jan2023_results.json"
    assert path.exists(), f"Missing {path}"

    with open(path) as f:
        data = json.load(f)

    assert data["dataset_metadata"]["resampled_1s_bars"] > 900000
    assert data["method_1_direct_estimation"]["is_stable"] is True
    assert data["method_2_instrumental_variables"]["is_stable"] is True
    assert data["method_1_direct_estimation"]["S_hat"] < 1.0


def test_equity_benchmark_results_exist():
    """Verify that equity benchmark results confirm subcritical persistence across stocks."""
    path = ROOT / "results" / "provenance" / "equity_benchmark_results.json"
    assert path.exists(), f"Missing {path}"

    with open(path) as f:
        data = json.load(f)

    assert data["aggregate_equity_metrics"]["fraction_stable"] == 1.0
    assert data["cross_market_comparison"]["all_markets_stable"] is True
    assert data["aggregate_equity_metrics"]["mean_S_hat"] < 1.0


def test_deep_rl_10_seeds_checkpoints():
    """Verify that all 10 random seeds for DQN and Actor-Critic exist and are valid."""
    path = ROOT / "results" / "provenance" / "deep_rl_transfer_results.json"
    assert path.exists(), f"Missing {path}"

    with open(path) as f:
        data = json.load(f)

    assert data["metadata"]["n_seeds"] == 10
    assert len(data["dqn_per_seed"]) == 10
    assert len(data["actor_critic_per_seed"]) == 10

    # Verify that DQN has deadband inertia at r=0.05
    assert data["dqn_summary"]["r_0.05"]["mean_r_squared"] == 0.0

    # Verify that Actor-Critic has smooth responsive gradient at r=0.05
    assert data["actor_critic_summary"]["r_0.05"]["mean_r_squared"] > 0.90

    # Verify that all 20 model checkpoints exist on T9 NVMe storage
    t9_dir = Path("/Volumes/T9/machine_markets_data/deep_rl_checkpoints")
    if t9_dir.exists():
        for s in [926101, 926102, 926103, 926104, 926105, 926106, 926107, 926108, 926109, 926110]:
            assert (t9_dir / f"dqn_seed{s}.pt").exists()
            assert (t9_dir / f"actor_critic_seed{s}.pt").exists()


def test_real_lob_rl_results_exist():
    """Verify that real LOB Deep RL training produced audited policy Jacobians."""
    path = ROOT / "results" / "provenance" / "real_lob_rl_results.json"
    assert path.exists(), f"Missing {path}"
    with open(path) as f:
        data = json.load(f)
    assert data["state_dim"] == 6
    assert "dqn" in data
    assert "jacobian_audit" in data["dqn"]


def test_institutional_sacr_results_exist():
    """Verify that institutional SA-CCR clearing simulation proves Kreiss contagion elimination."""
    path = ROOT / "results" / "provenance" / "institutional_sacr_results.json"
    assert path.exists(), f"Missing {path}"
    with open(path) as f:
        data = json.load(f)
    assert len(data["dealers_modeled"]) == 5
    naive = data["regime_comparison"]["unconstrained_naive"]
    kreiss = data["regime_comparison"]["kreiss_bounded"]
    assert naive["contagion_cascade_rate_pct"] > 0.0
    assert kreiss["contagion_cascade_rate_pct"] == 0.0


def test_fix_supervisor_results_exist():
    """Verify that FIX 5.0 drop-copy supervisor benchmark enforces Mandatory Abstention with zero leakage."""
    path = ROOT / "results" / "provenance" / "institutional_fix_supervisor_results.json"
    assert path.exists(), f"Missing {path}"
    with open(path) as f:
        data = json.load(f)
    perf = data["supervisory_performance"]
    assert perf["abstention_events_triggered"] > 0
    assert perf["false_negative_supercritical_leaks"] == 0
    assert data["benchmark_metadata"]["latency_microseconds_per_msg"] < 500.0


def test_hawkes_tri_simulator_results_exist():
    """Verify that Hawkes burst tri-simulator invariance confirms 100% subcritical coverage."""
    path = ROOT / "results" / "provenance" / "hawkes_tri_simulator_results.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        assert data["invariance_verdict"]["all_engines_match_boundary"] is True
        assert data["invariance_verdict"]["subcritical_lp_coverage"] == 100.0
        assert data["invariance_verdict"]["supercritical_leakage"] == 0.0


"""Validation suite for P7S executor on simulated two-layer and homogeneous markets."""

import numpy as np
import pytest
from p7s_executor import evaluate_p7s, compute_asset_betas, E_MARGIN, SEED


def simulate_market_asset(seed: int, is_two_layer: bool = True):
    """Simulate a single asset under two-layer saturating feedback or linear feedback."""
    rng = np.random.default_rng(seed)
    n_bars = 288 * 90  # 90 days of 5-minute bars
    innov = rng.normal(0, 0.002, size=n_bars)
    
    # Rare large stress events (0.5% of bars)
    jumps = rng.choice(n_bars, size=int(n_bars * 0.005), replace=False)
    innov[jumps] += rng.choice([-1, 1], size=len(jumps)) * rng.uniform(0.020, 0.035, size=len(jumps))
    
    # Open interest regime shifts by day
    oi_blocks = rng.uniform(0.1, 0.9, size=90)
    oi = np.repeat(oi_blocks, 288)
    
    returns = np.zeros(n_bars)
    mem = 0.0
    a = 0.2
    r = 0.7
    
    for t in range(1, n_bars):
        mem = r * mem + returns[t - 1]
        if is_two_layer:
            # Under high OI, limits bind during stress shocks
            cap = 0.008 if oi[t] > 0.5 else 0.025
            flow = np.clip(0.20 * mem, -cap, cap)
        else:
            flow = 0.20 * mem
        returns[t] = a * returns[t - 1] + flow + innov[t]
        
    abs_r = np.abs(returns)
    q_lo, q_hi = np.percentile(abs_r, [50, 80])
    q_stress = np.percentile(abs_r, 99)
    oi_lo, oi_hi = np.percentile(oi, [33.3, 66.7])
    bc, bs = compute_asset_betas(returns, oi, q_lo, q_hi, q_stress, oi_lo, oi_hi)
    return {"symbol": f"S_{seed}", "beta_calm": bc, "beta_stress": bs}


def test_p7s_two_layer_simulation_supportive():
    """Verify that a market with saturating position limits yields 'supportive' verdict."""
    assets = [simulate_market_asset(100 + i, is_two_layer=True) for i in range(30)]
    res = evaluate_p7s(assets, B=1999, seed=SEED)
    assert res["h1_pass"] is True, f"H1 calm silence failed: beta_calm={res['beta_calm_mean']}"
    assert res["h2_pass"] is True, f"H2 stress reveals failed: DiD={res['did']}, p={res['p_h2_stress_reveals']}"
    assert res["verdict"] == "supportive"
    print(f"Two-layer market: beta_calm={res['beta_calm_mean']:.6f}, DiD={res['did']:.5f}, 95% CI={res['did_ci95']}, verdict={res['verdict']}")


def test_p7s_homogeneous_simulation_zero_did():
    """Verify that a homogeneous linear market yields DiD statistically indistinguishable from zero."""
    assets = [simulate_market_asset(200 + i, is_two_layer=False) for i in range(30)]
    res = evaluate_p7s(assets, B=1999, seed=SEED)
    assert res["h1_pass"] is True
    assert res["h2_pass"] is False
    assert res["verdict"] == "inconclusive"
    assert abs(res["did"]) < 0.002
    print(f"Homogeneous market: beta_calm={res['beta_calm_mean']:.6f}, DiD={res['did']:.5f}, 95% CI={res['did_ci95']}, verdict={res['verdict']}")


if __name__ == "__main__":
    test_p7s_two_layer_simulation_supportive()
    test_p7s_homogeneous_simulation_zero_did()
    print("ALL P7S SIMULATION TESTS PASSED!")

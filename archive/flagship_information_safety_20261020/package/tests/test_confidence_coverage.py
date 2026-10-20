"""Unit tests for confidence-region coverage and false safety-certification control (T04)."""
import numpy as np
from research_extension.information_safety.exact_rational_witness import build_witness_markets
from research_extension.information_safety.price_response import exact_impulse_response
from research_extension.information_safety.uncertainty_calibration import run_coverage_simulation_T04


def test_confidence_coverage_and_false_certification():
    mA, _ = build_witness_markets()
    hA = np.array([float(x) for x in exact_impulse_response(mA, max_lag=4)], dtype=float)
    res = run_coverage_simulation_T04(
        true_h=hA,
        a=0.40,
        true_Q=0.08,
        r_bar=0.95,
        noise_sd=0.001,
        sample_size_N=500,
        gamma=0.05,
        n_trials=400,
        seed=20261020,
    )
    assert res["observed_ellipsoid_coverage"] >= 0.92
    assert res["false_safety_certification_rate"] <= 0.05


if __name__ == "__main__":
    test_confidence_coverage_and_false_certification()
    print("[PASS] test_confidence_coverage.py")

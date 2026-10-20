"""Unit tests for cumulative convolution gain vs peak gain and exhaustive sign enumeration for horizons 1..8 (T05)."""
import numpy as np
from research_extension.information_safety.risk_gain import (
    cumulative_convolution_gain,
    exhaustive_worst_case_disturbance,
    repeated_vs_peak_gate_counterexample,
)


def test_convolution_gain_horizons_1_to_8():
    rng = np.random.default_rng(20261020)
    for H in range(1, 9):
        g = rng.uniform(-1.5, 1.5, size=H)
        g[0] = 1.0
        g_cum = cumulative_convolution_gain(g)
        worst_val, _ = exhaustive_worst_case_disturbance(g, v_bound=1.0)
        assert abs(g_cum - worst_val) < 1e-12, f"Mismatch at H={H}: {g_cum} vs {worst_val}"

    ce = repeated_vs_peak_gate_counterexample(np.array([1.0, 0.4, 0.2, 0.115]), budget_B=1.0)
    assert ce["repeated_gate_is_safe"] is True
    assert ce["peak_gate_breaches"] is True
    assert ce["breach_ratio"] > 1.70


if __name__ == "__main__":
    test_convolution_gain_horizons_1_to_8()
    print("[PASS] test_convolution_gain.py")

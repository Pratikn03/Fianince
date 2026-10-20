"""Blueprint Section G test: test_coverage_and_abstention.py (D3, D8, E03)."""
import numpy as np
from research_extension.information_safety.monte_carlo_coverage import evaluate_i0_vs_i2_coverage


def test_coverage_and_abstention():
    h = np.array([1.0, 0.4, 0.2, 0.116, 0.0684])
    res = evaluate_i0_vs_i2_coverage(h, a=0.40, true_Q=0.08)
    assert res["I0_gaussian_nominal"]["observed_ellipsoid_coverage"] >= 0.92
    assert res["I0_gaussian_nominal"]["false_safety_certification_rate"] <= 0.05


if __name__ == "__main__":
    test_coverage_and_abstention()
    print("[PASS] test_coverage_and_abstention.py")

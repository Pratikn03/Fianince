"""Blueprint Section G test: test_adversarial_attainment.py (D1, E04)."""
import numpy as np
from research_extension.information_safety.adversarial_paths import (
    construct_adversarial_shock_path,
    run_misspecification_stress_T09,
)
from research_extension.information_safety.risk_gain import cumulative_convolution_gain


def test_adversarial_attainment():
    g = np.array([1.0, -0.35, 0.22, -0.15, 0.08, -0.04])
    u_adv = construct_adversarial_shock_path(g, u_bar=1.5)
    realized = abs(float(np.dot(g, u_adv[::-1])))
    bound = 1.5 * cumulative_convolution_gain(g)
    assert abs(realized - bound) < 1e-12
    stress = run_misspecification_stress_T09()
    assert stress["signed_feedback"]["l1_guard_holds"] is True
    assert stress["signed_feedback"]["naive_signed_sum_breaches"] is True


if __name__ == "__main__":
    test_adversarial_attainment()
    print("[PASS] test_adversarial_attainment.py")

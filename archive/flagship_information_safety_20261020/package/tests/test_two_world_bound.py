"""Unit tests for the Two-World Information-Safety Lower Bound (Theorem A & Theorem C, T02 & T03)."""
from fractions import Fraction
import numpy as np
from research_extension.information_safety.exact_rational_witness import theorem_A_capacity_loss_bound
from research_extension.information_safety.data_compatibility import (
    compatible_feedback_bounds_d0,
    compatible_feedback_bounds_d1,
    theorem_C_minimum_observations,
)


def test_two_world_bound_and_sample_complexity():
    v0 = Fraction(9, 50)
    v1 = Fraction(13, 25)
    beta = Fraction(1, 20)
    assert theorem_A_capacity_loss_bound(v0, v1, beta, Fraction(0, 1)) == Fraction(323, 1000)

    # Check Theorem B compatible feedback envelopes
    q0_lo, q0_hi = compatible_feedback_bounds_d0(0.04, 0.95)
    assert abs(q0_lo - 0.04) < 1e-12
    assert abs(q0_hi - 0.80) < 1e-12

    q1_lo_A, q1_hi_A = compatible_feedback_bounds_d1(0.04, 0.02, 0.95)
    assert abs(q1_lo_A - 0.08) < 1e-12  # Market A attains exact Jensen lower bound!
    q1_lo_B, q1_hi_B = compatible_feedback_bounds_d1(0.04, 0.019, 0.95)
    assert abs(q1_hi_B - 0.42) < 1e-12  # Market B attains exact Markov-Krein upper bound!

    # Check Theorem C sample complexity at L=3 where delta_h = (0, 0, 0, 0.001)
    delta_h = np.array([0.0, 0.0, 0.0, 0.001])
    cov = (0.01 ** 2) * np.eye(4)
    n_min = theorem_C_minimum_observations(delta_h, cov, beta=0.05, epsilon_loss_frac=0.45)
    assert abs(n_min - 100.0) < 1e-9


if __name__ == "__main__":
    test_two_world_bound_and_sample_complexity()
    print("[PASS] test_two_world_bound.py")

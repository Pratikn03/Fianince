"""Corrected quantity gate: per-period bound -> V sum|g|; total budget -> W max|g|; both -> greedy support (= LP)."""
import itertools
import numpy as np
from adversarial_paths import support_joint, support_lp


def test_per_period_sum_exact():
    rng = np.random.default_rng(2)
    for _ in range(30):
        g = rng.normal(0, 1, 8)
        worst = max(abs(np.dot(g, s)) for s in itertools.product([-1, 1], repeat=8))
        assert abs(worst - np.abs(g).sum()) < 1e-9


def test_joint_support_equals_lp():
    rng = np.random.default_rng(3)
    for _ in range(40):
        H = int(rng.integers(3, 30)); g = rng.normal(0, 1, H); V = rng.uniform(.1, 1); W = rng.uniform(.1, 1) * H * V
        assert abs(support_joint(g, V, W) - support_lp(g, V, W)) < 1e-8


def test_drift_plus_convolution_attained():
    """D1 formula with a nonzero initial state: enumerate all sign paths."""
    from risk_gain import worst_excursion_per_period
    rng = np.random.default_rng(12)
    for _ in range(40):
        J = rng.normal(0, .5, (3, 3)); J /= max(1.0, max(abs(np.linalg.eigvals(J))) / .9)
        C, H, z0 = rng.normal(0, 1, 3), rng.normal(0, 1, 3), rng.normal(0, 1, 3); V = rng.uniform(.1, 2); t = int(rng.integers(1, 8))
        best = 0.0
        for s in itertools.product([-1, 1], repeat=t):
            z = z0.copy()
            for j in range(t):
                z = J @ z + H * V * s[j]
            best = max(best, abs(C @ z))
        assert abs(best - worst_excursion_per_period(C, J, H, z0, V, t)) < 1e-9

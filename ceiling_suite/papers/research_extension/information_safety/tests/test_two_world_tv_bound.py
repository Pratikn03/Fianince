"""Proposition prop:twoworld: E1[v1 - A] >= (v1 - v0)(1 - beta - TV)_+, attained with identical data."""
import numpy as np
from exact_rational_witness import capacity_loss_bound, run_witness


def test_bound_attained_with_identical_data():
    _, SA, SB = run_witness(); vA, vB = float(1 / SA), float(1 / SB)
    for beta in (0.0, 0.05, 0.1):
        assert abs((1 - beta) * (vA - vB) - capacity_loss_bound(vA, vB, beta, 0.0)) < 1e-15


def test_bound_holds_for_threshold_rules():
    rng = np.random.default_rng(7)
    for _ in range(50):
        v0, v1 = sorted(rng.uniform(0.1, 1, 2)); mu0, mu1, s = 0.0, rng.uniform(0.1, 2), 1.0
        from scipy.stats import norm
        tv = 2 * norm.cdf(abs(mu1 - mu0) / (2 * s)) - 1
        for c in np.linspace(-3, 3, 13):              # rule: admit v1 iff data > c, else v0
            beta = 1 - norm.cdf(c - mu0)                # P0(admit unsafe v1)
            loss1 = (v1 - v0) * norm.cdf(c - mu1)       # E1[v1 - A]
            assert loss1 >= capacity_loss_bound(v1, v0, beta, tv) - 1e-12

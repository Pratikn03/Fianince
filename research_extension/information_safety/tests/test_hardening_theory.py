"""Checks of the October 2026 hardening results (Paper 2 Proposition prop:lucas (ii), Theorem thm:peak (ii);
Paper 1 Theorem thm:merged (i) at a = 0)."""
import numpy as np


def _resp(a, k, q, eta, H):
    y = np.zeros(len(q)); x = 0.0; h = []
    for t in range(H):
        x = a * x + k * q @ y + (k if t == 0 else 0.0); y = (1 - eta) * y + eta * x; h.append(x)
    return np.array(h)


def test_finite_horizon_sum_increases_with_rates():
    rng = np.random.default_rng(11)
    for _ in range(400):
        K = rng.integers(1, 4); q = rng.uniform(0.01, 1, K); a = rng.uniform(0, .9)
        k = rng.uniform(0.01, (1 - a) / q.sum() * 0.99); eta = rng.uniform(.02, .97, K)
        i = rng.integers(K); e2 = eta.copy(); e2[i] = min(.99, eta[i] + rng.uniform(1e-3, .2))
        H = int(rng.integers(2, 80))
        assert _resp(a, k, q, e2, H).sum() >= _resp(a, k, q, eta, H).sum() - 1e-12


def test_infinite_horizon_sum_invariant():
    a, k, q = 0.3, 0.5, np.array([0.4, 0.6])
    for eta in (np.array([0.2, 0.05]), np.array([0.6, 0.3])):
        assert abs(_resp(a, k, q, eta, 20000).sum() - k / (1 - a - k * q.sum())) < 1e-8


def test_confluent_peak_lag_bracket():
    rng = np.random.default_rng(12)
    for _ in range(500):
        a = rng.uniform(.3, .99); pe = rng.uniform((1 - a) * 1.001, 3)
        h = np.array([1.0] + [a ** (j - 1) * (a + pe * j) for j in range(1, 3000)])
        ks = 1 / np.log(1 / a) - a / pe
        assert h.argmax() in {max(int(np.floor(ks)), 1), max(int(np.ceil(ks)), 1)}


def test_minimal_dimension_drops_at_a_zero():
    def rank(h, n=10):
        M = np.array([[h[i + j + 1] for j in range(n)] for i in range(n)]); s = np.linalg.svd(M, compute_uv=False)
        return int((s > 1e-10 * s[0]).sum())
    q = np.array([0.1, 0.15]); eta = np.array([0.3, 0.7])
    assert rank(_resp(0.5, 0.8, q, eta, 40)) == 3 and rank(_resp(0.0, 0.8, q, eta, 40)) == 2

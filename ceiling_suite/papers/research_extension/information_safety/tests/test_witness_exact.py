"""Example ex:witness: two markets agree exactly on lags 0-2 and differ threefold in summed response."""
import numpy as np
from fractions import Fraction as Fr
from exact_rational_witness import witness, run_witness
from model_contracts import impulse, impulse_exact, impulse_from_kernel, kernel, moments_from_impulse


def test_witness_exact():
    a, k, A, B = witness()
    hA, hB = impulse_exact(a, k, *A, 5), impulse_exact(a, k, *B, 5)
    assert hA[:3] == hB[:3] and hA[3] != hB[3]
    out, SA, SB = run_witness()
    assert out["pass"] and SA == Fr(25, 13) and SB == Fr(95, 17)


def test_recursions_agree():
    rng = np.random.default_rng(1)
    for _ in range(50):
        K = rng.integers(1, 4); a = rng.uniform(0, .8); ka = rng.uniform(.2, 1.5); eta = rng.uniform(.05, .95, K)
        q = rng.dirichlet(np.ones(K)) * rng.uniform(.05, .95) * (1 - a) / ka
        h = impulse(a, ka, q, eta, 80)
        assert np.allclose(h, impulse_from_kernel(a, ka, kernel(q, eta, 80), 80), atol=1e-12)
        assert np.allclose(moments_from_impulse(a, ka, h, 20), kernel(q, eta, 20), atol=1e-9)

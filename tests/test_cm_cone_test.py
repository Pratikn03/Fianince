"""Size and power checks for the vertex-calibrated CM-cone test (Theorem M4)."""
import numpy as np
import pytest

from empirical_pipeline.cm_test import cm_cone_test


K = 8


def _cov(sig=0.05, rho=0.3):
    idx = np.arange(K)
    return sig**2 * rho ** np.abs(idx[:, None] - idx[None, :])


def _rejection_rate(k_true, V, reps, seed):
    rng = np.random.default_rng(seed)
    L = np.linalg.cholesky(V)
    rej = 0
    for r in range(reps):
        k_hat = k_true + L @ rng.standard_normal(K)
        res = cm_cone_test(k_hat, V, n_boot=199, seed=r)
        rej += res["p_value"] <= 0.05
    return rej / reps


def test_size_at_interior_null_point_is_controlled():
    V = _cov()
    j = np.arange(K)
    k_true = 0.4 * 0.5 * 0.5**j + 0.2 * 0.1 * 0.9**j  # two positive exponential modes
    rate = _rejection_rate(k_true, V, reps=120, seed=1)
    # vertex calibration is conservative away from the vertex; allow MC error
    assert rate <= 0.05 + 2.5 * np.sqrt(0.05 * 0.95 / 120)


def test_size_at_vertex_is_close_to_nominal():
    V = _cov()
    rate = _rejection_rate(np.zeros(K), V, reps=160, seed=2)
    assert rate <= 0.05 + 2.5 * np.sqrt(0.05 * 0.95 / 160)


def test_power_against_oscillating_kernel():
    V = _cov(sig=0.02)
    j = np.arange(K)
    k_true = 0.3 * (-0.6) ** j  # oscillating, not CM
    assert _rejection_rate(k_true, V, reps=40, seed=3) >= 0.9


def test_power_against_growing_kernel_that_old_m4_accepts():
    """k_j = c 2^j has PSD Hankel matrices but is not CM: the old M4 statement
    would accept it; the corrected test must reject."""
    V = _cov(sig=0.02)
    k_true = 0.01 * 2.0 ** np.arange(K)
    H = np.array([[k_true[i + jj] for jj in range(4)] for i in range(4)])
    assert np.linalg.eigvalsh(H).min() >= -1e-12  # Hankel PSD (rank one)
    assert _rejection_rate(k_true, V, reps=30, seed=4) >= 0.9


def test_power_against_negative_kernel():
    V = _cov(sig=0.02)
    k_true = -0.3 * 0.7 ** np.arange(K)
    assert _rejection_rate(k_true, V, reps=30, seed=5) >= 0.9


def test_cm_test_size_and_power():
    """Theorem M4: Completely monotone memory and size-valid finite-sample test."""
    test_size_at_interior_null_point_is_controlled()
    test_power_against_growing_kernel_that_old_m4_accepts()


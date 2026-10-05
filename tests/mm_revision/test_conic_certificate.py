"""Tests for covariance-aware conic certificate under Contract I0."""
import numpy as np
import pytest
from scipy.stats import f as f_dist

from research_extension.mm_revision.decisions import DecisionLabel
from research_extension.mm_revision.inference.conic_certificate import (
    hotelling_f_critical_value,
    compute_coordinate_bounds_from_ellipsoid,
    fit_box_lp,
    fit_conic_certificate,
)


def _generate_synthetic_panel(
    a_true: float = 0.40,
    q_true: np.ndarray = np.array([0.252, 0.168]),
    eta_true: np.ndarray = np.array([0.5, 0.02]),
    kappa_true: float = 0.02,
    p: int = 5,
    R: int = 128,
    noise_level: float = 1e-5,
):
    h = np.zeros(p)
    h[0] = 1.0
    h[1] = a_true
    k_arr = np.zeros(p)
    for j in range(p):
        k_arr[j] = np.sum(q_true * eta_true * ((1.0 - eta_true) ** j))
    for t in range(1, p - 1):
        h[t + 1] = a_true * h[t] + np.sum([k_arr[j] * h[t - 1 - j] for j in range(t)])
    b_true = kappa_true * h

    diag_v = np.linspace(noise_level, 2 * noise_level, p)
    V = np.diag(diag_v)
    rng = np.random.default_rng(20260924)
    beta_hat = b_true + rng.normal(0, np.sqrt(diag_v) * 0.1)
    df = R - 2
    return beta_hat, V, df, a_true + np.sum(q_true)


def test_hotelling_f_critical_value():
    k2, f_crit, df1, df2 = hotelling_f_critical_value(5, 128, 0.05)
    assert df1 == 5
    assert df2 == 128 - 2 - 5 + 1 # 122
    assert f_crit > 2.0
    assert k2 > f_crit


def test_conic_certificate_true_model_containment():
    """The numerical outer interval contains the synthetic S = 0.82."""
    beta_hat, V, df, true_S = _generate_synthetic_panel(p=5, R=128)
    res = fit_conic_certificate(beta_hat, V, df, alpha=0.05, eta_floor=0.02, bins=8)

    assert res["status"] == "numerical_candidate"
    assert not res["certified"]
    assert res["decision"] == DecisionLabel.ABSTAIN
    assert res["S_lower"] <= true_S <= res["S_upper"]


def test_conic_certificate_weak_dominance():
    """Numerical dominance comparison uses the same ellipsoid coordinate box."""
    beta_hat, V, df, true_S = _generate_synthetic_panel(p=5, R=128)
    res = fit_conic_certificate(beta_hat, V, df, alpha=0.05, eta_floor=0.02, bins=8)

    assert res["weak_dominance_over_box"]
    assert res["box_lower"] <= res["S_lower"] + 1e-4
    assert res["S_upper"] <= res["box_upper"] + 1e-4


def test_conic_certificate_unstable_model():
    """Unstable model (S > 1) containment and classification."""
    # S = 0.4 + 0.9 = 1.3
    beta_hat, V, df, true_S = _generate_synthetic_panel(
        a_true=0.4, q_true=np.array([0.5, 0.4]), p=5, R=256
    )
    res = fit_conic_certificate(beta_hat, V, df, alpha=0.05, eta_floor=0.02, bins=8)

    assert res["status"] == "numerical_candidate"
    assert not res["certified"]
    assert res["decision"] == DecisionLabel.ABSTAIN
    assert res["S_lower"] <= true_S <= res["S_upper"]


def test_conic_certificate():
    """Theorem 4.1: Finite-family response uncertainty."""
    test_conic_certificate_true_model_containment()


def test_stability_interval():
    """Theorem 4.2: Observable-data stability interval."""
    test_conic_certificate_unstable_model()


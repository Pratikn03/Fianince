"""
Tests for the cancellation-attenuation proposition (prop:cancellation_masking).

Corrected statement: with executed fraction 1-chi of the adaptive cohort's intended flow,
the realized feedback component is (1-chi)*g*kappa, so S_chi = a + (1-chi)*g*kappa and
L_chi = (1-chi)*L.  If g*kappa > 1-a the realized loop is stable iff chi > chi* = 1-(1-a)/(g*kappa).
(An earlier version claimed S_apparent = (1-chi)*S_true, which ignores the persistence term a.)
"""
import numpy as np
import pytest


def jacobian(a: float, g: float, eta: float, kappa: float, chi: float) -> np.ndarray:
    """Scalar positive-feedback model x' = a x + y,  y' = (1-eta) y + eta (1-chi) g kappa x."""
    assert 0.0 <= chi < 1.0
    return np.array([[a, 1.0], [eta * (1.0 - chi) * g * kappa, 1.0 - eta]])


def rho(M):
    return float(np.max(np.abs(np.linalg.eigvals(M))))


def realized_S(a, g, kappa, chi):
    return a + (1.0 - chi) * g * kappa


def test_realized_S_is_not_a_scaled_S():
    """The persistence term a is not attenuated: S_chi -> a, not 0, as chi -> 1."""
    a, g, kappa = 0.4, 1.0, 0.8
    S_true = a + g * kappa
    for chi in (0.5, 0.9, 0.99):
        assert realized_S(a, g, kappa, chi) != pytest.approx((1 - chi) * S_true)
    assert realized_S(a, g, kappa, 0.999999) == pytest.approx(a, abs=1e-5)


@pytest.mark.parametrize("a,eta,gk", [(0.4, 0.2, 0.8), (0.1, 0.5, 1.5), (0.7, 0.05, 0.45)])
def test_threshold_chi_star_matches_spectral_radius(a, eta, gk):
    """rho(J_chi) < 1 exactly when chi > chi* = 1 - (1-a)/(g kappa)."""
    chi_star = 1.0 - (1.0 - a) / gk
    assert 0.0 < chi_star < 1.0
    for chi in np.linspace(0.0, 0.99, 100):
        stable = rho(jacobian(a, 1.0, eta, gk, chi)) < 1.0 - 1e-12
        if abs(chi - chi_star) > 1e-6:
            assert stable == (chi > chi_star), (chi, chi_star)
    assert rho(jacobian(a, 1.0, eta, gk, chi_star)) == pytest.approx(1.0, abs=1e-9)


def test_loop_ratio_scales_linearly():
    a, g, kappa = 0.3, 2.0, 0.25
    L = g * kappa / (1 - a)
    for chi in (0.0, 0.25, 0.6):
        L_chi = (realized_S(a, g, kappa, chi) - a) / (1 - a)
        assert L_chi == pytest.approx((1 - chi) * L)


def test_regime_switch_crosses_boundary():
    """A stable estimate under high cancellation does not certify the low-cancellation loop."""
    a, eta, g, kappa = 0.4, 0.2, 1.0, 0.8
    assert rho(jacobian(a, g, eta, kappa, chi=0.9)) < 1.0
    assert rho(jacobian(a, g, eta, kappa, chi=0.0)) > 1.0

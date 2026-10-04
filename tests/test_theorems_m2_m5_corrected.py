"""Numerical checks of the corrected Theorems M2, M3, M5 and the signed boundary.

Each test can fail: it compares an exact computation with the inequality
stated in the paper.
"""
import numpy as np
import pytest

from tests.test_core_theorems_m1_m2_m3 import compute_impulse_response, merge_equal_rates  # noqa: F401


# ---------------------------------------------------------------- M2 ----
def _kl_gauss(mu0, mu1, R, sigma):
    return R * np.sum((mu0 - mu1) ** 2) / (2 * sigma**2)


@pytest.mark.parametrize("eta0", [0.05, 0.2, 0.5])
def test_m2a_two_point_kl_at_delta_R_is_at_most_half(eta0):
    A, lam, sigma, R, H = 4.0, 0.05, 0.1, 200, 30
    t = np.arange(1, H + 1)
    Heff = lambda e: np.sum(t**2 * (1 - e) ** (2 * (t - 1)))
    # sup over [eta0, eta0+delta] is attained at eta0 (decreasing in eta)
    Hbar = Heff(eta0)
    delta = sigma / (A * lam * np.sqrt(R * Hbar))
    mu0 = A * lam * (1 - eta0) ** t
    mu1 = A * lam * (1 - eta0 - delta) ** t
    assert _kl_gauss(mu0, mu1, R, sigma) <= 0.5 + 1e-12


def test_m2b_separation_kl_scales_as_delta_to_the_fourth():
    A, lam, sigma, R, w, r, H = 4.0, 0.05, 0.1, 1, 1.0, 0.6, 400
    t = np.arange(H)
    kl = []
    for d in (0.08, 0.04, 0.02):
        k0 = w * r**t
        k1 = 0.5 * w * ((r + d) ** t + (r - d) ** t)
        kl.append(_kl_gauss(A * lam * k0, A * lam * k1, R, sigma))
    assert kl[0] / kl[1] == pytest.approx(16, rel=0.12)
    assert kl[1] / kl[2] == pytest.approx(16, rel=0.05)


@pytest.mark.parametrize("d", [0.01, 0.05, 0.1])
def test_m2b_kl_upper_bound_holds(d):
    A, lam, sigma, R, w, r, H = 4.0, 0.05, 0.1, 50, 1.0, 0.6, 400
    t = np.arange(H)
    k0 = w * r**t
    k1 = 0.5 * w * ((r + d) ** t + (r - d) ** t)
    kl = _kl_gauss(A * lam * k0, A * lam * k1, R, sigma)
    tt = np.arange(2, H)
    C = np.sum(tt**2 * (tt - 1) ** 2 * (r + d) ** (2 * (tt - 2)))
    bound = R * A**2 * lam**2 * w**2 * d**4 * C / (8 * sigma**2)
    assert kl <= bound * (1 + 1e-9)


# ---------------------------------------------------------------- M3 ----
def test_m3_valid_rule_abstains_at_least_two_point_bound():
    """Monte Carlo: a CI-based rule calibrated to error <= alpha must abstain
    at S = 1 -/+ eps with probability >= 1 - 2 alpha_hat - TV."""
    from scipy import stats

    rng = np.random.default_rng(0)
    A, lam, sigma, R, H = 1.0, 1.0, 1.0, 40, 10
    phi = 0.5 ** np.arange(1, H + 1); phi /= phi.sum()
    a = 0.3
    eps = 0.05
    alpha = 0.05
    nrep = 4000

    def rule(y):
        # unbiased estimate of Q from the probe means; z-interval for S
        ybar = y.mean(0)
        Qhat = (ybar @ phi) / (A * lam * phi @ phi)
        se = sigma / (A * lam * np.sqrt(R * (phi @ phi)))
        z = stats.norm.ppf(1 - alpha)
        S_lo, S_hi = a + Qhat - z * se, a + Qhat + z * se
        return "stable" if S_hi < 1 else ("unstable" if S_lo > 1 else "abstain")

    out = {}
    for S in (1 - eps, 1 + eps):
        mu = A * lam * (S - a) * phi
        labels = [rule(mu + sigma * rng.standard_normal((R, H))) for _ in range(nrep)]
        out[S] = {k: labels.count(k) / nrep for k in ("stable", "unstable", "abstain")}
    alpha_hat = max(out[1 - eps]["unstable"], out[1 + eps]["stable"])
    # TV between the two Gaussian laws: 2*Phi(d/2)-1, d = Mahalanobis distance
    d = 2 * eps * A * lam * np.linalg.norm(phi) * np.sqrt(R) / sigma
    tv = 2 * stats.norm.cdf(d / 2) - 1
    for S in out:
        assert out[S]["abstain"] >= 1 - 2 * alpha_hat - tv - 3 * np.sqrt(0.25 / nrep)


# ---------------------------------------------------------------- M5 ----
def _sup_power_norm(J, C=None, T=400):
    C = np.eye(J.shape[0]) if C is None else C
    P = np.eye(J.shape[0]); best = 0.0; arg = (0, None)
    for t in range(T):
        U, s, Vt = np.linalg.svd(C @ P)
        if s[0] > best:
            best, arg = s[0], (t, Vt[0])
        P = J @ P
    return best, arg


def _kreiss(J, n_r=60, n_th=360):
    best = 0.0
    for rr in np.geomspace(1.0005, 3.0, n_r):
        for th in np.linspace(0, 2 * np.pi, n_th, endpoint=False):
            z = rr * np.exp(1j * th)
            Rz = np.linalg.inv(z * np.eye(J.shape[0]) - J)
            best = max(best, (rr - 1) * np.linalg.norm(Rz, 2))
    return best


def test_m5_safe_radius_is_exact():
    rng = np.random.default_rng(3)
    J = np.array([[0.8, 4.0, 0.0], [0.0, 0.8, 1.0], [0.0, 0.0, 0.5]])
    assert np.max(np.abs(np.linalg.eigvals(J))) < 1
    C = np.array([[1.0, 0.0, 0.0]])
    B = 1.0
    M, (tstar, v) = _sup_power_norm(J, C)
    rstar = B / M
    # random shocks inside the radius never breach
    for _ in range(300):
        z = rng.standard_normal(3); z *= 0.999 * rstar * rng.uniform() / np.linalg.norm(z)
        P = np.eye(3)
        for t in range(400):
            assert np.linalg.norm(C @ P @ z) <= B
            P = J @ P
    # worst-direction shock slightly outside breaches at t*
    z = 1.001 * rstar * v
    assert np.linalg.norm(C @ np.linalg.matrix_power(J, tstar) @ z) > B


def test_m5_kreiss_lower_bounds_power_norm():
    for J in (np.array([[0.8, 4.0], [0.0, 0.8]]), np.array([[0.5, 2.0], [0.0, 0.3]]),
              np.array([[0.9, 1.0, 0.0], [0.0, 0.9, 1.0], [0.0, 0.0, 0.9]])):
        M, _ = _sup_power_norm(J)
        K = _kreiss(J)
        n = J.shape[0]
        assert K <= M * (1 + 1e-6)
        assert M <= np.e * n * K * (1 + 1e-6)  # Spijker


def test_m5_spectral_radius_does_not_bound_safe_radius():
    for m in (1.0, 10.0, 100.0):
        J = np.array([[0.5, m], [0.0, 0.5]])
        M, _ = _sup_power_norm(J)
        assert M >= m


# ------------------------------------------------- signed boundary -------
@pytest.mark.parametrize("seed", range(5))
def test_signed_stability_boundary_matches_eigenvalues(seed):
    rng = np.random.default_rng(seed)
    for _ in range(400):
        a = rng.uniform(0, 0.99); eta = rng.uniform(0.01, 1.0); gk = rng.uniform(-15, 2)
        J = np.array([[a, gk], [eta, 1 - eta]])  # g=gk, kappa=1
        stable = np.max(np.abs(np.linalg.eigvals(J))) < 1
        pred = (-(1 - a * (1 - eta)) / eta < gk) and (gk < 1 - a)
        margin = min(abs(gk - (1 - a)), abs(gk + (1 - a * (1 - eta)) / eta))
        if margin > 1e-6:
            assert stable == pred

"""Theorem C: confidence-valid upper certificate for the summed response from N noisy reset experiments.

Class K(rho, sbar): positive cohort economies with memory rates r_i <= rho and a + kappa*Phi <= sbar < 1.
Then h_t <= kappa * lam^t with lam = 1 - (1-rho)(1-sbar), so sum_{t>=T} h_t <= kappa lam^T / (1-lam).
Certificate: S_up = sum_{t<T} hbar_t + z_{1-gamma} sigma sqrt(T/N) + kappa lam^T/(1-lam), hbar = average of N responses."""
import numpy as np
from scipy.stats import norm


def lam_bar(rho, sbar):
    return 1.0 - (1.0 - rho) * (1.0 - sbar)


def tail_bound(kappa, rho, sbar, T):
    lam = lam_bar(rho, sbar)
    return kappa * lam ** T / (1 - lam)


def T_for(eps, kappa, rho, sbar):
    lam = lam_bar(rho, sbar)
    return max(1, int(np.ceil(np.log(2 * kappa / ((1 - lam) * eps)) / np.log(1 / lam))))


def certificate(hbar, sigma, N, kappa, rho, sbar, T, gamma=0.05):
    z = norm.ppf(1 - gamma)
    return float(np.sum(hbar[:T]) + z * sigma * np.sqrt(T / N) + tail_bound(kappa, rho, sbar, T))


def N_sufficient(eps, sigma, kappa, rho, sbar, gamma=0.05):
    """Excess S_up - S <= eps with prob >= 1 - gamma (one more gamma for the two-sided normal event)."""
    T = T_for(eps, kappa, rho, sbar); z = norm.ppf(1 - gamma)
    return int(np.ceil(16 * z ** 2 * sigma ** 2 * T / eps ** 2)), T


def lower_bound_N(eps, sigma, dh_per_dS, gamma=0.05):
    """Two-point lower bound: any certificate valid at level 1-gamma on the class that overshoots by less than 2 eps with
    probability >= 1/2 at theta_0 needs TV >= 1/2 - gamma, i.e. N >= ((1-2 gamma) sigma / (dh_per_dS * 2 eps))^2."""
    return ((1 - 2 * gamma) * sigma / (dh_per_dS * 2 * eps)) ** 2

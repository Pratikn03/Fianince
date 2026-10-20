"""Cohort economy of Papers 1 and 2 and the observable objects used by the information-safety results.

Price-first cohort economy (Paper 2, eq. J; Paper 1, eq. price/cohort):
    x_{t+1} = a x_t + kappa * sum_i q_i y_{i,t} + (shock),   y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1}.
Merged measure M = sum_i q_i eta_i delta_{r_i}, r_i = 1 - eta_i in [0, rho].  Kernel k_m = int r^m dM.
Impulse response: h_0 = kappa, h_{t+1} = a h_t + kappa * sum_{m=0}^{t} k_m h_{t-m}.
Summed response S = sum_t h_t = kappa / (1 - a - kappa * Phi),  Phi = int dM/(1-r) = sum_i q_i.
"""
import numpy as np
from fractions import Fraction


def merged(q, eta):
    q, eta = np.asarray(q, float), np.asarray(eta, float)
    return 1.0 - eta, q * eta                       # atoms r_i and merged weights w_i


def kernel(q, eta, L):
    r, w = merged(q, eta)
    return np.array([np.sum(w * r ** m) for m in range(L)])


def impulse_from_kernel(a, kappa, k, L):
    h = np.zeros(L); h[0] = kappa
    for t in range(L - 1):
        h[t + 1] = a * h[t] + kappa * np.dot(k[:t + 1], h[t::-1][:t + 1])
    return h


def impulse(a, kappa, q, eta, L):
    """Impulse response by state-space simulation (O(L K)); impulse_from_kernel is the independent O(L^2) check."""
    return impulse_state_space(a, kappa, q, eta, L)


def impulse_state_space(a, kappa, q, eta, L):
    """Direct simulation of the stacked state (independent check of impulse())."""
    q, eta = np.asarray(q, float), np.asarray(eta, float)
    x = kappa; y = eta * x; h = [x]
    for _ in range(L - 1):
        x = a * x + kappa * np.dot(q, y); y = (1 - eta) * y + eta * x; h.append(x)
    return np.array(h)


def Phi(q, eta):
    return float(np.sum(q))


def summed_response(a, kappa, Phi_):
    den = 1.0 - a - kappa * Phi_
    return np.inf if den <= 0 else kappa / den


def moments_from_impulse(a, kappa, h, n):
    """Exact inversion: h_0..h_n determine k_0..k_{n-1} (the moments of M of orders 0..n-1)."""
    k = np.zeros(n)
    for t in range(n):
        k[t] = (h[t + 1] - a * h[t] - kappa * np.dot(k[:t], h[t:0:-1][:t])) / kappa ** 2
    return k


def impulse_exact(a, kappa, q, eta, L):
    """Rational-arithmetic impulse response (inputs as Fractions)."""
    x = kappa; y = [e * x for e in eta]; h = [x]
    for _ in range(L - 1):
        x = a * x + kappa * sum(qi * yi for qi, yi in zip(q, y)); y = [(1 - e) * yi + e * x for e, yi in zip(eta, y)]; h.append(x)
    return h


def closed_loop_matrix(a, kappa, q, eta):
    q, eta = np.asarray(q, float), np.asarray(eta, float); K = len(q)
    J = np.zeros((K + 1, K + 1)); J[0, 0] = a; J[0, 1:] = kappa * q
    J[1:, 0] = eta * a; J[1:, 1:] = np.diag(1 - eta) + np.outer(eta, kappa * q)
    return J

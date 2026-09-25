"""Continuous-time stability, spectral abscissa, Euler scaling, and sampling limits.

Implements:
1. Lemma 3.1: Positive-vector characterization for Metzler/Hurwitz matrices.
2. Theorem 3.3: Continuous-time positive-feedback boundary rho(Gamma^{-1} * g * B * C) < 1.
3. Proposition 3.4: Boundary and supercritical behavior.
4. Proposition 3.5: Common-rate spectral abscissa sa(A_c).
5. Theorem 3.6: Euler scaling, Schur equivalence, and error bound.
6. Remark 3.7: Exact sampling vs Euler discretization.
7. Continuous hidden-memory tails.
"""
from typing import Dict, Any, Tuple, Optional
import numpy as np
from scipy import linalg


def build_continuous_matrix(
    Gamma: np.ndarray,
    B: np.ndarray,
    C: np.ndarray,
    E: np.ndarray,
    g: float,
) -> np.ndarray:
    """Construct the continuous-time block system matrix A_c.

    A_c = [[-Gamma,  g * B],
           [ E * C,   -E  ]]
    """
    Gamma = np.asarray(Gamma, dtype=float)
    E = np.asarray(E, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)

    if Gamma.ndim == 1:
        Gamma = np.diag(Gamma)
    if E.ndim == 1:
        E = np.diag(E)

    top = np.hstack([-Gamma, g * B])
    bottom = np.hstack([E @ C, -E])
    return np.vstack([top, bottom])


def is_metzler(A: np.ndarray, tol: float = 1e-12) -> bool:
    """Check if off-diagonal entries of A are nonnegative."""
    n = A.shape[0]
    off_diag = A[~np.eye(n, dtype=bool)]
    return bool(np.all(off_diag >= -tol))


def spectral_radius(M: np.ndarray) -> float:
    """Compute the spectral radius rho(M) = max |lambda_i|."""
    eigvals = np.linalg.eigvals(M)
    return float(np.max(np.abs(eigvals)))


def spectral_abscissa(A: np.ndarray) -> float:
    """Compute the spectral abscissa sa(A) = max Re(lambda_i)."""
    eigvals = np.linalg.eigvals(A)
    return float(np.max(np.real(eigvals)))


def is_hurwitz(A: np.ndarray, tol: float = 1e-12) -> bool:
    """Check if all eigenvalues of A have strictly negative real parts."""
    return spectral_abscissa(A) < -tol


def hurwitz_threshold_spectral_radius(
    Gamma: np.ndarray, B: np.ndarray, C: np.ndarray, g: float
) -> float:
    """Evaluate rho(Gamma^{-1} * g * B * C).

    Theorem 3.3 proves A_c is Hurwitz <=> rho(Gamma^{-1} * g * B * C) < 1.
    """
    if Gamma.ndim == 1:
        Gamma_inv = np.diag(1.0 / Gamma)
    elif np.allclose(Gamma, np.diag(np.diag(Gamma))):
        Gamma_inv = np.diag(1.0 / np.diag(Gamma))
    else:
        Gamma_inv = np.linalg.inv(Gamma)

    K = Gamma_inv @ (g * (B @ C))
    return spectral_radius(K)


def common_rate_spectral_abscissa_formula(
    gamma: float, lambda_rate: float, nu: float, g: float
) -> float:
    """Closed expression for spectral abscissa in common-rate case (Proposition 3.5).

    sa(A_c) = [ -(gamma + lambda) + sqrt((gamma - lambda)^2 + 4 * g * lambda * nu) ] / 2
    """
    disc = (gamma - lambda_rate) ** 2 + 4.0 * g * lambda_rate * nu
    return float((- (gamma + lambda_rate) + np.sqrt(max(0.0, disc))) / 2.0)


def forward_euler_parameters(
    gamma: float, g: float, lambda_rate: float, h: float
) -> Tuple[float, float, float]:
    """Scaled discrete parameters under forward Euler step h (Equation 3.5).

    a_h = 1 - h * gamma, g_h = h * g, eta_h = h * lambda
    """
    return float(1.0 - h * gamma), float(h * g), float(h * lambda_rate)


def max_admissible_euler_step(Gamma: np.ndarray, E: np.ndarray) -> float:
    """Maximum step size ensuring P_h >= 0 (Theorem 3.6).

    h_max = min( min_i gamma_i^{-1}, min_j lambda_j^{-1} )
    """
    if Gamma.ndim == 1:
        gamma_diag = Gamma
    else:
        gamma_diag = np.diag(Gamma)

    if E.ndim == 1:
        e_diag = E
    else:
        e_diag = np.diag(E)

    return float(min(np.min(1.0 / gamma_diag), np.min(1.0 / e_diag)))


def forward_euler_matrix(A_c: np.ndarray, h: float) -> np.ndarray:
    """Compute forward Euler transition P_h = I + h * A_c."""
    return np.eye(A_c.shape[0]) + h * A_c


def exact_sampled_matrix(A_c: np.ndarray, h: float) -> np.ndarray:
    """Compute exact sampled transition e^{h * A_c}."""
    return linalg.expm(h * A_c)


def euler_error_theoretical_bound(
    A_c: np.ndarray, h: float, T: float, ord: int = 2
) -> float:
    """Theoretical upper bound on ||(I + h A_c)^k - e^{k h A_c}|| for k h <= T.

    Bound = 0.5 * T * h * ||A_c||^2 * e^{T * ||A_c||}
    """
    norm_A = float(np.linalg.norm(A_c, ord=ord))
    return float(0.5 * T * h * (norm_A ** 2) * np.exp(T * norm_A))


def continuous_tail_bound(Q_max: float, lambda_0: float, T: float) -> float:
    """Continuous hidden-memory tail bound: int_T^infty K(t) dt <= Q_max * e^{-lambda_0 * T}."""
    return float(Q_max * np.exp(-lambda_0 * T))

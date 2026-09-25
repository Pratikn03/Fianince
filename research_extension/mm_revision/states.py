"""Pure dynamical systems state-space transitions, Jacobians, kernels, and impulse responses.

Contains no file I/O or network calls.
"""
from typing import Tuple, Optional, Union
import numpy as np


def build_transition_matrix(
    a: float,
    eta: Union[float, np.ndarray, list],
    q: Union[float, np.ndarray, list]
) -> np.ndarray:
    """Construct the discrete-time state transition matrix J for the linear market model.

    State vector: z_t = [x_t, y_{1,t}, ..., y_{n,t}]^T
    Transitions:
      x_{t+1} = a * x_t + sum_{k=1}^n y_{k,t}
      y_{k,t+1} = (1 - eta_k) * y_{k,t} + eta_k * q_k * x_t

    Matrix form (size (n+1) x (n+1)):
      J = [[a, 1, ..., 1],
           [eta_1 * q_1, 1 - eta_1, 0, ..., 0],
           ...
           [eta_n * q_n, 0, ..., 1 - eta_n]]
    """
    eta_arr = np.atleast_1d(np.asarray(eta, dtype=float))
    q_arr = np.atleast_1d(np.asarray(q, dtype=float))
    if len(eta_arr) != len(q_arr):
        raise ValueError(f"Lengths of eta ({len(eta_arr)}) and q ({len(q_arr)}) must match.")
    
    n = len(eta_arr)
    dim = 1 + n
    J = np.zeros((dim, dim), dtype=float)
    J[0, 0] = float(a)
    J[0, 1:] = 1.0
    for k in range(n):
        J[1 + k, 0] = eta_arr[k] * q_arr[k]
        J[1 + k, 1 + k] = 1.0 - eta_arr[k]
    return J


def spectral_radius(J: np.ndarray) -> float:
    """Compute the spectral radius rho(J) = max |lambda_i(J)|."""
    eigvals = np.linalg.eigvals(J)
    return float(np.max(np.abs(eigvals)))


def total_feedback_gain(a: float, q: Union[float, np.ndarray, list]) -> float:
    """Compute structural feedback gain sum S = a + sum(q)."""
    q_arr = np.atleast_1d(np.asarray(q, dtype=float))
    return float(a + np.sum(q_arr))


def steady_state_multiplier(a: float, q: Union[float, np.ndarray, list]) -> float:
    """Compute steady-state multiplier G = Q / (1 - a), where Q = sum(q)."""
    q_arr = np.atleast_1d(np.asarray(q, dtype=float))
    Q = float(np.sum(q_arr))
    if abs(1.0 - a) < 1e-15:
        raise ZeroDivisionError("Steady-state multiplier undefined when a = 1.")
    return Q / (1.0 - a)


def compute_impulse_response(
    a: float,
    eta: Union[float, np.ndarray, list],
    q: Union[float, np.ndarray, list],
    kappa: float = 1.0,
    H: int = 64
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute the normalized impulse response h_j and price response beta_j = kappa * h_j for j = 0, ..., H.

    Uses the exact transition matrix:
      h_j = e_1^T J^j e_1
      beta_j = kappa * h_j
    """
    J = build_transition_matrix(a, eta, q)
    dim = J.shape[0]
    e1 = np.zeros(dim)
    e1[0] = 1.0

    h = np.zeros(H + 1, dtype=float)
    state = e1.copy()
    for j in range(H + 1):
        h[j] = state[0]
        state = J @ state
    beta = float(kappa) * h
    return h, beta


def compute_kernel_taps(
    eta: Union[float, np.ndarray, list],
    q: Union[float, np.ndarray, list],
    H: int = 64
) -> np.ndarray:
    """Compute the latent memory kernel taps k_tau for tau = 0, ..., H.
    k_tau = sum_{i=1}^n q_i * eta_i * (1 - eta_i)^tau
    """
    eta_arr = np.atleast_1d(np.asarray(eta, dtype=float))
    q_arr = np.atleast_1d(np.asarray(q, dtype=float))
    k_taps = np.zeros(H + 1, dtype=float)
    for tau in range(H + 1):
        k_taps[tau] = np.sum(q_arr * eta_arr * ((1.0 - eta_arr) ** tau))
    return k_taps


def simulate_discrete_trajectory(
    a: float,
    eta: Union[float, np.ndarray, list],
    q: Union[float, np.ndarray, list],
    u: np.ndarray,
    innovations: Optional[np.ndarray] = None,
    kappa: float = 1.0,
    x0: float = 0.0,
    y0: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """Simulate exact discrete-time trajectory for T steps given input u and optional disturbances.

    Returns:
      x: array of length T+1 (prices)
      y: array of shape (T+1, n) (internal memory states)
    """
    eta_arr = np.atleast_1d(np.asarray(eta, dtype=float))
    q_arr = np.atleast_1d(np.asarray(q, dtype=float))
    n = len(eta_arr)
    T = len(u)

    if innovations is None:
        innovations = np.zeros(T, dtype=float)
    if y0 is None:
        y0 = np.zeros(n, dtype=float)
    else:
        y0 = np.asarray(y0, dtype=float)

    x = np.zeros(T + 1, dtype=float)
    y = np.zeros((T + 1, n), dtype=float)

    x[0] = x0
    y[0] = y0

    for t in range(T):
        x[t + 1] = a * x[t] + np.sum(y[t]) + kappa * u[t] + innovations[t]
        y[t + 1] = (1.0 - eta_arr) * y[t] + eta_arr * q_arr * x[t]

    return x, y

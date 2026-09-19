"""Positive adaptive-feedback model and independent numerical realizations.

These simple exponential-learning agents are not trained neural policies.
A time step has no fixed mapping to seconds, days, or trading sessions.
"""
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class Market:
    a: float
    q: NDArray[np.float64]
    eta: NDArray[np.float64]

    def __post_init__(self) -> None:
        q = np.asarray(self.q, dtype=float).copy()
        eta = np.asarray(self.eta, dtype=float).copy()
        if q.ndim != 1 or eta.shape != q.shape or q.size == 0:
            raise ValueError('q and eta must be nonempty one-dimensional arrays of equal shape')
        if not (np.isfinite(self.a) and 0 <= self.a < 1):
            raise ValueError('a must be finite and in [0,1)')
        if not np.all(np.isfinite(q)) or not np.all(q >= 0):
            raise ValueError('q must be finite and nonnegative')
        if not np.all(np.isfinite(eta)) or not np.all((eta > 0) & (eta <= 1)):
            raise ValueError('eta must lie in (0,1]')
        q.setflags(write=False)
        eta.setflags(write=False)
        object.__setattr__(self, 'q', q)
        object.__setattr__(self, 'eta', eta)

    @property
    def feedback(self) -> float:
        return float(self.q.sum())

    @property
    def margin(self) -> float:
        """Positive means Schur stable within this fixed positive model."""
        return 1.0 - self.a - self.feedback

    def matrix(self) -> NDArray[np.float64]:
        n = len(self.q)
        J = np.zeros((n+1, n+1), dtype=float)
        J[0, 0] = self.a
        J[0, 1:] = 1.0
        J[1:, 0] = self.eta*self.q
        J[1:, 1:] = np.diag(1.0-self.eta)
        return J

    def spectral_radius(self) -> float:
        return float(np.max(np.abs(np.linalg.eigvals(self.matrix()))))

    def simulate(self, shocks: NDArray[np.float64], initial_price: float = 0.0,
                 freeze: bool = False) -> NDArray[np.float64]:
        """Agent-loop route. shocks[t] enters the price at time t+1.

        All learning states start at zero. freeze=True holds them there.
        It does NOT model freezing already nonzero real portfolios.
        """
        shocks = np.asarray(shocks, dtype=float)
        if shocks.ndim != 1 or not np.all(np.isfinite(shocks)):
            raise ValueError('shocks must be a finite one-dimensional array')
        if not np.isfinite(initial_price):
            raise ValueError('initial_price must be finite')
        y = np.zeros(len(self.q), dtype=float)
        x = float(initial_price)
        out = np.empty(len(shocks)+1, dtype=float)
        out[0] = x
        for t, epsilon in enumerate(shocks):
            next_x = self.a*x + float(y.sum()) + epsilon
            if not freeze:
                y = (1-self.eta)*y + self.eta*self.q*x
            x = next_x
            out[t+1] = x
        return out

    def impulse(self, horizon: int) -> NDArray[np.float64]:
        if int(horizon) != horizon or horizon < 0:
            raise ValueError('horizon must be a nonnegative integer')
        return self.simulate(np.zeros(horizon), initial_price=1.0)

    def impulse_matrix(self, horizon: int) -> NDArray[np.float64]:
        """Separate full-state matrix route used as a cross-check."""
        if int(horizon) != horizon or horizon < 0:
            raise ValueError('horizon must be a nonnegative integer')
        z = np.zeros(len(self.q)+1)
        z[0] = 1.0
        J = self.matrix()
        result = np.empty(horizon+1)
        for h in range(horizon+1):
            result[h] = z[0]
            z = J @ z
        return result

    def kernel(self, horizon: int) -> NDArray[np.float64]:
        if int(horizon) != horizon or horizon < 1:
            raise ValueError('kernel horizon must be a positive integer')
        j = np.arange(horizon, dtype=int)
        return (self.q*self.eta) @ ((1-self.eta)[:, None]**j[None, :])

    def loop_open_kernel(self, horizon: int) -> NDArray[np.float64]:
        """Shadow replay: pulse input once, then clamp subsequent inputs to zero."""
        if int(horizon) != horizon or horizon < 1:
            raise ValueError('kernel horizon must be a positive integer')
        y = self.eta*self.q
        result = np.empty(horizon)
        for j in range(horizon):
            result[j] = y.sum()
            y = (1-self.eta)*y
        return result


def recover_kernel(impulse: NDArray[np.float64], a: float) -> NDArray[np.float64]:
    """Exact triangular deconvolution; no noise guarantee is attached.

    h[0:H+2] gives k[0:H]. h[0]=1 and h[1]=a are required.
    """
    h = np.asarray(impulse, dtype=float)
    if h.ndim != 1 or len(h) < 3 or not np.all(np.isfinite(h)):
        raise ValueError('at least three finite impulse coefficients required')
    if not np.isclose(h[0], 1.0, atol=1e-10) or not np.isclose(h[1], a, atol=1e-10):
        raise ValueError('impulse must use a unit initial-price perturbation')
    H = len(h)-2
    k = np.empty(H)
    for j in range(H):
        convolution = sum(k[r]*h[j-r] for r in range(j))
        k[j] = h[j+2]-a*h[j+1]-convolution
    return k

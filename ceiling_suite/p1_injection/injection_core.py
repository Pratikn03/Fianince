"""Core of the Paper 1 real-noise injection test (P1_injection).

Synthetic cohorts with known memory spacing are probed in reset experiments whose observation errors are drawn from
real market price changes (or, in the control arm, i.i.d. Gaussian noise of the same variance). The question is
whether the price-only sample requirement still scales as (Delta eta)^-(4K-2) and the class-tagged requirement stays
flat when the noise has real heavy tails, autocorrelation and volatility clustering.
"""
import numpy as np
from numpy.polynomial import legendre as L


def gauss_rule(K):
    x, w = L.leggauss(K)
    return x, w / w.sum()


def economy(K, d_eta, rc, W):
    s, om = gauss_rule(K)
    return rc + d_eta * s, W * om                              # memory rates r_i and merged weights w_i


def impulse(a, kappa, w, r, T):
    k = np.array([np.sum(w * r ** m) for m in range(T)])
    h = np.zeros(T); h[0] = kappa
    for t in range(1, T):
        h[t] = a * h[t - 1] + kappa * np.dot(k[:t], h[t - 1::-1][:t])
    return h


def class_flows(w, r, h):
    """f_{i,t} = w_i sum_{s<=t} r_i^{t-s} h_s, i.e. f_{i,t} = r_i f_{i,t-1} + w_i h_t."""
    T = len(h); F = np.zeros((len(w), T))
    for i in range(len(w)):
        acc = 0.0
        for t in range(T):
            acc = r[i] * acc + w[i] * h[t]; F[i, t] = acc
    return F


def prony_weights(hbar, a, kappa, K):
    """Rows of hbar are averaged responses h_0..h_{2K} (h_0 = kappa is known). Returns rate-ordered weights, or NaN
    rows when the Prony polynomial has non-real or out-of-range roots."""
    R_, T = hbar.shape
    k = np.zeros((R_, 2 * K))
    for t in range(1, 2 * K + 1):                             # deconvolve the closed loop: kernel values k_0..k_{2K-1}
        conv = np.zeros(R_)
        for m in range(t - 1):
            conv += k[:, m] * hbar[:, t - 1 - m]
        k[:, t - 1] = (hbar[:, t] - a * hbar[:, t - 1] - kappa * conv) / (kappa * kappa)
    out = np.full((R_, K), np.nan)
    for j in range(R_):
        H = np.array([[k[j, m + i] for i in range(K)] for m in range(K)])
        rhs = -np.array([k[j, m + K] for m in range(K)])
        try:
            c = np.linalg.solve(H, rhs)
        except np.linalg.LinAlgError:
            continue
        roots = np.roots(np.concatenate([[1.0], c[::-1]]))
        if np.max(np.abs(roots.imag)) > 1e-9 or np.min(roots.real) <= 0 or np.max(roots.real) >= 1:
            continue
        rr = np.sort(roots.real)
        V = np.vstack([rr ** m for m in range(K)])
        try:
            out[j] = np.linalg.solve(V, k[j, :K])
        except np.linalg.LinAlgError:
            continue
    return out


def tagged_weights(fbar, hbar_long):
    """Per class, regress fbar_t on (fbar_{t-1}, hbar_t), t >= 1. Returns estimated weights (one per class)."""
    R_, K, T = fbar.shape
    out = np.zeros((R_, K))
    for i in range(K):
        y = fbar[:, i, 1:]; x1 = fbar[:, i, :-1]; x2 = hbar_long[:, 1:T]
        for j in range(R_):
            X = np.column_stack([x1[j], x2[j]])
            out[j, i] = np.linalg.lstsq(X, y[j], rcond=None)[0][1]
    return out


class NoisePool:
    """Windows of standardized observation errors. Real arm: consecutive one-minute log-price changes, demeaned and
    scaled to unit variance. Averages of N windows are drawn exactly for N <= exact_max and, by the central limit
    theorem, as Gaussian vectors with the windows' empirical covariance for larger N."""

    def __init__(self, windows, exact_max=4096):
        self.W = np.asarray(windows, float)
        self.cov = np.cov(self.W.T, bias=True)
        self.chol = np.linalg.cholesky(self.cov + 1e-12 * np.eye(self.W.shape[1]))
        self.exact_max = exact_max

    def mean_of(self, N, R_, rng):
        T = self.W.shape[1]
        if N <= self.exact_max:
            idx = rng.integers(0, len(self.W), size=(R_, N))
            return self.W[idx].mean(axis=1)
        return (rng.standard_normal((R_, T)) @ self.chol.T) / np.sqrt(N)


def gaussian_pool(T, n=200000, seed=0):
    return NoisePool(np.random.default_rng(seed).standard_normal((n, T)))


def failure_rate(arm, K, d_eta, N, pool_p, pool_f, cfg, rng):
    a, kappa, rc, W, sig, sigf, R_ = (cfg[k] for k in ("a", "kappa", "rc", "W", "sigma", "sigma_f", "reps"))
    r, w = economy(K, d_eta, rc, W)
    eps = cfg["eps_rel"] * w.min()
    if arm == "price":
        T = 2 * K + 1
        h = impulse(a, kappa, w, r, T)
        hbar = h + sig * pool_p.mean_of(N, R_, rng)
        hbar[:, 0] = kappa
        est = prony_weights(hbar, a, kappa, K)
    else:
        T = cfg["tagged_taps"]
        h = impulse(a, kappa, w, r, T)
        hbar = h + sig * pool_p.mean_of(N, R_, rng)
        F = class_flows(w, r, h)
        fbar = F[None] + sigf * np.stack([pool_f.mean_of(N, R_, rng) for _ in range(K)], axis=1)
        est = tagged_weights(fbar, hbar)
    bad = ~np.isfinite(est).all(axis=1) | (np.nanmax(np.abs(est - w), axis=1) > eps)
    return float(bad.mean())


def n_star(arm, K, d_eta, pool_p, pool_f, cfg, rng):
    """Smallest N on the grid at which the failure rate is <= target there and at the next grid point."""
    grid = cfg["n_grid"]; fr = []
    for N in grid:
        fr.append(failure_rate(arm, K, d_eta, int(N), pool_p, pool_f, cfg, rng))
        if len(fr) >= 2 and fr[-2] <= cfg["target_failure"] and fr[-1] <= cfg["target_failure"]:
            return float(grid[len(fr) - 2]), fr
    return None, fr


def slope(d_etas, ns):
    pts = [(np.log(d), np.log(n)) for d, n in zip(d_etas, ns) if n is not None]
    if len(pts) < 3:
        return None
    x, y = np.array(pts).T
    return float(np.polyfit(x, y, 1)[0])

"""Numerical illustrations of Theorems thm:hidden, thm:uniformcert and thm:absresp (Chapter 4). Not evidence;
a check that the statements behave as claimed on simulated economies. Writes uniform_certification_numeric_check.json."""
import json
from pathlib import Path
import numpy as np

rng = np.random.default_rng(20261025)
CV = -1.95                                     # Dickey-Fuller 5% critical value, no deterministic terms


def simulate(phi_fn, T, burn=0):
    """phi_fn(t, x_hist) -> conditional mean of x_{t+1}; x_0 = 0; unit innovations."""
    x = np.zeros(T + 1)
    for t in range(T):
        x[t + 1] = phi_fn(t, x) + rng.normal()
    return x


def adf_t(x, p):
    dx = np.diff(x)
    rows = range(p, len(x) - 1)
    X = np.array([[x[t]] + [dx[t - i] for i in range(1, p + 1)] for t in rows])   # dx[t-i] = x[t-i+1]-x[t-i]
    y = np.array([dx[t] for t in rows])
    b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b
    s2 = e @ e / (len(y) - X.shape[1]); se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[0, 0])
    return b[0] / se


out = {}
# (A) hidden slow feedback: safe economy (margin c) vs unsafe economy with a slow momentum cohort (margin -mu)
c, mu, T, R = 0.2, 0.2, 1000, 400
rho = 1 - c; kq = c + mu
res = {}
for r in (0.99, 0.999, 0.9999):
    def safe(t, x): return rho * x[t]
    def unsafe(t, x):
        m = np.arange(t + 1); return rho * x[t] + kq * (1 - r) * np.sum(r ** m * x[t - m])
    rate_s = np.mean([adf_t(simulate(safe, T), 2) < CV for _ in range(R)])
    rate_u = np.mean([adf_t(simulate(unsafe, T), 2) < CV for _ in range(R)])
    res[str(r)] = {"certified_safe_rate_safe_economy": float(rate_s), "certified_safe_rate_unsafe_economy": float(rate_u),
                   "kl_bound": float(kq ** 2 * (1 - r) ** 2 * T ** 3 / (2 * c))}
out["hidden"] = {"c": c, "mu": mu, "T": T, "reps": R, "by_memory_rate": res}

# (B) uniform certification: ADF power as a function of c = T(1-rho) = T M / g(1), across g and T
def ar_from_roots(rho, groots):
    g = np.poly1d([1.0])
    for z in groots:
        g = g * np.poly1d([-1 / z, 1.0])
    f = g * np.poly1d([-rho, 1.0]); coef = np.real(f.coeffs[::-1]); return -coef[1:], float(np.real(g(1.0)))
power = {}
for name, groots in (("g_roots_2_-3", [2.0, -3.0]), ("g_roots_1.5pm_i", [1.5 + 1j, 1.5 - 1j])):
    for T in (500, 2000):
        for cc in (0.0, 5.0, 10.0, 20.0, 40.0):
            phi, g1 = ar_from_roots(1 - cc / T, groots); L = len(phi)
            def f(t, x, phi=phi, L=L):
                return sum(phi[i] * x[t - i] for i in range(L) if t - i >= 0)
            rate = np.mean([adf_t(simulate(f, T), L - 1) < CV for _ in range(300)])
            power[f"{name}|T={T}|c={cc:g}"] = {"rate_certified_safe": float(rate), "margin": float(cc / T * g1), "g1": g1}
out["uniform_power"] = power

# (C) absolute-response certificate: coverage of the Lipschitz interval for Psi_H = sum_{j<H} |psi_j|
def psi(phi, H):
    L = len(phi); p = np.zeros(H); p[0] = 1.0
    for j in range(1, H):
        p[j] = sum(phi[i] * p[j - 1 - i] for i in range(L) if j - 1 - i >= 0)
    return p
H, T = 12, 2000
phi_true = np.array([0.5, 0.3, -0.4])          # signed kernel: oscillating, stationary
Psi = np.abs(psi(phi_true, H)).sum(); cover, widths = [], []
from scipy.stats import chi2
q = chi2.ppf(0.95, len(phi_true))
for _ in range(300):
    x = simulate(lambda t, x: sum(phi_true[i] * x[t - i] for i in range(3) if t - i >= 0), T)
    X = np.array([[x[t - i] if t - i >= 0 else 0.0 for i in range(3)] for t in range(T)]); y = x[1:T + 1]
    b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b; S = (e @ e / (T - 3)) * np.linalg.inv(X.T @ X)
    rad = np.sqrt(q * np.linalg.eigvalsh(S).max())
    # Lipschitz constant of Psi_H over the ball, by the sum of gradient norms on a few points of the ball
    G = 0.0
    for _ in range(8):
        u = rng.normal(size=3); u /= np.linalg.norm(u); pt = b + rad * rng.random() * u
        J = np.array([(psi(pt + 1e-6 * np.eye(3)[k], H) - psi(pt - 1e-6 * np.eye(3)[k], H)) / 2e-6 for k in range(3)])
        G = max(G, np.linalg.norm(J, axis=0).sum())
    hw = G * rad; est = np.abs(psi(b, H)).sum()
    cover.append(abs(est - Psi) <= hw); widths.append(hw)
out["absresp"] = {"H": H, "T": T, "phi": phi_true.tolist(), "Psi_H": float(Psi), "coverage": float(np.mean(cover)),
                  "median_half_width": float(np.median(widths)), "signed_sum_S": float(psi(phi_true, 400).sum())}
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))

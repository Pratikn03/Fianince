"""Numerical checks for the second batch of results on Paper 1's open questions (core section app:openres).

B1 smooth saturation of every order: two populations with equal kernels and equal cubic leverage measure but
   different fifth moments differ by order A^5 (slope in A about 5) and the first tap's A^5 coefficient is
   kappa * (2/15) * kappa^5 * dM5.
B2 noisy stress rate: the differential of the two-date flow map has full rank at random irreducible tanh populations.
B3 largest weights: (max Gauss-Radau weight - max Gauss weight) * K^2 approaches pi/4 (60-digit arithmetic).
B4 cascades with forward-looking dealers: above the threshold, three equilibria for an intermediate shock.
Run: python3 open_checks2.py -> open_checks2_results.json"""
import json, math
import numpy as np
import mpmath as mp
from numpy.polynomial import legendre as Lg

out = {}

# ---------- B1
def response(pop, A, a=0.1, kap=0.3, T=80):
    c = np.array([p[0] for p in pop]); r = np.array([p[1] for p in pop]); l = np.array([p[2] for p in pop])
    x = np.zeros(T); m = np.zeros(len(pop)); x[0] = kap * A
    for t in range(1, T):
        m = r * m + x[t - 1]
        x[t] = a * x[t - 1] + kap * np.sum(c * np.tanh(l * m))
    return x
mp.mp.dps = 40
P = [(1.0, 0.5, 1.0)]
P2 = [(1.25, 0.5, 0.5), (0.25, 0.5, 1.5)]
dM5 = sum(c * l ** 5 for c, _, l in P) - sum(c * l ** 5 for c, _, l in P2)
As = np.array([0.02, 0.04, 0.08, 0.16])
d = [np.linalg.norm(response(P, A) - response(P2, A)) for A in As]
out["B1_slope_in_A"] = float(np.polyfit(np.log(As), np.log(d), 1)[0])
A = 0.01; kap = 0.3
first = response(P, A)[1] - response(P2, A)[1]
out["B1_first_tap_coeff"] = float(first / A ** 5)
out["B1_first_tap_theory"] = float(kap * (2 / 15) * kap ** 5 * dM5)
out["B1_ok"] = bool(abs(out["B1_slope_in_A"] - 5) < 0.1 and abs(out["B1_first_tap_coeff"] / out["B1_first_tap_theory"] - 1) < 0.01)

# ---------- B2
rng = np.random.default_rng(7)
ok = True
for _ in range(50):
    n = int(rng.integers(1, 4))
    c = rng.uniform(0.3, 1.5, n) * rng.choice([-1, 1], n); r = rng.uniform(0, 0.9, n); l = rng.uniform(0.5, 2.0, n)
    pts = rng.uniform(-0.3, 0.3, (12 * n, 2))
    J = []
    for u1, u2 in pts:
        z = r * u1 + u2; sech2 = 1 / np.cosh(l * z) ** 2
        J.append(np.r_[np.tanh(l * z), c * z * sech2, c * l * u1 * sech2])
    J = np.array(J); sv = np.linalg.svd(J, compute_uv=False)
    if sv.min() / sv.max() < 1e-12: ok = False
out["B2_jacobian_full_rank_50_random"] = ok

# ---------- B3
mp.mp.dps = 60
def gauss_max(K):
    xs = [mp.findroot(lambda x: mp.legendre(K, x), mp.mpf(float(rr))) for rr in np.real(Lg.legroots([0] * K + [1]))]
    return max(2 / ((1 - x ** 2) * mp.diff(lambda y: mp.legendre(K, y), x) ** 2) for x in xs) / 2
def radau_max(K):
    cc = [0] * (K + 1); cc[K - 1] = 1; cc[K] = 1
    rr = [q for q in np.sort(np.real(Lg.legroots(cc))) if q > -0.999999]
    f = lambda x: mp.legendre(K - 1, x) + mp.legendre(K, x)
    xs = [mp.findroot(f, mp.mpf(float(q)), tol=mp.mpf(10) ** -50) for q in rr]
    ws = [mp.mpf(2) / K ** 2] + [(1 - x) / (K ** 2 * mp.legendre(K - 1, x) ** 2) for x in xs]
    return max(ws) / 2
rows = []
for K in (10, 20, 30, 40, 50, 60):
    dd = radau_max(K) - gauss_max(K)
    rows.append({"K": K, "gap_times_K2": float(dd * K ** 2), "minus_pi_over_4_times_K": float((dd * K ** 2 - mp.pi / 4) * K)})
out["B3_rows"] = rows
out["B3_ok"] = bool(all(r["gap_times_K2"] > 0 for r in rows) and abs(rows[-1]["gap_times_K2"] - math.pi / 4) < 0.03)

# ---------- B4
from scipy.stats import norm
kap = 0.5; height = 4.0
L = lambda dl: height * 0.1 * np.sqrt(2 * np.pi) * (norm.cdf((dl - 0.5) / 0.1) - norm.cdf(-5.0))
grid = np.linspace(0, 3, 300001); psi = grid - kap * L(grid)
s = 0.5 * (psi[grid <= 0.5].max() + psi[(grid > 0.5) & (grid < 1.2)].min())
roots = grid[np.where(np.diff(np.sign(psi - s)))[0]]
out["B4_shock"] = float(s); out["B4_equilibria"] = [float(x) for x in roots]
out["B4_ok"] = bool(len(roots) == 3)

print(json.dumps(out, indent=1))
json.dump(out, open("open_checks2_results.json", "w"), indent=1)

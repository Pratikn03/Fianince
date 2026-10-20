"""Numerical checks for the Paper 1 hardening edits (items 1, 2, 4(iii), 5)."""
import numpy as np, json
from numpy.polynomial.legendre import leggauss
from scipy.linalg import toeplitz, svdvals
rng = np.random.default_rng(7); out = {}
def imp(a, k, q, eta, L=600, unit=False):
    y = np.zeros(len(q)); h = []; xp = 0.0
    for t in range(L):
        xt = a * xp + k * np.dot(q, y) + ((1.0 if unit else k) if t == 0 else 0.0); y = (1 - eta) * y + eta * xt; h.append(xt); xp = xt
    return np.array(h)
# (1) Hankel rank (McMillan degree) at a>0 and a=0
def hrank(h, n=12):
    Hk = np.array([[h[i + j + 1] for j in range(n)] for i in range(n)])   # strictly proper part
    s = svdvals(Hk); return int((s > 1e-10 * s[0]).sum())
r = {}
for a in (0.5, 0.0):
    for K in (1, 2, 3):
        q = rng.uniform(.05, .2, K); eta = np.sort(rng.uniform(.1, .9, K))
        r[f"a={a},K={K}"] = hrank(imp(a, 0.8, q, eta))
out["mcmillan_degree"] = r
# (2) sigma_min of finite lower-triangular Toeplitz section of H/kappa >= 1/2 in positive economies
mins = []
for _ in range(300):
    K = rng.integers(1, 4); q = rng.uniform(0, .3, K); a = rng.uniform(0, .9)
    k = rng.uniform(0.05, 1.5); 
    if a + k * q.sum() >= 0.98: continue
    eta = rng.uniform(.02, .98, K); g = imp(a, k, q, eta, L=400) / k
    for n in (5, 40, 200):
        Gm = np.tril(toeplitz(g[:n])); mins.append(svdvals(Gm).min())
out["sigma_min_G"] = {"min": float(min(mins)), "n_cases": len(mins)}
# (4iii) passive Whittle divergence for Gauss vs Gauss-Radau K-cohort economies
def radau(K):
    # Gauss-Radau nodes on [-1,1] with fixed node -1: roots of (P_{K-1}+P_K)/(1+x)
    from numpy.polynomial import legendre as Lg
    c = np.zeros(K + 1); c[K - 1] = 1; c[K] = 1
    x = np.sort(np.real(Lg.legroots(c)))
    V = np.vander(x, K, increasing=True).T; m = np.array([2 / (j + 1) if j % 2 == 0 else 0 for j in range(K)])
    w = np.linalg.solve(V, m); return x, w / 2
def whittle(hA, hB):
    om = np.linspace(-np.pi, np.pi, 8193)[:-1]
    E = np.exp(-1j * np.outer(om, np.arange(len(hA))))
    rho = np.abs(E @ hA) ** 2 / np.abs(E @ hB) ** 2
    return float(np.mean(rho - 1 - np.log(rho)) / 2)  # (1/4pi) int = (1/2) mean
slopes = {}
for K in (2, 3, 4):
    xg, wg = leggauss(K); wg = wg / 2; xr, wr = radau(K)
    ds = np.array([0.08, 0.06, 0.045, 0.034, 0.025]); Ds = []
    for d in ds:
        rA, rB = 0.7 + d * xg, 0.7 + d * xr
        # merged weights W*omega at rates r: q_i eta_i = w_i with eta = 1-r
        WA, WB = 0.1 * wg, 0.1 * wr
        hA = imp(0.5, 1.0, WA / (1 - rA), 1 - rA, L=1500); hB = imp(0.5, 1.0, WB / (1 - rB), 1 - rB, L=1500)
        Ds.append(whittle(hA, hB))
    slopes[K] = float(np.polyfit(np.log(ds), np.log(Ds), 1)[0])
out["passive_K_slopes_of_D"] = {"theory": {K: 4 * K - 2 for K in (2, 3, 4)}, "fitted": slopes}
# (5) IV Jacobian determinant formula vs simulation
a, k = 0.5, 0.8; q = np.array([0.15, 0.1]); eta = np.array([0.3, 0.35]); w = q * eta; r = 1 - eta
T = 400000; x = np.zeros(T); y = np.zeros(2); u = np.zeros((T, 2)); xi = rng.standard_normal(T)
xp = 0.0
for t in range(T):
    xt = a * xp + k * q @ y + xi[t]; y = (1 - eta) * y + eta * xt; u[t] = q * y; x[t] = xt; xp = xt
i = 0; Z = np.c_[x[1:-1], x[2:]]; X = np.c_[u[1:-1, i], x[2:]]
det_sim = np.linalg.det(Z.T @ X / len(Z))
# closed form: gamma_s = sum_l c_l lam_l^s with h response to price innovation
J = np.array([[a, k * q[0], k * q[1]], [eta[0] * a, 1 - eta[0] + eta[0] * k * q[0], eta[0] * k * q[1]], [eta[1] * a, eta[1] * k * q[0], 1 - eta[1] + eta[1] * k * q[1]]])
b = np.array([1.0, eta[0], eta[1]])
lam, Vv = np.linalg.eig(J); om_ = (Vv[0, :] * np.linalg.solve(Vv, b)).real; lam = lam.real
c = np.array([om_[l] * sum(om_[m] / (1 - lam[l] * lam[m]) for m in range(3)) for l in range(3)])
det_cf = w[i] * sum(c[l] * c[m] * (1 - lam[l] * lam[m]) / (1 - r[i] * lam[m]) for l in range(3) for m in range(3))
out["iv_det"] = {"simulated": float(det_sim), "closed_form": float(det_cf), "weights_c_nonneg": bool((c >= -1e-12).all())}
print(json.dumps(out, indent=1)); json.dump(out, open("R_P1_hardening_checks.json", "w"), indent=1)

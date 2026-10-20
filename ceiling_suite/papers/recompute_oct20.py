"""Re-runs of numbers previously marked 'not re-run' (Oct 20, 2026).
(A) Paper 2, Prop. lucas: is the transient gain non-decreasing in the adaptation rate eta? (T6 book with momentum)
(B) Paper 2, Prop. invariance: impulse coefficients of observationally equivalent cohort splittings.
(C) Paper 1: symmetric multi-asset cohort network: spectral radius and Kreiss constant vs number of assets."""
import json, numpy as np
out = {}
# ---------------- (A)
def impulse_t6(a, phi, kappa, r, eps, eta, q, L=400):
    x = np.zeros(L); dd = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        tot = (1.0 if t == 0 else 0.0) + f[t]
        x[t] = (a * x[t - 1] + phi * dd[t - 1] if t else 0) + kappa * tot
        dd[t] = ((1 - r) * dd[t - 1] if t else 0) + eps * tot
    return x
def trans(a, phi, kappa, r, eps, eta, q):
    # state (x, d, f): f_{t} = (1-eta) f_{t-1} + eta q x_{t-1}; x_t = a x_{t-1} + phi d_{t-1} + kappa f_t ; d_t = (1-r) d_{t-1} + eps f_t
    F = np.array([[0, 0, 1 - eta], [0, 0, 0], [eta * q, 0, 0]], float)
    M = np.zeros((3, 3))
    M[2] = [eta * q, 0, 1 - eta]
    M[0] = [a + kappa * eta * q, phi, kappa * (1 - eta)]
    M[1] = [eps * eta * q, 1 - r, eps * (1 - eta)]
    return M
R = np.random.default_rng(20261020); draws = []; n = 0
etas = np.linspace(0.05, 0.95, 19)
while len(draws) < 3000:
    a = R.uniform(0.3, 0.97); kappa = R.uniform(0.2, 1.5); r = R.uniform(0.05, 0.9)
    phi = R.uniform(0, 3); eps = R.uniform(-0.05, 0.05); q = R.uniform(-0.3, 0.3)
    ok = all(max(abs(np.linalg.eigvals(trans(a, phi, kappa, r, eps, e, q)))) < 0.995 for e in etas)
    n += 1
    if not ok:
        continue
    peak, summ = [], []
    for e in etas:
        h = impulse_t6(a, phi, kappa, r, eps, e, q)
        peak.append(np.max(np.abs(h))); summ.append(np.sum(np.abs(h)))
    peak, summ = np.array(peak), np.array(summ)
    tol = 1e-9 * max(1, peak.max())
    draws.append({"q": q, "peak_monotone": bool(np.all(np.diff(peak) >= -tol)),
                  "sum_monotone": bool(np.all(np.diff(summ) >= -1e-9 * max(1, summ.max()))),
                  "sum_const": bool(np.ptp(summ) <= 1e-6 * summ.max()),
                  "S_formula": (kappa + phi * eps / r) / ((1 - a) - q * (kappa + phi * eps / r)),
                  "sum_signed": float(np.sum(impulse_t6(a, phi, kappa, r, eps, 0.5, q)))})
D = draws
qpos = [d for d in D if d["q"] > 0]; qneg = [d for d in D if d["q"] <= 0]
out["A_lucas"] = {"stable_draws": len(D), "attempts": n, "eta_grid": [0.05, 0.95, 19],
    "share_peak_nondecreasing": float(np.mean([d["peak_monotone"] for d in D])),
    "share_sum_nondecreasing": float(np.mean([d["sum_monotone"] for d in D])),
    "share_sum_nondecreasing_q_pos": float(np.mean([d["sum_monotone"] for d in qpos])),
    "share_peak_nondecreasing_q_pos": float(np.mean([d["peak_monotone"] for d in qpos])),
    "share_sum_nondecreasing_q_neg": float(np.mean([d["sum_monotone"] for d in qneg])),
    "max_rel_err_signed_sum_vs_S_formula": float(max(abs(d["sum_signed"] - d["S_formula"]) / abs(d["S_formula"]) for d in D))}
print("A", out["A_lucas"])
# ---------------- (B)
def cohort_imp(a, kappa, w, eta, L=200):
    y = np.zeros(len(w)); h = []; xp = 0.0
    for t in range(L):
        xt = a * xp + kappa * np.dot(w, y) + (kappa if t == 0 else 0.0); y = (1 - eta) * y + eta * xt; h.append(xt); xp = xt
    return np.array(h)
mx = 0.0
for _ in range(1000):
    K = R.integers(1, 5); w = R.uniform(0.01, 0.1, K); eta = R.uniform(0.05, 0.9, K); a = R.uniform(0.2, 0.8); kap = R.uniform(0.3, 1.0)
    i = R.integers(0, K); s = R.uniform(0.1, 0.9)
    w2 = np.concatenate([w, [w[i] * (1 - s)]]); w2[i] *= s; eta2 = np.concatenate([eta, [eta[i]]])
    mx = max(mx, float(np.max(np.abs(cohort_imp(a, kap, w, eta) - cohort_imp(a, kap, w2, eta2)))))
out["B_invariance"] = {"economies": 1000, "max_abs_diff_impulse": mx}
print("B", out["B_invariance"])
# ---------------- (C) symmetric cohort network across M assets
def kreiss(J):
    best = 0.0; n = len(J)
    for rr in 1 + np.logspace(-4, 2, 120):
        for th in np.linspace(0, 2 * np.pi, 73):
            z = rr * np.exp(1j * th); best = max(best, (rr - 1) * np.linalg.norm(np.linalg.inv(z * np.eye(n) - J), 2))
    return best
a, kap, eta, qw, c = 0.5, 0.8, 0.30, 0.20, 0.05
res = {}
for M in (1, 2, 5, 10, 15):
    C = np.eye(M) + c * (np.ones((M, M)) - np.eye(M))            # symmetric nonnegative cross-impact
    b = kap * qw
    # price-first symmetric form of Lemma cm per asset: J' = diag(0, r) + u u^T, u = (sqrt(a), sqrt(b*eta)); coupled through C
    r_ = 1 - eta; u = np.array([np.sqrt(a), np.sqrt(b * eta)])
    Jp = np.kron(np.eye(M), np.diag([0.0, r_])) + np.kron(C, np.outer(u, u))
    rho = float(max(abs(np.linalg.eigvals(Jp))))
    res[M] = {"spectral_radius": rho, "kreiss_2norm_symmetric_coords": kreiss(Jp), "symmetric": bool(np.allclose(Jp, Jp.T)),
              "nonnegative": bool((Jp >= -1e-15).all())}
out["C_network"] = {"params": {"a": a, "kappa": kap, "eta": eta, "q": qw, "cross_impact": c}, "by_M": res}
print("C", json.dumps(res, indent=0))
json.dump(out, open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "recomputed", "R_oct20_reruns.json"), "w"), indent=1)

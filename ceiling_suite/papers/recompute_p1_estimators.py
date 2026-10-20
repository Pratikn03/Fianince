"""Paper 1, re-implemented estimator checks (Oct 20, 2026).
(1) Table tab:crb: maximum likelihood at the critical noise level (success rate and RMSE/CRB), per scenario.
(2) Table tab:lecam: worst-case failure of four estimators at N=50 on the two-point family of Theorem twocohort."""
import json, numpy as np
from scipy.optimize import least_squares
a, k, L = 0.5, 0.8, 121
def imp(w, eta):
    w = np.asarray(w, float); eta = np.asarray(eta, float)
    y = np.zeros(len(w)); h = np.empty(L); xp = 0.0
    for t in range(L):
        xt = a * xp + k * np.dot(w, y) + (k if t == 0 else 0.0); y = (1 - eta) * y + eta * xt; h[t] = xt; xp = xt
    return h
def jac(w, eta, e=1e-6):
    th = np.concatenate([w, eta]); K = len(w); cols = []
    for j in range(2 * K):
        tp = th.copy(); tm = th.copy(); tp[j] += e; tm[j] -= e
        cols.append((imp(tp[:K], tp[K:]) - imp(tm[:K], tm[K:])) / (2 * e))
    return np.array(cols).T
def fit(hobs, K, prior=None, starts=None):
    """Least squares (ML under Gaussian noise) over (w, eta); optional Gaussian prior (center, sd, sigma) -> MAP."""
    lo = np.r_[np.zeros(K), np.full(K, 0.02)]; hi = np.r_[np.full(K, 0.4), np.full(K, 0.98)]
    best = None
    for s in starts:
        def res(th):
            r = imp(th[:K], th[K:]) - hobs
            if prior is not None:
                c, sd, sig = prior
                r = np.r_[r, sig * (th - c) / sd]
            return r
        sol = least_squares(res, np.clip(s, lo + 1e-6, hi - 1e-6), bounds=(lo, hi), x_scale="jac")
        if best is None or sol.cost < best.cost:
            best = sol
    th = best.x; order = np.argsort(th[K:])                          # label cohorts by rate
    return th[:K][order], th[K:][order]
def starts_for(K, rng, n=6):
    S = []
    for _ in range(n):
        eta = np.sort(rng.uniform(0.1, 0.9, K)); w = np.full(K, 0.2 / K) * rng.uniform(0.7, 1.3, K)
        S.append(np.r_[w, eta])
    return S
import sys
RUN1 = "--part1" in sys.argv or "--all" in sys.argv
RUN2 = "--part2" in sys.argv or "--all" in sys.argv
out = json.load(open("/home/claude/papers/recomputed/R_P1_estimators.json")) if __import__("os").path.exists("/home/claude/papers/recomputed/R_P1_estimators.json") else {}
rng = np.random.default_rng(20261020)
# (1) ML at the critical noise level
cases = {"K1_eta0.30": ([0.2], [0.30]), "K2_d0.30": ([0.1, 0.1], [0.25, 0.55]), "K2_d0.20": ([0.1, 0.1], [0.30, 0.50]),
         "K2_d0.10": ([0.1, 0.1], [0.35, 0.45]), "K2_d0.05": ([0.1, 0.1], [0.375, 0.425]),
         "K3_s0.10": ([0.2 / 3] * 3, [0.30, 0.40, 0.50]), "K3_s0.20": ([0.2 / 3] * 3, [0.20, 0.40, 0.60])}
res1 = {}
for nm, (w, e) in (cases.items() if RUN1 else []):
    w = np.array(w); e = np.array(e); K = len(w)
    J = jac(w, e); Finv = np.linalg.inv(J.T @ J); kk = int(np.argmax(np.diag(Finv)[:K])); crb_sd = np.sqrt(Finv[kk, kk])
    sig = (0.01 / 1.96) / crb_sd; h0 = imp(w, e); errs = []
    for _ in range(200):
        hobs = h0 + rng.normal(0, sig, L)
        st = [np.r_[np.full(K, 0.2 / K), np.linspace(0.2, 0.7, K)]] + starts_for(K, rng, 5)   # generic + random starts (never the truth)
        wh, eh = fit(hobs, K, starts=st)
        errs.append(wh - w)
    errs = np.array(errs)
    succ = float(np.mean(np.all(np.abs(errs) <= 0.01, axis=1)))
    rmse_crb = float(np.sqrt(np.mean(errs[:, kk] ** 2)) / (sig * crb_sd))
    res1[nm] = {"sigma_crit": float(sig), "ML_success": succ, "RMSE_over_CRB_worst_weight": rmse_crb}
    print(nm, res1[nm])
if RUN1: out["crb_ml"] = res1
# (2) four estimators on the two-point family, N=50
q, eb, tau, dE, sh, N = 0.20, 0.40, 0.01, 0.10, 1.6e-3, 50
pm, pp = 0.5 - tau / q, 0.5 + tau / q
th0 = (np.array([q * pm, q * pp]), np.array([eb - pp * dE, eb + pm * dE]))
th1 = (np.array([q * pp, q * pm]), np.array([eb - pm * dE, eb + pp * dE]))
center = np.r_[q / 2, q / 2, eb - dE / 2, eb + dE / 2]
sig_avg = sh / np.sqrt(N)
J = jac(*th0); Finv = np.linalg.inv(J.T @ J); var_w = sig_avg ** 2 * np.diag(Finv)[:2]
fails = {m: [0, 0] for m in ("ML", "ridge", "positive_part_shrinkage", "heavy_prior")}
T = 1000
for j, (w, e) in enumerate((th0, th1) if RUN2 else ()):
    h0 = imp(w, e)
    for _ in range(T):
        hobs = h0 + rng.normal(0, sig_avg, L)
        st = [center] + starts_for(2, rng, 3)
        wml, _ = fit(hobs, 2, starts=st)
        wr, _ = fit(hobs, 2, prior=(center, np.r_[0.05, 0.05, 0.10, 0.10], sig_avg), starts=st)
        wh, _ = fit(hobs, 2, prior=(center, np.r_[0.005, 0.005, 0.02, 0.02], sig_avg), starts=st)
        m_ = wml.mean(); d_ = wml - m_; s_ = max(0.0, 1 - var_w.mean() / max(d_ @ d_ / 2, 1e-18)); wjs = m_ + s_ * d_
        for nm, est in (("ML", wml), ("ridge", wr), ("positive_part_shrinkage", wjs), ("heavy_prior", wh)):
            fails[nm][j] += int(np.max(np.abs(est - w)) >= tau)
res2 = None if not RUN2 else {nm: {"fail_theta0": v[0] / T, "fail_theta1": v[1] / T, "worst_case": max(v) / T} for nm, v in fails.items()}
print(res2)
if RUN2: out["lecam_estimators"] = {"N": N, "trials_per_hypothesis": T, "sigma_h": sh, "results": res2,
    "definitions": {"ML": "least squares over (w, eta), 4 starts", "ridge": "MAP with prior sd 0.05 (w), 0.10 (eta) around the symmetric centre",
                    "positive_part_shrinkage": "ML weights shrunk toward their mean, factor (1 - CRB var / spread)_+",
                    "heavy_prior": "MAP with prior sd 0.005 (w), 0.02 (eta)"}}
OUTF = "/home/claude/papers/recomputed/R_P1_estimators_crb.json" if (RUN1 and not RUN2) else "/home/claude/papers/recomputed/R_P1_estimators.json"
if RUN1 and not RUN2: out = {"crb_ml": out["crb_ml"]}
json.dump(out, open(OUTF, "w"), indent=1)

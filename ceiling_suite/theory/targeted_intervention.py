"""Market-wide versus targeted intervention (Paper 1, Proposition prop:target).

Two K-cohort economies built from the K-point Gauss-Legendre and Gauss-Radau rules (as in Theorem thm:kcohort):
same merged moments of order 0..2K-2. Computes the closed-loop persistence S, the largest single-cohort
intensity q_max, the threshold window in which halting the largest cohort restores S <= s_bar in one economy
but not the other, the response distance ||h^A - h^B||_2 and the exact Gaussian-shift sample size for a
decision that is correct with probability >= 3/4 in both economies.
"""
import json, numpy as np
from pathlib import Path
from scipy.stats import norm

def gauss(K):
    x, w = np.polynomial.legendre.leggauss(K); return x, w / w.sum()

def radau(K):
    # left Gauss-Radau: node -1 plus roots of (P_{K-1}+P_K)/(1+x)
    from numpy.polynomial import legendre as L
    c = np.zeros(K + 1); c[K - 1] = 1; c[K] = 1
    roots = np.sort(np.real(L.legroots(c)))
    x = roots  # includes -1
    # weights: exact on polynomials of degree <= 2K-2
    V = np.vstack([x ** m for m in range(K)])
    mom = np.array([(1 - (-1) ** (m + 1)) / (m + 1) for m in range(K)])
    w = np.linalg.solve(V, mom); return x, w / w.sum()

def response(a, kappa, w, r, T=400):
    k = lambda m: np.sum(w * r ** m)
    h = np.zeros(T); h[0] = kappa
    ks = np.array([k(m) for m in range(T)])
    for t in range(1, T):
        h[t] = a * h[t - 1] + kappa * np.dot(ks[:t], h[t - 1::-1][:t])
    return h

out = {"max_normalized_weight": {}}
for K in range(2, 9):
    xg, wg = gauss(K); xr, wr = radau(K)
    assert np.all(wg > 0) and np.all(wr > 0)
    for m in range(2 * K - 1):
        assert abs(np.dot(wg, xg ** m) - np.dot(wr, xr ** m)) < 1e-12
    out["max_normalized_weight"][K] = {"gauss": float(wg.max()), "radau": float(wr.max()),
                                       "gap": float(abs(wg.max() - wr.max()))}

a, kappa, W, rc, sigma = 0.5, 0.8, 0.08, 0.60, 0.01
rows = []
for K in (2, 3):
    for de in (0.20, 0.10, 0.05):
        econ = {}
        for name, (x, om) in {"gauss": gauss(K), "radau": radau(K)}.items():
            r = rc + de * x; w = W * om; q = w / (1 - r)
            S = a + kappa * q.sum()
            assert S < 1
            econ[name] = dict(S=S, qmax=q.max(), post=S - kappa * q.max(), h=response(a, kappa, w, r))
        lo, hi = sorted([econ["gauss"]["post"], econ["radau"]["post"]])
        dh = float(np.linalg.norm(econ["gauss"]["h"] - econ["radau"]["h"]))
        N = (2 * norm.ppf(0.75) * sigma / dh) ** 2
        rows.append(dict(K=K, delta_eta=de, S_gauss=econ["gauss"]["S"], S_radau=econ["radau"]["S"],
                         qmax_gauss=econ["gauss"]["qmax"], qmax_radau=econ["radau"]["qmax"],
                         s_bar_window=[lo, hi], window_width=hi - lo, S_gap=abs(econ["gauss"]["S"] - econ["radau"]["S"]),
                         response_distance=dh, N_decision=N))
out["calibration"] = dict(a=a, kappa=kappa, W=W, r_c=rc, sigma=sigma)
out["rows"] = rows
dst = Path(__file__).resolve().parents[1] / "recomputed" / "R_P1_targeted_intervention.json"
dst.write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=1))

"""Tracking a moving population (Paper 1, core thm:track): numerical check of the rates.

Two groups whose rescaled configuration moves along the moment-matched family R_c (nodes: zeros of
P_2 + c P_1 on [-1,1]; weights exact for degree <= 2), rates r = r_c + d * node, total weight W. The family
parameter drifts linearly, c_t = c0 + v t. Each period gives n reset experiments; the observer sees the first four
kernel taps with noise sd sigma per experiment. A window of m periods is averaged; Prony's method returns the
weights, compared with the true weights at the last period. The window m is chosen on a grid to minimize the
median error (the oracle window of the theory).

Predictions (theorem thm:track, K = 2): weight error ~ (sigma^2 v d^-6 / n)^(1/3): slope 1/3 in v and -2 in d.
For the discounted feedback int (1 - beta r)^-1 dM (a parametric question): error ~ (sigma^2 v / n)^(1/3),
slope 1/3 in v and 0 in d.
Run: python3 tracking_check.py -> tracking_check_results.json"""
import json, math
import numpy as np
from numpy.polynomial import legendre as Lg

rng = np.random.default_rng(20261113)
RC, W, SIGMA, N_PER, BETA, L = 0.5, 0.3, 1.0, 10_000_000, 0.9, 60
C0, REPS = 0.2, 400
WINDOWS = np.unique(np.round(np.logspace(0, 8, 49)).astype(int))


def rule(c):
    coef = np.zeros(3); coef[2] = 1; coef[1] += c
    x = np.sort(Lg.legroots(coef).real)
    V = np.vander(x, 2, increasing=True).T
    w = np.linalg.solve(V, [1.0, 0.0])          # moments of the uniform probability on [-1, 1]
    return x, W * w


def kernel(c, d, T=L):
    x, w = rule(c)
    r = RC + d * x
    return (w[None, :] * r[None, :] ** np.arange(T)[:, None]).sum(1)


def window_mean_kernel(cT, v, m, d):
    # exact average of the kernel over the last m periods, c_t = cT - v j, j = 0..m-1 (Gauss-Legendre in c)
    nodes, wts = Lg.leggauss(20)
    cs = cT - v * (m - 1) * (nodes + 1) / 2
    return sum(wt / 2 * kernel(c, d) for c, wt in zip(cs, wts))


def prony2(k, d):
    # centre at RC and rescale by d, then two-node Prony on the first four moments
    t = np.array([sum(math.comb(p, j) * (-RC) ** (p - j) * k[j] for j in range(p + 1)) / d ** p for p in range(4)])
    H = np.array([[t[0], t[1]], [t[1], t[2]]]); cc = np.linalg.solve(H, -np.array([t[2], t[3]]))
    x = np.sort(np.roots([1.0, cc[1], cc[0]]).real)
    return np.linalg.solve(np.vander(x, 2, increasing=True).T, t[:2])


def run(v, d):
    cT = C0 + 0.3                      # the configuration at the estimation date
    _, wT = rule(cT)
    FT = float((wT / (1 - BETA * (RC + d * rule(cT)[0]))).sum())
    best_w, best_f = np.inf, np.inf
    for m in WINDOWS:
        if v * (m - 1) > 0.5:          # stay inside the family's range
            break
        kbar = window_mean_kernel(cT, v, m, d)
        sd = SIGMA / np.sqrt(N_PER * m)
        ew, ef = [], []
        for _ in range(REPS):
            kh = kbar + sd * rng.standard_normal(L)
            try:
                ew.append(np.max(np.abs(prony2(kh, d) - wT)))
            except Exception:
                ew.append(np.inf)
            ef.append(abs((BETA ** np.arange(L) * kh).sum() - FT))
        best_w = min(best_w, float(np.median(ew))); best_f = min(best_f, float(np.median(ef)))
    return best_w, best_f


out = {"grid_v": [], "grid_d": []}
for v in (1e-7, 1e-6, 1e-5, 1e-4):
    out["grid_v"].append(dict(v=v, d=0.1, **dict(zip(("weights", "discounted_feedback"), run(v, 0.1)))))
for d in (0.2, 0.1, 0.05):
    out["grid_d"].append(dict(v=1e-6, d=d, **dict(zip(("weights", "discounted_feedback"), run(1e-6, d)))))
lv = np.log([r["v"] for r in out["grid_v"]]); ld = np.log([r["d"] for r in out["grid_d"]])
out["slope_weights_v"] = float(np.polyfit(lv, np.log([r["weights"] for r in out["grid_v"]]), 1)[0])
out["slope_feedback_v"] = float(np.polyfit(lv, np.log([r["discounted_feedback"] for r in out["grid_v"]]), 1)[0])
out["slope_weights_d"] = float(np.polyfit(ld, np.log([r["weights"] for r in out["grid_d"]]), 1)[0])
out["slope_feedback_d"] = float(np.polyfit(ld, np.log([r["discounted_feedback"] for r in out["grid_d"]]), 1)[0])
print(json.dumps(out, indent=1))
json.dump(out, open("tracking_check_results.json", "w"), indent=1)

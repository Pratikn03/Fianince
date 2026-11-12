"""Numerical check of the partial-disclosure theorem (Paper 1, thm:partial).

K = 3 groups with memories in r_c + d[-1, 1]. m of them are tagged (their flow responses are recorded with noise);
the untagged K' = K - m form the K'-node Gauss / Gauss-Radau pair, the tagged ones are identical in both economies.
Per-experiment KL divergence of the reset records (price taps and tagged flow taps, Gaussian noise) is computed
exactly from the closed-loop impulse responses. Theory: KL ~ d^(4K'-2), i.e. slopes 10 (m=0), 6 (m=1);
for K' = 1 there is no hard pair and weights are learned at a cost independent of d.
Run: python3 partial_disclosure_check.py -> partial_disclosure_check_results.json
"""
import json
import numpy as np
from fragility_scan import rules

A, KAPPA, RC, T, SIG, SIGF = 0.3, 0.5, 0.5, 60, 1.0, 1.0


def impulse(w, r):
    k = np.array([np.sum(w * r ** m) for m in range(T)])
    h = np.zeros(T); h[0] = KAPPA
    for t in range(1, T):
        h[t] = A * h[t - 1] + KAPPA * np.sum(k[:t] * h[t - 1::-1][:t])
    return h


def flow(wi, ri, h):
    return np.array([wi * np.sum(ri ** (t - np.arange(t + 1)) * h[:t + 1]) for t in range(T)])


def kl_pair(Kp, d, tagged):
    (xg, wg), (xr, wr) = rules(Kp)
    tw = np.array([g[0] for g in tagged]); tr = np.array([RC + d * g[1] for g in tagged])
    out = []
    for x, wq in ((xg, wg), (xr, wr)):
        w = np.concatenate([0.3 * wq, tw]); r = np.concatenate([RC + d * x, tr])
        h = impulse(w, r)
        out.append((h, [flow(wi, ri, h) for wi, ri in zip(tw, tr)]))
    (hA, fA), (hB, fB) = out
    kl = np.sum((hA - hB) ** 2) / (2 * SIG ** 2) + sum(np.sum((a - b) ** 2) for a, b in zip(fA, fB)) / (2 * SIGF ** 2)
    return float(kl)


ds = np.array([0.2, 0.141, 0.1, 0.0707, 0.05])
res = {}
for m, Kp, tagged in ((0, 3, []), (1, 2, [(0.1, 0.3)]), (2, 2, [(0.1, 0.3), (0.1, -0.6)])):
    kls = [kl_pair(Kp, d, tagged) for d in ds]
    slope = float(np.polyfit(np.log(ds), np.log(kls), 1)[0])
    res[f"K={Kp + m}, tagged={m}, untagged={Kp}"] = {"d": ds.tolist(), "kl_per_experiment": kls, "slope": slope,
                                                    "theory": 4 * Kp - 2}
    print(f"K={Kp + m} tagged={m} untagged={Kp}: KL slope {slope:.2f} (theory {4 * Kp - 2})", [f"{k:.2e}" for k in kls])
json.dump(res, open("partial_disclosure_check_results.json", "w"), indent=1)

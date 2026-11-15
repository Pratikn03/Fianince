"""Surveillance-hiding game (Paper 1, core prop:hidegame): numerical illustration.

A group chooses the spacing D in (0, D0] between its memory and its neighbour's. Moving away from its preferred
spacing D0 costs k (D0 - D)^2. Without tags, a supervisor with N observations detects it with probability
pi(N D^6) = Phi(a sqrt(N D^6) - z_{0.95}) (the two-group exponent 4K - 2 = 6); detection costs the group L.
The group minimizes k (D0 - D)^2 + L pi(N D^6). With tags, detection does not depend on D, so D = D0.

Predictions: (a) without tags the group always crowds (D* < D0); (b) when L(1 - pi(0)) > k D0^2 (high stakes),
D* falls at least as fast as N^(-1/6) (fitted: about N^(-1/4)) and the detection probability stays near the
false-alarm level for every N (surveillance without
tags is self-limiting); (c) when k D0^2 > L (low stakes), the group stops hiding once N is large.
Run: python3 hiding_game_check.py -> hiding_game_check_results.json"""
import json
import numpy as np
from scipy.stats import norm

A, Z, D0 = 1.0, norm.ppf(0.95), 0.1
GRID = np.linspace(1e-6, D0, 200001)


def best(N, k, L):
    f = k * (D0 - GRID) ** 2 + L * norm.cdf(A * np.sqrt(N * GRID ** 6) - Z)
    i = int(np.argmin(f))
    return float(GRID[i]), float(norm.cdf(A * np.sqrt(N * GRID[i] ** 6) - Z))


out = {}
for label, k, L in (("high stakes (L = 1, k D0^2 = 0.01)", 1.0, 1.0), ("low stakes (L = 0.005, k D0^2 = 0.01)", 1.0, 0.005)):
    rows = []
    for N in 10.0 ** np.arange(4, 17, 2):
        d, p = best(N, k, L)
        rows.append({"N": N, "D_star": d, "detection": p})
    out[label] = rows
hs = out["high stakes (L = 1, k D0^2 = 0.01)"]
big = [r for r in hs if r["N"] >= 1e10]
out["high_stakes_slope_logD_logN"] = float(np.polyfit(np.log([r["N"] for r in big]), np.log([r["D_star"] for r in big]), 1)[0])
out["high_stakes_max_detection"] = max(r["detection"] for r in hs)
print(json.dumps(out, indent=1))
json.dump(out, open("hiding_game_check_results.json", "w"), indent=1)

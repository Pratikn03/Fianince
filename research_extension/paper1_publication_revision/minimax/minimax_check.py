"""Numerical check of Theorem n:minimax on random economies: for convex losses and convex relabeling-invariant costs,
the uniform policy's loss + cost is at most the worst-labelling loss + cost of any label-based policy."""
import itertools, json
import numpy as np
rng = np.random.default_rng(20261121)
worst_margin, n_cases, strict = np.inf, 0, 0
losses = {"quadratic excess over ceiling": lambda s, sbar: max(s - sbar, 0.0) ** 2,
          "hinge": lambda s, sbar: max(s - sbar, 0.0),
          "exponential": lambda s, sbar: np.exp(3 * (s - sbar))}
costs = {"sum of squares": lambda th: float(np.sum((1 - th) ** 2)),
         "max shortfall": lambda th: float(np.max(1 - th)),
         "zero": lambda th: 0.0}
for K in (2, 3, 4, 5):
    perms = list(itertools.permutations(range(K)))
    for _ in range(400):
        H = rng.normal(0.05, 0.08, K); A = rng.uniform(0.3, 0.9); sbar = rng.uniform(0.6, 1.0)
        th = rng.uniform(0, 1, K); tb = th.mean()
        for ln, L in losses.items():
            for cn, C in costs.items():
                worst = max(L(A + float(np.dot(th, H[list(p)])), sbar) for p in perms) + C(th)
                unif = L(A + tb * H.sum(), sbar) + C(np.full(K, tb))
                worst_margin = min(worst_margin, worst - unif); n_cases += 1
                strict += worst - unif > 1e-12
out = {"cases": n_cases, "min(worst - uniform)": worst_margin, "share strictly better": strict / n_cases,
       "pass": bool(worst_margin >= -1e-12)}
print(json.dumps(out, indent=1))
json.dump(out, open(__file__.replace(".py", "_output.json"), "w"), indent=1)

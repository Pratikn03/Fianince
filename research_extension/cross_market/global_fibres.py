"""Global identification for the pooling theorem. For a configuration x0 = (s, W) (K nodes in [-1, 1], weights in
[0.2, 2], D markets), search for other configurations x with the same rescaled moments t_{j,l}, l <= L, in every
market (up to relabelling). The smallest L at which no other configuration exists is the global order l_g; the global
data exponent is 2 l_g, while the local one is 2 l* with l* = K - 1 + ceil(K/D).
Method: many random starts of a bounded least-squares solve; a solution counts if the residual is below 1e-10 and
it differs from every relabelling of x0 by more than 1e-3."""
import json, math, itertools, sys
import numpy as np
from scipy.optimize import least_squares
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)


def moments(x, K, D, L):
    s = x[:K]; W = x[K:].reshape(D, K)
    return np.array([W[j] @ s ** l for j in range(D) for l in range(L + 1)])


def other_solutions(x0, K, D, L, starts=400):
    target = moments(x0, K, D, L)
    lo = np.r_[-np.ones(K), 0.05 * np.ones(K * D)]; hi = np.r_[np.ones(K), 3 * np.ones(K * D)]
    perms = [np.r_[x0[:K][list(p)], x0[K:].reshape(D, K)[:, list(p)].ravel()] for p in itertools.permutations(range(K))]
    found = []
    for _ in range(starts):
        z0 = rng.uniform(lo, hi)
        r = least_squares(lambda z: moments(z, K, D, L) - target, z0, bounds=(lo, hi), xtol=1e-14, ftol=1e-14, gtol=1e-14)
        if np.max(np.abs(r.fun)) < 1e-10 and min(np.max(np.abs(r.x - p)) for p in perms) > 1e-3:
            if all(np.max(np.abs(r.x - f)) > 1e-4 for f in found):
                found.append(r.x)
    return found


if __name__ == "__main__":
    out = {}
    for K, D in ((2, 2), (3, 2), (3, 3), (4, 2), (4, 4)):
        lstar = K - 1 + math.ceil(K / D)
        res = {}
        for trial in range(3):
            s = np.sort(rng.uniform(-0.9, 0.9, K)); W = rng.uniform(0.4, 1.6, (D, K))
            x0 = np.r_[s, W.ravel()]
            for L in range(lstar, 2 * K):
                n_other = len(other_solutions(x0, K, D, L))
                res.setdefault(L, []).append(n_other)
                if n_other == 0:
                    break
        out[f"{K},{D}"] = {"lstar": lstar, "other_solutions_by_order": res}
        print(f"K={K} D={D} l*={lstar}: other positive configurations by order {res}", flush=True)
    json.dump(out, open("global_fibres_results.json", "w"), indent=1)

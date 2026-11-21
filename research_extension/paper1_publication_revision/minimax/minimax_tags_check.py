"""Numerical check of Theorem n:minimaxtags on random economies with random tag partitions: the group-average policy's
worst-case loss + cost over tag-consistent labellings is at most that of any label policy; the value of tags (best
uniform minus best group policy, worst case over consistent labellings) is nonnegative and positive when groups differ."""
import itertools, json
import numpy as np
rng = np.random.default_rng(20261121)

def consistent_perms(tags):
    K = len(tags)
    return [p for p in itertools.permutations(range(K)) if all(tags[p[c]] == tags[c] for c in range(K))]

def worst(th, H, A, perms, L):
    return max(L(A + float(np.dot(th, H[list(p)]))) for p in perms)

def gavg(th, tags):
    out = np.empty_like(th)
    for g in set(tags):
        idx = [i for i, t in enumerate(tags) if t == g]
        out[idx] = th[idx].mean()
    return out

min_margin, n, values, pos = np.inf, 0, [], 0
for K in (2, 3, 4, 5):
    for _ in range(300):
        tags = list(rng.integers(0, rng.integers(1, K + 1), K))
        perms = consistent_perms(tags)
        H = rng.normal(0.05, 0.08, K); A = rng.uniform(0.3, 0.9); sbar = rng.uniform(0.6, 1.0)
        L = lambda s: max(s - sbar, 0.0) ** 2 * 10
        C = lambda th: float(np.sum((1 - th) ** 2)) * 0.1
        th = rng.uniform(0, 1, K)
        g = gavg(th, tags)
        margin = (worst(th, H, A, perms, L) + C(th)) - (worst(g, H, A, perms, L) + C(g))
        min_margin = min(min_margin, margin); n += 1
        # value of tags on a grid: best uniform vs best group policy (group-wise constant)
        groups = sorted(set(tags))
        grid = np.linspace(0, 1, 11)
        best_u = min(worst(np.full(K, x), H, A, perms, L) + C(np.full(K, x)) for x in grid)
        best_g = np.inf
        for vals in itertools.product(grid, repeat=len(groups)):
            thg = np.array([vals[groups.index(t)] for t in tags])
            best_g = min(best_g, worst(thg, H, A, perms, L) + C(thg))
        values.append(best_u - best_g); pos += (best_u - best_g) > 1e-9
out = {"cases": n, "min(worst(theta) - worst(group average))": min_margin,
       "value of tags: min": min(values), "share positive": pos / n, "pass": bool(min_margin >= -1e-12 and min(values) >= -1e-12)}
print(json.dumps(out, indent=1)); json.dump(out, open(__file__.replace(".py", "_output.json"), "w"), indent=1)

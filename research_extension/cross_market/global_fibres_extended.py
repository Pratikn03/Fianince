"""Extended global search for the pooling theorem (proof check of 12 November 2026).
Same method as global_fibres.py, with 12 random configurations per case instead of 3, and the same 400 starts each.
Reports, for each (K, D), how many configurations have another positive configuration (not a relabelling) sharing
all rescaled moments up to order l*, and, for those, up to order l*+1. Square cases (D divides K) are flagged:
there the system at order l* has as many equations as unknowns, so several solutions can occur generically.
Run: python3 global_fibres_extended.py -> global_fibres_extended_results.json (P1_STOP=4,2 stops after that case)"""
import json, math, os
import numpy as np
import global_fibres as gf   # reuses moments() and other_solutions(); importing runs nothing heavy only if guarded

out = {}
rng = np.random.default_rng(20261112)
gf.rng = rng
CASES = ((2, 2), (3, 2), (3, 3), (4, 2), (4, 4))
STOP = tuple(map(int, os.environ['P1_STOP'].split(','))) if os.environ.get('P1_STOP') else None   # e.g. P1_STOP=4,2
saved = {}
for K, D in CASES:
    lstar = K - 1 + math.ceil(K / D)
    square = D * (lstar + 1) == K * (D + 1)
    hits_l, hits_l1 = 0, 0
    for trial in range(12):
        s = np.sort(rng.uniform(-0.9, 0.9, K)); W = rng.uniform(0.4, 1.6, (D, K))
        x0 = np.r_[s, W.ravel()]
        sol = gf.other_solutions(x0, K, D, lstar)
        if len(sol) > 0:
            hits_l += 1
            sol1 = gf.other_solutions(x0, K, D, lstar + 1) if lstar + 1 <= 2 * K - 1 else []
            hits_l1 += len(sol1) > 0
            saved.setdefault(f"{K},{D}", []).append({"x0": x0.tolist(), "at_lstar": [x.tolist() for x in sol],
                                                     "at_lstar_plus_1": [x.tolist() for x in sol1]})
    out[f"{K},{D}"] = {"lstar": lstar, "square_at_lstar": bool(square), "configurations": 12,
                       "with_other_solution_at_lstar": hits_l, "with_other_solution_at_lstar_plus_1": hits_l1}
    print(K, D, out[f"{K},{D}"], flush=True)
    if STOP == (K, D):
        break
tag = "" if STOP is None else f"_upto_{STOP[0]}_{STOP[1]}"
json.dump(out, open(f"global_fibres_extended_results{tag}.json", "w"), indent=1)
json.dump(saved, open(f"global_fibres_extended_solutions{tag}.json", "w"), indent=1)

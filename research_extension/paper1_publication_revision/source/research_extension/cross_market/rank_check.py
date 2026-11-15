"""Rank check behind the cross-market exponent. With rescaled nodes s and market weights W (K x D), the rescaled
moments t_{j,l} = sum_i W_ij s_i^l. The data exponent is 2 l*, where l* is the smallest power such that the
Jacobian of (t_{j,l}: l <= l*) in (s, W) has full column rank K(D+1). Conjecture: l* = K - 1 + ceil(K/D).
Exact rational arithmetic (sympy) on random rational configurations."""
import json, math, random
import sympy as sp
random.seed(1)
out = {}
for K in range(2, 8):
    for D in range(1, K + 1):
        s = sp.symbols(f"s0:{K}"); W = sp.Matrix(K, D, lambda i, j: sp.Symbol(f"w{i}_{j}"))
        subs = {}
        nodes = sorted(random.sample(range(-50, 51), K))
        for i in range(K): subs[s[i]] = sp.Rational(nodes[i], 50)
        for i in range(K):
            for j in range(D): subs[W[i, j]] = sp.Rational(random.randint(50, 150), 100)
        params = list(s) + [W[i, j] for j in range(D) for i in range(K)]
        lstar = None
        for l in range(0, 2 * K + 1):
            rows = [[sp.diff(sum(W[i, j] * s[i] ** p for i in range(K)), x) for x in params] for j in range(D) for p in range(l + 1)]
            M = sp.Matrix(rows).subs(subs)
            if M.rank() == len(params):
                lstar = l; break
        conj = K - 1 + math.ceil(K / D)
        out[f"{K},{D}"] = {"lstar": lstar, "conjecture": conj}
        print(f"K={K} D={D}: l* = {lstar}, conjecture {conj}, data exponent {2*lstar} (single market {4*K-2})", flush=True)
json.dump(out, open("rank_check_results.json", "w"), indent=1)

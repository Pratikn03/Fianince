"""Exact rank check (rational arithmetic) of the cross-market exponent formula l* = K - 1 + ceil(K/D), built
directly from the Jacobian entries: d t_{j,p}/d s_i = W_ij p s_i^(p-1), d t_{j,p}/d W_ij = s_i^p."""
import json, math, random, sys
import sympy as sp
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
Ks = [int(k) for k in sys.argv[1].split(",")] if len(sys.argv) > 1 else [2, 3, 4, 5, 6, 7]
out = {}
for K in Ks:
    for D in range(1, K + 1):
        s = [sp.Rational(x, 50) for x in sorted(random.sample(range(-50, 51), K))]
        W = [[sp.Rational(random.randint(50, 150), 100) for _ in range(D)] for _ in range(K)]
        lstar = None
        for l in range(K - 1, 2 * K):
            rows = []
            for j in range(D):
                for p in range(l + 1):
                    row = [W[i][j] * p * s[i] ** (p - 1) if p > 0 else sp.Integer(0) for i in range(K)]
                    blk = [sp.Integer(0)] * (K * D)
                    for i in range(K):
                        blk[j * K + i] = s[i] ** p
                    rows.append(row + blk)
            if sp.Matrix(rows).rank() == K * (D + 1):
                lstar = l; break
        conj = K - 1 + math.ceil(K / D)
        out[f"{K},{D}"] = {"lstar": lstar, "conjecture": conj, "match": lstar == conj}
        print(f"K={K} D={D}: l*={lstar} conjecture={conj} {'OK' if lstar == conj else 'MISMATCH'}", flush=True)
json.dump(out, open(f"rank_check_fast_{'_'.join(map(str, Ks))}.json", "w"), indent=1)

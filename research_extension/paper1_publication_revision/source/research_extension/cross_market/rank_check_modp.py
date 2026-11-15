"""Exact verification of condition (R) at order l* = K - 1 + ceil(K/D) by rank modulo a large prime.
Integer nodes and weights; full rank modulo p implies full rank over the rationals (a nonzero maximal minor mod p is
nonzero over Z). Rank deficiency below l* holds for every configuration by counting (fewer rows than columns)."""
import json, math, random, sys
P = 2_147_483_647
random.seed(7)

def rank_mod(M):
    M = [row[:] for row in M]; r = 0; cols = len(M[0])
    for c in range(cols):
        piv = next((i for i in range(r, len(M)) if M[i][c] % P), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], P - 2, P)
        M[r] = [x * inv % P for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % P:
                f = M[i][c]; M[i] = [(a - f * b) % P for a, b in zip(M[i], M[r])]
        r += 1
    return r

out = {}
for K in range(2, 9):
    for D in range(1, K + 1):
        l = K - 1 + math.ceil(K / D)
        s = random.sample(range(-60, 61), K); W = [[random.randint(1, 97) for _ in range(D)] for _ in range(K)]
        rows = []
        for j in range(D):
            for p in range(l + 1):
                row = [W[i][j] * p * s[i] ** (p - 1) if p > 0 else 0 for i in range(K)]
                blk = [0] * (K * D)
                for i in range(K): blk[j * K + i] = s[i] ** p
                rows.append([x % P for x in row + blk])
        full = rank_mod(rows) == K * (D + 1)
        assert D * l < K * (D + 1)  # counting: below l* the differential cannot be injective
        out[f"{K},{D}"] = {"lstar": l, "R_holds_at_lstar": full}
        print(f"K={K} D={D}: l*={l}  condition (R) at l*: {'holds' if full else 'FAILS'}", flush=True)
json.dump(out, open("rank_check_modp_results.json", "w"), indent=1)

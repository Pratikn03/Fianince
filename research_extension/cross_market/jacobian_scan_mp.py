"""High-precision version of jacobian_scan.py: local slopes of sigma_min(J) in d."""
import json
import mpmath as mp
import numpy as np
mp.mp.dps = 60
rng = np.random.default_rng(0)

def smin(K, D, d, W, rc=mp.mpf("0.5"), L=None):
    L = L or 2 * K + 2
    s = [mp.mpf(-1) + 2 * mp.mpf(i) / (K - 1) for i in range(K)]
    r = [rc + d * si for si in s]
    rows = []
    for j in range(D):
        for l in range(L):
            g = [W[i][j] * l * r[i] ** max(l - 1, 0) * d for i in range(K)]
            g += [mp.mpf(0)] * (K * D)
            for i in range(K):
                g[K + j * K + i] = r[i] ** l
            rows.append(g)
    A = mp.matrix(rows)
    return min(mp.svd_r(A, compute_uv=False))

res = {}
for K in (2, 3, 4):
    for D in range(1, K + 1):
        W = [[mp.mpf(str(x)) for x in row] for row in rng.uniform(0.5, 1.5, (K, D))]
        ds = [mp.mpf(1) / 2 ** k for k in range(5, 10)]
        sv = [smin(K, D, d, W) for d in ds]
        loc = [float(mp.log(sv[k + 1] / sv[k]) / mp.log(ds[k + 1] / ds[k])) for k in range(len(ds) - 1)]
        res[f"{K},{D}"] = {"local_slopes": loc, "lstar": K - 1 + -(-K // D)}
        print(f"K={K} D={D}: local slopes {['%.2f' % x for x in loc]} -> data exponent ~{2*loc[-1]:.2f} (single 4K-2={4*K-2})", flush=True)
json.dump(res, open("jacobian_scan_mp_results.json", "w"), indent=1)

"""Exploration: does diversity of participation across markets lower the composition exponent?
K algorithms with common memory rates r_i = rc + d*s_i trade in D markets with market-specific weights W[:, j].
Market j's kernel moments: m_{j,l} = sum_i W[i,j] r_i^l, l = 0..L-1.
We compute the Jacobian of (s, W) -> all moments and its smallest singular value as d -> 0.
Cramer-Rao: data needed for fixed accuracy ~ sigma_min^-2. Single market: sigma_min ~ d^(2K-1)."""
import numpy as np
rng = np.random.default_rng(0)

def jac(K, D, d, rc=0.5, L=None, W=None, s=None):
    L = L or 2 * K + 2
    s = np.linspace(-1, 1, K) if s is None else s
    r = rc + d * s
    rows = []
    for j in range(D):
        for l in range(L):
            g = np.zeros(K + K * D)
            g[:K] = W[:, j] * l * r ** max(l - 1, 0) * d      # d m / d s_i
            g[K + j * K: K + (j + 1) * K] = r ** l           # d m / d W[i, j]
            rows.append(g)
    return np.array(rows)

for K in (2, 3, 4):
    for D in range(1, K + 1):
        W = rng.uniform(0.5, 1.5, (K, D))
        ds = np.array([0.1, 0.05, 0.025, 0.0125])
        sv = [np.linalg.svd(jac(K, D, d, W=W), compute_uv=False)[-1] for d in ds]
        slope = np.polyfit(np.log(ds), np.log(sv), 1)[0]
        print(f"K={K} D={D}: sigma_min slope {slope:.2f}  -> data exponent {2*slope:.2f}  (single-market 4K-2={4*K-2}, guess 4K-2D={4*K-2*D})")

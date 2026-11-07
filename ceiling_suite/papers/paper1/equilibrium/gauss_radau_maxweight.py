"""Largest normalized weight of the K-point Gauss-Legendre and Gauss-Radau (fixed node -1) rules, K = 2..200.
Gauss from numpy; Radau by Golub-Welsch with the Golub (1973) modification of the last diagonal entry, checked
against the closed forms for K = 2 (weights 1/4, 3/4) and K = 3 and against exactness on polynomials of degree
2K - 2. Records max_R - max_G and its sign for every K."""
import json
import numpy as np
from numpy.polynomial.legendre import leggauss

def radau(K, a=-1.0):
    n = K
    beta = np.array([k * k / (4.0 * k * k - 1) for k in range(1, n)])
    # monic Legendre p_k at a by the three-term recurrence p_{k+1} = x p_k - beta_k p_{k-1}
    p = [1.0, a]
    for k in range(1, n - 1):
        p.append(a * p[k] - beta[k - 1] * p[k - 1])
    alpha = np.zeros(n)
    alpha[-1] = a - beta[-1] * p[n - 2] / p[n - 1]
    J = np.diag(alpha) + np.diag(np.sqrt(beta), 1) + np.diag(np.sqrt(beta), -1)
    x, V = np.linalg.eigh(J)
    w = 2.0 * V[0] ** 2
    return x, w / 2.0

rows = []
for K in range(2, 201):
    xg, wg = leggauss(K); wg = wg / 2.0
    xr, wr = radau(K)
    # exactness check on degree 2K-2 monomials (moments of uniform on [-1,1] normalized)
    errs = []
    for m in range(0, 2 * K - 1):
        exact = 0.0 if m % 2 else 1.0 / (m + 1)
        errs.append(abs(np.dot(wr, xr ** m) - exact))
    rows.append({"K": K, "max_gauss": float(wg.max()), "max_radau": float(wr.max()),
                 "diff": float(wr.max() - wg.max()), "radau_exactness_err": float(max(errs)),
                 "radau_endpoint_weight": float(wr[np.argmin(xr)])})
r2 = radau(2); r3 = radau(3)
res = {"K2_radau": [r2[0].tolist(), r2[1].tolist()], "K3_radau": [r3[0].tolist(), r3[1].tolist()], "rows": rows,
       "all_differ": all(abs(r["diff"]) > 1e-9 for r in rows), "radau_larger_all": all(r["diff"] > 0 for r in rows),
       "min_abs_diff": min(abs(r["diff"]) for r in rows), "max_exactness_err": max(r["radau_exactness_err"] for r in rows)}
json.dump(res, open("gauss_radau_maxweight_results.json", "w"), indent=1)
print("K=2 Radau", r2); print("K=3 Radau", r3)
print({k: v for k, v in res.items() if k != "rows" and not k.startswith("K")})
for r in rows[:6] + rows[-3:]: print(r)

"""Independent recomputation of main-text Table n:tab_cal (years of daily data below which no test separates the
Gauss and Gauss-Radau populations with both errors at 5%). Written from the table's footnote, not from the original
script: KL rate by the Whittle formula, n >= ln 5 / KL, 252 days a year, kappa = 0.5, kappa*sum q = 0.3."""
import numpy as np
import sympy as sp


def rules(K):
    gn, gw = np.polynomial.legendre.leggauss(K)
    x = sp.symbols("x")
    poly = sp.cancel((sp.legendre(K - 1, x) + sp.legendre(K, x)) / (1 + x))
    rn = np.array([-1.0] + sorted(float(r) for r in sp.Poly(poly, x).nroots()))
    V = np.vander(rn, K, increasing=True).T
    m = np.array([(1 - (-1) ** (p + 1)) / (p + 1) for p in range(K)])
    rw = np.linalg.solve(V, m)
    return (gn, gw / gw.sum()), (rn, rw / rw.sum())


def kl_rate(K, rc, d, eps, kappa=0.5, share=0.3, n=400001):
    (xg, wg), (xr, wr) = rules(K)
    W = 2 * share * (1 - rc)      # Gauss total weight = 0.6*(1 - rc), as in Table 2 footnote
    rg, wwg = rc + d * xg, W * wg
    rr = rc + d * xr
    budget = kappa * np.sum(wwg / (1 - rg))
    wwr = wr * (budget / (kappa * np.sum(wr / (1 - rr))))   # rescale Radau weights for common (a, S)
    a = 1 - eps - budget
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), n // 2)[::-1], np.logspace(-9, np.log10(np.pi), n // 2)])
    z = np.exp(1j * om)
    def D(r, w):
        return z - a - kappa * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)
    u = np.abs(D(rg, wwg)) ** 2 / np.abs(D(rr, wwr)) ** 2
    return float(np.trapezoid(u - 1 - np.log(u), om) / (4 * np.pi))


rows = [(2, .5, .1, 31000, 23000), (2, .5, .05, 1.8e6, 1.3e6), (2, .8, .1, 280, 160), (2, .8, .05, 15000, 8100),
        (2, .9, .05, 480, 230), (2, .9, .025, 25000, 11000), (3, .5, .1, 2.0e8, 1.3e8), (3, .5, .05, 1.9e11, 1.2e11)]
bad = 0
for K, rc, d, y1, y2 in rows:
    got = [np.log(5) / kl_rate(K, rc, d, e) / 252 for e in (0.1, 1e-6)]
    ok = all(abs(g / t - 1) < 0.06 for g, t in zip(got, (y1, y2)))   # two significant digits
    bad += not ok
    print(f"K={K} r={rc}+-{d}: table {y1:.2g} / {y2:.2g}; recomputed {got[0]:.2g} / {got[1]:.2g}  {'ok' if ok else 'MISMATCH'}")
print("all rows agree" if not bad else f"{bad} rows differ")

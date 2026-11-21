"""Brute-force check of the disclosure-game closed forms (Proposition 'hiding', added 21 November 2026).

Model: H share theta, net values nH<0<nS, H private benefit bH, relabeling cost gamma*z^2/2 per unit of H activity.
Class-tag regime: retention y (H label), x (S label), H routes z = min(1, bH*max(x-y,0)/gamma) through S labels.
W(x,y) = theta*((1-z)*y + z*x)*nH + (1-theta)*x*nS - theta*gamma*z^2/2.
The script maximizes W on a fine grid (and a local refinement) and compares with the closed form.
"""
import itertools
import numpy as np


def W(x, y, th, nH, nS, bH, g):
    z = np.minimum(1.0, bH * np.maximum(x - y, 0) / g)
    return th * ((1 - z) * y + z * x) * nH + (1 - th) * x * nS - th * g * z ** 2 / 2


def brute(th, nH, nS, bH, g, n=801):
    v = np.linspace(0, 1, n)
    X, Y = np.meshgrid(v, v, indexing="ij")
    w = W(X, Y, th, nH, nS, bH, g)
    i = np.unravel_index(np.argmax(w), w.shape)
    x0, y0 = v[i[0]], v[i[1]]
    h = 2.0 / (n - 1)  # refine
    u = np.linspace(-h, h, 201)
    X2, Y2 = np.meshgrid(np.clip(x0 + u, 0, 1), np.clip(y0 + u, 0, 1), indexing="ij")
    w2 = W(X2, Y2, th, nH, nS, bH, g)
    j = np.unravel_index(np.argmax(w2), w2.shape)
    return w2[j], X2[j], Y2[j]


def closed(th, nH, nS, bH, gam):
    a = -nH
    m = th * nH + (1 - th) * nS
    gg = gam / (bH * (2 * a + bH))
    if m >= 0:
        dhat = a * gg
        if dhat <= 1:
            return m + th * a * a * gg / 2, 1.0, 1 - dhat
        return (1 - th) * nS - th / (2 * gg), 1.0, 0.0
    xhat = (1 - th) * nS * gg / th
    if xhat <= 1:
        return ((1 - th) * nS) ** 2 * gg / (2 * th), xhat, 0.0
    return (1 - th) * nS - th / (2 * gg), 1.0, 0.0


rng = np.random.default_rng(20261121)
worst, n = 0.0, 0
for _ in range(400):
    th = rng.uniform(0.05, 0.95); nH = -rng.uniform(0.05, 2); nS = rng.uniform(0.05, 2)
    bH = rng.uniform(0.05, 2); gam = np.exp(rng.uniform(np.log(0.01), np.log(20)))
    wb, xb, yb = brute(th, nH, nS, bH, gam)
    wc, xc, yc = closed(th, nH, nS, bH, gam)
    assert wb <= wc + 1e-9, (th, nH, nS, bH, gam, wb, wc)   # closed form is an upper bound on the grid
    worst = max(worst, wc - wb); n += 1
    # the closed-form policy attains the closed-form value
    assert abs(W(xc, yc, th, nH, nS, bH, gam) - wc) < 1e-12
print(f"{n} random economies: closed form attained, and grid maximum within {worst:.2e} of it")

# properties: V_C increasing in gamma, -> 0 as gamma -> 0, -> V_A as gamma -> infinity, V_C < V_A
for th, nH, nS, bH in [(0.3, -1.0, 0.8, 0.5), (0.7, -1.0, 0.8, 0.5), (0.5, -0.2, 1.5, 1.2)]:
    m = th * nH + (1 - th) * nS
    WN = max(0.0, m); VA = (1 - th) * nS - WN
    gs = np.exp(np.linspace(np.log(1e-4), np.log(1e4), 2000))
    VC = np.array([closed(th, nH, nS, bH, g)[0] - WN for g in gs])
    assert np.all(np.diff(VC) > 0) and VC[0] < 1e-3 * VA and VA - VC[-1] < 1e-3 * VA and np.all(VC < VA)
    print(f"theta={th}: m={m:+.3f}; V_C rises from {VC[0]:.2e} to {VC[-1]:.4f} < V_A={VA:.4f}")
print("all checks pass")


# ---- many classes (Proposition prop:relabelK): three classes, nearest-neighbour channels both ways
def welfare_K(x, th, n, b, cbar, eps):
    K = len(x)
    W = 0.0
    for j in range(K):
        best = (0.0, 0.0, 0.0)  # payoff, gain z*d, cost
        for k in (j - 1, j + 1):
            if 0 <= k < K:
                d = max(x[k] - x[j], 0.0); c = eps * cbar[j][k]
                z = min(1.0, b[j] * d / c) if d > 0 else 0.0
                pay = b[j] * d * z - c * z * z / 2
                if pay > best[0]:
                    best = (pay, z * d, c * z * z / 2)
        W += th[j] * (n[j] * (x[j] + best[1]) - best[2])
    return W


grid = np.linspace(0, 1, 21)
pols = np.array(list(itertools.product(grid, grid, grid)))
for trial in range(30):
    th = rng.dirichlet(np.ones(3)); n = rng.uniform(-1.5, 1.5, 3); b = rng.uniform(0.1, 2, 3)
    cbar = rng.uniform(0.5, 2, (3, 3))
    coarse = max(sum(th[j] * n[j] * max(x[max(j - 1, 0):j + 2]) for j in range(3)) for x in pols)
    WA = sum(th * np.maximum(n, 0))
    for eps in (1e-3, 1e-2, 1e-1):
        WC = max(welfare_K(x, th, n, b, cbar, eps) for x in pols)
        bound = eps * sum(th[j] * (abs(n[j]) / (2 * b[j]) + 0.5) * cbar[j].max() for j in range(3))
        assert abs(WC - coarse) <= bound + 1e-12, ("cheap", trial, eps, WC, coarse, bound)
    for eps in (1e2, 1e3):
        WC = max(welfare_K(x, th, n, b, cbar, eps) for x in pols)
        bound = sum(th[j] * (abs(n[j]) * b[j] + b[j] ** 2) / (eps * cbar[j].min()) for j in range(3))
        assert abs(WC - WA) <= bound + 1e-12, ("expensive", trial, eps, WC, WA, bound)
print("many classes: cheap- and expensive-channel bounds hold on 30 random three-class economies")

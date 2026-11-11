"""Scoping check: does information about trader composition grow as the market approaches instability?
Model of Paper 1: x_t = a x_{t-1} + kappa*sum_i q_i y_{i,t-1} + kappa v_t ; y_{i,t} = (1-eta_i) y_{i,t-1} + eta_i x_t.
Pair: K-group Gauss and Gauss-Radau economies (moments 0..2K-2 equal). Vary the persistence a so that S -> 1.
Measures: (1) active: squared norm of the impulse-response difference, ||h^A - h^B||^2;
          (2) passive: Gaussian KL rate between the two stationary price processes driven by unit innovations.
Fit the exponent of each in (1 - S). Numerical scoping only."""
import json
import numpy as np
from numpy.polynomial import legendre as L

def rules(K):
    xg, wg = L.leggauss(K); wg = wg / 2
    # left Gauss-Radau with node -1 (K nodes), weights by moments
    c = np.zeros(K + 1); c[K - 1] = 1; c[K] = 1           # P_{K-1} + P_K vanishes at -1
    xr = np.sort(np.real(L.legroots(c)))
    V = np.vander(xr, K, increasing=True).T
    mom = np.array([0.0 if m % 2 else 1.0 / (m + 1) for m in range(K)])
    wr = np.linalg.solve(V, mom)
    return (xg, wg), (xr, wr)

def response(a, kappa, r, w, n):
    """impulse response h_t of the price to a unit probe, and transfer H on a grid via FFT of h."""
    q = w / (1 - r); eta = 1 - r
    x = np.zeros(n); y = np.zeros(len(r)); xprev = 0.0
    for t in range(n):
        xt = a * xprev + kappa * np.dot(q, y) + (kappa if t == 0 else 0.0)
        y = (1 - eta) * y + eta * xt
        x[t] = xt; xprev = xt
    return x

def run(K, rc=0.5, dEta=0.1, W=0.3, kappa=0.5):
    (xg, wg), (xr, wr) = rules(K)
    rA, wA = rc + dEta * xg, W * wg; rB, wB = rc + dEta * xr, W * wr
    Ssum = kappa * W / (1 - rc)                            # approx feedback part of S
    out = []
    for gap in [0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625]:
        a = 1 - gap - kappa * np.sum(wA / (1 - rA))
        SA = a + kappa * np.sum(wA / (1 - rA)); SB = a + kappa * np.sum(wB / (1 - rB))
        n = int(60 / gap) + 400
        hA = response(a, kappa, rA, wA, n); hB = response(a, kappa, rB, wB, n)
        act = float(np.sum((hA - hB) ** 2))
        # passive Gaussian KL rate (Whittle): (1/4pi) int (fA/fB - 1 - log(fA/fB)) dw ; f = |H|^2
        m = 1 << int(np.ceil(np.log2(8 * n)))
        HA = np.fft.rfft(hA, m); HB = np.fft.rfft(hB, m)
        ratio = np.abs(HA) ** 2 / np.abs(HB) ** 2
        kl = float(np.mean(ratio - 1 - np.log(ratio)) / 2)
        out.append({"1-S": 1 - SA, "S_B-S_A": SB - SA, "active_sq_norm": act, "passive_kl_rate": kl, "n": n, "a": a})
    g = np.log([o["1-S"] for o in out])
    fa = np.polyfit(g[-4:], np.log([o["active_sq_norm"] for o in out][-4:]), 1)[0]
    fp = np.polyfit(g[-4:], np.log([o["passive_kl_rate"] for o in out][-4:]), 1)[0]
    return out, fa, fp

if __name__ == "__main__":
    res = {}
    for K in (2, 3):
        out, fa, fp = run(K)
        res[K] = {"rows": out, "active_exponent_in_1-S": fa, "passive_exponent_in_1-S": fp}
        print(f"K={K}: active info ~ (1-S)^{fa:.2f}   passive KL rate ~ (1-S)^{fp:.2f}")
        for o in out: print("   1-S=%.5f  dS=%.2e  active=%.3e  passiveKL=%.3e" % (o["1-S"], o["S_B-S_A"], o["active_sq_norm"], o["passive_kl_rate"]))
    json.dump(res, open("fragility_scan_results.json", "w"), indent=1)

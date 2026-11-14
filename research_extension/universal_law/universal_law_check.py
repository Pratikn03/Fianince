"""Universal identification law: numerical check (14 November 2026).

Claim tested. Let each trader type theta have a linear causal rule with kernel taps k_m(theta), smooth in theta.
A population is a measure nu = sum_i w_i delta_{theta_i}; its kernel is sum_i w_i k(theta_i), linear in nu.
For two K-type populations whose type measures match moments below order 2K-1 and have spacing D
(the Gauss / Gauss-Radau pair, rescaled), the kernels and closed-loop responses differ at order D^(2K-1),
so telling them apart needs N of order D^-(4K-2), for ANY smooth family, not only exponential memory.
If the jets k, dk, ..., d^(2K-1)k at the centre are linearly independent, the Fisher information for the
weights has smallest eigenvalue of the same order, so the bound is matched (Cramer-Rao side).

Families (none is exponential memory):
  power : k_m = (m+1)^(-theta)                  (power-law memory, theta = decay exponent)
  hump  : k_m = (m+1) theta^m (1-theta)^2       (hump-shaped memory, theta = location)
  window: k_m = 1/(1+exp((m-theta)/1.5))/theta  (smoothed fixed window of length theta)
"""
import json
import numpy as np
from numpy.polynomial import legendre as Lg
import mpmath as mp

mp.mp.dps = 40
M = 400          # taps
a, kappa, W = 0.3, 0.5, 0.2

def taps(fam, th):
    m = np.arange(M, dtype=float)
    if fam == "power":  return (m + 1.0) ** (-th)
    if fam == "hump":   return (m + 1.0) * th ** m * (1 - th) ** 2
    if fam == "window": return 1.0 / (1.0 + np.exp((m - th) / 1.5)) / th
    raise ValueError

CENTRE = {"power": 2.5, "hump": 0.5, "window": 8.0}
SCALE = {"power": 1.0, "hump": 0.2, "window": 3.0}   # spacing D multiplies this

def gauss(K):
    x, w = Lg.leggauss(K); return x, w / 2
def radau(K):
    c = [0] * (K + 1); c[K - 1] = 1; c[K] = 1
    x = np.sort(np.real(Lg.legroots(c)))
    V = np.vander(x, K, increasing=True).T
    mom = np.array([(1 + (-1) ** j) / (2 * (j + 1)) for j in range(K)])
    return x, np.linalg.solve(V, mom)

def kernel(fam, nodes, wts, D):
    return sum(W * w * taps(fam, CENTRE[fam] + SCALE[fam] * D * s) for s, w in zip(nodes, wts))

def response(k, T=300):
    h = np.zeros(T); h[0] = kappa
    for t in range(1, T):
        h[t] = a * h[t - 1] + kappa * np.dot(k[:t][::-1][:t], h[:t][:min(t, M)]) if t <= M else 0
    return h

def response2(k, T=300):
    h = np.zeros(T); h[0] = kappa
    for t in range(1, T):
        n = min(t, M)
        h[t] = a * h[t - 1] + kappa * np.dot(k[:n], h[t - 1::-1][:n])
    return h

out = {}
Ds = np.array([0.4, 0.2, 0.1, 0.05])
for fam in ("power", "hump", "window"):
    for K in (2, 3):
        gx, gw = gauss(K); rx, rw = radau(K)
        dk, dh = [], []
        for D in Ds:
            kA, kB = kernel(fam, gx, gw, D), kernel(fam, rx, rw, D)
            assert kappa * max(np.abs(kA).sum(), np.abs(kB).sum()) + a < 1, "unstable"
            dk.append(np.linalg.norm(kA - kB)); dh.append(np.linalg.norm(response2(kA) - response2(kB)))
        sk = np.polyfit(np.log(Ds), np.log(dk), 1)[0]; sh = np.polyfit(np.log(Ds), np.log(dh), 1)[0]
        # jets at the centre: numerical derivatives in theta up to order 2K-1, rank and conditioning
        th0 = mp.mpf(CENTRE[fam])
        def tap_mp(th, m):
            if fam == "power":  return (m + 1) ** (-th)
            if fam == "hump":   return (m + 1) * th ** m * (1 - th) ** 2
            return 1 / (1 + mp.e ** ((m - th) / mp.mpf("1.5"))) / th
        J = np.array([[float(mp.diff(lambda t: tap_mp(t, m), th0, j)) for j in range(2 * K)] for m in range(60)])
        J = J / np.linalg.norm(J, axis=0)
        sv = np.linalg.svd(J, compute_uv=False)
        # Cramer-Rao side: Fisher information for (weights, types) from the response; smallest eigenvalue vs D
        lam = []
        for D in Ds:
            th = CENTRE[fam] + SCALE[fam] * D * gx; w = W * gw
            def resp(p):
                return response2(sum(p[i] * taps(fam, p[K + i]) for i in range(K)))
            p0 = np.concatenate([w, th]); cols = []
            for i in range(2 * K):
                e = np.zeros(2 * K); e[i] = 1e-6 * max(1.0, abs(p0[i]))
                cols.append((resp(p0 + e) - resp(p0 - e)) / (2 * e[i]))
            Jr = np.array(cols).T
            F = Jr.T @ Jr
            lam.append(1.0 / np.linalg.inv(F)[0, 0])       # information about the first weight
        sl = np.polyfit(np.log(Ds[:3]), np.log(lam[:3]), 1)[0]
        out[f"{fam}_K{K}"] = {"slope_kernel_gap": float(sk), "slope_response_gap": float(sh), "predicted": 2 * K - 1,
                               "jet_min_singular_value": float(sv[-1]), "jet_rank_full": bool(sv[-1] > 1e-8),
                               "slope_information_for_weight": float(sl), "predicted_information_slope": 4 * K - 2}
out["ok"] = all(abs(v["slope_response_gap"] - v["predicted"]) < 0.35 and v["jet_rank_full"]
                for k, v in out.items() if k != "ok")
json.dump(out, open("universal_law_results.json", "w"), indent=1)
for k, v in out.items(): print(k, v)

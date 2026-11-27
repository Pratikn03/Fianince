"""Numerical check of the passive upper bound (27 November 2026).

One stationary pricing-error record x_t = a x_{t-1} + kappa * sum_j k_j x_{t-1-j} + eps_t from a K = 2 economy with
memory rates r_c + Delta * s_i. Estimator: least squares on L lags (long autoregression), kernel taps from the
coefficients, centred rescaled moments, Prony. Prediction: weight RMSE ~ C * T^(-1/2) * Delta^(-(2K-1)), i.e. slope -3
in log Delta at fixed T and slope -1/2 in log T at fixed Delta.
"""
import json
import sys
from math import comb
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

A, KAPPA, RC, W = 0.1, 1.0, 0.45, 0.2
S_NODES = np.array([-0.5, 0.5])
W_SPLIT = np.array([0.45, 0.55])


def economy(delta):
    r = RC + delta * S_NODES
    w = W * W_SPLIT
    return r, w


def simulate(r, w, T, rng, burn=2000):
    # x (1 - aL - kappa L sum_i w_i/(1 - r_i L)) = eps; clear denominators.
    P = np.array([1.0])
    for ri in r:
        P = np.convolve(P, [1.0, -ri])
    ar = np.convolve(P, [1.0, -A])
    for i, wi in enumerate(w):
        Q = np.array([1.0])
        for j, rj in enumerate(r):
            if j != i:
                Q = np.convolve(Q, [1.0, -rj])
        term = KAPPA * wi * np.concatenate([[0.0], Q])  # L * Q
        ar[:len(term)] -= term
    eps = rng.standard_normal(T + burn)
    return lfilter(P, ar, eps)[burn:]


def long_ar(x, L, chunk=200_000):
    y = x[L:] - A * x[L - 1:-1]
    n = len(y)
    XtX = np.zeros((L, L))
    Xty = np.zeros(L)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        idx = np.arange(s, e)[:, None] + L - 1 - np.arange(L)[None, :]
        X = x[idx]
        XtX += X.T @ X
        Xty += X.T @ y[s:e]
    phi = np.linalg.solve(XtX, Xty)
    return phi / KAPPA  # k_hat_j for j = 0..L-1 (coefficient on x_{t-1-j})


def prony_weights(k, delta, K=2):
    # k_j = sum_l C(j,l) rc^(j-l) delta^l mu_l, mu_l = sum_i w_i s_i^l
    m = np.zeros(2 * K)
    for j in range(2 * K):
        acc = k[j] - sum(comb(j, l) * RC ** (j - l) * delta ** l * m[l] for l in range(j))
        m[j] = acc / delta ** j
    H = np.array([[m[0], m[1]], [m[1], m[2]]])
    c = np.linalg.solve(H, -np.array([m[2], m[3]]))
    s = np.sort(np.roots([1.0, c[1], c[0]]).real)
    V = np.vstack([s ** 0, s ** 1])
    wts = np.linalg.solve(V, m[:2])
    return s, wts


def run(deltas, Ts, reps, L, seed=20261127):
    rng = np.random.default_rng(seed)
    out = []
    for d in deltas:
        r, w = economy(d)
        for T in Ts:
            errs = []
            tap_errs = []
            ktrue = np.array([np.sum(w * r ** j) for j in range(4)])
            for _ in range(reps):
                x = simulate(r, w, T, rng)
                k = long_ar(x, L)
                tap_errs.append(np.max(np.abs(k[:4] - ktrue)))
                try:
                    _, wh = prony_weights(k, d)
                    errs.append(np.max(np.abs(wh - w)))
                except np.linalg.LinAlgError:
                    errs.append(np.inf)
            errs = np.array(errs)
            rmse = float(np.sqrt(np.mean(np.minimum(errs, 1.0) ** 2)))  # capped at 1 for failed solves
            med = float(np.median(errs))
            tap = float(np.median(tap_errs))
            S = A + KAPPA * float(np.sum(w / (1 - r)))
            out.append({'delta': d, 'T': T, 'S': S, 'rmse_maxweight_err': rmse, 'median_err': med, 'median_tap_err': tap})
            print(f"delta={d:.3f} T={T:>9d} S={S:.3f} tap={tap:.3g} rmse={rmse:.4g} median={med:.4g}", flush=True)
    return out


if __name__ == '__main__':
    quick = len(sys.argv) > 1 and sys.argv[1] == 'quick'
    L = 30
    res_d = run([0.7, 0.56, 0.45, 0.36], [1_000_000], 12 if quick else 40, L)
    res_t = run([0.56], [250_000, 1_000_000, 4_000_000], 12 if quick else 40, L)
    ld = np.log([r['delta'] for r in res_d]); le = np.log([r['median_err'] for r in res_d])
    lt = np.log([r['T'] for r in res_t]); lte = np.log([r['median_err'] for r in res_t])
    sd = float(np.polyfit(ld, le, 1)[0]); st = float(np.polyfit(lt, lte, 1)[0])
    lte_tap_d = np.log([r['median_tap_err'] for r in res_d]); lte_tap_t = np.log([r['median_tap_err'] for r in res_t])
    sdt = float(np.polyfit(ld, lte_tap_d, 1)[0]); stt = float(np.polyfit(lt, lte_tap_t, 1)[0])
    print(f"weights: slope in log Delta (theory -3): {sd:.2f}; slope in log T (theory -0.5): {st:.2f}")
    print(f"taps:    slope in log Delta (theory 0): {sdt:.2f}; slope in log T (theory -0.5): {stt:.2f}")
    Path(__file__).with_name('passive_upper_check_results.json').write_text(json.dumps(
        {'params': {'a': A, 'kappa': KAPPA, 'r_c': RC, 'W': W, 's': S_NODES.tolist(), 'split': W_SPLIT.tolist(), 'L': L},
         'by_delta': res_d, 'by_T': res_t, 'slope_log_delta': sd, 'slope_log_T': st,
         'tap_slope_log_delta': sdt, 'tap_slope_log_T': stt}, indent=1))

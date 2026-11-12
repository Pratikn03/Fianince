"""Monte Carlo checks of the upper bounds (estimators attain the rates).

Pipeline as in the proofs: averaged noisy impulse responses (taps) -> kernel by inverting the closed-loop recursion
-> (partial disclosure) tagged groups estimated from their averaged flow records and subtracted -> Prony with the
untagged node count; (pooling) joint least squares over markets with common nodes. Averaging N experiments is
simulated exactly as Gaussian noise of standard deviation sigma / sqrt(N) on each averaged tap.
The weight error should scale like d^-(2K'-1) (partial disclosure, K' untagged) and like d^-l* (pooling,
l* = K - 1 + ceil(K/D)) at fixed N; equivalently the data needed scale like d^-(4K'-2) and d^-2l*.
Run: python3 mc_rates.py -> mc_rates_results.json
"""
import json, math
import numpy as np
from scipy.optimize import least_squares

A, KAP, RC, SIG = 0.3, 0.5, 0.5, 1.0
rng = np.random.default_rng(2026)


def impulse(k, T):
    h = np.zeros(T); h[0] = KAP
    for t in range(T - 1):
        h[t + 1] = A * h[t] + KAP * np.sum(k[:t + 1] * h[t::-1])
    return h


def kernel_from_taps(h, L):
    k = np.zeros(L)
    for t in range(L):
        k[t] = (h[t + 1] - A * h[t] - KAP * np.sum(k[:t] * h[t:0:-1])) / (KAP * h[0])
    return k


def prony(kv, K):
    """Weights and rates of sum_i w_i r_i^m from k_0..k_{2K-1}."""
    H = np.array([[kv[i + j] for j in range(K)] for i in range(K)])
    c = np.linalg.solve(H, -kv[K:2 * K])
    r = np.roots(np.r_[1, c[::-1]]).real
    V = np.vander(r, 2 * K, increasing=True).T
    w = np.linalg.lstsq(V, kv[:2 * K], rcond=None)[0]
    o = np.argsort(r); return w[o], r[o]


def partial_disclosure(K, tagged_idx, d, N, reps=300):
    s = np.linspace(-1, 1, K); r = RC + d * s; w = np.full(K, 0.3 / K)
    untag = [i for i in range(K) if i not in tagged_idx]; Kp = len(untag)
    T = 2 * K + 4
    kern = np.array([np.sum(w * r ** m) for m in range(T)])
    h = impulse(kern, T)
    flows = {i: np.array([w[i] * np.sum(r[i] ** (u - np.arange(u + 1)) * h[:u + 1]) for u in range(T)]) for i in tagged_idx}
    errs = []
    for _ in range(reps):
        hn = h + SIG / math.sqrt(N) * rng.standard_normal(T)
        kv = kernel_from_taps(hn, 2 * Kp + 2)
        for i in tagged_idx:
            fn = flows[i] + SIG / math.sqrt(N) * rng.standard_normal(T)
            X = np.c_[fn[:-1], hn[1:]]; ri, wi = np.linalg.lstsq(X, fn[1:], rcond=None)[0]
            kv = kv - wi * ri ** np.arange(len(kv))
        try:
            we, re = prony(kv, Kp)
            errs.append(np.max(np.abs(we - w[untag])))
        except np.linalg.LinAlgError:
            errs.append(np.nan)
    return float(np.sqrt(np.nanmean(np.square(errs))))


def pooling(K, D, d, N, reps=200):
    s = np.linspace(-1, 1, K); r = RC + d * s
    W = rng.uniform(0.5, 1.5, (D, K)) * 0.3 / K if D > 1 else np.full((1, K), 0.3 / K)
    W = W_fixed[(K, D)]
    T = 2 * K + 4; L = 2 * K
    hs = [impulse(np.array([np.sum(W[j] * r ** m) for m in range(T)]), T) for j in range(D)]
    errs = []
    for _ in range(reps):
        kvs = [kernel_from_taps(hs[j] + SIG / math.sqrt(N) * rng.standard_normal(T), L) for j in range(D)]
        def resid(z):
            rr = RC + d * z[:K]; WW = z[K:].reshape(D, K)
            return np.concatenate([(np.array([WW[j] @ rr ** m for m in range(L)]) - kvs[j]) for j in range(D)])
        z0 = np.r_[s, W.ravel()]
        sol = least_squares(resid, z0, xtol=1e-15, ftol=1e-15, gtol=1e-15)
        errs.append(np.max(np.abs(sol.x[K:] - W.ravel())))
    return float(np.sqrt(np.mean(np.square(errs))))


W_fixed = {(2, 1): np.full((1, 2), 0.15), (2, 2): np.array([[0.10, 0.20], [0.20, 0.10]]),
           (3, 1): np.full((1, 3), 0.1), (3, 3): np.array([[0.05, 0.10, 0.15], [0.15, 0.05, 0.10], [0.10, 0.15, 0.05]])}
out = {"partial_disclosure": {}, "pooling": {}}
ds = np.array([0.2, 0.1, 0.05])
for K, tagged, label in ((3, [], "K=3 untagged=3"), (3, [1], "K=3 untagged=2"), (3, [0, 2], "K=3 untagged=1")):
    N = 1e20 if len(tagged) == 0 else 1e14     # three untagged groups need much less noise to reach the asymptotic regime
    e = [partial_disclosure(K, tagged, d, N) for d in ds]
    sl = float(np.polyfit(np.log(ds), np.log(e), 1)[0])
    Kp = K - len(tagged)
    th = -(2 * Kp - 1) if Kp >= 2 else 0
    out["partial_disclosure"][label] = {"d": ds.tolist(), "rmse": e, "slope": sl, "theory_slope": th}
    print(f"partial disclosure {label}: weight-error slope {sl:.2f} (theory {th})", e, flush=True)
for K, D in ((2, 1), (2, 2), (3, 1), (3, 3)):
    N = 1e20 if (K, D) == (3, 1) else 1e14
    e = [pooling(K, D, d, N) for d in ds]
    sl = float(np.polyfit(np.log(ds), np.log(e), 1)[0])
    lstar = K - 1 + math.ceil(K / D)
    out["pooling"][f"K={K} D={D}"] = {"d": ds.tolist(), "rmse": e, "slope": sl, "theory_slope": -lstar}
    print(f"pooling K={K} D={D}: weight-error slope {sl:.2f} (theory {-lstar})", e, flush=True)
json.dump(out, open("mc_rates_results.json", "w"), indent=1)

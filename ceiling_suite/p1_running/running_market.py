"""Paper 1, numerical check (not a proof, not pre-specified): probing a running market without resets.

The reset benchmark (Theorems 5.3-5.4) averages N independent reset experiments. Here the observer instead sends a
known i.i.d. +/-1 probe into one long stationary run of the same closed loop, which is also driven by its own price
innovations w_t ~ N(0, s_w^2); prices are observed with noise nu_t ~ N(0, s_nu^2). The groups' state is never reset
or known: its free response is part of the noise. The observer estimates taps h_1..h_{2K} by least squares of the
observed price on the current and 200 lagged probe values, then applies the same Prony estimator and the same success
rule as the reset experiments (every weight within 25% of the smallest true weight in at least 75% of 200
replications). T* is the number of periods needed. Because the probe is white and independent of the noise, the
least-squares error is asymptotically Gaussian with covariance Gamma_e / T (Gamma_e the autocovariance of the
residual); T* is computed from that law and the law is checked against direct simulation of long runs.
"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p1_injection"))
from injection_core import economy, impulse, prony_weights, slope

HERE = os.path.dirname(__file__)
a, kappa, W, rc, K = 0.5, 0.8, 0.08, 0.6, 2            # the economy of the injection test (K = 2)
s_nu = 1e-3                                             # observation noise, as in the reset experiments
D_ETA = [0.5, 0.4, 0.32, 0.25, 0.2, 0.16]
LAGS, HLEN, REPS = 200, 800, 200
GRID = np.unique(np.round(2.0 ** (np.arange(130) / 2))).astype(float)
rng = np.random.default_rng(20261031)


def resid_cov(h, s_w):
    """Autocovariance of the regression residual: innovation response (h/kappa)*w, probe tail beyond LAGS, and nu."""
    g = h / kappa
    tail = np.where(np.arange(len(h)) > LAGS, h, 0.0)
    m = 2 * K
    G = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            l = abs(i - j)
            G[i, j] = s_w ** 2 * np.dot(g[:len(g) - l], g[l:]) + np.dot(tail[:len(h) - l], tail[l:]) + (s_nu ** 2 if l == 0 else 0)
    return G


def fail_rate(h, w, C):
    L = np.linalg.cholesky(C)
    hb = np.tile(h[:2 * K + 1], (REPS, 1))
    hb[:, 1:] += rng.standard_normal((REPS, 2 * K)) @ L.T
    hb[:, 0] = kappa
    est = prony_weights(hb, a, kappa, K)
    bad = ~np.isfinite(est).all(axis=1) | (np.nanmax(np.abs(est - w), axis=1) > 0.25 * w.min())
    return float(bad.mean())


def t_star(h, w, Gam):
    fr = []
    for T in GRID:
        fr.append(fail_rate(h, w, Gam / T))
        if len(fr) >= 2 and fr[-2] <= 0.25 and fr[-1] <= 0.25:
            return float(GRID[len(fr) - 2])
    return None


res = {"kind": "numerical check (not pre-specified)", "economy": dict(a=a, kappa=kappa, W=W, rc=rc, K=K),
       "s_nu": s_nu, "lags": LAGS, "d_eta": D_ETA, "arms": {}}
arms = {"reset": None, "running_sw_1x": 1.0, "running_sw_3x": 3.0}
for name, mult in arms.items():
    ns = []
    for de in D_ETA:
        r, w = economy(K, de, rc, W)
        h = impulse(a, kappa, w, r, HLEN)
        Gam = s_nu ** 2 * np.eye(2 * K) if mult is None else resid_cov(h, mult * s_nu)
        ns.append(t_star(h, w, Gam))
        print(name, de, ns[-1], flush=True)
    res["arms"][name] = {"required": ns, "slope": slope(D_ETA, ns),
                         "unit": "reset experiments" if mult is None else "periods of one running market"}
for name in ("running_sw_1x", "running_sw_3x"):
    R, B = res["arms"][name]["required"], res["arms"]["reset"]["required"]
    res["arms"][name]["ratio_to_reset"] = [None if (x is None or y is None) else x / y for x, y in zip(R, B)]

# Validation: simulate long running markets and compare the least-squares error covariance with Gamma_e / T.
de = 0.5; r, w = economy(K, de, rc, W); h = impulse(a, kappa, w, r, HLEN); s_w = s_nu
Tval, nrun = 100_000, 120
errs = []
for _ in range(nrun):
    n = Tval + HLEN + LAGS
    v = rng.choice([-1.0, 1.0], size=n); wv = s_w * rng.standard_normal(n)
    x = np.convolve(v, h)[:n] + np.convolve(wv, h / kappa)[:n] + s_nu * rng.standard_normal(n)
    X = np.column_stack([v[HLEN + LAGS - j: n - j] for j in range(LAGS + 1)]); y = x[HLEN + LAGS:]
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    errs.append(beta[1:2 * K + 1] - h[1:2 * K + 1])
errs = np.array(errs)
pred = resid_cov(h, s_w) / Tval
res["validation"] = {"d_eta": de, "T": Tval, "runs": nrun, "s_w": s_w,
                     "empirical_sd": errs.std(axis=0, ddof=1).tolist(), "predicted_sd": np.sqrt(np.diag(pred)).tolist(),
                     "empirical_mean_bias_over_sd": (errs.mean(axis=0) / errs.std(axis=0, ddof=1)).tolist()}
res["timestamp_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
json.dump(res, open(os.path.join(HERE, "results", "R1_running_market.json"), "w"), indent=2)
print(json.dumps({k: (v["slope"], v.get("ratio_to_reset")) for k, v in res["arms"].items()}, indent=1))
print(json.dumps(res["validation"], indent=1))

"""Simulation power analysis for the Taiwan tagged-flow test (no market data).

Data-generating process: the paper's recursion with price-first ordering,
    x_{t+1} = a x_t + kappa * sum_i u_{i,t} + xi_{t+1},   u_{i,t+1} = r_i u_{i,t} + w_i x_{t+1},
for one tracked class (cohort 1) and one other cohort (cohort 2). Reported flow is u_1 + eps.

Test: the class-flow equation u~_t = r u~_{t-1} + w x_t + e_t, estimated by two-step efficient GMM with lagged
instruments Z_t = (x_{t-1}, x_{t-2}, x_{t-3}) and a Newey-West weight (lag 2). Hansen J ~ chi2(1) under the model.

Scenarios:
  null       : model holds; reporting noise only
  null_shock : model holds plus i.i.d. structural flow shocks (nuisance; lagged instruments stay valid)
  alt_mix    : the class is a merged pair of cohorts with rates r_a, r_b (one exponential memory fails)
  alt_trend  : flow also chases the price change, + phi (x_t - x_{t-1})
"""
import json, sys
import numpy as np

def simulate(T, rng, scen, r=0.8, w=0.3, a=0.6, kappa=-0.15, r2=0.5, w2=0.2, noise=0.5, burn=300):
    n = T + burn
    xi = rng.standard_normal(n)
    x = np.zeros(n); u1 = np.zeros(n); u1b = np.zeros(n); u2 = np.zeros(n)
    shock = rng.standard_normal(n) * (0.5 if scen == "null_shock" else 0.0)
    for t in range(1, n):
        tot = u1[t-1] + u1b[t-1] + u2[t-1]
        x[t] = a * x[t-1] + kappa * tot + xi[t]
        if scen == "alt_mix":
            u1[t] = 0.95 * u1[t-1] + 0.5 * w * x[t]
            u1b[t] = 0.30 * u1b[t-1] + 0.5 * w * x[t]
        elif scen == "alt_trend":
            u1[t] = r * u1[t-1] + w * x[t] + 0.25 * (x[t] - x[t-1])
        else:
            u1[t] = r * u1[t-1] + w * x[t] + shock[t]
        u2[t] = r2 * u2[t-1] + w2 * x[t]
    flow = (u1 + u1b)[burn:]
    sd = flow.std()
    rep = flow + noise * sd * rng.standard_normal(T)
    return x[burn:], rep

def gmm_J(x, u, lags=3, nw=2):
    T = len(x); L = lags
    y = u[L:]; X = np.column_stack([u[L-1:-1], x[L:]])
    Z = np.column_stack([x[L-k:T-k] for k in range(1, L+1)])
    n = len(y)
    def est(W):
        A = X.T @ Z @ W @ Z.T @ X
        b = X.T @ Z @ W @ Z.T @ y
        return np.linalg.solve(A, b)
    W1 = np.linalg.inv(Z.T @ Z / n)
    b1 = est(W1)
    g = Z * (y - X @ b1)[:, None]
    S = g.T @ g / n
    for l in range(1, nw + 1):
        G = g[l:].T @ g[:-l] / n
        S += (1 - l / (nw + 1)) * (G + G.T)
    W2 = np.linalg.inv(S)
    b2 = est(W2)
    gbar = (Z * (y - X @ b2)[:, None]).mean(0)
    J = n * gbar @ W2 @ gbar
    # sandwich SE for r
    D = Z.T @ X / n
    V = np.linalg.inv(D.T @ W2 @ D) / n
    return J, b2, np.sqrt(np.diag(V))

def run(reps, Ts, scens, seed=20261107, **kw):
    from math import erf
    out = []
    crit = 3.841458820694124  # chi2(1) 95%
    for scen in scens:
        for T in Ts:
            rng = np.random.default_rng([seed, Ts.index(T), scens.index(scen)])
            rej = 0; cover = 0; bias = []; fails = 0
            for _ in range(reps):
                x, u = simulate(T, rng, scen, **kw)
                try:
                    J, b, se = gmm_J(x, u)
                except np.linalg.LinAlgError:
                    fails += 1; continue
                rej += J > crit
                if scen in ("null", "null_shock"):
                    r0 = kw.get("r", 0.8)
                    cover += abs(b[0] - r0) <= 1.96 * se[0]
                    bias.append(b[0] - r0)
            m = reps - fails
            out.append({"scenario": scen, "T": T, "reps": reps, "failures": fails,
                        "reject_rate": rej / m, "mc_se": float(np.sqrt((rej / m) * (1 - rej / m) / m)),
                        "coverage_r": (cover / m) if scen in ("null", "null_shock") else None,
                        "bias_r": float(np.mean(bias)) if bias else None, "params": kw})
            print(json.dumps(out[-1]), flush=True)
    return out

if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    Ts = [250, 500, 1000, 1500, 2500]
    res = {}
    for name, kw in {"base": {}, "noisy": {"noise": 1.0}, "persistent": {"r": 0.95}}.items():
        res[name] = run(reps, Ts, ["null", "null_shock", "alt_mix", "alt_trend"], **kw)
    json.dump(res, open("power_results.json", "w"), indent=1)

"""P1A (draft): power simulation for the liquidity-side bridge test of Theorem 4.1(iii). No data is read.

The test asks whether, across Uniswap v3 pool-weeks, liquidity-provider depth depends on the arbitrage population
only through its aggregate response to the pool-CEX basis (Theorem 4.1(iii): the equilibrium depends on the trader
population solely through G). The registered statistic would be the coefficient gamma of a composition measure C
(the concentration of arbitrage volume across addresses) in a two-way fixed-effects regression of log depth on the
aggregate response R, C and controls. Sufficiency predicts gamma = 0; the rule is an equivalence test (TOST) against a
smallest effect of interest delta, with R's own effect as a positive control.

This script simulates pool-week panels in which the truth is known and reports, for each design and estimator:
    P(supportive | gamma = 0)        power: the theory is true and the test says so
    P(supportive | gamma = delta)    size of the equivalence claim at its boundary (should be <= 5%)
    P(contrary  | gamma = 0)         false rejection of a true theory
    P(contrary  | gamma = 2 delta)   power to reject a false theory
under the three threats that matter for this design:
    (a) the aggregate response is estimated with noise (reliability rho of the pool-week estimate), and composition is
        correlated with the true response (psi): naive OLS then loads the response's omitted part onto C;
    (b) depth feeds back on composition in the same week (lambda): simultaneity;
    (c) depth residuals are serially correlated within a pool, and there are few pools (clustering).
Estimators:
    OLS: two-way FE OLS on the average of two half-sample response estimates, pool-clustered standard errors;
    IV:  two-way FE 2SLS. The response from one half-sample is instrumented by the other half-sample's (errors in
         variables). Composition is instrumented by a leave-one-out shift-share of arbitrage bots' activity in OTHER
         pools, with exposures fixed in a pre-period.

Units: depth in log points; R and C have unit standard deviation; beta is the effect of one SD of response on log
depth, delta the smallest composition effect of interest per SD of C.
Run: python power_sim.py   (writes power_sim_results.json; about 10 minutes)
"""
import itertools
import json
import time
from pathlib import Path

import numpy as np

SEED = 20261122
REPS = 400
Z90 = 1.6448536269514722          # one-sided 5% critical value (TOST at 5% = 90% interval)
BETA = 0.30                       # positive control: log depth per SD of aggregate response
DELTA = 0.05                      # smallest composition effect of interest: 5% depth per SD of composition
SIG_EPS = 0.30                    # within-pool residual SD of log depth
PHI_EPS = 0.5                     # AR(1) of depth residuals within a pool
PHI_R = 0.7                       # AR(1) of the true response within a pool
N_BOTS = 15                       # arbitrage bots with pool exposures fixed in a pre-period
PHI_G = 0.8                       # AR(1) of each bot's global activity

DESIGNS = [(20, 52), (30, 104), (40, 104)]                     # (pools, weeks)
RELIAB = [0.6, 0.8, 0.95]                                      # reliability of the pool-week response estimate
PSI = [0.0, 0.5]                                               # corr. of composition with the true response
LAMBDA = [0.0, 0.3]                                            # same-week feedback of depth on composition
PI_ZS = [0.15, 0.3, 0.6]                                       # strength of the shift-share instrument (SD units)
GAMMAS = {"0": 0.0, "delta": DELTA, "2delta": 2 * DELTA}


def ar1(rng, shape, phi):
    """Stationary AR(1) along the last axis with unit variance."""
    e = rng.standard_normal(shape)
    out = np.empty(shape)
    out[..., 0] = e[..., 0]
    s = np.sqrt(1 - phi ** 2)
    for t in range(1, shape[-1]):
        out[..., t] = phi * out[..., t - 1] + s * e[..., t]
    return out


def demean2(x):
    """Two-way (pool, week) within transformation of a balanced P x W array."""
    return x - x.mean(1, keepdims=True) - x.mean(0, keepdims=True) + x.mean()


def simulate(rng, P, W, rho, psi, lam, gamma, PI_Z=0.6):
    # true aggregate response: pool level + AR(1) within pool
    Rstar = 0.5 * rng.standard_normal((P, 1)) + ar1(rng, (P, W), PHI_R)
    Rstar = (Rstar - Rstar.mean()) / Rstar.std()
    # two independent half-sample estimates; the average has reliability rho
    s2 = (1 - rho) / rho * 2.0          # noise variance of each half so that var(avg noise) = (1 - rho)/rho
    R1 = Rstar + np.sqrt(s2) * rng.standard_normal((P, W))
    R2 = Rstar + np.sqrt(s2) * rng.standard_normal((P, W))
    # shift-share instrument: bots' global activity times pre-period exposure, leave-one-out by construction
    expo = rng.dirichlet(np.full(N_BOTS, 0.5), size=P)            # P x B exposures (pre-period)
    g = ar1(rng, (N_BOTS, W), PHI_G)                                # bots' activity in other pools
    Z = expo @ g
    Z = (Z - Z.mean()) / Z.std()
    # composition and depth, solved jointly (simultaneity when lam != 0)
    alpha = 0.8 * rng.standard_normal((P, 1))
    tau = 0.2 * rng.standard_normal((1, W))
    eps = SIG_EPS * ar1(rng, (P, W), PHI_EPS)
    v = rng.standard_normal((P, W))
    a = np.sqrt(max(1 - PI_Z ** 2 - psi ** 2, 0.05))
    base_C = PI_Z * Z + psi * Rstar + a * v                         # composition before feedback from depth
    base_D = alpha + tau + BETA * Rstar + eps
    C = (base_C + lam * base_D) / (1 - lam * gamma)
    D = base_D + gamma * C
    return D, R1, R2, C, Z


def cluster_cov(X, u, P, W):
    """CR1 pool-clustered covariance for the coefficients of X (n x k), residuals u."""
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    Xu = (X * u[:, None]).reshape(P, W, k).sum(1)
    meat = Xu.T @ Xu
    c = P / (P - 1) * (n - 1) / (n - k)
    return c * XtX_inv @ meat @ XtX_inv


def ols(D, R1, R2, C):
    P, W = D.shape
    y = demean2(D).ravel()
    X = np.column_stack([demean2((R1 + R2) / 2).ravel(), demean2(C).ravel()])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    V = cluster_cov(X, y - X @ b, P, W)
    return b, np.sqrt(np.diag(V)), None


def iv(D, R1, R2, C, Z):
    """2SLS: endogenous (R1, C), instruments (R2, Z); pool-clustered covariance."""
    P, W = D.shape
    y = demean2(D).ravel()
    X = np.column_stack([demean2(R1).ravel(), demean2(C).ravel()])
    Zm = np.column_stack([demean2(R2).ravel(), demean2(Z).ravel()])
    PzX = Zm @ np.linalg.lstsq(Zm, X, rcond=None)[0]
    b = np.linalg.lstsq(PzX, y, rcond=None)[0]
    u = y - X @ b
    n, k = X.shape
    A = np.linalg.inv(PzX.T @ PzX)
    Xu = (PzX * u[:, None]).reshape(P, W, k).sum(1)
    V = P / (P - 1) * (n - 1) / (n - k) * A @ (Xu.T @ Xu) @ A
    # first-stage strength for C: partial F of Z (cluster-robust Wald / 1)
    fs = np.linalg.lstsq(Zm, X[:, 1], rcond=None)[0]
    e1 = X[:, 1] - Zm @ fs
    V1 = cluster_cov(Zm, e1, P, W)
    F = fs[1] ** 2 / V1[1, 1]
    return b, np.sqrt(np.diag(V)), F


def verdict(b, se):
    """Registered rule (draft): positive control, then TOST on gamma against +-DELTA, contrary beyond DELTA."""
    beta, gamma = b
    sb, sg = se
    control = abs(beta) > 1.959963984540054 * sb          # two-sided: the bridge does not fix the sign
    if gamma - Z90 * sg > DELTA or gamma + Z90 * sg < -DELTA:
        return "contrary"
    if control and gamma - Z90 * sg > -DELTA and gamma + Z90 * sg < DELTA:
        return "supportive"
    return "inconclusive"


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    t0 = time.time()
    for (P, W), rho, psi, lam, piz in itertools.product(DESIGNS, RELIAB, PSI, LAMBDA, PI_ZS):
        for gname, gamma in GAMMAS.items():
            counts = {"OLS": {"supportive": 0, "contrary": 0, "inconclusive": 0},
                      "IV": {"supportive": 0, "contrary": 0, "inconclusive": 0}}
            se_g = {"OLS": [], "IV": []}
            bias_g = {"OLS": [], "IV": []}
            Fs = []
            for _ in range(REPS):
                D, R1, R2, C, Z = simulate(rng, P, W, rho, psi, lam, gamma, piz)
                b, se, _ = ols(D, R1, R2, C)
                counts["OLS"][verdict(b, se)] += 1
                se_g["OLS"].append(se[1]); bias_g["OLS"].append(b[1] - gamma)
                b, se, F = iv(D, R1, R2, C, Z)
                counts["IV"][verdict(b, se)] += 1
                se_g["IV"].append(se[1]); bias_g["IV"].append(b[1] - gamma)
                Fs.append(F)
            for est in ("OLS", "IV"):
                rows.append({"pools": P, "weeks": W, "reliability": rho, "psi": psi, "lambda": lam, "pi_Z": piz, "gamma": gname,
                             "estimator": est, **{k: v / REPS for k, v in counts[est].items()},
                             "mean_bias_gamma": float(np.mean(bias_g[est])), "median_se_gamma": float(np.median(se_g[est])),
                             "median_first_stage_F": float(np.median(Fs)) if est == "IV" else None})
        print(f"{P}x{W} rho={rho} psi={psi} lam={lam} piZ={piz} done ({time.time() - t0:.0f}s)", flush=True)
    out = {"seed": SEED, "reps": REPS, "params": {"beta": BETA, "delta": DELTA, "sig_eps": SIG_EPS, "phi_eps": PHI_EPS,
                                                  "phi_R": PHI_R, "n_bots": N_BOTS, "phi_g": PHI_G},
           "rows": rows, "seconds": time.time() - t0}
    Path(__file__).with_name("power_sim_results.json").write_text(json.dumps(out, indent=1))
    print("wrote power_sim_results.json")


if __name__ == "__main__":
    main()

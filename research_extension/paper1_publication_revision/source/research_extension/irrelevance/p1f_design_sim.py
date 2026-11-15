"""P1F (forecast irrelevance) design check by simulation, 14 November 2026. DRAFT; nothing registered.

Per symbol, 30-minute bars: fundamental f (random walk), pricing error x, three trader classes.
Class c's flow:  F_c,t = w_c * EMA_c(returns)_{t-1} + u_c,t,   u_c AR(1) with persistence rho_c (exogenous, uninformed)
Price:           x_t = a x_{t-1} + kappa * sum_c F_c,t + noise,   p = f + x,   r_t = p_t - p_{t-1}
Observed:        returns; aggregate taker flow A_t = sum_c F_c,t + noise; class ratios n_c,t = tanh(P_c,t / S) + noise,
                 P_c the class's position (mean-reverting at 0.5% per bar).
Worlds:          NULL      feedback + uninformed exogenous flows (the theory's prediction plus the aggregation channel)
                 PURE      feedback only, exogenous flows share one persistence (no aggregation channel)
                 INFORMED  class 1 also trades on next-bar fundamental news (the theory is false for forecasting)
Pipeline:        pooled panel regression, common coefficients, features standardized per symbol on the training
                 half; train on the first half, test on the second; baseline = price and public-flow features (lags and
                 EMAs at half-lives 2, 8, 32, 128 bars); augmented = baseline + 1-bar change, 8-bar change and detrended level of each class ratio.
                 dR2 = pooled (MSE_base - MSE_aug) / pooled Var(r), 90% one-sided bounds by a test-day block bootstrap.
Verdicts (A2):   'irrelevant' if upper bound < delta;  'relevant' if lower bound > 0 and dR2 >= delta;  else inconclusive.
A1:              out-of-sample R2 of the 8-bar change in class-1 ratio from baseline features < 0.5 in >= 75% of symbols.
A3 (power gate, training half only): inject a synthetic class feature with true dR2 = 2*delta; the pipeline must call it
                 'relevant' in >= 80% of draws, else the test is declared uninformative before the test half is read.
"""
import json, sys
import numpy as np

S_SYM, DAYS, BPD = 30, 60, 48
T = DAYS * BPD; HALF = T // 2
HL = (2, 8, 32, 128)

def ema(z, hl):
    lam = 0.5 ** (1 / hl); out = np.zeros_like(z); acc = np.zeros(z.shape[1:])
    for t in range(z.shape[0]):
        acc = lam * acc + (1 - lam) * z[t]; out[t] = acc
    return out

def simulate(world, nsim, seed, harsh=False, beta_override=None):
    """harsh: Student-t(3) shocks, volatility clustering, and a common market factor across symbols."""
    rng = np.random.default_rng(seed)
    sh = (nsim, S_SYM)
    a, kappa = 0.3, 0.15
    w = np.array([0.25, -0.15, 0.10]); hlc = np.array([2.0, 10.0, 50.0]); lamc = 0.5 ** (1 / hlc)
    rho = np.array([0.3, 0.7, 0.95]) if world != "PURE" else np.array([0.7, 0.7, 0.7])
    su = np.sqrt(1 - rho ** 2)
    beta = 0.45 if world == "INFORMED" else 0.0
    if beta_override is not None and world == "INFORMED": beta = beta_override
    if harsh:
        z = rng.standard_t(3, (T + 1,) + sh) / np.sqrt(3.0)
        common = rng.standard_t(3, (T + 1, nsim, 1)) / np.sqrt(3.0)
        vol = np.ones(sh); vols = np.zeros((T + 1,) + sh)
        for t in range(T + 1):
            vol = np.sqrt(0.05 + 0.90 * vol ** 2 + 0.05 * (z[t - 1] if t else 0) ** 2); vols[t] = vol
        df = vols * (0.8 * z + 0.6 * common) / np.sqrt(0.05 / (1 - 0.95))
    else:
        df = rng.standard_normal((T + 1,) + sh)
    f = np.cumsum(df, axis=0)
    x = np.zeros(sh); u = np.zeros(sh + (3,)); e = np.zeros(sh + (3,)); P = np.zeros(sh + (3,)); p_prev = np.zeros(sh)
    R = np.zeros((T,) + sh); A = np.zeros((T,) + sh); N = np.zeros((T,) + sh + (3,))
    r_prev = np.zeros(sh)
    for t in range(T):
        e = lamc * e + (1 - lamc) * r_prev[..., None]
        u = rho * u + su * rng.standard_normal(sh + (3,))
        F = w * e + u
        F[..., 0] += beta * df[t + 1]
        x = a * x + kappa * F.sum(-1) + 0.3 * rng.standard_normal(sh)
        p = f[t] + x
        r = p - p_prev; p_prev = p; r_prev = r
        P = 0.995 * P + F                       # class positions mean-revert (accounts close out)
        R[t] = r; A[t] = F.sum(-1) + 0.3 * rng.standard_normal(sh)
        N[t] = np.tanh(P / 40.0) + 0.02 * rng.standard_normal(sh + (3,))
    return R, A, N

def features(R, A):
    cols = [R, np.roll(R, 1, 0), np.roll(R, 2, 0), A, np.roll(A, 1, 0), np.roll(A, 2, 0)]
    for hl in HL: cols += [ema(R, hl), ema(A, hl)]
    return np.stack(cols, -1)                              # features at t predict r_{t+1}

def class_features(N):
    """Stationary class features: 1-bar change, 8-bar change, and level minus its 48-bar trailing mean."""
    d1 = N - np.roll(N, 1, 0); d8 = N - np.roll(N, 8, 0); lev = N - ema(N, 48)
    return np.concatenate([d1, d8, lev], -1)

def ols_mse(Xtr, ytr, Xte, yte):
    Xtr = np.column_stack([np.ones(len(Xtr)), Xtr]); Xte = np.column_stack([np.ones(len(Xte)), Xte])
    b = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]; return (yte - Xte @ b) ** 2

def _std(Z, tr):
    mu = Z[tr].mean(0); sd = Z[tr].std(0); sd[sd == 0] = 1.0
    return (Z - mu) / sd

def evaluate(R, A, N, delta, inject=None, rng=None, split=HALF, end=T):
    """Pooled panel regression with common coefficients; every feature and the target standardized per symbol on
    the training rows. Returns verdict, dR2 and the 90% one-sided bounds from a test-day block bootstrap."""
    X = features(R, A); C = class_features(N)
    if inject is not None:
        C = np.concatenate([C, inject[..., None]], -1)
    y = np.roll(R, -1, 0)
    lo, hi = 200, end - 1
    tr = slice(lo, split); te = slice(split, hi)
    Xs = np.stack([_std(X[:, s], tr) for s in range(R.shape[1])], 1)
    Cs = np.stack([_std(C[:, s], tr) for s in range(R.shape[1])], 1)
    ys = np.stack([_std(y[:, s][:, None], tr)[:, 0] for s in range(R.shape[1])], 1)
    def fit(Z):
        Ztr = Z[tr].reshape(-1, Z.shape[-1]); Zte = Z[te]
        Ztr = np.column_stack([np.ones(len(Ztr)), Ztr])
        b = np.linalg.lstsq(Ztr, ys[tr].reshape(-1), rcond=None)[0]
        return (ys[te] - (b[0] + Zte @ b[1:])) ** 2
    nb = fit(Xs); na = fit(np.concatenate([Xs, Cs], -1))
    var = ys[te].var(0)
    d = nb - na; nday = (hi - split) // BPD
    dd = d[:nday * BPD].reshape(nday, BPD, -1).sum((1, 2)); vv = np.full(nday, BPD * var.sum())
    est = dd.sum() / vv.sum()
    rng = rng or np.random.default_rng(0)
    idx = rng.integers(0, nday, (500, nday)); boots = dd[idx].sum(1) / vv[idx].sum(1)
    lob, upb = np.quantile(boots, [0.10, 0.90])
    if upb < delta: v = "irrelevant"
    elif lob > 0 and est >= delta: v = "relevant"
    else: v = "inconclusive"
    return v, float(est), float(lob), float(upb)

def a1(R, A, N):
    X = features(R, A); tgt = np.roll(N[..., 0], -8, 0) - N[..., 0]
    ok = 0
    for s in range(R.shape[1]):
        e = ols_mse(X[200:HALF, s], tgt[200:HALF, s], X[HALF:T - 9, s], tgt[HALF:T - 9, s])
        r2 = 1 - e.mean() / np.var(tgt[HALF:T - 9, s]); ok += r2 < 0.5
    return ok / R.shape[1] >= 0.75

def power_gate(R, A, N, delta, rng, ndraw=40):
    """Uses the training half only: split it in two and inject a feature with dR2 about 2*delta."""
    y = np.roll(R, -1, 0); hits = 0
    for k in range(ndraw):
        sd = np.std(y[200:HALF]); c = np.sqrt(2 * delta) * sd
        z = c * (y - y.mean(0)) / sd + rng.standard_normal(y.shape) * sd
        z[HALF:] = 0.0
        v = evaluate(R, A, N, delta, inject=z, rng=rng, split=(200 + HALF) // 2, end=HALF)[0]
        hits += v == "relevant"
    return hits / ndraw

def robustness(delta, nsim):
    rows = {}
    cases = [("NULL", None, True), ("PURE", None, True), ("INFORMED", 0.45, True),
             ("INFORMED", 0.22, False), ("INFORMED", 0.16, False), ("INFORMED", 0.22, True)]
    for k, (world, b, harsh) in enumerate(cases):
        R, A, N = simulate(world, nsim, 200 + k, harsh=harsh, beta_override=b)
        rng = np.random.default_rng(300 + k); vs, ests = [], []
        for i in range(nsim):
            v, est, lo, hi = evaluate(R[:, i], A[:, i], N[:, i], delta, rng=rng); vs.append(v); ests.append(est)
        key = f"{world}{'' if b is None else ' beta=' + str(b)}{' harsh' if harsh else ''}"
        rows[key] = {"irrelevant": vs.count("irrelevant") / nsim, "relevant": vs.count("relevant") / nsim,
                     "inconclusive": vs.count("inconclusive") / nsim, "mean_dR2": float(np.mean(ests)), "sd_dR2": float(np.std(ests))}
        print(key, rows[key], flush=True)
    return rows

if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[3] == "robust":
    d = float(sys.argv[1]); json.dump(robustness(d, int(sys.argv[2])), open(f"p1f_design_robust_delta{d}.json", "w"), indent=1)
    sys.exit()

if __name__ == "__main__":
    delta = float(sys.argv[1]) if len(sys.argv) > 1 else 0.005
    nsim = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    res = {"delta": delta, "nsim": nsim}
    for world, seed in (("NULL", 11), ("PURE", 12), ("INFORMED", 13)):
        R, A, N = simulate(world, nsim, seed)
        rng = np.random.default_rng(seed + 100)
        vs, ests, a1s, gates = [], [], [], []
        for i in range(nsim):
            v, est, lo, hi = evaluate(R[:, i], A[:, i], N[:, i], delta, rng=rng)
            vs.append(v); ests.append(est); a1s.append(a1(R[:, i], A[:, i], N[:, i]))
            if i < 8: gates.append(power_gate(R[:, i], A[:, i], N[:, i], delta, rng, ndraw=25))
        res[world] = {"irrelevant": vs.count("irrelevant") / nsim, "relevant": vs.count("relevant") / nsim,
                      "inconclusive": vs.count("inconclusive") / nsim, "mean_dR2": float(np.mean(ests)),
                      "sd_dR2": float(np.std(ests)), "A1_pass": float(np.mean(a1s)), "A3_gate_power": float(np.mean(gates))}
        print(world, res[world], flush=True)
    json.dump(res, open(f"p1f_design_sim_delta{delta}.json", "w"), indent=1)

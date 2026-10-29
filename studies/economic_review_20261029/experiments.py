"""Experiments with explicit targets; all new analyses are exploratory.

Synthetic experiments test internal mechanisms and estimator behavior. They do not
identify algorithmic feedback in public market data or establish economic welfare.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

from .models import cumulative_drift, finite_peak_envelope, impulse, state_matrix, uniform_tail, box_admission


def drift_experiment(rng, reps, horizon):
    rows = []
    for eta in [0.005, 0.01, 0.1, 0.5, 1.0]:
        J = state_matrix(.4, 1., [.4], [eta])
        z = np.array([0., .25])
        resolved = np.linalg.solve(np.eye(2) - J, z)[0]
        corrected = cumulative_drift(.4, 1., [.4], [eta], 0., [.25])
        rows.append(dict(case="drift_identity", eta=eta, original_expression=.5,
                         corrected=corrected, resolvent=resolved,
                         identity_error=abs(corrected - resolved)))
    alpha = box_admission(.4, 1., .4, 1., 1., .48, 0., .25)
    for draw in range(reps):
        K = int(rng.integers(1, 6))
        q, eta = .4 * rng.dirichlet(np.ones(K)), rng.uniform(.005, 1., K)
        for level in [.24, alpha, min(1., alpha + .05)]:
            path = finite_peak_envelope(.4, 1., q, eta, 0., .25, .48, horizon, level)
            margin = 1 - .4 - level * .4
            rows.append(dict(case="peak_bound", draw=draw, alpha=level, peak=path.max(),
                             breached=bool(path.max() > 1 + 1e-10),
                             infinite_forced_limit=.48 / margin,
                             horizon=horizon, eta_min=eta.min()))
    return pd.DataFrame(rows)


def ema(x, span):
    return pd.Series(x).ewm(span=span, adjust=False).mean().to_numpy()


def var_fit(x, flow):
    X = np.column_stack([np.ones(len(x)-1), x[:-1], flow[:-1]])
    fit = np.linalg.lstsq(X, np.column_stack([x[1:], flow[1:]]), rcond=None)[0]
    a, b, c, d = fit[1, 0], fit[2, 0], fit[1, 1], fit[2, 1]
    Q = b*c/(1-d) if abs(1-d) > 1e-6 else np.nan
    return a, b, c, d, Q


def filtering_experiment(rng, reps, n):
    rows = []
    for draw in range(reps):
        returns = rng.normal(size=n+500)
        price = np.cumsum(returns)
        for persistence in [0., .8]:
            flow = np.zeros(len(price))
            eps = rng.normal(size=len(price))
            for t in range(1, len(flow)):
                flow[t] = persistence * flow[t-1] + eps[t]
            for span in [15, 31, 61, 121]:
                x = price - ema(price, span)
                a, b, c, d, Q = var_fit(x[500:], flow[500:])
                rows.append(dict(draw=draw, dgp="martingale_independent_flow", flow_ar=persistence,
                                 span=span, mechanical_persistence=1-2/(span+1),
                                 estimated_price_persistence=a, estimated_loop_proxy=Q,
                                 timing="contemporaneously_available_flow"))
        # A distinct structural positive-feedback DGP; fundamental displacement is observed here.
        x, y, flow = np.zeros(n+500), 0., np.zeros(n+500)
        shocks = rng.normal(size=n+500)
        for t in range(1, len(x)):
            flow[t-1] = .25*y
            x[t] = .4*x[t-1] + flow[t-1] + shocks[t]
            y = .7*y + .3*x[t]
        flow[-1] = .25*y
        for obs, value in [("true_displacement", x), ("ema_proxy", x-ema(x, 31))]:
            a, b, c, d, Q = var_fit(value[500:], flow[500:])
            rows.append(dict(draw=draw, dgp="positive_cohort", flow_ar=np.nan, span=31,
                             observation=obs, estimated_price_persistence=a, estimated_loop_proxy=Q,
                             structural_phi=.25))
    return pd.DataFrame(rows)


def information_experiment(rng, reps, horizon):
    rows = []
    sigma, a, kappa, phi = .02, .4, 1., .4
    tail = uniform_tail(a, kappa, phi, .2, horizon)
    for delta in [.1, .05, .025, .0125]:
        h0 = impulse(a, kappa, [phi], [.5], horizon)
        h1 = impulse(a, kappa, [phi/2, phi/2], [.5-delta, .5+delta], horizon)
        distance = np.linalg.norm(h1-h0)
        N95 = int(np.ceil((2*sigma*norm.ppf(.95)/distance)**2))
        for N in [32, 128, 512, 2048]:
            observations = h1 + rng.normal(0, sigma/np.sqrt(N), (reps, horizon))
            # Independent Gaussian tap errors: variance of their sum is H*sigma^2/N.
            estimate = observations.sum(axis=1)
            se = sigma*np.sqrt(horizon/N)
            lower, upper = estimate-norm.ppf(.975)*se, estimate+norm.ppf(.975)*se+tail
            S = kappa/(1-a-kappa*phi)
            error = norm.cdf(-np.sqrt(N)*distance/(2*sigma))
            rows.append(dict(delta=delta, N=N, horizon=horizon, elapsed_observations=N*horizon,
                             known_pair_optimal_error=error, known_pair_N_for_5pct_error=N95,
                             risk_target_single=S, risk_target_split=S,
                             risk_interval_coverage=np.mean((lower <= S)&(S <= upper)),
                             risk_interval_mean_width=np.mean(upper-lower), deterministic_tail=tail,
                             target_note="same-risk witness; not a uniform identification/certification theorem"))
    return pd.DataFrame(rows)


def _episodes(rng, count, horizon, regime):
    phi = rng.uniform(.05, .5, count)
    sigma = rng.uniform(.04, .12, count)
    if regime == "feedback_tracks_volatility":
        sigma = .04 + .16*phi + rng.uniform(0, .015, count)
    if regime == "zero_feedback":
        phi[:] = 0
    x, y, peak = np.zeros(count), np.zeros(count), np.zeros(count)
    for _ in range(horizon):
        u = 3*sigma*rng.uniform(-1, 1, count)
        x = .4*x + phi*y + u
        y = .7*y + .3*x
        peak = np.maximum(peak, abs(x))
    se = .015
    phi_hat = phi + rng.normal(0, se, count)
    phi_up = np.maximum(0., phi_hat+norm.ppf(.975)*se)
    # Inventory control takes the market as given; it does not change phi.
    S_up = np.where(phi_up < .6, 1/np.maximum(.6-phi_up, 1e-12), np.inf)
    B, cap = .2, 1.
    inventories = dict(certificate=np.minimum(cap, B/(3*sigma*S_up)),
                       oracle=np.minimum(cap, B*(.6-phi)/(3*sigma)),
                       static=np.ones(count), volatility=1/sigma,
                       volatility_and_persistence=(.6-phi_hat).clip(.01, .6)/sigma)
    return peak, inventories, phi <= phi_up


def _match_capacity(score, target):
    lo, hi = 0., 1.
    while np.minimum(1, hi*score).mean() < target and hi < 1e12:
        hi *= 2
    for _ in range(70):
        mid = (lo+hi)/2
        if np.minimum(1, mid*score).mean() < target:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def paired_mean_interval(rng, values, bootstrap=500, block=1):
    values = np.asarray(values, dtype=float)
    if len(values) < 2 or block < 1:
        raise ValueError("need observations and a positive block length")
    n = len(values)
    samples = np.empty(bootstrap)
    for b in range(bootstrap):
        starts = rng.integers(0, n, int(np.ceil(n/block)))
        idx = ((starts[:, None]+np.arange(block)) % n).ravel()[:n]
        samples[b] = values[idx].mean()
    return tuple(np.quantile(samples, [.025, .975]))


def benchmarks_experiment(rng, reps, horizon):
    rows = []
    for regime in ["independent_feedback_volatility", "feedback_tracks_volatility", "zero_feedback"]:
        _, train, _ = _episodes(rng, max(100, reps), horizon, regime)
        peak, test, covered = _episodes(rng, reps, horizon, regime)
        target = train["certificate"].mean()
        guard_loss = test["certificate"]*peak
        for policy, score in test.items():
            multiplier = 1. if policy in ["certificate", "oracle"] else _match_capacity(train[policy], target)
            inventory = np.minimum(1., multiplier*score)
            loss = inventory*peak
            ci = paired_mean_interval(rng, loss-guard_loss)
            rows.append(dict(regime=regime, policy=policy, training_capacity_target=target,
                             test_mean_inventory=inventory.mean(), capacity_multiplier=multiplier,
                             mean_loss=loss.mean(), loss_q95=np.quantile(loss,.95),
                             expected_shortfall95=np.sort(loss)[int(.95*reps):].mean(),
                             budget_breach_rate=np.mean(loss>.2),
                             paired_mean_loss_minus_guard_ci_low=ci[0],
                             paired_mean_loss_minus_guard_ci_high=ci[1],
                             certificate_pointwise_phi_coverage=covered.mean(),
                             scope="synthetic reset episodes; fixed inventory; no P&L or welfare claim"))
    return pd.DataFrame(rows)


def coverage_experiment(rng, reps, horizon):
    rows = []
    sigma, N, a, phi, eta_floor = .05, 32, .4, .4, .2
    tail = uniform_tail(a, 1., phi, eta_floor, horizon)
    for setting in ["iid_gaussian", "serially_correlated_tap_errors", "heavy_tailed_t3", "biased_readings", "hidden_slow_memory"]:
        eta = .002 if setting == "hidden_slow_memory" else .3
        h = impulse(a, 1., [phi], [eta], horizon)
        noise = rng.normal(size=(reps, horizon))*sigma/np.sqrt(N)
        if setting == "serially_correlated_tap_errors":
            for t in range(1, horizon):
                noise[:,t] = .8*noise[:,t-1] + np.sqrt(1-.8**2)*noise[:,t]
        elif setting == "heavy_tailed_t3":
            noise = np.zeros((reps,horizon))
            for _ in range(N):
                noise += rng.standard_t(3,(reps,horizon))*sigma/np.sqrt(3)/N
        elif setting == "biased_readings":
            noise -= .001
        estimate = h.sum()+noise.sum(axis=1)
        radius = norm.ppf(.975)*sigma*np.sqrt(horizon/N)
        S = 1/(1-a-phi)
        covered = (estimate-radius<=S)&(S<=estimate+radius+tail)
        p = covered.mean()
        z = norm.ppf(.975)
        center = (p+z*z/(2*reps))/(1+z*z/reps)
        half = z*np.sqrt(p*(1-p)/reps+z*z/(4*reps**2))/(1+z*z/reps)
        rows.append(dict(setting=setting, nominal=.95, coverage=p, mc_ci_low=min(p,max(0.,center-half)),
                         mc_ci_high=max(p,min(1.,center+half)), repetitions=reps, N=N, horizon=horizon,
                         interval_width=2*radius+tail, actual_eta=eta, assumed_eta_floor=eta_floor,
                         guarantee_applicable=setting=="iid_gaussian",
                         note="failure under violated assumptions is a scope diagnostic, not a theorem counterexample"))
    return pd.DataFrame(rows)


def load_market_csv(path):
    df = pd.read_csv(path)
    required = {"timestamp", "market", "price", "signed_flow"}
    if not required <= set(df):
        raise ValueError("CSV needs columns: "+", ".join(sorted(required)))
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True, errors="raise")
    if df[list(required)].isna().any().any() or df.duplicated(["market","timestamp"]).any():
        raise ValueError("missing required values or duplicate market/timestamp")
    for col in ["price","signed_flow"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if not np.isfinite(df[col]).all():
            raise ValueError("nonfinite "+col)
    if (df.price<=0).any():
        raise ValueError("price must be positive")
    for _, group in df.groupby("market",sort=False):
        if not group.timestamp.is_monotonic_increasing:
            raise ValueError("sort each market chronologically before submitting")
        step = group.timestamp.diff().dropna()
        if len(step) and step.nunique() != 1:
            raise ValueError("each market must use regular bars; disclose aggregation and gap handling")
    return df


def market_features(group, window=120, horizon=12):
    group = group.reset_index(drop=True)
    logp = np.log(group.price.to_numpy())
    x, flow = logp-ema(logp,31), group.signed_flow.to_numpy()
    ret = np.r_[np.nan,np.diff(logp)]
    rows = []
    for t in range(window, len(group)-horizon):
        a,b,c,d,Q = var_fit(x[t-window:t+1],flow[t-window:t+1])
        J = np.array([[a,b],[c,d]])
        z = np.array([1.,0.]); gain = 0.
        for _ in range(horizon):
            gain += abs(z[0]); z = J@z
        target = np.max(abs(logp[t+1:t+horizon+1]-logp[t]))
        rows.append(dict(timestamp=group.timestamp.iloc[t], market=group.market.iloc[t],
                         source_row=t, target_end_row=t+horizon, target=target,
                         volatility=np.std(ret[t-window+1:t+1],ddof=1),
                         finite_response_proxy=gain, margin_proxy=1-a-Q))
    return pd.DataFrame(rows)


def _ridge_predict(train, validation, test, cols):
    # Transformations, clipping and standardization use training observations only.
    trainX = train[cols].to_numpy(float)
    low, high = np.quantile(trainX,[.01,.99],axis=0)
    scale = np.std(np.clip(trainX,low,high),axis=0)
    scale[scale<1e-12] = 1.
    mean = np.mean(np.clip(trainX,low,high),axis=0)
    def X(frame):
        return np.column_stack([np.ones(len(frame)),(np.clip(frame[cols].to_numpy(float),low,high)-mean)/scale])
    Xt, Xv, Xe = X(train), X(validation), X(test)
    pen = np.eye(Xt.shape[1]);pen[0,0]=0
    best = None
    for ridge in [1e-4,.01,1.,100.]:
        coef = np.linalg.solve(Xt.T@Xt+ridge*pen,Xt.T@train.target.to_numpy())
        mse = np.mean((Xv@coef-validation.target.to_numpy())**2)
        if best is None or mse<best[0]:best=(mse,coef,ridge)
    return Xe@best[1],best[2]


def real_data_experiment(path, rng, window=120, horizon=12):
    data = load_market_csv(path)
    rows, predictions = [], []
    for market, group in data.groupby("market",sort=False):
        features = market_features(group,window,horizon)
        if features.empty:
            raise ValueError(f"{market}: insufficient history")
        valid = np.isfinite(features[["target","volatility","finite_response_proxy","margin_proxy"]]).all(axis=1)
        if not valid.all():
            raise ValueError(f"{market}: nonfinite features; inspect the input rather than dropping rows silently")
        n = len(features);i,j=int(.6*n),int(.8*n)
        if min(i-horizon,j-i-horizon,n-j)<40:
            raise ValueError(f"{market}: need longer sample for purged train/validation/test")
        train, val, test = features.iloc[:i-horizon],features.iloc[i:j-horizon],features.iloc[j:]
        base, lb = _ridge_predict(train,val,test,["volatility"])
        aug, la = _ridge_predict(train,val,test,["volatility","finite_response_proxy","margin_proxy"])
        y = test.target.to_numpy()
        differences = (y-base)**2-(y-aug)**2
        ci = paired_mean_interval(rng,differences,bootstrap=1000,block=max(horizon,5))
        benchmark = np.mean((y-train.target.mean())**2)
        if benchmark<=0:
            raise ValueError("constant test target; predictive comparison undefined")
        out = test.copy();out["baseline_prediction"]=base;out["augmented_prediction"]=aug
        predictions.append(out)
        rows.append(dict(market=market,train_rows=len(train),validation_rows=len(val),test_rows=len(test),
                         horizon=horizon,purge_rows=horizon,baseline_ridge=lb,augmented_ridge=la,
                         baseline_mse=np.mean((y-base)**2),augmented_mse=np.mean((y-aug)**2),
                         delta_oos_R2_percentage_points=100*differences.mean()/benchmark,
                         paired_mse_improvement=differences.mean(),ci_low=ci[0],ci_high=ci[1],
                         bootstrap_block=max(horizon,5),
                         interpretation="exploratory reduced-form forecast; no structural or causal certificate"))
    return pd.DataFrame(rows), pd.concat(predictions,ignore_index=True)

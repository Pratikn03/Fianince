"""P1B: estimators and simulator for the Korea short-selling ban test (draft, not registered).

One module serves both the simulation check and, if the design passes and is registered, the data run, so the
statistic the simulation evaluates is the statistic the data run computes.

Panel layout: arrays of shape (N stocks, T trading days). NaN marks a day without a valid observation.
  r  daily log return of the stock          m  daily log return of the stock's market index (same shape)
  s  short-selling share of volume (short volume / total volume); NaN when short selling is not allowed
Windows are slices of the day axis.
"""
import numpy as np

LAGS = 5            # outcome: sum of the first 5 autocorrelations; kernel regressor: sum of the last 5 returns
WINSOR = (0.5, 99.5)
MIN_VALID = 0.80    # a stock-window needs at least 80% of the window's trading days valid
VOL_SCALE = True    # standardize each day by a volatility forecast from earlier days (a weighted estimator)


# ----------------------------------------------------------------------------------------------------------------
# Stock-level statistics
# ----------------------------------------------------------------------------------------------------------------
def _winsor_rows(x):
    lo, hi = np.nanpercentile(x, WINSOR, axis=1, keepdims=True)
    return np.clip(x, lo, hi)


def standardized_residual(r, m, w, sector=None):
    """Market- and sector-adjusted, winsorized, standardized daily return in window w (slice). Returns (z, valid_share).

    valid_share counts days with a return and a market return (before the sector step).
    """
    r, m = r[:, w], m[:, w]
    ok = np.isfinite(r) & np.isfinite(m)
    n = ok.sum(1)
    rr, mm = np.where(ok, r, 0.0), np.where(ok, m, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        rbar, mbar = rr.sum(1) / n, mm.sum(1) / n
        cov = (ok * (rr - rbar[:, None]) * (mm - mbar[:, None])).sum(1) / n
        var = (ok * (mm - mbar[:, None]) ** 2).sum(1) / n
        beta = cov / var
    e = np.where(ok, r - rbar[:, None] - beta[:, None] * (m - mbar[:, None]), np.nan)
    e = _winsor_rows(e)
    if sector is not None:  # subtract the leave-one-out mean of the stock's sector (sectors with >= 3 stocks)
        for sec in np.unique(sector):
            idx = np.where(sector == sec)[0]
            if idx.size < 3:
                continue
            blk = e[idx]
            cnt = np.isfinite(blk).sum(0)
            tot = np.nansum(blk, 0)
            with np.errstate(invalid="ignore", divide="ignore"):
                loo = (tot[None, :] - np.nan_to_num(blk)) / (cnt[None, :] - np.isfinite(blk))
            e[idx] = np.where(cnt[None, :] - np.isfinite(blk) >= 2, blk - loo, np.nan)
    if VOL_SCALE:  # divide by a volatility forecast built from earlier days only (EWMA, decay 0.94)
        e = e / _ewma_vol(e)
        e = _winsor_rows(e)
    e = e - np.nanmean(e, 1, keepdims=True)
    z = e / np.nanstd(e, 1, keepdims=True)
    return z, n / r.shape[1]


def _ewma_vol(e, lam=0.94, warm=20):
    """sigma_t from e_{t-1}, e_{t-2}, ...; started at the variance of the first `warm` valid days of the window."""
    N, T = e.shape
    out = np.full((N, T), np.nan)
    v = np.array([np.nanvar(row[np.isfinite(row)][:warm]) if np.isfinite(row).sum() >= 5 else np.nan for row in e])
    for t in range(T):
        out[:, t] = np.sqrt(v)
        x = e[:, t]
        v = np.where(np.isfinite(x), lam * v + (1 - lam) * x ** 2, v)
    return out


def autocorr_sum(z, lags=LAGS):
    """A = sum_{j=1..lags} rho_j, rho_j = sum z_t z_{t-j} / sum z_t^2 over days where both are valid."""
    den = np.nansum(z * z, 1)
    a = np.zeros(z.shape[0])
    for j in range(1, lags + 1):
        a += np.nansum(z[:, j:] * z[:, :-j], 1) / den
    return a


def past_sum(z, lags=LAGS):
    """R_{t-1} = z_{t-1} + ... + z_{t-lags}; NaN unless all are valid."""
    out = np.full_like(z, np.nan)
    acc = np.zeros((z.shape[0], z.shape[1] - lags))
    for j in range(1, lags + 1):
        acc = acc + z[:, lags - j: z.shape[1] - j]
    out[:, lags:] = acc
    return out


def shorting_kernel(s, z):
    """gamma_i: OLS coefficient of the shorting share s_t on (1, R_{t-1}): the class's response to past prices only.

    Positive gamma means short sellers short more after the stock has risen (contrarian). The same-day return is not
    a regressor: it is moved by the same day's short sales, so controlling for it would bias gamma.
    Returns (gamma, se_iid, nobs). The standard error is reported only; no decision uses it.
    """
    R = past_sum(z)
    s = _winsor_rows(s)
    ok = np.isfinite(s) & np.isfinite(R)
    X = np.stack([np.ones_like(z), np.where(ok, R, 0)], -1) * ok[..., None]
    y = np.where(ok, s, 0.0)
    XtX = np.einsum("ntk,ntl->nkl", X, X)
    Xty = np.einsum("ntk,nt->nk", X, y)
    n = ok.sum(1)
    good = n >= 30
    b = np.full((z.shape[0], 2), np.nan)
    b[good] = np.linalg.solve(XtX[good], Xty[good][..., None])[..., 0]
    res = y - np.einsum("ntk,nk->nt", X, np.nan_to_num(b))
    s2 = (ok * res ** 2).sum(1) / np.maximum(n - 2, 1)
    se = np.full(z.shape[0], np.nan)
    se[good] = np.sqrt(s2[good] * np.linalg.inv(XtX[good])[:, 1, 1])
    return b[:, 1], se, n


# ----------------------------------------------------------------------------------------------------------------
# Cross-sectional regressions
# ----------------------------------------------------------------------------------------------------------------
def ols_hc3(y, X):
    """OLS with HC3 standard errors. Returns (coef, se)."""
    ok = np.isfinite(y) & np.isfinite(X).all(1)
    y, X = y[ok], X[ok]
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, XtXi, X)
    u = e / (1 - h)
    V = XtXi @ (X.T * u ** 2) @ X @ XtXi
    return b, np.sqrt(np.diag(V)), ok.sum()


def _z(x):
    return (x - np.nanmean(x)) / np.nanstd(x)


def p_one_sided(t, sign):
    """One-sided p-value for H1: coefficient has the given sign (normal approximation)."""
    from math import erfc, sqrt
    return 0.5 * erfc(sign * t / sqrt(2))


def decide(stats, alpha=0.05):
    """Registered verdict.

    Primary statistic K: slope theta of D_i = A_i(ban) - [A_i(before) + A_i(after)]/2 on the standardized pre-ban
    shorting kernel gamma_i (treated stocks). Theory: removing a contrarian class (gamma > 0) raises A in
    proportion to gamma, and its return lowers A again, so theta > 0. K2 (ban only) and K3 (reinstatement only)
    must agree in sign for a supportive verdict.
    """
    pK = p_one_sided(stats["t_K"], +1)
    if p_one_sided(stats["t_K"], -1) < alpha:
        return "contradicted"
    if pK < alpha and stats["theta_K2"] > 0 and stats["theta_K3"] < 0:
        return "supportive"
    return "inconclusive"


def run_statistics(panel, W):
    """All registered statistics from a panel dict and window dict. Uses no data outside the windows in W."""
    r, m, s = panel["r"], panel["m"], panel["s"]
    treated, kosdaq = panel["treated"], panel["kosdaq"]
    logcap, logturn = panel["logcap"], panel["logturn"]
    sec = panel.get("sector")
    z0a, v0a = standardized_residual(r, m, W["W0a"], sec)
    z0b, v0b = standardized_residual(r, m, W["W0b"], sec)
    z1, v1 = standardized_residual(r, m, W["W1"], sec)
    z2, v2 = standardized_residual(r, m, W["W2"], sec)
    gam, gse, _ = shorting_kernel(s[:, W["W0a"]], z0a)
    A0, A1, A2 = autocorr_sum(z0b), autocorr_sum(z1), autocorr_sum(z2)
    with np.errstate(all="ignore"):
        sbar = np.nanmean(np.where(np.isfinite(s[:, W["W0a"]]), s[:, W["W0a"]], np.nan), 1)
    valid = (v0a >= MIN_VALID) & (v0b >= MIN_VALID) & (v1 >= MIN_VALID) & (v2 >= MIN_VALID)
    T = valid & treated & np.isfinite(gam) & np.isfinite(sbar)
    C = valid & ~treated
    out = {"n_treated": int(T.sum()), "n_control": int(C.sum())}
    g = _z(np.where(T, gam, np.nan))[T]
    ctrl = [_z(np.where(T, sbar, np.nan))[T], logcap[T], logturn[T], kosdaq[T].astype(float)]
    X = np.column_stack([np.ones(T.sum()), g] + ctrl)
    for key, y in [("K", A1 - (A0 + A2) / 2), ("K2", A1 - A0), ("K3", A2 - A1)]:
        b, se, _ = ols_hc3(y[T], X)
        out.update({f"theta_{key}": b[1], f"se_{key}": se[1], f"t_{key}": b[1] / se[1]})
        if key == "K":
            out.update(sbar_K5=b[2], t_K5=b[2] / se[2])
    # K4 (reported): equal magnitude in the two events, theta_K2 + theta_K3 = 0 (conservative s.e.)
    out["t_K4"] = (out["theta_K2"] + out["theta_K3"]) / np.hypot(out["se_K2"], out["se_K3"])
    # K6 (reported): does gamma add to the price-only predictor A(before)?  Theory: yes (class tags are needed)
    X6 = np.column_stack([X, _z(np.where(T, A0, np.nan))[T]])
    b6, se6, _ = ols_hc3((A1 - A0)[T], X6)
    out.update(theta_K6=b6[1], t_K6=b6[1] / se6[1])
    # K1 (reported): difference in differences, treated against controls, with covariates
    TC = T | C
    XD = np.column_stack([np.ones(TC.sum()), treated[TC].astype(float), logcap[TC], logturn[TC],
                          kosdaq[TC].astype(float)])
    bd, sed, _ = ols_hc3((A1 - A0)[TC], XD)
    gbar, gsd = np.nanmean(gam[T]), np.nanstd(gam[T]) / np.sqrt(T.sum())
    out.update(did_K1=bd[1], t_K1=bd[1] / sed[1], gamma_mean=gbar, t_gamma_mean=gbar / gsd,
               gamma_sd=np.nanstd(gam[T]), gamma_se_median=np.nanmedian(gse[T]))
    out = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in out.items()}
    out["verdict"] = decide(out)
    return out


# ----------------------------------------------------------------------------------------------------------------
# Simulator
# ----------------------------------------------------------------------------------------------------------------
PRIOR = dict(  # literature-informed prior values; replaced by the pre-ban calibration before the official runs
    n_treated=300, n_control=300,
    days=dict(W0a=300, W0b=290, gap1=20, W1=330, gap2=22, W2=360, burn=120),
    sbar_logmu=-3.12, sbar_logsd=0.5,       # log of a stock's mean shorting share of volume (mean about 5%)
    gamma_mean=0.002, gamma_sd=0.002,       # shorting-share response per unit of R (R has s.d. about sqrt(5))
    v_cv=0.6, v_ar=0.5,                     # shorting-share noise, s.d. relative to the stock's mean; persistence
    same_day=0.003,                         # same-day response of shorting share to z_t (not a price effect)
    phi_sd=0.01,                            # other classes' feedback per lag (A_other has s.d. about 5*phi_sd)
    garch=(0.08, 0.90), t_df=5,
    sector_n=20, sector_share=0.15, gamma_sector_share=0.3,
    halt_rate=0.01, long_halt_share=0.02,
)


def simulate(rng, P, kappa, confound=0.0, shift_sd=0.0, lag_profile="flat"):
    """One simulated panel. kappa scales the price effect of the shorting class's flow (kappa=0: no effect).

    confound: post-ban change in other classes' feedback per lag that loads on log size, with gamma also loading
      on size (correlation 0.4), so a size-driven change looks like a gamma effect unless controls remove it.
    shift_sd: s.d. of a common post-ban shift for treated stocks (affects K1 only).
    lag_profile: 'flat' (kernel spread over lags 1-5) or 'lag1' (all on lag 1) or 'late' (lags 6-10; outside A).
    """
    d = P["days"]
    NT, NC = P["n_treated"], P["n_control"]
    N = NT + NC
    order = ["burn", "W0a", "W0b", "gap1", "W1", "gap2", "W2"]
    edges = np.cumsum([0] + [d[k] for k in order])
    T = edges[-1]
    W = {k: slice(edges[i], edges[i + 1]) for i, k in enumerate(order)}
    ban, rein = edges[order.index("gap1")], edges[order.index("gap2")]
    treated = np.arange(N) < NT
    kosdaq = rng.random(N) < 0.4
    logcap = np.where(treated, rng.normal(0.6, 0.8, N), rng.normal(-0.6, 0.8, N))
    logturn = 0.5 * logcap + rng.normal(0, 0.8, N)
    sector = rng.integers(0, P["sector_n"], N)
    sec_eff = rng.normal(0, 1, P["sector_n"])[sector]
    zc = (logcap - logcap.mean()) / logcap.std()
    gamma = P["gamma_mean"] + P["gamma_sd"] * (np.sqrt(P["gamma_sector_share"]) * sec_eff
                                               + 0.4 * zc * np.sqrt(1 - P["gamma_sector_share"])
                                               + np.sqrt(max(0.0, 0.84 - P["gamma_sector_share"])) * rng.normal(0, 1, N))
    sbar = np.exp(rng.normal(P["sbar_logmu"], P["sbar_logsd"], N))
    v_sd = P["v_cv"] * sbar
    phi = rng.normal(0, P["phi_sd"], N)
    dphi_ban = confound * zc + (rng.normal(0, shift_sd) if shift_sd else 0.0) * treated
    dphi_rein = -confound * zc
    beta = rng.uniform(0.5, 1.5, N)
    mk = rng.normal(0, 1, T) * 0.8
    secshock = rng.standard_t(P["t_df"], (P["sector_n"], T)) / np.sqrt(P["t_df"] / (P["t_df"] - 2))
    a_g, b_g = P["garch"]
    h = np.ones(N)
    eps_prev = np.zeros(N)
    u = np.zeros((N, T))                         # idiosyncratic return in units of the stock's s.d.
    v = np.zeros(N)
    s = np.full((N, T), np.nan)
    if lag_profile == "flat":
        lw = np.r_[np.ones(LAGS), np.zeros(5)]
    elif lag_profile == "lag1":
        lw = np.r_[LAGS, np.zeros(9)]
    else:
        lw = np.r_[np.zeros(5), np.ones(5)]
    for t in range(T):
        active = np.where(treated, (t < ban) | (t >= rein), t >= rein)
        h = (1 - a_g - b_g) + a_g * eps_prev ** 2 * h + b_g * h
        eps = rng.standard_t(P["t_df"], N) / np.sqrt(P["t_df"] / (P["t_df"] - 2))
        noise = np.sqrt(h) * eps * np.sqrt(1 - P["sector_share"]) + np.sqrt(P["sector_share"]) * secshock[sector, t]
        past = u[:, max(0, t - 10):t][:, ::-1]
        k = past.shape[1]
        Rk = past @ lw[:k] if k else np.zeros(N)
        R5 = past[:, :LAGS].sum(1) if k else np.zeros(N)
        ph = phi + np.where(t >= ban, dphi_ban, 0) + np.where(t >= rein, dphi_rein, 0)
        v = P["v_ar"] * v + np.sqrt(1 - P["v_ar"] ** 2) * v_sd * rng.normal(0, 1, N)
        flow = gamma * Rk + v                    # the class's flow beyond its mean (shorting share units)
        u[:, t] = ph * R5 - kappa * active * flow + noise
        st = sbar + gamma * Rk + P["same_day"] * u[:, t] + v
        s[:, t] = np.where(active, np.clip(st, 0, 1), np.nan)
        eps_prev = eps
    sd = np.exp(rng.normal(np.log(0.022), 0.3, N))
    r = beta[:, None] * mk[None, :] * 0.01 + sd[:, None] * u
    m = np.tile(mk * 0.01, (N, 1))
    halt = rng.random((N, T)) < P["halt_rate"]
    long = rng.random(N) < P["long_halt_share"]
    start = rng.integers(0, T - 200, N)
    for i in np.where(long)[0]:
        halt[i, start[i]:start[i] + 150] = True
    r[halt] = np.nan
    s[halt] = np.nan
    panel = dict(r=r, m=m, s=s, treated=treated, kosdaq=kosdaq, logcap=logcap, logturn=logturn, sector=sector)
    Wuse = {k: W[k] for k in ["W0a", "W0b", "W1", "W2"]}
    truth = dict(theta_per_sd=5 * kappa * np.std(gamma[treated]), gamma=gamma)
    return panel, Wuse, truth


# ----------------------------------------------------------------------------------------------------------------
# Calibration of the simulator from pre-ban data only (windows W0a and W0b end before 6 November 2023)
# ----------------------------------------------------------------------------------------------------------------
def _ac(x, k):
    a, b = x[:, k:], x[:, :-k]
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = np.where(ok, a, 0), np.where(ok, b, 0)
    n = ok.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ma, mb = a.sum(1) / n, b.sum(1) / n
        c = (ok * (a - ma[:, None]) * (b - mb[:, None])).sum(1) / n
        va = (ok * (a - ma[:, None]) ** 2).sum(1) / n
        vb = (ok * (b - mb[:, None]) ** 2).sum(1) / n
        return c / np.sqrt(va * vb)


def _garch_from_acf(ac1, ac5):
    pers = float(np.clip((max(ac5, 1e-4) / max(ac1, 1e-4)) ** 0.25, 0.5, 0.995))
    best, ab = 1e9, (0.05, pers - 0.05)
    for al in np.linspace(0.01, min(0.3, pers - 0.01), 300):
        be = pers - al
        den = 1 - 2 * al * be - be ** 2
        if den <= 0:
            continue
        rho1 = al * (1 - al * be - be ** 2) / den
        if abs(rho1 - ac1) < best:
            best, ab = abs(rho1 - ac1), (float(al), float(be))
    return ab


def _df_from_kurtosis(garch, target, T, grid=(4.5, 5, 6, 7, 8, 10, 15, 30), n=400, seed=20261121):
    rng = np.random.default_rng(seed)
    al, be = garch
    best, out = 1e9, 30.0
    for df in grid:
        h, x = np.ones(n), np.zeros((n, T + 100))
        ep = np.zeros(n)
        for t in range(T + 100):
            h = (1 - al - be) + al * ep ** 2 * h + be * h
            ep = rng.standard_t(df, n) / np.sqrt(df / (df - 2))
            x[:, t] = np.sqrt(h) * ep
        x = _winsor_rows(x[:, 100:])
        k = np.nanmedian(np.mean(x ** 4, 1) / np.mean(x ** 2, 1) ** 2 - 3)
        if abs(k - target) < best:
            best, out = abs(k - target), float(df)
    return out


def calibrate(panel, Wa, Wb, later_days=(329, 373)):
    """Simulator parameters and descriptive statistics from the pre-ban windows Wa (kernel) and Wb (outcome).

    Every quantity uses only the days in Wa and Wb. later_days are calendar estimates of the lengths of W1 and W2;
    they are not read from data.
    """
    r, m, s, sec = panel["r"], panel["m"], panel["s"], panel.get("sector")
    treated = panel["treated"]
    za, va = standardized_residual(r, m, Wa, sec)
    zb, vb = standardized_residual(r, m, Wb, sec)
    valid = (va >= MIN_VALID) & (vb >= MIN_VALID)
    sa = s[:, Wa]
    gam, gse, _ = shorting_kernel(sa, za)
    h = za.shape[1] // 2
    g1, _, _ = shorting_kernel(sa[:, :h], za[:, :h])
    g2, _, _ = shorting_kernel(sa[:, h:], za[:, h:])
    with np.errstate(all="ignore"):
        sbar = np.nanmean(sa, 1)
    ok = valid & treated & np.isfinite(gam) & np.isfinite(g1) & np.isfinite(g2) & (sbar > 0)
    cov12 = float(np.cov(g1[ok], g2[ok])[0, 1])
    gamma_sd = float(np.sqrt(max(cov12, 0.0)))
    if sec is not None and gamma_sd > 0:
        m1, m2 = g1.copy(), g2.copy()
        for q in np.unique(sec[ok]):
            j = ok & (sec == q)
            m1[j], m2[j] = g1[j].mean(), g2[j].mean()
        gshare = float(np.clip(np.cov(m1[ok], m2[ok])[0, 1] / cov12, 0.0, 0.8))
    else:
        gshare = 0.0
    with np.errstate(all="ignore"):
        cv = np.nanstd(sa, 1) / sbar
    Aa, Ab = autocorr_sum(za), autocorr_sum(zb)
    phi_sd = float(np.sqrt(max(np.cov(Aa[ok], Ab[ok])[0, 1], 0.0)) / LAGS)
    zz = zb[ok] ** 2
    ac1, ac5 = float(np.nanmedian(_ac(zz, 1))), float(np.nanmedian(_ac(zz, 5)))
    garch = _garch_from_acf(ac1, ac5)
    # tails: choose the t degrees of freedom whose GARCH-t series, winsorized like the data, matches the median
    # sample excess kurtosis of z in Wb
    with np.errstate(all="ignore"):
        kurt = np.nanmean(zb[ok] ** 4, 1) / np.nanmean(zb[ok] ** 2, 1) ** 2 - 3
    kx = float(np.nanmedian(kurt))
    t_df = _df_from_kurtosis(garch, kx, zb.shape[1])
    # sector common share: mean within-sector correlation of market-adjusted (not sector-adjusted) residuals
    zm, _ = standardized_residual(r, m, Wb, None)
    cors, ns = [], 0
    if sec is not None:
        for q in np.unique(sec[valid]):
            j = np.where(valid & (sec == q))[0]
            if j.size < 3:
                continue
            ns += 1
            C = np.ma.corrcoef(np.ma.masked_invalid(zm[j]))
            cors.append((C.sum() - np.trace(C)) / (j.size * (j.size - 1)))
    sector_share = float(np.clip(np.mean(cors), 0.0, 0.6)) if cors else 0.0
    vt = (va + vb) / 2
    sim = dict(
        n_treated=int(ok.sum()), n_control=int((valid & ~treated).sum()),
        days=dict(W0a=int(za.shape[1]), W0b=int(zb.shape[1]), W1=int(later_days[0]), W2=int(later_days[1])),
        sbar_logmu=float(np.mean(np.log(sbar[ok]))), sbar_logsd=float(np.std(np.log(sbar[ok]))),
        gamma_mean=float(np.mean(gam[ok])), gamma_sd=gamma_sd,
        v_cv=float(np.nanmedian(cv[ok])), v_ar=float(np.nanmedian(_ac(sa[ok], 1))),
        phi_sd=phi_sd, garch=list(garch), t_df=t_df,
        sector_n=int(max(ns, 1)), sector_share=sector_share, gamma_sector_share=gshare,
        halt_rate=float(1 - np.mean(vt[valid])), long_halt_share=float(1 - valid[treated].mean()),
    )
    # descriptive: the pre-ban cross-section of A(W0b) on gamma (theory: slope -theta, if the association is causal)
    g = _z(np.where(ok, gam, np.nan))[ok]
    X = np.column_stack([np.ones(ok.sum()), g, _z(np.where(ok, sbar, np.nan))[ok], panel["logcap"][ok],
                         panel["logturn"][ok], panel["kosdaq"][ok].astype(float)])
    b, se, _ = ols_hc3(Ab[ok], X)
    rep = dict(gamma_mean_t=float(np.mean(gam[ok]) / (np.std(gam[ok]) / np.sqrt(ok.sum()))),
               gamma_hat_sd=float(np.std(gam[ok])), gamma_split_half_cov=cov12,
               gamma_se_median=float(np.nanmedian(gse[ok])), A_split_half_cov=float(np.cov(Aa[ok], Ab[ok])[0, 1]),
               A0_mean=float(np.mean(Ab[ok])), A0_sd=float(np.std(Ab[ok])), zsq_ac1=ac1, zsq_ac5=ac5,
               excess_kurtosis_median=kx, theta_pre=float(b[1]), t_theta_pre=float(b[1] / se[1]),
               implied_theta_per_sd_if_causal=float(-b[1]))
    return sim, rep

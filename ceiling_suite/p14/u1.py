# ============================================================================
# CELL U1 — FUNCTIONS (same code as Part 6, plus the Part 9 volatility benchmarks at the end)
# ============================================================================
FALLBACK = ("BTCUSDT ETHUSDT BNBUSDT XRPUSDT ADAUSDT DOGEUSDT SOLUSDT DOTUSDT LTCUSDT LINKUSDT BCHUSDT TRXUSDT "
            "AVAXUSDT ATOMUSDT ETCUSDT FILUSDT NEARUSDT AAVEUSDT UNIUSDT SANDUSDT MANAUSDT AXSUSDT XLMUSDT ALGOUSDT "
            "VETUSDT EOSUSDT XTZUSDT THETAUSDT ICPUSDT EGLDUSDT CHZUSDT ENJUSDT ZILUSDT KAVAUSDT RUNEUSDT GALAUSDT "
            "CRVUSDT DYDXUSDT 1INCHUSDT COMPUSDT SNXUSDT ZECUSDT DASHUSDT NEOUSDT IOTAUSDT ONTUSDT QTUMUSDT BATUSDT "
            "ZRXUSDT KNCUSDT").split()
def list_bucket_symbols(ds="bookDepth"):
    url0 = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/"
            f"&prefix=data/futures/um/daily/{ds}/")
    syms, marker = [], ""
    for _ in range(20):
        code, raw = _http(url0 + (f"&marker={marker}" if marker else ""), timeout=60)
        if code != 200 or not raw:
            return []
        root = ET.fromstring(raw)
        ns = {"s": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {}
        pref = [e.text for e in (root.findall(".//s:CommonPrefixes/s:Prefix", ns) if ns else root.findall(".//CommonPrefixes/Prefix"))]
        syms += [p.rstrip("/").split("/")[-1] for p in pref]
        trunc = (root.find("s:IsTruncated", ns) if ns else root.find("IsTruncated"))
        if trunc is None or trunc.text != "true" or not pref:
            break
        marker = pref[-1]
    return sorted(set(syms))
EARLY, LATE = "2023-03-10", "2026-06-10"
def span_ok(s):
    return exists("bookDepth", s, EARLY) and exists("bookDepth", s, LATE)
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
           "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
def day_quote_volume(s):
    raw = fetch("klines", s, LIQ_RANK_DATE)
    return np.nan if raw is None else float(read_zip_csv(raw, KL_COLS)["quote_volume"].astype(float).sum())
NEED_BANDS = [-5, -2, -1, 1, 2, 5]
def nice_tick(x):
    """Snap a positive increment to the nearest 1, 2 or 5 x 10^k (exchange tick grids)."""
    if not np.isfinite(x) or x <= 0:
        return np.nan
    e = math.floor(math.log10(x)); m = x / 10 ** e
    c = min([1, 2, 5, 10], key=lambda v: abs(math.log(m / v)))
    return c * 10 ** e
def infer_tick(k):
    v = np.unique(np.round(k[["open", "high", "low", "close"]].astype(float).to_numpy().ravel(), 10))
    dv = np.diff(v); dv = dv[dv > 0]
    return nice_tick(np.quantile(dv, 0.02)) if len(dv) > 5 else np.nan
def validated_snapshots(sym, date, close_by_minute, t0):
    """Validated bookDepth snapshots: DataFrame indexed by second with bid/ask notional at 1,2,5% ($M)."""
    raw = fetch("bookDepth", sym, date)
    if raw is None:
        return None, {"snapshots": 0}
    b = read_zip_csv(raw)
    b["sec"] = to_utc_seconds(b["timestamp"])
    b["percentage"] = pd.to_numeric(b["percentage"], errors="coerce").round().astype("Int64")
    piv_n = b.pivot_table(index="sec", columns="percentage", values="notional", aggfunc="last")
    piv_d = b.pivot_table(index="sec", columns="percentage", values="depth", aggfunc="last")
    n0 = len(piv_n)
    ok = piv_n.reindex(columns=NEED_BANDS).notna().all(axis=1) & piv_d.reindex(columns=NEED_BANDS).notna().all(axis=1)
    piv_n, piv_d = piv_n[ok], piv_d[ok]
    mono = (piv_d[-2] >= piv_d[-1]) & (piv_d[-5] >= piv_d[-2]) & (piv_d[2] >= piv_d[1]) & (piv_d[5] >= piv_d[2])
    minute = ((piv_n.index.to_numpy() - t0) // 60).clip(0, 1439)
    ref = close_by_minute[minute]
    imp_b, imp_a = piv_n[-1] / piv_d[-1], piv_n[1] / piv_d[1]
    price_ok = (np.abs(imp_b / ref - 1) < 0.03) & (np.abs(imp_a / ref - 1) < 0.03)
    sig = piv_n[NEED_BANDS].round(2).astype(str).agg("|".join, axis=1)
    runlen = sig.groupby((sig != sig.shift()).cumsum()).transform("size")
    not_stale = runlen <= 10
    good = mono & price_ok & not_stale
    g = piv_n[good]
    snap = pd.DataFrame({"bid1": g[-1], "ask1": g[1], "bid2": g[-2], "ask2": g[2], "bid5": g[-5], "ask5": g[5]}) / 1e6
    st = {"snapshots": n0, "drop_V1": int((~ok).sum()), "drop_V2": int((~mono).sum()),
          "drop_V3": int((~price_ok).sum()), "drop_V4": int((~not_stale).sum())}
    return snap, st
def build_day(sym, date):
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    idx = np.arange(1440)
    raw = fetch("klines", sym, date)
    if raw is None:
        return None, {"symbol": sym, "date": date, "reason": "no klines"}
    k = read_zip_csv(raw, KL_COLS)
    tick = infer_tick(k)
    k = k.assign(m=(to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(idx)
    out = pd.DataFrame(index=idx)
    out["close"] = k["close"].astype(float).ffill().bfill()
    out["flow"] = (2 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)).fillna(0) / 1e6
    out["vol"] = k["quote_volume"].astype(float).fillna(0) / 1e6
    st = {"symbol": sym, "date": date, "tick": tick}
    snap, s2 = validated_snapshots(sym, date, out["close"].to_numpy(), t0)
    st.update(s2)
    for c in ["bid1", "ask1", "bid2", "ask2", "bid5", "ask5"]:
        out[c] = np.nan
    if snap is not None and len(snap):
        mm = ((snap.index.to_numpy() - t0) // 60).clip(0, 1439)
        sm = snap.assign(m=mm).groupby("m").last().reindex(idx).ffill(limit=2)
        for c in snap.columns:
            out[c] = sm[c].to_numpy()
    st["minute_coverage"] = float(out["bid1"].notna().mean())
    st["depth_day_ok"] = st["minute_coverage"] >= 0.80
    for c in ["oi", "top_pos_ratio", "top_acc_ratio", "acc_ratio", "taker_ratio"]:
        out[c] = np.nan
    raw = fetch("metrics", sym, date)
    if raw is not None:
        mt = read_zip_csv(raw)
        tcol = "create_time" if "create_time" in mt.columns else mt.columns[0]
        mm = ((to_utc_seconds(mt[tcol]) - t0) // 60).clip(0, 1439)
        for c, src, scale in [("oi", "sum_open_interest_value", 1e6),
                              ("top_pos_ratio", "sum_toptrader_long_short_ratio", 1.0),
                              ("top_acc_ratio", "count_toptrader_long_short_ratio", 1.0),
                              ("acc_ratio", "count_long_short_ratio", 1.0),
                              ("taker_ratio", "sum_taker_long_short_vol_ratio", 1.0)]:
            if src in mt.columns:
                s = pd.Series(pd.to_numeric(mt[src], errors="coerce").to_numpy() / scale, index=mm)
                out[c] = s.groupby(level=0).last().reindex(idx).to_numpy()   # 5-min values, not filled
    out["symbol"], out["date"] = sym, date
    return out, st
MIN_DIR = os.path.join(XDATA, "minute")
def get_day(sym, date):
    d_ = os.path.join(MIN_DIR, sym); os.makedirs(d_, exist_ok=True)
    pq, js = os.path.join(d_, f"{date}.parquet"), os.path.join(d_, f"{date}.json")
    if os.path.exists(js):
        st = json.load(open(js))
        return (pd.read_parquet(pq) if os.path.exists(pq) else None), st
    df, st = build_day(sym, date)
    if df is not None:
        df.to_parquet(pq)
    json.dump(_clean(st), open(js, "w"))
    return df, st
def prep(df, flow_scale):
    p = np.log(df["close"].to_numpy()) * 1e4
    u = df["flow"].to_numpy() / flow_scale
    tot = (df["bid1"] + df["ask1"]).to_numpy()
    d = ((df["bid1"] - df["ask1"]) / (df["bid1"] + df["ask1"])).to_numpy()
    x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy()
    return p, u, d, x, tot
def ols(y, X):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 20:
        return None
    return np.linalg.lstsq(np.column_stack([np.ones(ok.sum()), X[ok]]), y[ok], rcond=None)[0][1:]
def impulse_t6(a, phi, kappa, r, eps, eta, q, L=120):
    x = np.zeros(L); dd = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        tot = (1.0 if t == 0 else 0.0) + f[t]
        x[t] = (a * x[t - 1] + phi * dd[t - 1] if t else 0) + kappa * tot
        dd[t] = ((1 - r) * dd[t - 1] if t else 0) + eps * tot
        if abs(x[t]) > 1e9:
            return np.full(L, np.nan)
    return x
def fit_t6(p, u, d, x):
    dp = np.diff(p, prepend=np.nan)
    bp = ols(dp[1:], np.column_stack([u[1:], d[:-1], x[:-1]]))
    bd = ols(d[1:], np.column_stack([d[:-1], u[1:]]))
    bm = ols(u[1:], np.column_stack([u[:-1], x[:-1]]))
    if bp is None or bd is None or bm is None:
        return None
    kappa, phi, a = bp[0], bp[1], 1 + bp[2]
    r, eps, eta = 1 - bd[0], bd[1], 1 - bm[0]
    q = bm[1] / eta if abs(eta) > 1e-6 else np.nan
    h = impulse_t6(a, phi, kappa, r, eps, eta, q)
    ok = np.all(np.isfinite(h)) and abs(h[0]) > 1e-12
    return {"kappa": kappa, "phi": phi, "a": a, "r": r, "eps": eps, "eta": eta, "q": q,
            "C2": phi * eps - (1 - a) * kappa, "C3": phi * eps + kappa ** 2 * eta * q - (1 - a) * kappa,
            "peak_ratio": float(np.max(h) / h[0]) if ok else np.nan, "peak_minute": int(np.argmax(h)) if ok else -1}
def loop_gain(p, u, span=30):
    x = p - pd.Series(p).ewm(span=span, adjust=False).mean().to_numpy()
    f = np.roll(u, -1)[:-1]; x = x[:-1]
    Z = np.column_stack([x, f])
    Y, X = Z[1:], np.column_stack([np.ones(len(Z) - 1), Z[:-1]])
    ok = np.all(np.isfinite(Y), 1) & np.all(np.isfinite(X), 1)
    if ok.sum() < 100:
        return np.nan
    J = np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0][1:].T
    return float(J[0, 1] * J[1, 0] / (1 - J[1, 1])) if abs(1 - J[1, 1]) > 1e-9 else np.nan
def auc_(y, s):
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    rk = stats.rankdata(np.concatenate([pos, neg]))
    return (rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
def cw_test(y, fb, ff, lags=6):
    adj = (y - fb) ** 2 - ((y - ff) ** 2 - (fb - ff) ** 2)
    m = adj.mean(); e = adj - m; n = len(adj)
    lrv = e @ e / n + 2 * sum((1 - l / (lags + 1)) * (e[l:] @ e[:-l]) / n for l in range(1, lags + 1))
    t_ = m / np.sqrt(lrv / n)
    return float(t_), float(1 - stats.norm.cdf(t_))
def design(D, cols, syms):
    X = [np.ones(len(D))] + [D[c].to_numpy() for c in cols] + [(D["symbol"] == s).to_numpy(float) for s in syms[1:]]
    return np.column_stack(X)
def evaluate(sub, outcome, cand):
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    lo, hi = A0[cand].quantile([0.01, 0.99]); A0["cand_w"] = A0[cand].clip(lo, hi); B0["cand_w"] = B0[cand].clip(lo, hi)
    need = CTRL + ["cand_w", outcome]
    A = A0.dropna(subset=need); B = B0.dropna(subset=need).sort_values(["date", "symbol", "hour"])
    if len(A) < 200 or len(B) < 200 or A[outcome].std() < 1e-8 or A["cand_w"].std() < 1e-8:
        return {"skipped": "too few blocks or no variation in outcome/candidate", "n_train": len(A), "n_test": len(B),
                "clark_west_p": np.nan, "delta_r2": np.nan, "delta_r2_ci": [np.nan, np.nan]}
    B = B[B["symbol"].isin(set(A["symbol"]))]
    syms = sorted(A["symbol"].unique()); y = B[outcome].to_numpy()
    bb = np.linalg.lstsq(design(A, CTRL, syms), A[outcome].to_numpy(), rcond=None)[0]
    bf = np.linalg.lstsq(design(A, CTRL + ["cand_w"], syms), A[outcome].to_numpy(), rcond=None)[0]
    fb = design(B, CTRL, syms) @ bb; ff = design(B, CTRL + ["cand_w"], syms) @ bf
    ybar = A[outcome].mean(); sst = np.sum((y - ybar) ** 2)
    t_, p_ = cw_test(y, fb, ff)
    tail = (y > A[outcome].quantile(0.9)).astype(int)
    Rb = rng(88); dd = B["date"].to_numpy(); ud = np.unique(dd)
    pos = {d: np.where(dd == d)[0] for d in ud}; dR2, dA = [], []
    for _ in range(2000):
        idx = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])
        s_ = np.sum((y[idx] - ybar) ** 2)
        dR2.append((np.sum((y[idx] - fb[idx]) ** 2) - np.sum((y[idx] - ff[idx]) ** 2)) / s_)
        dA.append(auc_(tail[idx], ff[idx]) - auc_(tail[idx], fb[idx]))
    return {"n_train": len(A), "n_test": len(B), "n_symbols": len(syms),
            "r2_base": 1 - np.sum((y - fb) ** 2) / sst, "r2_full": 1 - np.sum((y - ff) ** 2) / sst,
            "delta_r2": (np.sum((y - fb) ** 2) - np.sum((y - ff) ** 2)) / sst,
            "delta_r2_ci": [float(np.nanquantile(dR2, .025)), float(np.nanquantile(dR2, .975))],
            "auc_base": auc_(tail, fb), "auc_full": auc_(tail, ff),
            "delta_auc_ci": [float(np.nanquantile(dA, .025)), float(np.nanquantile(dA, .975))],
            "clark_west_t": t_, "clark_west_p": p_, "coef_candidate_train": float(bf[len(CTRL) + 1])}

# ---------------------------------------------------------------------------------------------
# Part 6 additions
# ---------------------------------------------------------------------------------------------
H_GUARD = 60          # guard horizon (minutes) for the summed and peak impulse response
CTRL = ["rv_60", "rv_360", "abs_ret_60", "flow_imb_60", "log_vol_60", "log_depth1", "imbalance", "oi_chg_60"]
IMPACT = ["kappa_hat", "kappa_sq", "kyle_lam", "amihud_60"]
TAGGED = ["n_top_pos", "d_top_pos_60", "n_all", "d_all_60"]

def _last_valid(v, lo, hi):
    w = v[lo:hi]; w = w[np.isfinite(w)]
    return w[-1] if len(w) else np.nan

def day_blocks6(s, d, flow_scale):
    """One row per hour 06-23 UTC. Features use minutes [t-360, t); outcomes use (t, t+60]."""
    df = PANEL[(s, d)]
    p, u, dd_, x, tot = prep(df, flow_scale)
    oi = df["oi"].ffill().to_numpy(); vol = df["vol"].to_numpy(); dp = np.diff(p, prepend=np.nan)
    ntag = {c: ((df[col] - 1) / (df[col] + 1)).to_numpy() for c, col in [("top_pos", "top_pos_ratio"), ("all", "acc_ratio")]}
    rows = []
    for hr in range(6, 24):
        t = hr * 60
        w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, min(t + 61, 1440))
        est = fit_t6(p[w], u[w], dd_[w], x[w])
        row = {"symbol": s, "date": d, "hour": hr}
        if est is not None:
            t1, t2, t3 = est["phi"] * est["eps"], est["kappa"] ** 2 * est["eta"] * est["q"], (1 - est["a"]) * est["kappa"]
            imp = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
            ok = np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12
            S60 = float(np.sum(np.abs(imp))) if ok else np.nan
            P60 = float(np.max(np.abs(imp))) if ok else np.nan
            row.update({"C3_hat": est["C3"], "term_depth": t1, "term_momentum": t2, "term_reversion": t3,
                        "kappa_hat": est["kappa"], "a_hat": est["a"], "S60": S60, "P60": P60,
                        "gain_multiple": S60 / abs(imp[0]) if ok else np.nan,
                        "log_halflife": float(np.log(1.0 / (1 - est["a"]))) if 0 < 1 - est["a"] < 1 else np.nan})
        # depth-free version of C3 (prices and flow only), for venues without depth data (Part 7)
        bp0 = ols(dp[w][1:], np.column_stack([u[w][1:], x[w][:-1]]))
        bm0 = ols(u[w][1:], np.column_stack([u[w][:-1], x[w][:-1]]))
        if bp0 is not None and bm0 is not None and abs(1 - bm0[0]) > 1e-6:
            k0, a0, e0 = bp0[0], 1 + bp0[1], 1 - bm0[0]
            row["C3_flow"] = k0 ** 2 * e0 * (bm0[1] / e0) - (1 - a0) * k0
        uu, yy = u[w][1:], dp[w][1:]; okk = np.isfinite(uu) & np.isfinite(yy)
        kl = float(np.polyfit(uu[okk], yy[okk], 1)[0]) if okk.sum() > 60 and np.std(uu[okk]) > 0 else np.nan
        v60 = np.nansum(vol[h]); au = np.abs(u[w]); au = au[np.isfinite(au)]
        row.update({
            "rv_60": np.nanstd(np.diff(p[h])), "rv_360": np.nanstd(np.diff(p[w])), "abs_ret_60": abs(p[t - 1] - p[t - 60]),
            "flow_imb_60": np.nansum(u[h]) / (np.nansum(np.abs(u[h])) + 1e-12), "log_vol_60": np.log1p(v60),
            "log_depth1": np.log(tot[t - 1]) if np.isfinite(tot[t - 1]) and tot[t - 1] > 0 else np.nan,
            "imbalance": dd_[t - 1],
            "oi_chg_60": (oi[t - 1] / oi[t - 60] - 1) * 100 if np.isfinite(oi[t - 60]) and oi[t - 60] > 0 else np.nan,
            "kyle_lam": kl,
            "amihud_60": np.log(abs(p[t - 1] - p[t - 60]) / v60 + 1e-9) if v60 > 0 and np.isfinite(p[t - 60]) else np.nan,
            "U6": float(np.quantile(au, 0.95)) if len(au) > 60 else np.nan,
            "n_top_pos": _last_valid(ntag["top_pos"], t - 60, t),
            "d_top_pos_60": _last_valid(ntag["top_pos"], t - 60, t) - _last_valid(ntag["top_pos"], t - 120, t - 60),
            "n_all": _last_valid(ntag["all"], t - 60, t),
            "d_all_60": _last_valid(ntag["all"], t - 60, t) - _last_valid(ntag["all"], t - 120, t - 60),
            "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1]))),
            "umax_next": float(np.nanmax(np.abs(u[f])))})
        rows.append(row)
    return rows

def winsor_train(D, cols):
    D = D.copy()
    for c in cols:
        lo, hi = D.loc[D["split"] == "train", c].quantile([0.01, 0.99])
        D[c] = D[c].clip(lo, hi)
    return D

def evaluate_g(sub, outcome, cands, ctrl, B=2000, level=0.95, seed=88):
    """Out-of-sample evaluation, as in Parts 4-5, for one or more candidates on top of `ctrl`.
    Candidates are winsorized at training 1%/99%; symbol fixed effects; date-block bootstrap."""
    cands = [cands] if isinstance(cands, str) else list(cands)
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    cw = []
    for c in cands:
        lo, hi = A0[c].quantile([0.01, 0.99]); A0[c + "_w"] = A0[c].clip(lo, hi); B0[c + "_w"] = B0[c].clip(lo, hi); cw.append(c + "_w")
    need = ctrl + cw + [outcome]
    A = A0.dropna(subset=need); Bt = B0.dropna(subset=need)
    Bt = Bt[Bt["symbol"].isin(set(A["symbol"]))].sort_values(["date", "symbol", "hour"])
    if len(A) < 200 or len(Bt) < 200 or A[outcome].std() < 1e-8 or any(A[c].std() < 1e-12 for c in cw):
        return {"skipped": "too few blocks or no variation", "n_train": len(A), "n_test": len(Bt),
                "clark_west_p": np.nan, "delta_r2": np.nan, "delta_r2_ci": [np.nan, np.nan]}
    syms = sorted(A["symbol"].unique()); y = Bt[outcome].to_numpy()
    bb = np.linalg.lstsq(design(A, ctrl, syms), A[outcome].to_numpy(), rcond=None)[0]
    bf = np.linalg.lstsq(design(A, ctrl + cw, syms), A[outcome].to_numpy(), rcond=None)[0]
    fb = design(Bt, ctrl, syms) @ bb; ff = design(Bt, ctrl + cw, syms) @ bf
    ybar = A[outcome].mean(); sst = np.sum((y - ybar) ** 2)
    t_, p_ = cw_test(y, fb, ff)
    tail = (y > A[outcome].quantile(0.9)).astype(int)
    Rb = rng(seed); dd = Bt["date"].to_numpy(); ud = np.unique(dd)
    pos = {d: np.where(dd == d)[0] for d in ud}; dR2, dA = [], []
    for _ in range(B):
        idx = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])
        s_ = np.sum((y[idx] - ybar) ** 2)
        dR2.append((np.sum((y[idx] - fb[idx]) ** 2) - np.sum((y[idx] - ff[idx]) ** 2)) / s_)
        dA.append(auc_(tail[idx], ff[idx]) - auc_(tail[idx], fb[idx]))
    qa = (1 - level) / 2
    return {"n_train": len(A), "n_test": len(Bt), "n_symbols": len(syms), "n_test_dates": len(ud),
            "r2_base": 1 - np.sum((y - fb) ** 2) / sst, "r2_full": 1 - np.sum((y - ff) ** 2) / sst,
            "delta_r2": (np.sum((y - fb) ** 2) - np.sum((y - ff) ** 2)) / sst,
            "delta_r2_ci": [float(np.nanquantile(dR2, qa)), float(np.nanquantile(dR2, 1 - qa))],
            "auc_base": auc_(tail, fb), "auc_full": auc_(tail, ff),
            "delta_auc_ci": [float(np.nanquantile(dA, qa)), float(np.nanquantile(dA, 1 - qa))],
            "clark_west_t": t_, "clark_west_p": p_, "ci_level": level,
            "coef_candidates_train": {c: float(bf[len(ctrl) + 1 + i]) for i, c in enumerate(cands)}}

# ---- Guard backtest (hypothesis B) ----------------------------------------------------------
# A dealer sizes its position each hour as q = c_s / R_t, where R_t is a rule's risk measure from
# the past 6 hours; c_s makes the TRAINING mean of q equal to 1 for every symbol and rule. The
# hour's loss is L = q * MAE_60 (worst adverse excursion, either direction). Tail-loss ratio:
#   TLR = ES95(L) / mean(q)   on the test sample: tail loss per unit of average position (lower is better).
GUARD_RULES = {"guard_summed": lambda D: D["U6"] * D["S60"],        # Paper 2 guard: shock envelope x summed |response|
               "guard_peak":   lambda D: D["U6"] * D["P60"],        # peak-response guard
               "vol":          lambda D: D["rv_360"],               # volatility-scaled limit
               "static":       lambda D: pd.Series(1.0, index=D.index)}

THETA_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
def choose_theta(D, gm_col="gain_multiple"):
    """Amplification-adjusted volatility limit R = rv_360 * GM^theta, theta chosen on TRAINING data only
    (minimum training TLR). theta = 0 is the plain volatility limit."""
    res = {}
    for th in THETA_GRID:
        G, _ = guard_frame(D, {"amp_vol": (lambda X, th=th: X["rv_360"] * X[gm_col] ** th)})
        Tr = G[G["split"] == "train"]
        res[th] = es95(Tr["L_amp_vol"]) / Tr["q_amp_vol"].mean()
    return min(res, key=res.get), res

def es95(v):
    v = np.asarray(v, float); q = np.quantile(v, 0.95); return float(v[v >= q].mean())

def guard_frame(D, extra_rules=None):
    rules = dict(GUARD_RULES); rules.update(extra_rules or {})
    G = D[["symbol", "date", "hour", "split", "MAE_60"]].copy()
    for r, fn in rules.items():
        G["R_" + r] = fn(D).astype(float).where(lambda v: v > 0)
    G = G.dropna(subset=["MAE_60"] + ["R_" + r for r in rules])
    for r in rules:                                          # winsorize risk at pooled training 1%/99%
        lo, hi = G.loc[G["split"] == "train", "R_" + r].quantile([0.01, 0.99])
        G["R_" + r] = G["R_" + r].clip(lo, hi)
        inv = 1.0 / G["R_" + r]
        c = inv[G["split"] == "train"].groupby(G["symbol"]).mean()
        G["q_" + r] = inv / G["symbol"].map(c)
        G["L_" + r] = G["q_" + r] * G["MAE_60"]
    G = G[G["symbol"].isin(c.index)]
    thr = G[G["split"] == "train"].groupby("symbol")["L_static"].quantile(0.95)
    for r in rules:
        G["breach_" + r] = (G["L_" + r] > G["symbol"].map(thr)).astype(float)
    return G, list(rules)

def guard_compare(G, rules, ref="vol", B=2000, level=0.95, seed=77):
    T = G[G["split"] == "test"].sort_values(["date", "symbol", "hour"])
    tlr = lambda X, r: es95(X["L_" + r]) / X["q_" + r].mean()
    point = {r: {"TLR": tlr(T, r), "mean_q": float(T["q_" + r].mean()), "breach_rate": float(T["breach_" + r].mean()),
                 "ES95_loss": es95(T["L_" + r])} for r in rules}
    Rb = rng(seed); dd = T["date"].to_numpy(); ud = np.unique(dd); pos = {d: np.where(dd == d)[0] for d in ud}
    bs = {r: [] for r in rules if r != ref}
    for _ in range(B):
        X = T.iloc[np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])]
        tr_ = tlr(X, ref)
        for r in bs:
            bs[r].append(np.log(tlr(X, r)) - np.log(tr_))
    qa = (1 - level) / 2
    comp = {r: {"log_TLR_minus_ref": float(np.log(point[r]["TLR"]) - np.log(point[ref]["TLR"])),
                "ci": [float(np.quantile(v, qa)), float(np.quantile(v, 1 - qa))],
                "share_boot_below_0": float(np.mean(np.array(v) < 0))} for r, v in bs.items()}
    return {"n_test_hours": len(T), "n_test_dates": len(ud), "ref": ref, "level": level, "point": point, "vs_ref": comp}

# ---- Paper 1 identification (hypothesis C) ---------------------------------------------------
CLASSES = {"top_position": "top_pos_ratio", "top_account": "top_acc_ratio", "all_accounts": "acc_ratio"}
def five_min(df, s):
    m = df.index[df["top_pos_ratio"].notna() | df["acc_ratio"].notna()].to_numpy()
    m = m[m >= 5]
    if len(m) < 100:
        return None
    p = np.log(df["close"].to_numpy()) * 1e4; fl = df["flow"].to_numpy() / FLOW_SCALE[s]
    cf = np.concatenate([[0.0], np.cumsum(fl)])
    out = pd.DataFrame({"m": m, "ret": p[m] - p[m - 5], "flow": cf[m + 1] - cf[m - 4]})
    for c, col in CLASSES.items():
        R = df[col].to_numpy()[m]
        out[c] = (R - 1) / (R + 1)
    return out
def tagged_fit(days5, c):
    Y, X = [], []
    for g in days5:
        n = g[c].to_numpy(); r = g["ret"].to_numpy()
        y, x1, x2 = n[1:], n[:-1], r[1:]
        ok = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2)
        if ok.sum() < 30:
            continue
        Y.append(y[ok] - y[ok].mean()); X.append(np.column_stack([x1[ok] - x1[ok].mean(), x2[ok] - x2[ok].mean()]))
    if not Y:
        return np.nan, np.nan
    b = np.linalg.lstsq(np.vstack(X), np.concatenate(Y), rcond=None)[0]
    return float(b[0]), float(b[1])
def kernel_fit(days5, L=12):
    """Price-only model: 5-min flow on 12 lagged 5-min returns; kernel k_m fitted by two exponentials.
    Also returns the merged moments the theory says prices DO identify: M0 = sum k_m, mean lag M1."""
    Y, X = [], []
    for g in days5:
        f, r = g["flow"].to_numpy(), g["ret"].to_numpy()
        if len(f) <= L + 10:
            continue
        Xl = np.column_stack([r[L - m:len(r) - m] for m in range(1, L + 1)]); y = f[L:]
        ok = np.all(np.isfinite(Xl), 1) & np.isfinite(y)
        Y.append(y[ok] - y[ok].mean()); X.append(Xl[ok] - Xl[ok].mean(0))
    k = np.linalg.lstsq(np.vstack(X), np.concatenate(Y), rcond=None)[0]
    m = np.arange(L)
    def resid(th):
        w1, r1, w2, r2 = th
        return w1 * r1 ** m + w2 * r2 ** m - k
    best = None
    for r1, r2 in [(0.2, 0.8), (0.1, 0.6), (0.4, 0.95), (0.05, 0.3)]:
        try:
            sol = optimize.least_squares(resid, [k[0] / 2, r1, k[0] / 2, r2],
                                         bounds=([-np.inf, 0, -np.inf, 0], [np.inf, 0.99, np.inf, 0.99]))
            if best is None or sol.cost < best.cost:
                best = sol
        except Exception:
            pass
    w1, r1, w2, r2 = best.x
    if r1 > r2:
        w1, r1, w2, r2 = w2, r2, w1, r1
    M0 = float(k.sum()); M1 = float(np.sum(np.arange(1, L + 1) * k) / M0) if abs(M0) > 1e-12 else np.nan
    return {"k": k, "r_fast": r1, "r_slow": r2, "M0": M0, "M1": M1}

def ident_symbol(s, days, B=200, seed=90):
    days5 = [g for g in (five_min(PANEL[(s, d)], s) for d in days if (s, d) in PANEL) if g is not None]
    if len(days5) < 15:
        return None
    R9 = rng(seed); n = len(days5)
    point = {c: tagged_fit(days5, c) for c in CLASSES}; kp = kernel_fit(days5)
    bt = {c: [] for c in CLASSES}; bk = []
    for _ in range(B):
        pick = [days5[i] for i in R9.integers(0, n, n)]
        for c in CLASSES:
            bt[c].append(tagged_fit(pick, c))
        try:
            kk = kernel_fit(pick); bk.append((kk["r_fast"], kk["r_slow"], kk["M0"]))
        except Exception:
            pass
    q = lambda v: [float(np.nanquantile(v, .025)), float(np.nanquantile(v, .975))]
    bk = np.array(bk)
    tag = {c: {"r": point[c][0], "r_ci": q([b[0] for b in bt[c]])} for c in CLASSES}
    w_tag = float(np.mean([tag[c]["r_ci"][1] - tag[c]["r_ci"][0] for c in CLASSES]))
    rf_ci, rs_ci, M0_ci = q(bk[:, 0]), q(bk[:, 1]), q(bk[:, 2])
    w_pr = float(np.mean([rf_ci[1] - rf_ci[0], rs_ci[1] - rs_ci[0]]))
    diff = np.array([b[0] for b in bt["top_position"]]) - np.array([b[0] for b in bt["all_accounts"]])
    return {"n_days": n, "tagged": tag, "price_only": {"r_fast": kp["r_fast"], "r_slow": kp["r_slow"], "r_fast_ci": rf_ci,
            "r_slow_ci": rs_ci, "M0": kp["M0"], "M0_ci": M0_ci, "M1": kp["M1"]},
            "width_tagged": w_tag, "width_price_only": w_pr, "width_ratio": w_pr / w_tag if w_tag > 0 else np.nan,
            "M0_identified": bool(M0_ci[0] > 0 or M0_ci[1] < 0), "rates_unidentified": bool(w_pr > 0.25),
            "top_minus_all_rate_ci": q(diff)}


# ---------------------------------------------------------------------------------------------
# Part 9 additions: volatility-forecasting benchmarks (all from data before t, same day)
# ---------------------------------------------------------------------------------------------
HOURS = list(range(7, 24))                                  # hour 6 is the omitted category
VOLBENCH = ["rv_15", "rv_day", "ewma_vol", "mae_lag60"] + [f"hr_{h}" for h in HOURS]
def day_blocks9(s, d, flow_scale):
    rows = day_blocks6(s, d, flow_scale)
    df = PANEL[(s, d)]; p = np.log(df["close"].to_numpy()) * 1e4; dp = np.diff(p, prepend=np.nan)
    ew = pd.Series(np.nan_to_num(dp) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()   # RiskMetrics lambda = 0.94
    for row in rows:
        t = row["hour"] * 60
        row["rv_15"] = np.nanstd(dp[t - 15:t]); row["rv_day"] = np.nanstd(dp[1:t])
        row["ewma_vol"] = float(np.sqrt(ew[t - 1]))
        row["mae_lag60"] = float(np.nanmax(np.abs(p[t - 60:t] - p[t - 61])))
        for h in HOURS:
            row[f"hr_{h}"] = float(row["hour"] == h)
    return rows

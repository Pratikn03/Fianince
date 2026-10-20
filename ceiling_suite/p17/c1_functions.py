# ============================================================================
# CELL C1 — FUNCTIONS (Coinbase trade loader, minute bars, depth-free features, evaluation). Defines only; nothing runs.
# ============================================================================
STABLE = {"USDT", "USDC", "DAI", "PYUSD", "EURC", "GUSD", "PAX", "PAXG", "BUSD", "UST", "TUSD", "USDS", "RLUSD", "FDUSD",
          "WBTC", "CBETH", "MSOL", "LSETH", "WETH", "CBBTC", "STETH", "WAXL"}

def _t(s):
    return pd.Timestamp(s).tz_convert("UTC") if pd.Timestamp(s).tzinfo else pd.Timestamp(s, tz="UTC")

OLDER = {"param": None}
def check_pagination(pid):
    """Find which cursor parameter returns OLDER trades (ids below the cursor). Recorded in C2."""
    p1 = api(f"/products/{pid}/trades", {"limit": 100})
    c = min(t["trade_id"] for t in p1)
    for prm in ("after", "before"):
        p2 = api(f"/products/{pid}/trades", {"limit": 100, prm: c})
        if p2 and max(t["trade_id"] for t in p2) < c:
            OLDER["param"] = prm
            return prm
    raise RuntimeError("could not determine the pagination direction")

def older_page(pid, cursor, limit=1000):
    """Trades with trade_id < cursor, newest first."""
    return api(f"/products/{pid}/trades", {"limit": limit, OLDER["param"]: int(cursor)}) or []

def trade_at(pid, tid):
    pg = older_page(pid, tid + 1, limit=1)
    return (pg[0]["trade_id"], _t(pg[0]["time"])) if pg else (None, None)

_BLOCK = threading.Lock(); _BMEM = {}
def _bounds(pid):
    if pid not in _BMEM:
        fp = os.path.join(CDATA, "bounds", f"{pid}.json")
        try:
            _BMEM[pid] = json.load(open(fp)) if os.path.exists(fp) else {}
        except Exception:
            _BMEM[pid] = {}
    return _BMEM[pid]

def cursor_at(pid, T):
    """A trade id whose time is >= T and that is within ~1,000 ids of the first such trade (cached)."""
    key = T.strftime("%Y-%m-%dT%H:%M:%S")
    with _BLOCK:
        cache = _bounds(pid)
        if key in cache:
            return cache[key]
    top = api(f"/products/{pid}/trades", {"limit": 1})
    hi_id, hi_t = top[0]["trade_id"], _t(top[0]["time"])
    if hi_t < T:
        return None
    lo_id, lo_t = trade_at(pid, 1)
    if lo_id is None:                                   # ids do not start at 1: find the first one
        lo_id, lo_t = 0, pd.Timestamp("2010-01-01", tz="UTC")
    if lo_t >= T:
        res = lo_id
    else:
        it = 0
        while hi_id - lo_id > 1000 and it < 60:
            it += 1
            if it % 3 == 0:
                g = (lo_id + hi_id) // 2
            else:
                fr = (T - lo_t) / (hi_t - lo_t) if hi_t > lo_t else 0.5
                g = int(lo_id + min(max(fr, 0.02), 0.98) * (hi_id - lo_id))
            g = min(max(g, lo_id + 1), hi_id - 1)
            gid, gt = trade_at(pid, g)
            if gid is None or gid <= lo_id:
                lo_id = g                                   # gap in ids: treat as below
                continue
            if gt < T:
                lo_id, lo_t = gid, gt
            else:
                hi_id, hi_t = gid, gt
        res = hi_id
    with _BLOCK:
        cache = _bounds(pid); cache[key] = int(res)
        fp = os.path.join(CDATA, "bounds", f"{pid}.json"); tmp = fp + f".tmp{threading.get_ident()}"
        json.dump(cache, open(tmp, "w")); os.replace(tmp, fp)             # atomic: safe with several threads
    return int(res)

MAX_PAGES = 400
def build_day(pid, date):
    """Minute bars for one UTC day: close (last trade), signed taker flow ($M; + = taker buy), volume ($M), trades."""
    t0 = _t(f"{date} 00:00:00"); t1 = t0 + pd.Timedelta("1D")
    cur = cursor_at(pid, t1)
    if cur is None:
        return None, {"symbol": pid, "date": date, "reason": "day not complete"}
    rows, pages = [], 0
    while pages < MAX_PAGES:
        pg = older_page(pid, cur); pages += 1
        if not pg:
            break
        rows += pg; cur = min(t["trade_id"] for t in pg)
        if _t(pg[-1]["time"]) < t0:                       # pages are newest first; the last trade is the oldest
            break
    if pages >= MAX_PAGES:
        return None, {"symbol": pid, "date": date, "reason": "too many trades", "pages": pages}
    if not rows:
        return None, {"symbol": pid, "date": date, "reason": "no trades"}
    T = pd.DataFrame(rows)
    T["ts"] = pd.to_datetime(T["time"], utc=True, format="ISO8601")
    T = T[(T["ts"] >= t0) & (T["ts"] < t1)].drop_duplicates("trade_id").sort_values("trade_id")
    if T.empty:
        return None, {"symbol": pid, "date": date, "reason": "no trades in day"}
    px, sz = T["price"].astype(float).to_numpy(), T["size"].astype(float).to_numpy()
    notional = px * sz / 1e6
    sign = np.where(T["side"].to_numpy() == "sell", 1.0, -1.0)        # maker sell = taker buy (up-tick)
    m = ((T["ts"] - t0).dt.total_seconds() // 60).astype(int).clip(0, 1439).to_numpy()
    idx = np.arange(1440)
    g = pd.DataFrame({"m": m, "px": px, "f": sign * notional, "v": notional}).groupby("m")
    out = pd.DataFrame(index=idx)
    out["close"] = g["px"].last().reindex(idx).ffill().bfill()
    out["flow"] = g["f"].sum().reindex(idx).fillna(0.0)
    out["vol"] = g["v"].sum().reindex(idx).fillna(0.0)
    out["ntr"] = g["px"].size().reindex(idx).fillna(0).astype(int)
    cov = float((out["ntr"] > 0).mean())
    st = {"symbol": pid, "date": date, "trades": int(len(T)), "pages": pages, "minute_coverage": cov,
          "day_ok": bool(cov >= MIN_COVERAGE), "first_id": int(T["trade_id"].iloc[0]), "last_id": int(T["trade_id"].iloc[-1]),
          "sha256": hashlib.sha256(pd.util.hash_pandas_object(T[["trade_id", "price", "size", "side"]], index=False).values.tobytes()).hexdigest()}
    out["symbol"], out["date"] = pid, date
    return out, st

MIN_COVERAGE = 0.60
def get_day(pid, date):
    d_ = os.path.join(CDATA, "minute", pid); os.makedirs(d_, exist_ok=True)
    pq, js = os.path.join(d_, f"{date}.parquet"), os.path.join(d_, f"{date}.json")
    if os.path.exists(js):
        st = json.load(open(js))
        return (pd.read_parquet(pq) if os.path.exists(pq) else None), st
    df, st = build_day(pid, date)
    if df is not None:
        df.to_parquet(pq)
    json.dump(_clean(st), open(js, "w"))
    return df, st

# ---- estimation helpers (same as Parts 9, 14 and 16) ------------------------------------------
def ols(y, X):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 20:
        return None
    return np.linalg.lstsq(np.column_stack([np.ones(ok.sum()), X[ok]]), y[ok], rcond=None)[0][1:]

def impulse_2s(a, kappa, eta, q, L=60):
    x = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        x[t] = (a * x[t - 1] if t else 0) + kappa * ((1.0 if t == 0 else 0.0) + f[t])
        if abs(x[t]) > 1e9:
            return np.full(L, np.nan)
    return x

def c3_flow(dpw, uw, xw):
    """Depth-free amplification margin and summed response from one window (prices and signed flow only)."""
    bp0 = ols(dpw[1:], np.column_stack([uw[1:], xw[:-1]]))
    bm0 = ols(uw[1:], np.column_stack([uw[:-1], xw[:-1]]))
    if bp0 is None or bm0 is None or abs(1 - bm0[0]) < 1e-6:
        return None
    k0, a0, e0 = bp0[0], 1 + bp0[1], 1 - bm0[0]; q0 = bm0[1] / e0
    imp = impulse_2s(a0, k0, e0, q0)
    return {"C3": k0 ** 2 * e0 * q0 - (1 - a0) * k0, "kappa": k0, "a": a0,
            "S60": float(np.sum(np.abs(imp))) if np.all(np.isfinite(imp)) else np.nan}

def vpin_window(vol, flow, nb=50):
    v = np.nan_to_num(vol); f = np.nan_to_num(flow); tot = v.sum()
    if tot <= 0:
        return np.nan
    buy = (v + f) / 2; cum = np.cumsum(v); edges = np.linspace(0, tot, nb + 1)
    k = np.clip(np.searchsorted(edges, cum, side="left") - 1, 0, nb - 1)
    imb = np.zeros(nb); np.add.at(imb, k, buy - (v - buy))
    return float(np.sum(np.abs(imb)) / tot)

HOURS = list(range(7, 24))
def cb_blocks(df, s, d, flow_scale):
    p = np.log(df["close"].to_numpy()) * 1e4; u = df["flow"].to_numpy() / flow_scale
    vol, flow = df["vol"].to_numpy(), df["flow"].to_numpy()
    x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy(); dp = np.diff(p, prepend=np.nan)
    ew = pd.Series(np.nan_to_num(dp) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()
    rows = []
    for hr in HOURS_EVAL:
        t = hr * 60; w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, min(t + 61, 1440))
        row = {"symbol": s, "date": d, "hour": hr}
        real = c3_flow(dp[w], u[w], x[w])
        plac = c3_flow(dp[w], np.roll(u[w], PLACEBO_SHIFT), x[w])          # order-splitting placebo
        if real is not None:
            row.update({"C3_flow": real["C3"], "S60": real["S60"], "kappa_hat": real["kappa"]})
        if plac is not None:
            row.update({"C3_placebo": plac["C3"], "S60_placebo": plac["S60"]})
        uu, yy = u[w][1:], dp[w][1:]; okk = np.isfinite(uu) & np.isfinite(yy)
        v60 = np.nansum(vol[h])
        row.update({"rv_60": np.nanstd(np.diff(p[h])), "rv_360": np.nanstd(np.diff(p[w])), "abs_ret_60": abs(p[t - 1] - p[t - 60]),
                    "flow_imb_60": np.nansum(u[h]) / (np.nansum(np.abs(u[h])) + 1e-12), "log_vol_60": np.log1p(v60),
                    "kyle_lam": float(np.polyfit(uu[okk], yy[okk], 1)[0]) if okk.sum() > 60 and np.std(uu[okk]) > 0 else np.nan,
                    "amihud_60": np.log(abs(p[t - 1] - p[t - 60]) / v60 + 1e-9) if v60 > 0 else np.nan,
                    "rv_15": np.nanstd(dp[t - 15:t]), "rv_day": np.nanstd(dp[1:t]), "ewma_vol": float(np.sqrt(ew[t - 1])),
                    "mae_lag60": float(np.nanmax(np.abs(p[t - 60:t] - p[t - 61]))),
                    "vpin": vpin_window(vol[w], flow[w]), "trades_6h": int(df["ntr"].to_numpy()[w].sum()),
                    "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1])))})
        for hh in HOURS:
            row[f"hr_{hh}"] = float(hr == hh)
        rows.append(row)
    return rows

CB_CTRL = ["rv_60", "rv_360", "abs_ret_60", "flow_imb_60", "log_vol_60", "kappa_hat", "kappa_sq", "kyle_lam", "amihud_60",
           "rv_15", "rv_day", "ewma_vol", "mae_lag60"] + [f"hr_{h}" for h in HOURS]

def winsor_train(D, cols):
    D = D.copy()
    for c in cols:
        lo, hi = D.loc[D["split"] == "train", c].quantile([0.01, 0.99])
        D[c] = D[c].clip(lo, hi)
    return D

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

def _fit_predict(A, Bt, outcome, cols, syms):
    b = np.linalg.lstsq(design(A, cols, syms), A[outcome].to_numpy(), rcond=None)[0]
    return design(Bt, cols, syms) @ b

def evaluate_set(sub, outcome, cand_sets, ctrl, B=2000, level=0.95, seed=88):
    """Out-of-sample evaluation of several candidate sets against one baseline on the SAME rows and the SAME bootstrap
    draws (so differences between candidates are paired). Candidates winsorized at training 1%/99%; symbol fixed effects."""
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    allc = sorted({c for cs in cand_sets.values() for c in cs})
    for c in allc:
        lo, hi = A0[c].quantile([0.01, 0.99]); A0[c + "_w"] = A0[c].clip(lo, hi); B0[c + "_w"] = B0[c].clip(lo, hi)
    need = ctrl + [c + "_w" for c in allc] + [outcome]
    A = A0.dropna(subset=need); Bt = B0.dropna(subset=need)
    Bt = Bt[Bt["symbol"].isin(set(A["symbol"]))].sort_values(["date", "symbol", "hour"])
    syms = sorted(A["symbol"].unique()); y = Bt[outcome].to_numpy()
    fb = _fit_predict(A, Bt, outcome, ctrl, syms)
    ff = {k: _fit_predict(A, Bt, outcome, ctrl + [c + "_w" for c in cs], syms) for k, cs in cand_sets.items()}
    ybar = A[outcome].mean(); sst = np.sum((y - ybar) ** 2); tail = (y > A[outcome].quantile(0.9)).astype(int)
    out = {"n_train": len(A), "n_test": len(Bt), "n_symbols": len(syms), "n_test_dates": int(Bt["date"].nunique()),
           "r2_base": float(1 - np.sum((y - fb) ** 2) / sst), "auc_base": auc_(tail, fb), "cands": {}}
    Rb = rng(seed); dd = Bt["date"].to_numpy(); ud = np.unique(dd); pos = {d: np.where(dd == d)[0] for d in ud}
    draws = [np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))]) for _ in range(B)]
    qa = (1 - level) / 2; boot = {}
    for k in cand_sets:
        t_, p_ = cw_test(y, fb, ff[k])
        dr = np.array([(np.sum((y[i] - fb[i]) ** 2) - np.sum((y[i] - ff[k][i]) ** 2)) / np.sum((y[i] - ybar) ** 2) for i in draws])
        da = np.array([auc_(tail[i], ff[k][i]) - auc_(tail[i], fb[i]) for i in draws])
        boot[k] = dr
        out["cands"][k] = {"delta_r2": float((np.sum((y - fb) ** 2) - np.sum((y - ff[k]) ** 2)) / sst),
                           "delta_r2_ci": [float(np.quantile(dr, qa)), float(np.quantile(dr, 1 - qa))],
                           "delta_auc": float(auc_(tail, ff[k]) - auc_(tail, fb)),
                           "delta_auc_ci": [float(np.nanquantile(da, qa)), float(np.nanquantile(da, 1 - qa))],
                           "clark_west_t": t_, "clark_west_p": p_}
    out["_boot"] = boot
    return out

def paired_diff(ev, a, b, level=0.95):
    d = ev["_boot"][a] - ev["_boot"][b]; qa = (1 - level) / 2
    return {"diff": ev["cands"][a]["delta_r2"] - ev["cands"][b]["delta_r2"],
            "ci": [float(np.quantile(d, qa)), float(np.quantile(d, 1 - qa))], "p_one_sided": float(np.mean(d <= 0))}

def holm(pd_):
    items = sorted((v, k) for k, v in pd_.items()); out, run = {}, 0.0
    for j, (p_, k) in enumerate(items):
        run = max(run, min(1.0, p_ * (len(items) - j))); out[k] = run
    return out

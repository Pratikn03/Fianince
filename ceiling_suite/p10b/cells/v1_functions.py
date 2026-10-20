# ============================================================================
# CELL V1 — FUNCTIONS (estimation code identical to Parts 6 and 9; Bybit readers added at the end)
# ============================================================================
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


# ---------------------------------------------------------------------------------------------
# Part 10: Bybit order-book files -> 1-minute depth; Bybit trades -> 1-minute price, flow, volume
# ---------------------------------------------------------------------------------------------
OB_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})_([A-Z0-9]+)USDT_ob(\d+)\.data$")

DEPTH_LEVELS = 200          # the pre-registered book is the top 200 levels; 2024 files carry 500, so only the best 200 are used
def book_minutes(fh, date, band=0.01, levels=DEPTH_LEVELS):
    """Rebuild the book from one day's messages (a 'snapshot' resets it; a 'delta' sets levels, size 0 deletes).
    Returns the book at the END of each UTC minute: best bid/ask and $ notional within 1% of mid ($M),
    counting only the best `levels` price levels on each side (identical for ob200 and ob500 files)."""
    t0 = int(pd.Timestamp(date, tz="UTC").timestamp() * 1000)
    bids, asks = {}, {}
    out = np.full((1440, 4), np.nan); cur = None; last_u = None; gaps = 0; n_msg = 0; n_snap = 0; crossed = 0
    def rec(m):
        nonlocal crossed
        if not (0 <= m < 1440) or not bids or not asks:
            return
        bb, ba = max(bids), min(asks)
        if bb >= ba:
            crossed += 1; return
        mid = 0.5 * (bb + ba)
        bl = sorted(bids, reverse=True)[:levels]; al = sorted(asks)[:levels]
        out[m] = (bb, ba, sum(p * bids[p] for p in bl if p >= mid * (1 - band)) / 1e6,
                  sum(p * asks[p] for p in al if p <= mid * (1 + band)) / 1e6)
    for line in fh:
        if not line.strip():
            continue
        r = json.loads(line); n_msg += 1
        m = (r["ts"] - t0) // 60000
        if cur is not None and m != cur:
            rec(cur)
        cur = m; d = r["data"]
        if r["type"] == "snapshot":
            n_snap += 1
            bids = {float(p): float(q) for p, q in d["b"]}; asks = {float(p): float(q) for p, q in d["a"]}
        else:
            if last_u is not None and d["u"] != last_u + 1:
                gaps += 1
            for side, book in (("b", bids), ("a", asks)):
                for p, q in d[side]:
                    p = float(p); q = float(q)
                    if q == 0:
                        book.pop(p, None)
                    else:
                        book[p] = q
        last_u = d.get("u", last_u)
    if cur is not None:
        rec(cur)
    df = pd.DataFrame(out, columns=["best_bid", "best_ask", "bid1", "ask1"])
    st = {"messages": n_msg, "snapshots": n_snap, "u_gaps": gaps, "crossed_minutes": crossed,
          "depth_rule": f"top{levels}_within_{band:g}",
          "book_minute_coverage": float(df["bid1"].notna().mean())}
    return df, st

def _convert_member(name, raw, source):
    mt = OB_NAME.search(os.path.basename(name))
    if not mt:
        return None
    date, coin = mt.group(1), mt.group(2)
    df, st = book_minutes(io.StringIO(raw.decode()), date)
    st.update({"coin": coin, "date": date, "depth_levels": int(mt.group(3)), "source_file": source,
               "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    d_ = os.path.join(OBMIN, coin); os.makedirs(d_, exist_ok=True)
    df.to_parquet(os.path.join(d_, f"{date}.parquet"))
    json.dump(_clean(st), open(os.path.join(d_, f"{date}.json"), "w"))
    return (coin, date)

def convert_zip(path):
    """Turn one uploaded Bybit file into small per-day book summaries; returns the (coin, date) pairs written.
    Accepts a daily .zip, a bundle .zip holding daily .zip files (one Bybit date-range download), or a loose .data file."""
    done = []
    if path.endswith(".data"):
        got = _convert_member(path, open(path, "rb").read(), os.path.basename(path))
        return [got] if got else []
    def walk(zf, src):
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            if name.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(zf.read(name))) as inner:
                    walk(inner, src)
            else:
                got = _convert_member(name, zf.read(name), src)
                if got:
                    done.append(got)
    with zipfile.ZipFile(path) as z:
        walk(z, os.path.basename(path))
    return done

def have_book(coin, date):
    js = os.path.join(OBMIN, coin, f"{date}.json")
    return os.path.exists(js) and json.load(open(js)).get("depth_rule", "").startswith(f"top{DEPTH_LEVELS}_")

def trade_minutes(coin, date):
    """Minute bars from Bybit trades (same code as Part 7): last price, signed taker notional and volume ($M)."""
    sym = f"{coin}USDT"
    d_ = os.path.join(TRMIN, coin); os.makedirs(d_, exist_ok=True)
    pq, js = os.path.join(d_, f"{date}.parquet"), os.path.join(d_, f"{date}.json")
    if os.path.exists(js):
        st = json.load(open(js)); return (pd.read_parquet(pq) if os.path.exists(pq) else None), st
    code, raw = _http(bb_url(sym, date), timeout=180)
    if code != 200 or not raw:
        st = {"coin": coin, "date": date, "reason": f"http {code}", "day_ok": False}
        json.dump(st, open(js, "w")); return None, st
    DL_LOG.append({"symbol": sym, "date": date, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    tr = pd.read_csv(io.BytesIO(gzip.decompress(raw)))
    tr.columns = [c.strip().lower() for c in tr.columns]
    ts = pd.to_numeric(tr["timestamp"], errors="coerce").to_numpy()
    ts = np.where(ts > 1e11, ts / 1000.0, ts)
    m = ((ts - pd.Timestamp(date, tz="UTC").timestamp()) // 60).astype("int64")
    px = pd.to_numeric(tr["price"], errors="coerce").to_numpy(); sz = pd.to_numeric(tr["size"], errors="coerce").to_numpy()
    notional = px * sz / 1e6; sign = np.where(tr["side"].astype(str).str.lower().str.startswith("b"), 1.0, -1.0)
    ok = (m >= 0) & (m < 1440) & np.isfinite(px) & np.isfinite(notional)
    T = pd.DataFrame({"m": m[ok], "ts": ts[ok], "px": px[ok], "flow": (sign * notional)[ok], "vol": notional[ok]}).sort_values("ts")
    idx = np.arange(1440); g = T.groupby("m")
    out = pd.DataFrame(index=idx)
    out["close"] = g["px"].last().reindex(idx).ffill().bfill()
    out["flow"] = g["flow"].sum().reindex(idx).fillna(0.0)
    out["vol"] = g["vol"].sum().reindex(idx).fillna(0.0)
    cover = float(g.size().reindex(idx).notna().mean())
    st = {"coin": coin, "date": date, "n_trades": int(ok.sum()), "trade_minute_coverage": cover,
          "day_ok": bool(cover >= 0.80 and out["close"].notna().all())}
    out.to_parquet(pq); json.dump(_clean(st), open(js, "w"))
    return out, st

def build_day_bybit_ob(coin, date):
    """Merge: price, flow and volume from trades (as Binance klines in Parts 4-9); depth within 1% from the book."""
    tr, st_t = trade_minutes(coin, date)
    st_b = json.load(open(os.path.join(OBMIN, coin, f"{date}.json")))
    st = {"symbol": coin, "date": date, **{k: v for k, v in st_t.items() if k not in ("coin", "date")},
          **{k: v for k, v in st_b.items() if k not in ("coin", "date")}}
    if tr is None or not st_t.get("day_ok"):
        st["depth_day_ok"] = False; return None, st
    bk = pd.read_parquet(os.path.join(OBMIN, coin, f"{date}.parquet"))
    out = tr.copy()
    mid = 0.5 * (bk["best_bid"] + bk["best_ask"])
    far = (np.abs(mid / out["close"] - 1) > 0.03).to_numpy()      # book far from traded price: treat as missing
    for c in ["bid1", "ask1"]:
        v = bk[c].to_numpy().copy(); v[far] = np.nan
        out[c] = pd.Series(v).ffill(limit=2).to_numpy()
    for c in ["oi", "top_pos_ratio", "top_acc_ratio", "acc_ratio", "taker_ratio"]:
        out[c] = np.nan
    cov = float(pd.Series(out["bid1"]).notna().mean())
    st.update({"merged_depth_coverage": cov, "book_far_from_trades": int(far.sum()),
               "depth_day_ok": bool(cov >= 0.80 and st_b.get("u_gaps", 99) <= 5 and st_b.get("snapshots", 0) >= 1)})
    out["symbol"], out["date"] = coin, date
    return out, st

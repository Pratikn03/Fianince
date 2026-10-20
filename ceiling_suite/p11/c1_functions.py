# ============================================================================
# CELL C1 — FUNCTIONS
# ============================================================================
def get_cot(mkt):
    m = MARKETS[mkt]; fp = os.path.join(CDIR, f"cot_{mkt}.csv")
    if os.path.exists(fp):
        return pd.read_csv(fp, parse_dates=["date"])
    q = {"cftc_contract_market_code": m["code"], "$limit": "50000", "$order": "report_date_as_yyyy_mm_dd"}
    code, raw = _http(SOCRATA[m["report"]] + "?" + urllib.parse.urlencode(q), timeout=300)
    assert code == 200, f"COT download failed for {mkt}: HTTP {code}"
    df = pd.DataFrame(json.loads(raw))
    cols = CLASSES[m["report"]]
    out = pd.DataFrame({"date": pd.to_datetime(df["report_date_as_yyyy_mm_dd"]).dt.tz_localize(None).dt.normalize(),
                        "oi": pd.to_numeric(df["open_interest_all"], errors="coerce"),
                        "market_name": df["market_and_exchange_names"]})
    for c, (lc, sc) in cols.items():
        out[f"{c}_long"] = pd.to_numeric(df[lc], errors="coerce"); out[f"{c}_short"] = pd.to_numeric(df[sc], errors="coerce")
    out = out.drop_duplicates("date").sort_values("date")
    out = out[out["date"] <= END_DATE].reset_index(drop=True)
    out.to_csv(fp, index=False)
    return out

def get_binance_daily(sym):
    fp = os.path.join(CDIR, f"px_{sym}.csv")
    if os.path.exists(fp):
        return pd.read_csv(fp, parse_dates=["date"]).set_index("date")["px"]
    rows = []
    for mth in pd.period_range("2017-08", END_DATE[:7], freq="M"):
        url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1d/{sym}-1d-{mth}.zip"
        code, raw = _http(url, timeout=120)
        if code != 200 or not raw:
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            k = pd.read_csv(z.open(z.namelist()[0]), header=None)
        t = pd.to_numeric(k[0]); t = np.where(t > 1e14, t / 1000, t)          # microseconds from 2025 on
        rows.append(pd.DataFrame({"date": pd.to_datetime(t, unit="ms").normalize(), "px": k[4].astype(float)}))
    s = pd.concat(rows).drop_duplicates("date").sort_values("date")
    s.to_csv(fp, index=False)
    return s.set_index("date")["px"]

def get_yahoo(ticker):
    fp = os.path.join(CDIR, "yahoo_" + ticker.replace("^", "").replace("=", "_") + ".csv")
    if not os.path.exists(fp):
        d = yf.download(ticker, start="2005-01-01", end=END_DATE, progress=False, auto_adjust=False)
        assert len(d) > 100, f"Yahoo {ticker}: no data"
        c = d["Close"]
        c = c.iloc[:, 0] if isinstance(c, pd.DataFrame) else c          # newer yfinance returns a one-column frame
        pd.DataFrame({"date": pd.to_datetime(c.index).tz_localize(None).normalize(), "v": c.to_numpy(float)}).to_csv(fp, index=False)
    d = pd.read_csv(fp, parse_dates=["date"]).dropna()
    d = d[d["v"] > 0].drop_duplicates("date")
    return d.set_index("date")["v"]

def weekly_panel(mkt):
    """COT report dates (Tuesdays) with class net positions as shares of open interest and the weekly return
    from the last price on or before each report date."""
    cot = get_cot(mkt); kind, sid = MARKETS[mkt]["price"]
    if kind == "binance":
        px = np.log(get_binance_daily(sid)); px.name = "lp"
    else:
        v = get_yahoo(sid)
        px = {"yahoo": np.log(v), "yahoo_inverse": -np.log(v), "yahoo_yield": -v}[kind]   # yield (^TNX, percent): return proxy = -change
    px = px.sort_index()
    lp = px.reindex(cot["date"], method="ffill").to_numpy()
    stale = (cot["date"] - px.index[np.clip(np.searchsorted(px.index, cot["date"], side="right") - 1, 0, len(px) - 1)]).dt.days.to_numpy()
    D = pd.DataFrame({"date": cot["date"], "lp": lp, "stale_days": stale})
    for c in ("fast", "slow", "dealer"):
        D[f"n_{c}"] = (cot[f"{c}_long"] - cot[f"{c}_short"]) / cot["oi"]
        D[f"n_{c}_lag"] = D[f"n_{c}"].shift(1)
    D["ret"] = D["lp"].diff()
    ok = (D["date"].diff().dt.days == 7) & (D["stale_days"] <= 4) & (D["stale_days"].shift(1) <= 4)
    D = D[ok].dropna().reset_index(drop=True)                 # consecutive weekly reports with recent prices
    return D

def tagged_fit(D, c):
    X = np.column_stack([np.ones(len(D)), D[f"n_{c}_lag"], D["ret"]]); y = D[f"n_{c}"].to_numpy()
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b[1], b[2]                                          # memory rate r_c, response to returns w_c

# price-only alternative: weekly returns on 12 own lags, then a two-exponential kernel phi_j = sum_i b_i r_i^(j-1)
LAGS = 12
RGRID = np.round(np.arange(0.0, 0.99 + 1e-9, 0.02), 2)
PAIRS = np.array([(r1, r2) for i, r1 in enumerate(RGRID) for r2 in RGRID[i + 1:]])
_J = np.arange(LAGS)
_RES = []
for r1, r2 in PAIRS:
    Xp = np.column_stack([r1 ** _J, r2 ** _J]); Hp = Xp @ np.linalg.pinv(Xp)
    _RES.append(np.eye(LAGS) - Hp)
_RES = np.array(_RES)                                           # (pairs, 12, 12)
def ar_coefs(ret):
    y = ret[LAGS:]; X = np.column_stack([np.ones(len(y))] + [ret[LAGS - j:-j] for j in range(1, LAGS + 1)])
    return np.linalg.lstsq(X, y, rcond=None)[0][1:]
def two_exp(phi):
    sse = np.einsum("i,pij,j->p", phi, _RES, phi)
    return PAIRS[int(np.argmin(sse))]

def block_index(T, block, R):
    nb = int(np.ceil(T / block)); starts = R.integers(0, T - block + 1, nb)
    return np.concatenate([np.arange(s, s + block) for s in starts])[:T]

def analyse(mkt, B=2000, block=13):
    D = weekly_panel(mkt); T = len(D); R = np.random.default_rng(SEED + sum(map(ord, mkt)))
    est = {c: tagged_fit(D, c) for c in ("fast", "slow", "dealer")}
    ret = D["ret"].to_numpy(); po = two_exp(ar_coefs(ret))
    bt = {c: [] for c in ("fast", "slow", "dealer")}; bpo = []
    for b in range(B):
        idx = block_index(T, block, R); Db = D.iloc[idx].reset_index(drop=True)
        for c in bt:
            bt[c].append(tagged_fit(Db, c))
        rb = ret[block_index(len(ret), block, R)]           # price-only: resample return blocks, refit
        bpo.append(two_exp(ar_coefs(rb)))
    q = lambda v: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]
    out = {"weeks": T, "first": str(D["date"].iloc[0].date()), "last": str(D["date"].iloc[-1].date())}
    for c in bt:
        a = np.array(bt[c])
        out[c] = {"r": float(est[c][0]), "r_ci": q(a[:, 0]), "w": float(est[c][1]), "w_ci": q(a[:, 1]),
                  "halflife_weeks": float(np.log(0.5) / np.log(est[c][0])) if 0 < est[c][0] < 1 else None}
    dfs = np.array(bt["fast"])[:, 0] - np.array(bt["slow"])[:, 0]
    out["fast_minus_slow_r"] = {"est": float(est["fast"][0] - est["slow"][0]), "ci": q(dfs)}
    bpo = np.array(bpo)
    out["price_only"] = {"r1": float(po[0]), "r2": float(po[1]), "r1_ci": q(bpo[:, 0]), "r2_ci": q(bpo[:, 1])}
    out["tagged_width_fast"] = out["fast"]["r_ci"][1] - out["fast"]["r_ci"][0]
    out["price_only_width"] = float(np.mean([out["price_only"]["r1_ci"][1] - out["price_only"]["r1_ci"][0],
                                             out["price_only"]["r2_ci"][1] - out["price_only"]["r2_ci"][0]]))
    out["width_ratio"] = out["price_only_width"] / out["tagged_width_fast"] if out["tagged_width_fast"] > 0 else None
    return out, D

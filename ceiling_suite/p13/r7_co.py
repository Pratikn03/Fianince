# ============================================================================
# CELL R7 — PAPER 1: COCHRANE-ORCUTT ON REAL SPOT DATA (post hoc; a 2024 sub-panel of Part 8: 8 pairs x 24 dates)
# Order splitting makes flow-equation errors serially correlated, which biases OLS feedback estimates (Paper 1,
# Section 9.5). Here the VAR(1) feedback index Q is re-estimated after quasi-differencing with the estimated AR(1)
# coefficient of the flow-equation residuals.
# ============================================================================
SPOT = "https://data.binance.vision/data/spot/daily/klines"
PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "BNBUSDT", "XRPUSDT", "LTCUSDT"]
CO_D = [d.strftime("%Y-%m-%d") for d in pd.date_range("2024-01-01", "2024-12-31", freq="D") if d.day in (10, 24)]
BAR, EMA_W = 10, 300
KCOLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
         "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
def bars10_spot(sym, date):
    code, raw = _http(f"{SPOT}/{sym}/1s/{sym}-1s-{date}.zip", timeout=240)
    if code != 200:
        return None
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        k = pd.read_csv(io.BytesIO(z.read([n for n in z.namelist() if n.endswith(".csv")][0])), header=None, names=KCOLS)
    if not str(k.iloc[0, 0]).replace(".", "").isdigit():
        k = k.iloc[1:]
    t = pd.to_numeric(k["open_time"]).to_numpy(); t = np.where(t > 1e14, t // 1000, t)
    t0 = pd.Timestamp(date, tz="UTC").value // 10 ** 6; b = ((t - t0) // (1000 * BAR)).astype(int); nb = 86400 // BAR
    ok = (b >= 0) & (b < nb); qv = pd.to_numeric(k["quote_volume"]).to_numpy(); tb = pd.to_numeric(k["taker_buy_quote_volume"]).to_numpy()
    D = pd.DataFrame({"b": b[ok], "c": pd.to_numeric(k["close"]).to_numpy()[ok], "f": (2 * tb - qv)[ok]}); g = D.groupby("b"); idx = np.arange(nb)
    return g["c"].last().reindex(idx).ffill().bfill().to_numpy(), g["f"].sum().reindex(idx).fillna(0.0).to_numpy() / 1e6
def q_index(X, F):
    Y = np.column_stack([X[1:], F[1:]]); Z = np.column_stack([np.ones(len(Y)), X[:-1], F[:-1]])
    ok = np.all(np.isfinite(Y), 1) & np.all(np.isfinite(Z), 1)
    B = np.linalg.lstsq(Z[ok], Y[ok], rcond=None)[0]; J = B[1:3].T; E = Y[ok] - Z[ok] @ B
    return J[0, 1] * J[1, 0] / (1 - J[1, 1]), E
def unit_co(sym, date):
    r = bars10_spot(sym, date)
    if r is None:
        return None
    c, f = r; p = np.log(c); al = 2 / (EMA_W / BAR + 1); x = p - pd.Series(p).ewm(alpha=al, adjust=False).mean().to_numpy()
    q_ols, E = q_index(x, f)
    rho = float(np.corrcoef(E[1:, 1], E[:-1, 1])[0, 1])                 # AR(1) of flow-equation residuals
    xs, fs = x[1:] - rho * x[:-1], f[1:] - rho * f[:-1]
    q_co, _ = q_index(xs, fs)
    return {"symbol": sym, "date": date, "Q_ols": float(q_ols), "Q_co": float(q_co), "rho_flow_resid": rho}
with ThreadPoolExecutor(6) as ex:
    CO = pd.DataFrame([u for u in ex.map(lambda sd: unit_co(*sd), [(s, d) for s in PAIRS for d in CO_D]) if u])
dm = CO.groupby("date")[["Q_ols", "Q_co", "rho_flow_resid"]].mean()
def mci(v):
    n = len(v); se = v.std(ddof=1) / np.sqrt(n); t = stats.t.ppf(0.975, n - 1); return [float(v.mean() - t * se), float(v.mean() + t * se)]
r7 = {"units": len(CO), "dates": len(dm), "Q_ols": {"mean": float(dm["Q_ols"].mean()), "ci": mci(dm["Q_ols"])},
      "Q_co": {"mean": float(dm["Q_co"].mean()), "ci": mci(dm["Q_co"])}, "rho_flow_resid_median": float(CO["rho_flow_resid"].median()),
      "by_pair": CO.groupby("symbol")[["Q_ols", "Q_co", "rho_flow_resid"]].mean().to_dict("index")}
print(json.dumps({k: v for k, v in r7.items() if k != "by_pair"}, indent=1))
record("R7_cochrane_orcutt_spot", None, "real-data", r7, note="post hoc; Paper 1; 2024 sub-panel of Part 8")
zp = os.path.join(BASE, "p13_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fp in glob.glob(os.path.join(RESULTS, "R[1-8]_*.json")):
        z.write(fp, os.path.relpath(fp, BASE))
print("zipped ->", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)

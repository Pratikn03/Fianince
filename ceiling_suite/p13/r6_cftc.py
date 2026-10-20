# ============================================================================
# CELL R6 — CFTC: IS THE NEGATIVE RESPONSE OF LEVERAGED FUNDS A BASIS-TRADE SIGNATURE? (post hoc; Part 11 data)
# In a cash-futures basis trade, leveraged funds sell futures that asset managers (or cash-holders) buy, so their weekly
# position changes move in opposite directions. We report corr(dn_fast, dn_slow) and the fast-class response to returns
# with the slow class's position change held fixed.
# ============================================================================
CDIR = os.path.join(BASE, "data_cot")
PX = {"BTC": ("binance", "px_BTCUSDT.csv"), "ETH": ("binance", "px_ETHUSDT.csv"), "ES": ("yahoo", "yahoo_GSPC.csv"),
      "TY": ("yield", "yahoo_TNX.csv"), "EUR": ("yahoo", "yahoo_EURUSD_X.csv"), "JPY": ("inverse", "yahoo_JPY_X.csv"),
      "CL": ("yahoo", "yahoo_CL_F.csv"), "NG": ("yahoo", "yahoo_NG_F.csv")}
r6 = {}
for mkt, (kind, f) in PX.items():
    fc, fp = os.path.join(CDIR, f"cot_{mkt}.csv"), os.path.join(CDIR, f)
    if not (os.path.exists(fc) and os.path.exists(fp)):
        print("missing", mkt); continue
    cot = pd.read_csv(fc, parse_dates=["date"]); P = pd.read_csv(fp, parse_dates=["date"]).dropna()
    v = P.set_index("date").iloc[:, 0].astype(float).sort_index()
    lp = {"binance": np.log(v), "yahoo": np.log(v), "inverse": -np.log(v), "yield": -v}[kind]
    D = pd.DataFrame({"date": cot["date"], "lp": lp.reindex(cot["date"], method="ffill").to_numpy()})
    for c in ("fast", "slow"):
        D[f"n_{c}"] = ((cot[f"{c}_long"] - cot[f"{c}_short"]) / cot["oi"]).to_numpy()
        D[f"dn_{c}"] = D[f"n_{c}"].diff(); D[f"n_{c}_lag"] = D[f"n_{c}"].shift(1)
    D["ret"] = D["lp"].diff(); D = D[D["date"].diff().dt.days == 7].dropna()
    X0 = np.column_stack([np.ones(len(D)), D["n_fast_lag"], D["ret"]])
    X1 = np.column_stack([X0, D["dn_slow"]])
    b0 = np.linalg.lstsq(X0, D["n_fast"], rcond=None)[0]; b1 = np.linalg.lstsq(X1, D["n_fast"], rcond=None)[0]
    Rb = rng(136); T = len(D); bs = []
    for _ in range(1000):
        nb = int(np.ceil(T / 13)); st = Rb.integers(0, T - 13 + 1, nb); idx = np.concatenate([np.arange(s, s + 13) for s in st])[:T]
        bs.append(np.linalg.lstsq(X1[idx], D["n_fast"].to_numpy()[idx], rcond=None)[0][2])
    r6[mkt] = {"weeks": T, "corr_dn_fast_dn_slow": float(np.corrcoef(D["dn_fast"], D["dn_slow"])[0, 1]),
               "w_fast": float(b0[2]), "w_fast_given_dn_slow": float(b1[2]), "ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))],
               "coef_dn_slow": float(b1[3])}
print(pd.DataFrame(r6).T.round(3).to_string())
record("R6_cftc_basis_signature", None, "real-data", r6, note="post hoc; Part 11 data")

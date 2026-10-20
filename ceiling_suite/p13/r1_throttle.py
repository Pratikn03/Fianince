# ============================================================================
# CELL R1 — THE GUARD AS A ONE-SIDED THROTTLE (post hoc; Part 12 blocks)
# Theorem 5.1's guard caps admission at min(1, B / (I U S)); it never levers up. Part 12 sized positions as c / R, which
# levers up when the estimated response is small. Here the certified guard only scales a volatility-sized position down.
# ============================================================================
QB = pd.read_parquet(os.path.join(XDATA, "blocks_p12.parquet")).dropna(subset=["MAE_60", "rv_360", "U_cert", "S60_cert"])
QB = QB[(QB["rv_360"] > 0) & (QB["U_cert"] * QB["S60_cert"] > 0)].copy()
tr = QB["split"] == "train"
for c in ["rv_360"]:
    lo, hi = QB.loc[tr, c].quantile([0.01, 0.99]); QB[c] = QB[c].clip(lo, hi)
QB["US"] = QB["U_cert"] * QB["S60_cert"]
kmed = QB[tr].groupby("symbol")["US"].median()
QB["throttle"] = np.minimum(1.0, QB["symbol"].map(kmed) / QB["US"])
def norm_q(raw):
    c = raw[tr].groupby(QB.loc[tr, "symbol"]).mean()
    return raw / QB["symbol"].map(c)
QB["q_vol"] = norm_q(1.0 / QB["rv_360"])
QB["q_vol_thr"] = norm_q((1.0 / QB["rv_360"]) * QB["throttle"])
QB["q_static_thr"] = norm_q(QB["throttle"])
QB["q_static"] = 1.0
def tlr(X, col):
    L = X[col] * X["MAE_60"]; return es95(L) / X[col].mean()
T = QB[~tr].sort_values(["date", "symbol", "hour"]); dd = T["date"].to_numpy(); ud = np.unique(dd)
pos = {d: np.where(dd == d)[0] for d in ud}; Rb = rng(131)
cols = ["q_vol", "q_vol_thr", "q_static", "q_static_thr"]
pt = {c: tlr(T, c) for c in cols}
bs = {c: [] for c in cols if c != "q_vol"}
for _ in range(2000):
    X = T.iloc[np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])]; ref = tlr(X, "q_vol")
    for c in bs:
        bs[c].append(np.log(tlr(X, c)) - np.log(ref))
r1 = {c: {"TLR": pt[c], "vs_vol": float(np.log(pt[c]) - np.log(pt["q_vol"])) if c != "q_vol" else 0.0,
          "ci": [float(np.quantile(bs[c], .025)), float(np.quantile(bs[c], .975))] if c in bs else None,
          "share_throttled": float((T["throttle"] < 1).mean())} for c in cols}
b2 = []
for _ in range(2000):
    X = T.iloc[np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])]
    b2.append(np.log(tlr(X, "q_static_thr")) - np.log(tlr(X, "q_static")))
r1["static_thr_vs_static"] = {"est": float(np.log(pt["q_static_thr"]) - np.log(pt["q_static"])),
                              "ci": [float(np.quantile(b2, .025)), float(np.quantile(b2, .975))]}
print(json.dumps(r1, indent=1, default=float))
record("R1_guard_throttle", None, "real-data", r1, note="post hoc; Part 12 test hours")

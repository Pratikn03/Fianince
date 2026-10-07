"""A2 timing checks on the Nielsen/Coinbase 1-second LOB files.

(i)  interval closure: 1-min buys/sells vs sums of 1-sec rows
(ii) lead/lag corr of d(mid) with signed flow
(iii) duplicated-render frequency (identical consecutive rows with nonzero flow)
"""
import json
import sys
import numpy as np
import pandas as pd

D = "/Users/pratik_n/Downloads/Machine_Markets_Master_Release/empirical_pipeline/data"
COLS = ["system_time", "midpoint", "spread", "buys", "sells",
        "bids_notional_0", "asks_notional_0", "bids_distance_0", "asks_distance_0"]
res = {}
for asset in sys.argv[1:] or ["BTC", "ETH", "ADA"]:
    s = pd.read_csv(f"{D}/{asset}_1sec.csv", usecols=COLS)
    m = pd.read_csv(f"{D}/{asset}_1min.csv", usecols=["system_time", "buys", "sells"])
    ts = pd.to_datetime(s["system_time"], utc=True)
    r = {"rows": int(len(s))}
    dt = ts.diff().dt.total_seconds().iloc[1:]
    r["dt_counts"] = {str(k): int(v) for k, v in dt.round(3).value_counts().head(6).items()}
    r["frac_us_unique"] = int(ts.dt.microsecond.nunique())
    # (iii) duplicate renders
    keycols = ["midpoint", "spread", "buys", "sells", "bids_notional_0", "asks_notional_0",
               "bids_distance_0", "asks_distance_0"]
    same = (s[keycols].shift(1) == s[keycols]).all(axis=1)
    nz = (s["buys"] + s["sells"]) > 0
    r["dup_rows"] = int(same.sum())
    r["dup_rows_nonzero_flow"] = int((same & nz).sum())
    r["nonzero_flow_rows"] = int(nz.sum())
    flow = (s["buys"] - s["sells"]).to_numpy()
    gross = (s["buys"] + s["sells"]).to_numpy()
    r["share_gross_notional_in_dups"] = float(gross[same.to_numpy()].sum() / gross.sum())
    # (i) interval closure against the 1-min file
    sec = ((ts - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).to_numpy()
    tm = pd.to_datetime(m["system_time"], utc=True)
    msec = ((tm - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).to_numpy()
    cs = np.concatenate([[0.0], np.cumsum(s["buys"].to_numpy())])
    csd = np.concatenate([[0.0], np.cumsum(np.where(same, 0.0, s["buys"].to_numpy()))])
    pos = pd.Series(np.arange(len(sec)), index=sec)
    pos = pos[~pos.index.duplicated()]
    out = {}
    for name, (lo, hi) in {"(T-60,T]": (-59, 0), "[T-60,T)": (-60, -1), "(T,T+60]": (1, 60)}.items():
        errs, errsd = [], []
        for T, b in zip(msec[5:2000], m["buys"].to_numpy()[5:2000]):
            if T + lo not in pos.index or T + hi not in pos.index:
                continue
            i0, i1 = pos[T + lo], pos[T + hi]
            if i1 - i0 != hi - lo:
                continue
            tot = cs[i1 + 1] - cs[i0]
            totd = csd[i1 + 1] - csd[i0]
            if b > 0:
                errs.append(abs(tot - b) / b)
                errsd.append(abs(totd - b) / b)
        out[name] = {"n": len(errs), "median_rel_err": float(np.median(errs)) if errs else None,
                     "share_exact_1e-6": float(np.mean(np.array(errs) < 1e-6)) if errs else None,
                     "median_rel_err_dedup": float(np.median(errsd)) if errsd else None,
                     "share_exact_dedup": float(np.mean(np.array(errsd) < 1e-6)) if errsd else None}
    r["closure_1min"] = out
    # (ii) lead/lag: corr(dmid_t, flow_{t+k})
    dmid = np.diff(np.log(s["midpoint"].to_numpy()))
    fl = flow[1:]
    fl_d = np.where(same.to_numpy()[1:], 0.0, fl)
    ll, lld = {}, {}
    for k in range(-3, 4):
        if k >= 0:
            a, b_, bd = dmid[: len(dmid) - k], fl[k:], fl_d[k:]
        else:
            a, b_, bd = dmid[-k:], fl[: len(fl) + k], fl_d[: len(fl_d) + k]
        ll[k] = float(np.corrcoef(a, b_)[0, 1])
        lld[k] = float(np.corrcoef(a, bd)[0, 1])
    r["corr_dmid_t_flow_t+k"] = ll
    r["corr_dmid_t_flow_t+k_dedup"] = lld
    res[asset] = r
    print(asset, json.dumps(r, indent=1), flush=True)
json.dump(res, open("/Users/pratik_n/Downloads/Machine_Markets_Master_Release/research_extension/paper_revision_20261006/results/recovered_timing_check.json", "w"), indent=1)

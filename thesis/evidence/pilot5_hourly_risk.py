"""EXPLORATORY Pilot 5 on the spent C3 symbols (not a registered test; nothing here is confirmatory evidence).

Pilot 4b found that the margin estimated on the previous 20 days forecasts the next day's risk out of sample (small
gains, Clark-West t between 3.6 and 4.9, not clustered by date). Paper 2's pre-registered thin-book results work at the
hourly horizon. Pilot 5 asks whether the thesis's own margin estimator works there too: the margin estimated on each
six-hour block of a valid day (hours 0-6, 6-12, 12-18) forecasts the next hour's maximum adverse excursion and realized
variance, beyond the block's realized variance and that of its last hour. Same pooled out-of-sample design as Test F1
(symbol fixed effects, first 60% of each symbol's blocks to fit, Clark-West differentials averaged within dates), four
variants: outcome in {log MAE, log RV} x margin in {winsorized, within-symbol rank}.
Usage (Colab): pilot5_hourly_risk.run(cache_dir, out_json)        Local test: python pilot5_hourly_risk.py --selftest
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402
import c2_margin_vs_identify as C2  # noqa: E402
import c3_margin_more_days as C3  # noqa: E402
import f1_flagship as F1  # noqa: E402

BLOCK, HOUR = 72, 12          # five-minute marks per six-hour block and per hour


def block_rows(df, sym, date):
    if C3.day_stats(df) is None:                       # C3's valid-day rule
        return []
    p1 = np.log(df["close"].to_numpy(float)) * 1e4
    fl = np.nan_to_num(df["flow"].to_numpy(float)); cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5)
    p, ret, flow = p1[m], p1[m] - p1[m - 5], cf[m + 1] - cf[m - 4]
    x = p - pd.Series(p).ewm(span=C3.SPAN, adjust=False).mean().to_numpy(); x[:C3.SPAN] = np.nan
    Xp = np.column_stack([flow, np.r_[np.nan, x[:-1]]]); Xk = C2.lags(x, C3.L)
    rows = []
    for b in range(3):
        idx = np.arange(b * BLOCK, (b + 1) * BLOCK)
        sp, sk = C2.ss(Xp[idx], ret[idx]), C2.ss(Xk[idx], flow[idx])
        if sp is None or sk is None:
            continue
        try:
            pr = np.linalg.solve(*sp); kx = np.linalg.solve(*sk)
        except np.linalg.LinAlgError:
            continue
        M = -pr[1] - pr[0] * kx.sum()
        nxt = np.arange((b + 1) * BLOCK, (b + 1) * BLOCK + HOUR)
        lo_min, hi_min = m[nxt[0]] - 5, m[nxt[-1]]
        seg = p1[lo_min:hi_min + 1]
        rows.append({"symbol": sym, "date": date, "block": b, "M": float(M),
                     "log_mae": np.log1p(float(np.max(np.maximum.accumulate(seg) - seg))),
                     "log_rv": np.log1p(float(np.sum(ret[nxt] ** 2))),
                     "log_rv_lag": np.log1p(float(np.sum(ret[idx[-HOUR:]] ** 2))),
                     "log_rv_trail": np.log1p(float(np.sum(ret[idx] ** 2)))})
    return rows


def load(cache_dir, symbols, dates, threads=16):
    rows = []
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s in symbols for d in dates}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            try:
                df, _ = f.result()
            except Exception:
                df = None
            if df is not None:
                rows += block_rows(df, s, d)
            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    return rows


def analyse(rows):
    d = pd.DataFrame(rows).sort_values(["symbol", "date", "block"])
    d["t"] = d.groupby("symbol").cumcount()
    d = d[np.isfinite(d["M"])]
    out = {}
    for y in ("log_mae", "log_rv"):
        for x in ("M_winsorized", "M_rank"):
            out[f"{y}|{x}"] = F1.pooled_forecast(d, y, x)
            print(y, x, json.dumps(out[f"{y}|{x}"]), flush=True)
    return {"n_symbols": int(d.symbol.nunique()), "n_blocks": int(len(d)), "variants": out}


def run(cache_dir, out_json, symbols=None):
    symbols = symbols or json.loads((HERE / "C3_universe.json").read_text())["symbols"]
    res = {"kind": "EXPLORATORY Pilot 5 (hourly risk forecast from six-hour margins on the spent C3 symbols); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), **analyse(load(cache_dir, symbols, C3.dates()))}
    Path(out_json).write_text(json.dumps(res, indent=1, default=float) + "\n")
    return res


def selftest():
    rng = np.random.default_rng(10); rows = []
    for j in range(5):
        for k, d in enumerate(pd.date_range("2025-01-01", periods=120).strftime("%Y-%m-%d")):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            rows += block_rows(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}), f"S{j}", d)
    out = analyse(rows)
    assert out["n_symbols"] == 5 and out["n_blocks"] > 1500 and all(v["evaluable"] for v in out["variants"].values())
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()

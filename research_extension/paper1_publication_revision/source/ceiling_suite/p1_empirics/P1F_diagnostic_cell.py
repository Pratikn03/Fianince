# P1F coverage diagnostic. Paste into a new Colab cell after cloning the repository. It reads ONLY two days that are
# OUTSIDE the P1F window and unused by any test (2022-02-27 and 2022-02-28), for BTCUSDT and ETHUSDT, and prints
# file structure and the bar-construction coverage per column. It computes no returns, forecasts or test statistics.
import sys, json, datetime as dt
sys.path.insert(0, '/content/Fianince/ceiling_suite/p1_empirics')
import p1f_executor as ex, pandas as pd, numpy as np
for day in (dt.date(2022, 2, 27), dt.date(2022, 2, 28)):
    for sym in ("BTCUSDT", "ETHUSDT"):
        s = day.isoformat()
        ktxt, kst = ex.get_zip_csv(f"{ex.BASE}/data/futures/um/daily/klines/{sym}/5m/{sym}-5m-{s}.zip")
        mtxt, mst = ex.get_zip_csv(f"{ex.BASE}/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{s}.zip")
        print(f"== {sym} {s} | klines {kst} | metrics {mst}")
        print("klines first line:", ktxt.split(chr(10))[0][:150])
        print("metrics first two lines:", mtxt.split(chr(10))[:2])
        k = ex.read_klines(ktxt); m = ex.read_metrics(mtxt)
        print("klines rows", len(k), "| metrics rows", len(m), "| metrics columns", list(m.columns))
        print("metrics non-null share:", {c: round(float(m[c].notna().mean()), 3) for c in m.columns})
        print("metrics create_time first/last:", m['create_time'].iloc[0], m['create_time'].iloc[-1])
        ex.WINDOW_START, ex.NDAYS = day, 1
        b = ex.to_bars(k, m)
        print("bar coverage by column:", {c: round(float(b[c].notna().mean()), 3) for c in b.columns})

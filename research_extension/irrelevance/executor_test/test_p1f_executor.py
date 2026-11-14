"""Offline test of p1f_executor on synthetic files in the Binance archive format (no market data).

Builds 5-minute klines and metrics for 30 symbols x 60 days from the design simulation's worlds, serves them through
a fake fetch (with CHECKSUM files, header and headerless klines, one missing day, a fake S3 listing), and checks
that the executor reproduces the simulated verdicts: NULL -> irrelevant, INFORMED -> relevant.
"""
import datetime as dt, hashlib, importlib.util, io, json, sys, zipfile
import numpy as np, pandas as pd

ROOT = "/home/claude/fianince/"
spec = importlib.util.spec_from_file_location("ex", ROOT + "ceiling_suite/p1_empirics/p1f_executor.py")
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)

def make_world(world, seed, S=30):
    rng = np.random.default_rng(seed)
    T5 = ex.NDAYS * 288
    a, kappa = 0.6, 0.06
    w = np.array([0.25, -0.15, 0.10]); hl = np.array([12.0, 60.0, 300.0]); lam = 0.5 ** (1 / hl)
    rho = np.array([0.8, 0.95, 0.99]); su = np.sqrt(1 - rho ** 2)
    beta = 0.18 if world == "INFORMED" else 0.0
    out = {}
    for s in range(S):
        df = 0.002 * rng.standard_normal(T5 + 6)
        f = np.cumsum(df)
        x = 0.0; u = np.zeros(3); e = np.zeros(3); P = np.zeros(3); r_prev = 0.0; p_prev = 0.0
        close = np.zeros(T5); flow = np.zeros(T5); Pm = np.zeros((T5, 3)); oi = np.zeros(T5)
        for t in range(T5):
            e = lam * e + (1 - lam) * r_prev / 0.002
            u = rho * u + su * rng.standard_normal(3)
            F = w * e + u
            F[0] += beta * df[t + 1:t + 7].sum() / 0.002     # informed about the next 30 minutes
            x = a * x + kappa * 0.002 * F.sum() + 0.0005 * rng.standard_normal()
            p = f[t] + x; r_prev = p - p_prev; p_prev = p
            P = 0.999 * P + F
            close[t] = 100 * np.exp(p); flow[t] = F.sum() * 1e5 + 2e4 * rng.standard_normal(); Pm[t] = P
            oi[t] = 1e8 * np.exp(0.01 * np.tanh(P.sum() / 200))
        out[f"S{s:02d}USDT"] = (close, flow, Pm, oi)
    return out

def build_files(world, seed):
    files = {}
    data = make_world(world, seed)
    t0 = pd.Timestamp(ex.WINDOW_START, tz="UTC")
    for sym, (close, flow, Pm, oi) in data.items():
        for d in range(ex.NDAYS):
            day = (ex.WINDOW_START + dt.timedelta(d)).isoformat()
            sl = slice(d * 288, (d + 1) * 288)
            ot = np.asarray([int((t0 + pd.Timedelta(minutes=5 * i)).timestamp() * 1000) for i in range(d * 288, (d + 1) * 288)])
            qv = 1e6 + np.abs(flow[sl]); tb = (qv + flow[sl]) / 2
            k = pd.DataFrame({"open_time": ot, "open": close[sl], "high": close[sl], "low": close[sl], "close": close[sl],
                              "volume": qv / close[sl], "close_time": ot + 299999, "quote_volume": qv, "count": 100,
                              "taker_buy_volume": tb / close[sl], "taker_buy_quote_volume": tb, "ignore": 0})
            ktxt = k.to_csv(index=False, header=(d % 2 == 0))      # alternate header / no header
            ct = [(t0 + pd.Timedelta(minutes=5 * (i + 1))).strftime("%Y-%m-%d %H:%M:%S") for i in range(d * 288, (d + 1) * 288)]
            R = np.exp(np.tanh(Pm[sl] / 60.0))                      # ratios in (1/e, e)
            m = pd.DataFrame({"create_time": ct, "symbol": sym, "sum_open_interest": oi[sl] / 100, "sum_open_interest_value": oi[sl],
                              "count_toptrader_long_short_ratio": R[:, 1], "sum_toptrader_long_short_ratio": R[:, 0],
                              "count_long_short_ratio": R[:, 2], "sum_taker_long_short_vol_ratio": 1.0})
            for kind, txt, url in (("k", ktxt, f"{ex.BASE}/data/futures/um/daily/klines/{sym}/5m/{sym}-5m-{day}.zip"),
                                   ("m", m.to_csv(index=False), f"{ex.BASE}/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{day}.zip")):
                if sym == "S03USDT" and d == 40 and kind == "m":
                    continue                                       # one missing file
                b = io.BytesIO()
                with zipfile.ZipFile(b, "w") as z: z.writestr(url.rsplit("/", 1)[1].replace(".zip", ".csv"), txt)
                blob = b.getvalue(); files[url] = blob
                files[url + ".CHECKSUM"] = (hashlib.sha256(blob).hexdigest() + "  x.zip\n").encode()
    return files

for world, seed, want in (("NULL", 1, "irrelevant"), ("INFORMED", 2, "relevant")):
    files = build_files(world, seed)
    ex.FETCH = lambda url, F=files: F.get(url)
    ex.LOG.clear()
    res = ex.run_all(f"/tmp/claude-0/p1f_test_{world}", syms=sorted({u.split('/')[8] for u in files if '/metrics/' in u}))
    a2 = res.get("A2_primary", {})
    print(world, "status", res["status"], "| gate", res.get("A3_power_gate"), "| A1", res.get("A1", {}).get("pass"),
          "| A2", a2.get("verdict"), round(a2.get("dR2", float('nan')), 5), "| expected", want, "| excluded", res["symbols_excluded"])

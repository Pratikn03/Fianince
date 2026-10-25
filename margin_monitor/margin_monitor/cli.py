"""Command line: margin-monitor data.csv --format trades|klines|bars [options]"""
import argparse
import json

import pandas as pd

from .core import bars_from_klines, bars_from_trades, certify, rolling_margin, throttle, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description="Certify a market's stability margin from prices and signed order flow.")
    ap.add_argument("csv")
    ap.add_argument("--format", choices=["trades", "klines", "bars"], default="trades",
                    help="trades: time, price, size, side; klines: open_time, close, quote_volume, taker_buy_quote_volume; "
                         "bars: time, p (log price in bp), f (signed flow)")
    ap.add_argument("--freq", default="5min"); ap.add_argument("--lags", type=int, default=12)
    ap.add_argument("--block", default="1D", help="bootstrap block for the full-sample certificate")
    ap.add_argument("--window", default="24h"); ap.add_argument("--step", default="1h")
    ap.add_argument("--buffer", type=float, default=0.1); ap.add_argument("--m-min", type=float, default=0.02)
    ap.add_argument("--m-max", type=float, default=0.10); ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    df = pd.read_csv(a.csv)
    if a.format == "trades":
        bars = bars_from_trades(df, freq=a.freq)
    elif a.format == "klines":
        bars = bars_from_klines(df, freq=a.freq)
    else:
        bars = df.assign(time=pd.to_datetime(df["time"], utc=True)).set_index("time")[["p", "f"]]
    cert = certify(bars, lags=a.lags, block=a.block)
    print(json.dumps(cert.to_dict(), indent=1))
    roll = warnings(rolling_margin(bars, window=a.window, step=a.step, lags=a.lags), buffer=a.buffer)
    roll["admit"] = [throttle(v, a.m_min, a.m_max) if pd.notna(v) else float("nan") for v in roll["lo"]]
    if a.out:
        roll.to_csv(a.out)
        print(f"rolling certificate written to {a.out} ({len(roll)} rows)")
    if len(roll):
        last = roll.iloc[-1]
        print(f"latest: margin {last['margin']:.4f} [{last['lo']:.4f}, {last['hi']:.4f}]  trend warning {bool(last['t2z'])}  "
              f"admit {last['admit']:.2f}")


if __name__ == "__main__":
    main()

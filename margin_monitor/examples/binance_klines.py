"""Certify a real market from Binance's public 1-minute klines (which report taker-buy volume).

Download a daily file by hand, e.g. https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1m/ , unzip it, and run
    python examples/binance_klines.py BTCUSDT-1m-2026-10-01.csv [more files ...]
A single day gives a wide interval; a week or more is better.
"""
import sys

import pandas as pd

from margin_monitor import bars_from_klines, certify

COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades",
        "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
k = pd.concat([pd.read_csv(f, header=None, names=COLS) for f in sys.argv[1:]])
if k["open_time"].max() > 1e14:                           # newer files use microseconds
    k["open_time"] //= 1000
bars = bars_from_klines(k, freq="5min")
print(certify(bars).to_dict())

"""P7S data layer (amendment A1): archive addresses, a cached downloader, parsers for the daily zip files and
assembly of one symbol on a complete 5-minute grid. This file computes no statistic.

File layout (schema probe of the burned day 2024-01-02, results/p7s_schema_probe_results.zip):
  klines 5m : open_time [ms], open, high, low, close, volume, close_time, quote_volume, count, ...   288 rows a day
  metrics   : create_time ['YYYY-MM-DD HH:MM:SS', UTC], symbol, sum_open_interest, sum_open_interest_value,
              count_toptrader_long_short_ratio, sum_toptrader_long_short_ratio, ...                   288 rows a day
Timing convention: the bar with open time t carries the return over [t, t + 5 min). Its state variables are the
metrics snapshot stamped t, which is taken before that return. A missing snapshot is filled forward for at most
30 minutes.
"""
from __future__ import annotations

import datetime as dt
import io
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

ROOT = "https://data.binance.vision/data/futures/um/daily"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
HEADERS = {"User-Agent": "Mozilla/5.0 (research data download)"}
BAR_MS = 300_000
BARS_PER_DAY = 288
FFILL_BARS = 6
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
           "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
# Excluded by name before ranking: bases that are stablecoins or fiat, and index products.
EXCLUDED_BASES = ("USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "EUR", "BTCDOM", "DEFI", "FOOTBALL", "BLUEBIRD")


def days(start: str, end: str) -> list[str]:
    a, b = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    return [(a + dt.timedelta(days=i)).isoformat() for i in range((b - a).days + 1)]


def shift_day(day: str, n: int) -> str:
    return (dt.date.fromisoformat(day) + dt.timedelta(days=n)).isoformat()


def day_start_ms(day: str) -> int:
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def kline_url(sym: str, day: str) -> str:
    q = urllib.parse.quote(sym)
    return f"{ROOT}/klines/{q}/5m/{q}-5m-{day}.zip"


def metrics_url(sym: str, day: str) -> str:
    q = urllib.parse.quote(sym)
    return f"{ROOT}/metrics/{q}/{q}-metrics-{day}.zip"


def candidate_symbols(folders: list[str]) -> list[str]:
    """USDT-margined perpetuals from the archive's folder names, after the exclusions by name."""
    out = []
    for s in folders:
        if not s.isascii() or not s.endswith("USDT") or "_" in s:
            continue
        if s[:-4] in EXCLUDED_BASES:
            continue
        out.append(s)
    return sorted(set(out))


def _read_zip_csv(raw: bytes, default_cols: list[str] | None) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = [n for n in z.namelist() if n.endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"expected one csv in the zip, found {names}")
        txt = z.read(names[0]).decode("utf-8")
    first = txt.split("\n", 1)[0].split(",")[0].strip()
    has_header = any(c.isalpha() for c in first)
    df = pd.read_csv(io.StringIO(txt), header=0 if has_header else None, float_precision="round_trip")
    if not has_header:
        if default_cols is None or df.shape[1] > len(default_cols):
            raise ValueError("file has no header and no default column names apply")
        df.columns = default_cols[: df.shape[1]]
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def parse_klines(raw: bytes) -> pd.DataFrame:
    """Columns: open_ms (int64, milliseconds), close, quote_volume. Microsecond stamps are converted."""
    df = _read_zip_csv(raw, KL_COLS)
    t = pd.to_numeric(df["open_time"], errors="coerce").astype("int64").to_numpy()
    if len(t) and t.max() > 10 ** 14:                           # microseconds
        t = t // 1000
    out = pd.DataFrame({"open_ms": t,
                        "close": pd.to_numeric(df["close"], errors="coerce").to_numpy(dtype="float64"),
                        "quote_volume": pd.to_numeric(df["quote_volume"], errors="coerce").to_numpy(dtype="float64")})
    return out


def parse_metrics(raw: bytes) -> pd.DataFrame:
    """Columns: ts_ms (stamp floored to the 5-minute grid), oi_value, top_ratio."""
    df = _read_zip_csv(raw, None)
    ts = pd.to_datetime(df["create_time"], utc=True, errors="coerce")
    ok = ts.notna().to_numpy()
    ms = ((ts[ok] - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(milliseconds=1)).to_numpy(dtype="int64")
    return pd.DataFrame({
        "ts_ms": (ms // BAR_MS) * BAR_MS,
        "oi_value": pd.to_numeric(df["sum_open_interest_value"], errors="coerce").to_numpy(dtype="float64")[ok],
        "top_ratio": pd.to_numeric(df["sum_toptrader_long_short_ratio"], errors="coerce").to_numpy(dtype="float64")[ok]})


def assemble(day_list: list[str], klines: dict[str, bytes | None], metrics: dict[str, bytes | None]) -> dict:
    """One symbol on the complete grid of `day_list` (consecutive days). Missing files or bars are NaN.
    Returns close, quote_volume, oi_value, top_ratio (each len(day_list) * 288) and counts of what was missing."""
    n = len(day_list) * BARS_PER_DAY
    t0 = day_start_ms(day_list[0])
    assert day_start_ms(day_list[-1]) - t0 == (len(day_list) - 1) * BARS_PER_DAY * BAR_MS, "days must be consecutive"
    close = np.full(n, np.nan); qv = np.full(n, np.nan); oi = np.full(n, np.nan); top = np.full(n, np.nan)
    miss_k = miss_m = 0
    for d in day_list:
        raw = klines.get(d)
        if raw is None:
            miss_k += 1
        else:
            k = parse_klines(raw)
            idx = (k["open_ms"].to_numpy() - t0) // BAR_MS
            ok = (idx >= 0) & (idx < n) & ((k["open_ms"].to_numpy() - t0) % BAR_MS == 0)
            close[idx[ok]] = k["close"].to_numpy()[ok]; qv[idx[ok]] = k["quote_volume"].to_numpy()[ok]
        raw = metrics.get(d)
        if raw is None:
            miss_m += 1
        else:
            m = parse_metrics(raw)
            idx = (m["ts_ms"].to_numpy() - t0) // BAR_MS
            ok = (idx >= 0) & (idx < n)
            oi[idx[ok]] = m["oi_value"].to_numpy()[ok]; top[idx[ok]] = m["top_ratio"].to_numpy()[ok]
    close[~(close > 0)] = np.nan
    oi[~(oi > 0)] = np.nan
    top[~(top > 0)] = np.nan
    raw_oi_bars = int(np.isfinite(oi).sum())
    oi = pd.Series(oi).ffill(limit=FFILL_BARS).to_numpy()
    top = pd.Series(top).ffill(limit=FFILL_BARS).to_numpy()
    return {"close": close, "quote_volume": qv, "oi_value": oi, "top_ratio": top,
            "missing_kline_files": miss_k, "missing_metrics_files": miss_m,
            "kline_bar_coverage": float(np.isfinite(close).mean()), "metrics_bar_coverage": raw_oi_bars / n}


def parse_listing(xml_text: str) -> tuple[list[str], str | None]:
    """(folder names, next marker or None) from one page of the bucket listing."""
    root = ET.fromstring(xml_text)
    ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
    names = [e.find(ns + "Prefix").text for e in root.findall(ns + "CommonPrefixes")]
    trunc = root.find(ns + "IsTruncated")
    nxt = root.find(ns + "NextMarker")
    more = trunc is not None and trunc.text == "true"
    return names, ((nxt.text if nxt is not None else (names[-1] if names else None)) if more else None)


def listing_has_key(xml_text: str, key: str) -> bool:
    """True if a bucket listing page names exactly this file."""
    root = ET.fromstring(xml_text)
    ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
    return any(e.find(ns + "Key") is not None and e.find(ns + "Key").text == key for e in root.findall(ns + "Contents"))


class Archive:
    """Downloader with a disk cache. `get` returns the file's bytes, or None if the archive does not have the file:
    a 404 answer, or a 403 answer for a file that the bucket listing does not name. Any other failure is retried
    and then raised, so a network problem is never read as a missing file."""

    def __init__(self, cache_dir: str, threads: int = 32, retries: int = 6):
        self.cache_dir, self.threads, self.retries = cache_dir, threads, retries
        self.n_downloaded = self.n_cached = self.n_absent = 0

    def _path(self, url: str) -> str:
        return os.path.join(self.cache_dir, urllib.parse.unquote(url.split("/data/futures/um/daily/")[1]))

    def get(self, url: str) -> bytes | None:
        p = self._path(url)
        if os.path.exists(p):
            self.n_cached += 1
            return open(p, "rb").read()
        if os.path.exists(p + ".404"):
            self.n_absent += 1
            return None
        os.makedirs(os.path.dirname(p), exist_ok=True)
        last = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
                    raw = r.read()
                with zipfile.ZipFile(io.BytesIO(raw)) as z:      # a truncated download fails here and is retried
                    z.namelist()
                tmp = p + ".part"
                open(tmp, "wb").write(raw); os.replace(tmp, p)
                self.n_downloaded += 1
                return raw
            except urllib.error.HTTPError as e:
                if e.code == 404 or (e.code == 403 and not self._listed(url)):
                    open(p + ".404", "w").close()
                    self.n_absent += 1
                    return None
                last = e
            except Exception as e:                               # noqa: BLE001
                last = e
            time.sleep(min(30, 2 ** attempt))
        raise RuntimeError(f"download failed after {self.retries} tries: {url}: {last!r}")

    def _listed(self, url: str) -> bool:
        """Asks the bucket listing whether the file exists. A failure of the listing request raises."""
        key = urllib.parse.unquote(url.split("data.binance.vision/")[1])
        q = f"{S3}?prefix={urllib.parse.quote(key)}"
        with urllib.request.urlopen(urllib.request.Request(q, headers=HEADERS), timeout=60) as r:
            return listing_has_key(r.read().decode(), key)

    def get_many(self, urls: list[str]) -> dict[str, bytes | None]:
        with ThreadPoolExecutor(self.threads) as pool:
            return dict(zip(urls, pool.map(self.get, urls)))

    def list_symbol_folders(self) -> list[str]:
        prefix = "data/futures/um/daily/klines/"
        out, marker = [], None
        for _ in range(100):
            url = f"{S3}?delimiter=/&prefix={urllib.parse.quote(prefix)}"
            if marker:
                url += "&marker=" + urllib.parse.quote(marker)
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
                names, marker = parse_listing(r.read().decode())
            out += names
            if marker is None:
                break
        return [n[len(prefix):].strip("/") for n in out]

"""Download and parse Binance USD-M futures daily archives from data.binance.vision.

Shared by the E1v2 pipeline and the E2 analysis. The parsing code is the code of the Paper 1 and
Paper 2 notebooks (Part 6, cells Z0-Z1), unchanged except that the archive root, the cache folder
and a local source for tests are configurable:

  E1V2_LOCAL_ROOT / BV_LOCAL_ROOT   read zip files from this folder instead of the network (tests)
  cache_dir                          minute frames are cached as parquet (or pickle) per symbol-day

Every downloaded file is checked against Binance's published .CHECKSUM and its SHA-256 is logged.
"""

import hashlib
import io
import math
import os
import re
import time
import urllib.error
import urllib.request
import zipfile

import numpy as np
import pandas as pd

ROOT = "https://data.binance.vision/data/futures/um/daily"
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
           "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
NEED_BANDS = [-5, -2, -1, 1, 2, 5]
DL_LOG = []


def local_root():
    return os.environ.get("BV_LOCAL_ROOT") or os.environ.get("E1V2_LOCAL_ROOT")


def _http(url, method="GET", timeout=60, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, (r.read() if method == "GET" else b"")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return e.code, b""
            last = e
        except Exception as e:  # network hiccup: back off and retry
            last = e
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"network error {url}: {last}")


def ds_url(ds, sym, date):
    if ds == "klines":
        return f"{ROOT}/klines/{sym}/1m/{sym}-1m-{date}.zip"
    return f"{ROOT}/{ds}/{sym}/{sym}-{ds}-{date}.zip"


def fetch(ds, sym, date):
    """Zip bytes, checked against Binance's .CHECKSUM when available; None if the file is missing."""
    lr = local_root()
    if lr:
        path = os.path.join(lr, ds, sym, os.path.basename(ds_url(ds, sym, date)))
        if not os.path.exists(path):
            return None
        raw = open(path, "rb").read()
        DL_LOG.append({"ds": ds, "symbol": sym, "date": date, "sha256": hashlib.sha256(raw).hexdigest(),
                       "checksum_verified": None, "source": "local"})
        return raw
    url = ds_url(ds, sym, date)
    code, raw = _http(url, timeout=180)
    if code != 200:
        return None
    sha = hashlib.sha256(raw).hexdigest()
    c2, chk = _http(url + ".CHECKSUM", timeout=30)
    verified = None
    if c2 == 200 and chk:
        if chk.decode().split()[0] != sha:
            raise RuntimeError(f"SHA-256 mismatch {url}")
        verified = True
    DL_LOG.append({"ds": ds, "symbol": sym, "date": date, "sha256": sha, "checksum_verified": verified})
    return raw


def read_zip_csv(raw, default_cols=None):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        txt = z.read(name).decode("utf-8", errors="ignore")
    first = txt.split("\n", 1)[0]
    has_header = bool(re.search(r"[A-Za-z_]", first.split(",")[0]))
    df = pd.read_csv(io.StringIO(txt), header=0 if has_header else None)
    if not has_header and default_cols is not None:
        df.columns = default_cols[:df.shape[1]]
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def to_utc_seconds(col):
    s = pd.Series(col)
    if pd.api.types.is_numeric_dtype(s):
        v = s.astype("int64").to_numpy()
        return np.where(v > 1e14, v // 1_000_000, np.where(v > 1e11, v // 1000, v))
    ts = pd.to_datetime(s, utc=True)
    return ((ts - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).astype("int64").to_numpy()


def nice_tick(x):
    if not np.isfinite(x) or x <= 0:
        return np.nan
    e = math.floor(math.log10(x)); m = x / 10 ** e
    c = min([1, 2, 5, 10], key=lambda v: abs(math.log(m / v)))
    return c * 10 ** e


def infer_tick(k):
    v = np.unique(np.round(k[["open", "high", "low", "close"]].astype(float).to_numpy().ravel(), 10))
    dv = np.diff(v); dv = dv[dv > 0]
    return nice_tick(np.quantile(dv, 0.02)) if len(dv) > 5 else np.nan


def validated_snapshots(sym, date, close_by_minute, t0):
    """Validated bookDepth snapshots: DataFrame indexed by second with bid/ask notional at 1,2,5% ($M)."""
    raw = fetch("bookDepth", sym, date)
    if raw is None:
        return None, {"snapshots": 0}
    b = read_zip_csv(raw)
    b["sec"] = to_utc_seconds(b["timestamp"])
    b["percentage"] = pd.to_numeric(b["percentage"], errors="coerce").round().astype("Int64")
    piv_n = b.pivot_table(index="sec", columns="percentage", values="notional", aggfunc="last")
    piv_d = b.pivot_table(index="sec", columns="percentage", values="depth", aggfunc="last")
    n0 = len(piv_n)
    ok = piv_n.reindex(columns=NEED_BANDS).notna().all(axis=1) & piv_d.reindex(columns=NEED_BANDS).notna().all(axis=1)
    piv_n, piv_d = piv_n[ok], piv_d[ok]
    mono = (piv_d[-2] >= piv_d[-1]) & (piv_d[-5] >= piv_d[-2]) & (piv_d[2] >= piv_d[1]) & (piv_d[5] >= piv_d[2])
    minute = ((piv_n.index.to_numpy() - t0) // 60).clip(0, 1439)
    ref = close_by_minute[minute]
    imp_b, imp_a = piv_n[-1] / piv_d[-1], piv_n[1] / piv_d[1]
    price_ok = (np.abs(imp_b / ref - 1) < 0.03) & (np.abs(imp_a / ref - 1) < 0.03)
    sig = piv_n[NEED_BANDS].round(2).astype(str).agg("|".join, axis=1)
    runlen = sig.groupby((sig != sig.shift()).cumsum()).transform("size")
    not_stale = runlen <= 10
    good = mono & price_ok & not_stale
    g = piv_n[good]
    snap = pd.DataFrame({"bid1": g[-1], "ask1": g[1], "bid2": g[-2], "ask2": g[2], "bid5": g[-5], "ask5": g[5]}) / 1e6
    st = {"snapshots": n0, "drop_V1": int((~ok).sum()), "drop_V2": int((~mono).sum()),
          "drop_V3": int((~price_ok).sum()), "drop_V4": int((~not_stale).sum())}
    return snap, st


def build_day(sym, date, depth=True):
    """Minute frame for one symbol-day: close, signed taker flow ($M), volume, depth bands, metrics."""
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    idx = np.arange(1440)
    raw = fetch("klines", sym, date)
    if raw is None:
        return None, {"symbol": sym, "date": date, "reason": "no klines"}
    k = read_zip_csv(raw, KL_COLS)
    tick = infer_tick(k)
    k = k.assign(m=(to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(idx)
    out = pd.DataFrame(index=idx)
    out["close"] = k["close"].astype(float).ffill().bfill()
    out["flow"] = (2 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)).fillna(0) / 1e6
    out["vol"] = k["quote_volume"].astype(float).fillna(0) / 1e6
    st = {"symbol": sym, "date": date, "tick": tick}
    for c in ["bid1", "ask1", "bid2", "ask2", "bid5", "ask5"]:
        out[c] = np.nan
    if depth:
        snap, s2 = validated_snapshots(sym, date, out["close"].to_numpy(), t0)
        st.update(s2)
        if snap is not None and len(snap):
            mm = ((snap.index.to_numpy() - t0) // 60).clip(0, 1439)
            sm = snap.assign(m=mm).groupby("m").last().reindex(idx).ffill(limit=2)
            for c in snap.columns:
                out[c] = sm[c].to_numpy()
        st["minute_coverage"] = float(out["bid1"].notna().mean())
        st["depth_day_ok"] = st["minute_coverage"] >= 0.80
    for c in ["oi", "top_pos_ratio", "top_acc_ratio", "acc_ratio", "taker_ratio"]:
        out[c] = np.nan
    raw = fetch("metrics", sym, date)
    st["metrics"] = raw is not None
    if raw is not None:
        mt = read_zip_csv(raw)
        tcol = "create_time" if "create_time" in mt.columns else mt.columns[0]
        mm = ((to_utc_seconds(mt[tcol]) - t0) // 60).clip(0, 1439)
        for c, src, scale in [("oi", "sum_open_interest_value", 1e6),
                              ("top_pos_ratio", "sum_toptrader_long_short_ratio", 1.0),
                              ("top_acc_ratio", "count_toptrader_long_short_ratio", 1.0),
                              ("acc_ratio", "count_long_short_ratio", 1.0),
                              ("taker_ratio", "sum_taker_long_short_vol_ratio", 1.0)]:
            if src in mt.columns:
                s = pd.Series(pd.to_numeric(mt[src], errors="coerce").to_numpy() / scale, index=mm)
                out[c] = s.groupby(level=0).last().reindex(idx).to_numpy()   # 5-min values, not filled
    out["symbol"], out["date"] = sym, date
    return out, st


def get_day(sym, date, cache_dir=None, depth=True):
    """build_day with an optional on-disk cache (pickle, so no pyarrow is needed)."""
    if cache_dir:
        d_ = os.path.join(cache_dir, sym); os.makedirs(d_, exist_ok=True)
        pk = os.path.join(d_, f"{date}{'' if depth else '_nodepth'}.pkl")
        if os.path.exists(pk):
            return pd.read_pickle(pk)
    out = build_day(sym, date, depth=depth)
    if cache_dir:
        pd.to_pickle(out, pk)
    return out

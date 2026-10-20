# ============================================================================
# CELL V0 — SETUP (self-contained; run first, every time you open the notebook)
# Part 10 (Paper 2): Bybit with REAL ORDER-BOOK DEPTH. Bybit's historical order-book files (ob200: a full-day snapshot
# plus every update to the top 200 levels), downloaded by hand from bybit.com/derivatives/en/history-data
# (Product Line: Contract, Data category: OB Data) and uploaded here. Trades come from Bybit's free archive
# (public.bybit.com, already used in Part 7). Same statistic and same baseline as Part 9.
# Part 7 tested Bybit with trades only and FAILED; this test is reported next to it, never instead of it.
# ============================================================================
import os, sys, json, time, math, glob, re, io, zipfile, hashlib, subprocess, warnings, gzip, shutil
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

IN_COLAB = "google.colab" in sys.modules
try:
    import pyarrow  # noqa: F401
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyarrow"], check=True)
import numpy as np
import pandas as pd
from scipy import stats, optimize
warnings.filterwarnings("ignore", category=RuntimeWarning)

if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    BASE = "/content/drive/MyDrive/ceiling_suite"
    UPLOAD_DIRS = ["/content/bybit_ob", os.path.join(BASE, "bybit_ob")]     # put the .zip files in either folder
else:
    BASE = os.path.abspath("ceiling_suite_local")
    UPLOAD_DIRS = [os.path.abspath("bybit_ob")]
RESULTS, PREREG = os.path.join(BASE, "results"), os.path.join(BASE, "prereg")
OBMIN = os.path.join(BASE, "data_bybit_ob", "book_minute")      # small per-day summaries (about 100 KB each)
TRMIN = os.path.join(BASE, "data_bybit_ob", "trade_minute")
for _d in [RESULTS, PREREG, OBMIN, TRMIN] + UPLOAD_DIRS:
    os.makedirs(_d, exist_ok=True)

SEED = 20261026
def rng(offset=0):
    return np.random.default_rng(SEED + offset)

def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o

def record(test_id, passed, kind, metrics, criterion="", note=""):
    assert kind in {"theorem-check", "simulation", "real-data", "audit"}, kind
    status = "REPORT" if passed is None else ("PASS" if passed else "FAIL")
    out = {"test_id": test_id, "status": status, "kind": kind, "criterion": criterion, "note": note,
           "metrics": _clean(metrics), "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "seed": SEED}
    with open(os.path.join(RESULTS, f"{test_id}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"[{status}] {test_id} ({kind})" + (f" — {criterion}" if criterion else ""))
    if note:
        print("        note:", note)
    return out

# ---- Design (fixed before any test-day file is opened) -------------------------------------------
COINS = ["ACH", "ALICE", "API3", "ARPA", "CELR", "CHR", "CVX", "GTC", "HOT", "ICX", "IOST", "IOTX", "LIT", "OGN", "QNT",
         "RLC", "SPELL", "T", "WOO", "ZEN"]                      # the 20 Binance thin-set coins of Parts 6 and 9
BATCHES = {"A": COINS[0:5], "B": COINS[5:10], "C": COINS[10:15], "D": COINS[15:20]}
# Days 11-16 of a month: never a test day in Part 7 (3, 10, 17, 24) or Part 9 (6, 20); contiguous so that one
# Bybit date-range download covers a whole window.
def _win(y, m):
    return [f"{y}-{m:02d}-{d:02d}" for d in range(11, 17)]
TRAIN_WINDOWS = [(2024, 3), (2024, 9)]
TEST_WINDOWS = [(2025, 1), (2025, 5), (2025, 9), (2026, 1), (2026, 5), (2026, 9)]
TRAIN_D = [d for y, m in TRAIN_WINDOWS for d in _win(y, m)]
TEST_D = [d for y, m in TEST_WINDOWS for d in _win(y, m)]
TRAIN_END = "2024-12-31"
THREADS = 8
print("BASE =", BASE, "| train days", len(TRAIN_D), "| test days", len(TEST_D))

BYBIT = "https://public.bybit.com/trading"
def _http(url, method="GET", timeout=120, tries=3):
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
        except Exception as e:
            last = e
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"network error {url}: {last}")
def bb_url(sym, date):
    return f"{BYBIT}/{sym}/{sym}{date}.csv.gz"
code, _ = _http(bb_url("BTCUSDT", "2024-06-10"), "HEAD", timeout=30)
print("Bybit trade archive reachable:", code == 200, f"(HTTP {code})")
assert code == 200, "public.bybit.com is not reachable from this runtime; tell Claude."
DL_LOG = []

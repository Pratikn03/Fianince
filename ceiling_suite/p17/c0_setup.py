# ============================================================================
# CELL C0 — SETUP (self-contained; run first)
# Part 17 (Paper 2): A NEW VENUE AND AN ORDER-SPLITTING PLACEBO.
# Coinbase Exchange spot (a US-regulated venue never used in Parts 1-16), public trade data only (no account, no keys).
# Two pre-registered primaries: (1) the depth-free amplification margin forecasts the next hour's adverse excursion beyond a
# volatility and impact baseline in thin Coinbase pairs; (2) the real statistic beats an ORDER-SPLITTING PLACEBO computed from
# the same flow with its minute alignment to prices broken (same flow distribution and persistence).
# ============================================================================
import os, sys, json, time, math, io, zipfile, hashlib, subprocess, warnings, threading
import urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

IN_COLAB = "google.colab" in sys.modules
try:
    import pyarrow  # noqa: F401
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyarrow"], check=True)
import numpy as np
import pandas as pd
from scipy import stats
warnings.filterwarnings("ignore", category=RuntimeWarning)

USE_DRIVE = True
if IN_COLAB and USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    BASE = "/content/drive/MyDrive/ceiling_suite"
elif IN_COLAB:
    BASE = "/content/ceiling_suite"
else:
    BASE = os.path.abspath("ceiling_suite_local")
RESULTS, PREREG = os.path.join(BASE, "results"), os.path.join(BASE, "prereg")
CDATA = os.path.join(BASE, "data_coinbase")
for _d in (RESULTS, PREREG, CDATA, os.path.join(CDATA, "minute"), os.path.join(CDATA, "bounds")):
    os.makedirs(_d, exist_ok=True)

SEED = 20261117
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
           "metrics": _clean(metrics), "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED}
    with open(os.path.join(RESULTS, f"{test_id}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"[{status}] {test_id} ({kind})" + (f" — {criterion}" if criterion else ""))
    return out

# ---- Calendar (fixed here, before anything is downloaded) -------------------------------------
TRAIN_DAYS = [d.strftime("%Y-%m-%d") for d in pd.date_range("2024-01-01", "2024-12-31") if d.day in (10, 24)]
TEST_DAYS = [d.strftime("%Y-%m-%d") for d in pd.date_range("2025-01-01", "2026-09-30") if d.day in (6, 20)]
TRAIN_END = "2024-12-31"
HOURS_EVAL = list(range(6, 24))          # forecast hours (UTC); features from [t-360, t), outcome over (t, t+60]
PLACEBO_SHIFT = 180                      # minutes; circular shift of flow inside the 360-minute window
print(f"BASE = {BASE} | {len(TRAIN_DAYS)} training and {len(TEST_DAYS)} test days")

# ---- HTTP with a shared rate limit (Coinbase public endpoints: 10 requests/s per IP; we use 7) ----
API = "https://api.exchange.coinbase.com"
_lock = threading.Lock(); _last = [0.0]; RATE = 7.0
def _throttle():
    with _lock:
        wait = _last[0] + 1.0 / RATE - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
N_REQ = [0]
def api(path, params=None, tries=8):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    last = None
    for i in range(tries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-replication/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                N_REQ[0] += 1
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                return None
            time.sleep(min(30, 1.5 * 2 ** i) if e.code == 429 else 1.5 * (i + 1))
        except Exception as e:
            last = e; time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"API error {url}: {last}")

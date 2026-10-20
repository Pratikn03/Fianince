# ============================================================================
# CELL U0 — SETUP (self-contained; run first; same code as Parts 9, 12, 15 and 16)
# Part 18 (Paper 2): POST-HOC CHECKS ON DATA ALREADY OPENED. Everything here is labelled post hoc in the paper.
#   (A) Order-splitting placebo on the Binance forecasting samples of Part 9 (20 thin symbols) and Part 16 (5 new thin symbols):
#       C3 recomputed with the flow series circularly shifted inside its six-hour window (same flow distribution and
#       persistence, minute alignment with prices broken). Does the real statistic beat the placebo?
#   (B) Three more guard baselines on the Part 15 and Part 16 guard samples: a certified PEAK-response guard, a PARTICIPATION
#       cap (position proportional to the last six hours' volume) and a MARGIN-style rule (exchange-style scanning range from
#       the three certification days). Does the uncertainty-aware guard beat them at matched activity?
# Needs the Drive cache from Parts 9, 15 and 16 (ceiling_suite/data_xsec); anything missing is re-downloaded.
# ============================================================================
import os, sys, json, time, math, glob, re, io, zipfile, hashlib, subprocess, warnings, zlib
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET

IN_COLAB = "google.colab" in sys.modules
try:
    import pyarrow  # noqa: F401
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyarrow"], check=True)
import numpy as np
import pandas as pd
from scipy import stats, optimize
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
XDATA = os.path.join(BASE, "data_xsec")
for _d in (RESULTS, PREREG, XDATA):
    os.makedirs(_d, exist_ok=True)

SEED = 20261031
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

def boot_ci(v, R, B=2000, stat=np.mean):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if len(v) < 3:
        return [np.nan, np.nan]
    bs = [stat(v[R.integers(0, len(v), len(v))]) for _ in range(B)]
    return [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]

# ---- Sample design --------------------------------------------------------------------------
FRESH_DAYS_OF_MONTH = (6, 20)   # never used in Parts 1-8
FRESH_START, FRESH_END = "2025-01-01", "2026-09-30"
N_SYMBOLS = 30                  # symbols in the cross-section, spread across liquidity (BTC and ETH always in)
PANEL_DAYS_OF_MONTH = (10, 24)  # same panel design as Part 1
PANEL_START, PANEL_END = "2023-01-01", "2026-09-30"
TRAIN_END, TEST_START = "2024-12-31", "2025-01-01"
LIQ_RANK_DATE = "2024-06-10"    # liquidity ranking day for choosing symbols (training period)
THREADS = 12
ROOT = "https://data.binance.vision/data/futures/um/daily"
print("BASE =", BASE)

def _http(url, method="GET", timeout=60, tries=3):
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

def ds_url(ds, sym, date):
    if ds == "klines":
        return f"{ROOT}/klines/{sym}/1m/{sym}-1m-{date}.zip"
    return f"{ROOT}/{ds}/{sym}/{sym}-{ds}-{date}.zip"

def exists(ds, sym, date):
    return _http(ds_url(ds, sym, date), "HEAD", timeout=20)[0] == 200

DL_LOG = []
def fetch(ds, sym, date):
    """Zip bytes, checked against Binance's published .CHECKSUM when available; None if missing."""
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

def panel_dates(start=PANEL_START, end=PANEL_END):
    ds = pd.date_range(start, end, freq="D")
    return [d.strftime("%Y-%m-%d") for d in ds if d.day in PANEL_DAYS_OF_MONTH]

def fresh_dates(start=FRESH_START, end=FRESH_END):
    ds = pd.date_range(start, end, freq="D")
    return [d.strftime("%Y-%m-%d") for d in ds if d.day in FRESH_DAYS_OF_MONTH]
def train_dates():
    return [d for d in panel_dates() if d <= TRAIN_END]

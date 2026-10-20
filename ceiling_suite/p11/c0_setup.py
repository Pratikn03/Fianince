# ============================================================================
# CELL C0 — SETUP (self-contained; run first)
# Part 11 (Paper 1): a SECOND DISCLOSURE REGIME. The CFTC's weekly Commitments of Traders reports publish positions by
# trader class (leveraged funds, asset managers, dealers; managed money, producers, swap dealers) for regulated US futures.
# This is legally mandated class-tagged disclosure, in a different market and under a different regulator than Binance.
# ============================================================================
import os, sys, json, time, io, zipfile, hashlib, subprocess, warnings, glob
import urllib.request, urllib.error, urllib.parse
IN_COLAB = "google.colab" in sys.modules
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore", category=RuntimeWarning)
if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    BASE = "/content/drive/MyDrive/ceiling_suite"
else:
    BASE = os.path.abspath("ceiling_suite_local")
RESULTS, PREREG = os.path.join(BASE, "results"), os.path.join(BASE, "prereg")
CDIR = os.path.join(BASE, "data_cot")
for _d in (RESULTS, PREREG, CDIR):
    os.makedirs(_d, exist_ok=True)
SEED = 20261027

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
    status = "REPORT" if passed is None else ("PASS" if passed else "FAIL")
    out = {"test_id": test_id, "status": status, "kind": kind, "criterion": criterion, "note": note,
           "metrics": _clean(metrics), "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED}
    json.dump(out, open(os.path.join(RESULTS, f"{test_id}.json"), "w"), indent=2)
    print(f"[{status}] {test_id} ({kind})" + (f" — {criterion}" if criterion else ""))
    return out

def _http(url, timeout=120, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404):
                return e.code, b""
            last = e
        except Exception as e:
            last = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"network error {url}: {last}")

# ---- Markets (fixed before any data are downloaded) -------------------------------------------
# report: TFF = Traders in Financial Futures (futures only); DIS = Disaggregated (futures only)
# fast class = leveraged funds / managed money; slow class = asset managers / producer-merchants
MARKETS = {
    "BTC": {"code": "133741", "report": "TFF", "price": ("binance", "BTCUSDT")},
    "ETH": {"code": "146021", "report": "TFF", "price": ("binance", "ETHUSDT")},
    "ES":  {"code": "13874A", "report": "TFF", "price": ("yahoo", "^GSPC")},
    "TY":  {"code": "043602", "report": "TFF", "price": ("yahoo_yield", "^TNX")},
    "EUR": {"code": "099741", "report": "TFF", "price": ("yahoo", "EURUSD=X")},
    "JPY": {"code": "097741", "report": "TFF", "price": ("yahoo_inverse", "JPY=X")},
    "CL":  {"code": "067651", "report": "DIS", "price": ("yahoo", "CL=F")},
    "NG":  {"code": "023651", "report": "DIS", "price": ("yahoo", "NG=F")},
}
SOCRATA = {"TFF": "https://publicreporting.cftc.gov/resource/gpe5-46if.json",
           "DIS": "https://publicreporting.cftc.gov/resource/72hh-3qpy.json"}
CLASSES = {"TFF": {"fast": ("lev_money_positions_long", "lev_money_positions_short"),
                   "slow": ("asset_mgr_positions_long", "asset_mgr_positions_short"),
                   "dealer": ("dealer_positions_long_all", "dealer_positions_short_all")},
           "DIS": {"fast": ("m_money_positions_long_all", "m_money_positions_short_all"),
                   "slow": ("prod_merc_positions_long", "prod_merc_positions_short"),
                   "dealer": ("swap_positions_long_all", "swap__positions_short_all")}}
END_DATE = "2026-10-13"
code, _ = _http(SOCRATA["TFF"] + "?$limit=1", timeout=60)
print("CFTC public reporting API reachable:", code == 200, f"(HTTP {code})")
try:
    import yfinance as yf
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yfinance"], check=True)
    import yfinance as yf
_t = yf.download("EURUSD=X", start="2024-01-01", end="2024-02-01", progress=False, auto_adjust=False)
print("Yahoo Finance reachable:", len(_t) > 10, f"({len(_t)} rows)")
code2, _ = _http("https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-2024-01.zip", timeout=60)
print("Binance archive reachable:", code2 == 200, f"(HTTP {code2})")
assert code == 200 and code2 == 200 and len(_t) > 10, "a data source is not reachable from this runtime; tell Claude."

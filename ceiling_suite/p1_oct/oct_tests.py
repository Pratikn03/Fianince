# ============================================================================
# P1O: pre-specified October 2026 Binance tests for Paper 1 (N2 feedback beyond persistence, N3 combined response
# from flow). Specification: prereg/P1O_october2026.json (SHA-256 checked below; committed before the run).
#
# Colab:  !git clone https://github.com/Pratikn03/Fianince.git
#         %cd Fianince/ceiling_suite/p1_oct
#         %run oct_tests.py
# Output: <BASE>/results/P1O_data_audit.json, P1O_N2_feedback.json, P1O_N3_combined.json,
#         <BASE>/prereg/P1O_unlocks.json and <BASE>/p1o_results.zip. Run it once.
# Dry run on synthetic data (no network, no unlock counter): set the environment variable P1O_DRYRUN=1.
# ============================================================================
import os, sys, json, time, hashlib, zipfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "thesis", "evidence")))
from oct_core import feedback_oos, combined_response   # noqa: E402

DRY = os.environ.get("P1O_DRYRUN") == "1"
IN_COLAB = "google.colab" in sys.modules
if IN_COLAB and not DRY:
    from google.colab import drive
    drive.mount("/content/drive")
    BASE = "/content/drive/MyDrive/ceiling_suite"
else:
    BASE = os.path.abspath("p1o_dryrun_output" if DRY else "ceiling_suite_local")
RESULTS, PREREG, CACHE = (os.path.join(BASE, d) for d in ("results", "prereg", "data_p1o"))
for d_ in (RESULTS, PREREG, CACHE):
    os.makedirs(d_, exist_ok=True)

SPEC_PATH = os.path.join(HERE, "prereg", "P1O_october2026.json")
SPEC_SHA256 = "72cbc8ba7340b1d7bf7b3eb6fd7dfb7bb859d6c8fc7967f7c53ea856e87bca86"
assert hashlib.sha256(open(SPEC_PATH).read().encode()).hexdigest() == SPEC_SHA256, "specification changed"
SPEC = json.load(open(SPEC_PATH))
SYMBOLS = SPEC["data"]["symbols_in_order"]
DATES = [str(d.date()) for d in pd.date_range("2026-10-01", "2026-10-30", freq="D")]
SEED = SPEC["seed"]


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def record(name, obj):
    obj = dict(obj, spec_sha256=SPEC_SHA256, dry_run=DRY, timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    json.dump(_clean(obj), open(os.path.join(RESULTS, name + ".json"), "w"), indent=2)


# ---------------------------------------------------------------------------- data
def synthetic_day(sym, date):
    """Dry-run stand-in for binance_vision.get_day: same columns, synthetic values with a known feedback effect."""
    R = np.random.default_rng(abs(hash((sym, date, SEED))) % 2**32)
    n = 1440
    ret = R.standard_t(5, n) * 4e-4
    close = 100 * np.exp(np.cumsum(ret))
    vol = R.uniform(1, 2, n)
    flow = vol * np.clip(0.05 * np.r_[np.zeros(5), np.convolve(ret, np.ones(60) / 60)[:n - 5]] / 4e-4 * 0.3
                         + R.normal(0, 0.3, n), -0.99, 0.99)
    out = pd.DataFrame({"close": close, "flow": flow, "vol": vol})
    pos = np.full(n, np.nan); y = 0.0
    for m in range(0, n, 5):
        y = 0.95 * y + 40 * (np.log(close[m - 1]) - np.log(close[max(m - 6, 0)]) if m >= 6 else 0) + R.normal(0, 0.01)
        pos[m] = np.exp(y)
    out["top_pos_ratio"] = pos
    out["symbol"], out["date"] = sym, date
    return out, {"symbol": sym, "date": date, "metrics": True}


def load_day(sym, date):
    if DRY:
        return synthetic_day(sym, date)
    import binance_vision as bv
    return bv.get_day(sym, date, cache_dir=CACHE, depth=False)


def build_panel(sym):
    """5-minute grid for one symbol over the 30 days: r, dy, x (NaN where missing) and the day index."""
    frames, days_ok = [], 0
    for di, date in enumerate(DATES):
        fr, st = load_day(sym, date)
        if fr is None:
            fr = pd.DataFrame({"close": np.full(1440, np.nan), "flow": np.nan, "vol": np.nan, "top_pos_ratio": np.nan})
        elif st.get("metrics") and fr["top_pos_ratio"].notna().any():
            days_ok += 1
        frames.append(fr[["close", "flow", "vol", "top_pos_ratio"]].reset_index(drop=True))
    M = pd.concat(frames, ignore_index=True)                         # global minute index
    close = M["close"].to_numpy(float); flow = M["flow"].to_numpy(float); vol = M["vol"].to_numpy(float)
    ratio = M["top_pos_ratio"].to_numpy(float)
    G = np.arange(5, len(M), 5)                                       # snapshot minutes (first one skipped)
    p = np.log(close[G - 1])
    y = np.log(np.where(ratio[G] > 0, ratio[G], np.nan))
    r = np.r_[np.nan, np.diff(p)]
    dy = np.r_[np.nan, np.diff(y)]
    # element i of reduceat over [0, G_0, G_1, ...] sums minutes [G_i - 5, G_i): the five bars ending at snapshot G_i
    fs = np.add.reduceat(np.nan_to_num(flow), np.r_[0, G])[:len(G)]
    vs = np.add.reduceat(np.nan_to_num(vol), np.r_[0, G])[:len(G)]
    x = np.where(vs > 0, fs / np.where(vs > 0, vs, 1), np.nan)
    day = G // 1440
    cover = float(np.mean(np.isfinite(y) & np.isfinite(r)))
    return {"r": r, "dy": dy, "x": x, "day": day}, {"days_with_metrics": days_ok, "grid_points": int(len(G)),
                                                    "finite_share": cover}


# ---------------------------------------------------------------------------- stage 1: data audit (no estimates)
t0 = time.time()
PANELS, AUDIT = {}, {}
for sym in SYMBOLS:
    try:
        PANELS[sym], AUDIT[sym] = build_panel(sym)
    except Exception as e:                                             # recorded, not hidden
        AUDIT[sym] = {"error": repr(e)[:300], "days_with_metrics": 0, "finite_share": 0.0}
    a = AUDIT[sym]
    a["included"] = bool(a.get("days_with_metrics", 0) >= 28 and a.get("finite_share", 0) >= 0.90)
    print(f"{sym}: days {a.get('days_with_metrics')} finite {a.get('finite_share', 0):.3f} included {a['included']}"
          f" ({time.time() - t0:.0f}s)")
INCLUDED = [s for s in SYMBOLS if AUDIT[s]["included"]]
record("P1O_data_audit", {"audit": AUDIT, "included": INCLUDED})
print("included:", len(INCLUDED), "of", len(SYMBOLS))
assert len(INCLUDED) > 0, "no symbol passed the data rule; send the audit file to Claude"

# ---------------------------------------------------------------------------- stage 2: the tests (run once)
unlock = os.path.join(PREREG, "P1O_unlocks.json")
if not DRY:
    n_runs = json.load(open(unlock))["n"] + 1 if os.path.exists(unlock) else 1
    json.dump({"n": n_runs, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": SPEC_SHA256},
              open(unlock, "w"), indent=2)
else:
    n_runs = 0
print("unlock count:", n_runs, "(should be 1)" if not DRY else "(dry run: not counted)")

N2, N3 = {}, {}
for sym in INCLUDED:
    P = PANELS[sym]; day = P["day"]
    N2[sym] = feedback_oos(P["dy"], P["r"], day < 20, day >= 20)
    full = combined_response(P["x"], P["r"], np.ones(len(day), bool))
    h1 = combined_response(P["x"], P["r"], day < 15)
    h2 = combined_response(P["x"], P["r"], day >= 15)
    d10 = combined_response(P["x"], P["r"], day < 10)
    N3[sym] = {"full": full, "first_half": h1, "second_half": h2, "first_10_days": d10,
               "halfwidth_ratio_10d_vs_full": d10["halfwidth"] / full["halfwidth"] if full["halfwidth"] > 0 else None}
    print(f"{sym}: N2 DM p={N2[sym]['dm_p']:.4f} R2 gain={N2[sym]['oos_r2_gain']:.4f} | N3 Psi={full['psi']:.4f} "
          f"[{full['ci'][0]:.4f}, {full['ci'][1]:.4f}] ratio10={N3[sym]['halfwidth_ratio_10d_vs_full']:.2f}")

n = len(INCLUDED)
n2_hits = {s: bool(N2[s]["dm_p"] < 0.05) for s in INCLUDED}
n3_h1 = {s: bool((N3[s]["full"]["ci"][0] > 0 or N3[s]["full"]["ci"][1] < 0) and
                 N3[s]["full"]["rel_halfwidth"] is not None and N3[s]["full"]["rel_halfwidth"] < 0.5) for s in INCLUDED}
n3_h2 = {s: bool(np.sign(N3[s]["first_half"]["psi"]) == np.sign(N3[s]["second_half"]["psi"])) for s in INCLUDED}
n3_h3 = {s: bool(N3[s]["halfwidth_ratio_10d_vs_full"] is not None and 1.2 <= N3[s]["halfwidth_ratio_10d_vs_full"] <= 2.5)
         for s in INCLUDED}
S2 = {"H1": {"count": sum(n2_hits.values()), "of": n, "required_share": 0.6, "pass": sum(n2_hits.values()) >= 0.6 * n}}
S3 = {"H1": {"count": sum(n3_h1.values()), "of": n, "required_share": 0.8, "pass": sum(n3_h1.values()) >= 0.8 * n},
      "H2": {"count": sum(n3_h2.values()), "of": n, "required_share": 0.8, "pass": sum(n3_h2.values()) >= 0.8 * n},
      "H3": {"count": sum(n3_h3.values()), "of": n, "required_share": 0.7, "pass": sum(n3_h3.values()) >= 0.7 * n}}
gains = [N2[s]["oos_r2_gain"] for s in INCLUDED]
S2["median_oos_r2_gain"] = float(np.median(gains))
record("P1O_N2_feedback", {"summary": S2, "by_symbol": N2, "hits": n2_hits, "unlock_count": n_runs,
                           "criterion": SPEC["N2_feedback_beyond_persistence"]["H1_primary"]})
record("P1O_N3_combined", {"summary": S3, "by_symbol": N3, "H1_hits": n3_h1, "H2_hits": n3_h2, "H3_hits": n3_h3,
                           "unlock_count": n_runs, "criterion": SPEC["N3_combined_response_from_flow"]["H1_primary"]})
print("\n=== N2 feedback beyond persistence (primary):", f"{S2['H1']['count']}/{n}", "PASS" if S2["H1"]["pass"] else "FAIL")
print("=== N3 combined response from flow (primary): ", f"{S3['H1']['count']}/{n}", "PASS" if S3["H1"]["pass"] else "FAIL")
print("=== N3 H2 (sign stable across halves):       ", f"{S3['H2']['count']}/{n}", "PASS" if S3["H2"]["pass"] else "FAIL")
print("=== N3 H3 (root-T shrinkage):                ", f"{S3['H3']['count']}/{n}", "PASS" if S3["H3"]["pass"] else "FAIL")

zp = os.path.join(BASE, "p1o_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fp in [os.path.join(RESULTS, f) for f in ("P1O_data_audit.json", "P1O_N2_feedback.json", "P1O_N3_combined.json")] + [unlock]:
        if os.path.exists(fp):
            z.write(fp, os.path.relpath(fp, BASE))
print("zipped ->", zp)
if IN_COLAB and not DRY:
    from google.colab import files
    files.download(zp)

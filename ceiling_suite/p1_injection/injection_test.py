# ============================================================================
# P1_injection: pre-specified real-noise injection test for Paper 1 (approved by the author on 2026-10-30).
# Specification: prereg/P1_injection.json (SHA-256 checked below; committed before any real noise was downloaded).
#
# Colab:  !git clone https://github.com/Pratikn03/Fianince.git
#         %cd Fianince/ceiling_suite/p1_injection
#         %run injection_test.py
# Output: <BASE>/results/I1_injection_test.json and the unlock counter <BASE>/prereg/P1_injection_unlocks.json
#         (BASE = /content/drive/MyDrive/ceiling_suite in Colab). Run it once.
# ============================================================================
import os, sys, io, json, time, zipfile, hashlib, urllib.request
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)
from injection_core import NoisePool, gaussian_pool, n_star, slope

SPEC_PATH = os.path.join(HERE, "prereg", "P1_injection.json")
SPEC_SHA256 = "596a700da2e4e28c657f41e9226ba30325b499df9dce40f3152f3ffa3e6e03ed"
raw = open(SPEC_PATH).read()
assert hashlib.sha256(raw.encode()).hexdigest() == SPEC_SHA256, "specification changed after it was fixed"
SPEC = json.loads(raw)

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    BASE = "/content/drive/MyDrive/ceiling_suite"
else:
    BASE = os.path.abspath("ceiling_suite_local")
RESULTS, PREREG, CACHE = (os.path.join(BASE, d) for d in ("results", "prereg", "data_injection"))
for d in (RESULTS, PREREG, CACHE):
    os.makedirs(d, exist_ok=True)

unlock = os.path.join(PREREG, "P1_injection_unlocks.json")
n_runs = json.load(open(unlock))["n"] + 1 if os.path.exists(unlock) else 1
json.dump({"n": n_runs, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": SPEC_SHA256},
          open(unlock, "w"), indent=2)
print("test-set unlock count:", n_runs, "(should be 1)")

# ---- real noise: Binance spot BTCUSDT one-minute klines, 6th of each month, Jan 2025 - Sep 2026 ----
DAYS = [f"{y}-{m:02d}-06" for y in (2025, 2026) for m in range(1, 13) if (y, m) <= (2026, 9)]


def day_changes(day):
    fp = os.path.join(CACHE, f"BTCUSDT-1m-{day}.npy")
    if os.path.exists(fp):
        return np.load(fp)
    url = f"https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{day}.zip"
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        rows = z.open(z.namelist()[0]).read().decode().strip().splitlines()
    close = np.array([float(r.split(",")[4]) for r in rows if r.split(",")[0].strip().isdigit()])  # skip any header row
    dlp = np.diff(np.log(close))
    np.save(fp, dlp)
    return dlp


changes = {d: day_changes(d) for d in DAYS}
pooled = np.concatenate(list(changes.values()))
mu, sd = pooled.mean(), pooled.std()
print(f"real noise: {len(DAYS)} days, {len(pooled)} one-minute changes; kurtosis {float(((pooled-mu)**4).mean()/sd**4):.1f}")


def real_pool(T):
    wins = []
    for d in DAYS:
        x = (changes[d] - mu) / sd
        n = len(x) // T
        wins.append(x[:n * T].reshape(n, T))
    return NoisePool(np.vstack(wins))


E = SPEC["economy"]; NL = SPEC["noise_levels"]
cfg = dict(a=E["a"], kappa=E["kappa"], W=E["W"], sigma=NL["sigma"], sigma_f=NL["sigma_f"], reps=200, eps_rel=0.25,
           tagged_taps=6, target_failure=0.25, n_grid=np.unique(np.round(2.0 ** (np.arange(60) / 2))).astype(float))
rng = np.random.default_rng(SPEC["seed"])
pools = {"real": {T: real_pool(T) for T in (5, 6, 7)}, "gaussian": {T: gaussian_pool(T, seed=T) for T in (5, 6, 7)}}

res = {"spec_sha256": SPEC_SHA256, "unlock_count": n_runs, "days": DAYS, "n_changes": int(len(pooled)),
       "window_lag1_autocorr": {}, "arms": {}}
for T in (5, 6, 7):
    C = np.corrcoef(pools["real"][T].W.T); res["window_lag1_autocorr"][T] = float(np.mean(np.diag(C, 1)))
for arm in ("real", "gaussian"):
    P = pools[arm]; out = {}
    cfg["rc"] = E["K2"]["rc"]; g2 = E["K2"]["d_eta"]
    ns_p, ns_t, regimes = [], [], []
    for de in g2:
        n, fr = n_star("price", 2, de, P[5], P[6], cfg, rng); ns_p.append(n)
        m, ft = n_star("tagged", 2, de, P[6], P[6], cfg, rng); ns_t.append(m)
        regimes.append("exact" if (n or 0) <= 4096 else "clt")
        print(arm, "K=2", de, "price N*", n, "tagged N*", m, flush=True)
    cfg["rc"] = E["K3"]["rc"]; g3 = E["K3"]["d_eta"]; ns_3 = []
    for de in g3:
        n, _ = n_star("price", 3, de, P[7], P[6], cfg, rng); ns_3.append(n)
        print(arm, "K=3", de, "price N*", n, flush=True)
    out = {"K2_d_eta": g2, "K2_price_N_star": ns_p, "K2_tagged_N_star": ns_t, "K2_price_regime": regimes,
           "K3_d_eta": g3, "K3_price_N_star": ns_3,
           "slope_K2_price": slope(g2, ns_p), "slope_K2_tagged": slope(g2, ns_t), "slope_K3_price": slope(g3, ns_3)}
    res["arms"][arm] = out

R = res["arms"]["real"]
inr = lambda v, lo, hi: v is not None and lo <= v <= hi
res["H1"] = {"slope": R["slope_K2_price"], "pass": inr(R["slope_K2_price"], -7.5, -4.5)}
tg = [n for n in R["K2_tagged_N_star"] if n is not None]
ratio = (max(tg) / min(tg)) if len(tg) == len(R["K2_tagged_N_star"]) else None
res["H2"] = {"max_over_min": ratio, "slope": R["slope_K2_tagged"], "pass": ratio is not None and ratio <= 8}
res["H3"] = {"slope": R["slope_K3_price"], "pass": inr(R["slope_K3_price"], -12.5, -7.5)}
G = res["arms"]["gaussian"]
res["H4_ratio_real_over_gaussian_K2_price"] = [None if (a is None or b is None) else a / b
                                              for a, b in zip(R["K2_price_N_star"], G["K2_price_N_star"])]
passed = res["H1"]["pass"] and res["H2"]["pass"]
out = {"test_id": "I1_injection_test", "status": "PASS" if passed else "FAIL", "kind": "semi-synthetic (real noise)",
       "criterion": SPEC["pass_rule"], "metrics": res, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(out, open(os.path.join(RESULTS, "I1_injection_test.json"), "w"), indent=2, default=float)
print(json.dumps({k: res[k] for k in ("H1", "H2", "H3")}, indent=1), "\nOVERALL:", out["status"])

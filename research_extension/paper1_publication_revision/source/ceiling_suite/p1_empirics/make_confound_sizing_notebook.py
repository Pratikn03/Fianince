"""Builds P1T_ConfoundSizing_Colab.ipynb: an exploratory sizing of the noisy-report confound (amendment A2, case c),
calibrated on DEVELOPMENT days only (2013-01-02 to 2016-12-30). It reads no validation or holdout flows, computes no
P1T statistic on data, and is labelled exploratory.

Steps: (1) per-stock calibration on development days of the Foreign-flow AR(1) and of the price basis
x_t = a x_{t-1} + k u_{F,t} + e_t; (2) simulate 300-stock panels at the median calibration with NO feedback and
reported Foreign flow = true flow + noise of s times its SD, for s in a grid; (3) the same panels with feedback w and no
reporting noise; (4) the forecast gain D (primary statistic definition) on each simulated panel, so the gain the
confound could produce can be compared with the gain feedback produces, at Taiwan-like parameters."""
import hashlib
import json

src = open("p1t_executor.py").read()
sha = hashlib.sha256(src.encode()).hexdigest()
nb = json.load(open("P1T_Validation_A1_Colab.ipynb"))
cell = "".join(nb["cells"][1]["source"])
i = cell.index("EXECUTOR_SHA256 = "); j = cell.index("\n", i)
cell = cell[:i] + f'EXECUTOR_SHA256 = "{sha}"' + cell[j:]
i = cell.index("EXECUTOR_SRC = "); j = cell.index("\n", i)
cell = cell[:i] + "EXECUTOR_SRC = " + json.dumps(src, ensure_ascii=False) + cell[j:]
k = cell.index("# 4. run the registered executor once on the validation period")
cell = cell[:k] + r'''# 4. exploratory confound sizing, development days only
def load(sub, d): return json.loads(gzip.open(os.path.join(ROOT, sub, d + ".json.gz")).read())
dev_days = [d for d in days if d <= DEV_END]
P = ex.build_panel([(d, load("T86", d), load("MI", d)) for d in dev_days], ev)
dev = np.ones(len(P.dates), bool)
prep = ex.prepare(P, dev)
x, uF, us = prep["x"], prep["u"]["Foreign"], prep["usable"]
cal = []
for i in prep["U"]:
    t = np.where(us[i] & np.isfinite(uF[i]))[0]; t = t[(t >= 1) & np.isfinite(uF[i, t - 1])]
    if len(t) < 200: continue
    y = uF[i, t]; ylag = uF[i, t - 1]
    r = float(np.polyfit(ylag, y, 1)[0]); eta = y - r * ylag; eta = eta - eta.mean()
    X = np.column_stack([x[i, t - 1], y, np.ones(len(t))]); b = np.linalg.lstsq(X, x[i, t], rcond=None)[0]
    e = x[i, t] - X @ b
    cal.append([r, b[0], b[1], float(e.std()), float(eta.std()), float(y.std())])
cal = np.array(cal); med = np.median(cal, axis=0)
r, a, kk, se, seta, sy = med
print("median calibration: r=%.3f a=%.3f k=%.4g sd_e=%.4g sd_eta=%.4g sd_u=%.4g (%d stocks)" % (r, a, kk, se, seta, sy, len(cal)))

def sim_D(noise=0.0, w=0.0, N=300, T=1475, T_dev=982, seed=1):
    rng = np.random.default_rng(seed); burn = 300; n = T + burn
    X = np.zeros((N, n)); Ut = np.zeros((N, n))
    for t in range(1, n):
        # price-first: x_t moves with this period's true flow; with feedback, flow responds to x_{t-1}
        Ut[:, t] = r * Ut[:, t - 1] + w * X[:, t - 1] + seta * rng.standard_normal(N)
        X[:, t] = a * X[:, t - 1] + kk * Ut[:, t] + se * rng.standard_normal(N)
    X, Ut = X[:, burn:], Ut[:, burn:]
    Ur = Ut + noise * Ut.std(axis=1, keepdims=True) * rng.standard_normal(Ut.shape)
    us_ = np.zeros((N, T), bool); us_[:, 2:-1] = True
    pr = {"U": range(N), "x": X, "u": {"Foreign": Ur}, "limit": np.zeros((N, T)), "usable": us_}
    devm = np.zeros(T, bool); devm[:T_dev] = True
    D, _ = ex.panel_D(ex.panel_L(pr, devm, ~devm, "Foreign"))
    return float(D)

noise_grid = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
D_noise = {s: sim_D(noise=s) for s in noise_grid}
# feedback grid: w = f (1 - max(a, r))/|k|, so that k w is a fraction f of the stability gap; unstable cases skipped
wunit = (1 - max(a, r)) / max(abs(kk), 1e-12)
def rho(w): return float(max(abs(np.linalg.eigvals(np.array([[a + kk * w, kk * r], [w, r]])))))
w_grid = [0.0, 0.01, 0.03, 0.1, 0.3, 0.6]
D_feedback = {f: (sim_D(w=f * wunit) if rho(f * wunit) < 0.999 else None) for f in w_grid}
res = {"label": "exploratory confound sizing, development days only; not a P1T statistic",
       "executor_sha256": EXECUTOR_SHA256, "run_utc": now(), "n_stocks_calibrated": int(len(cal)),
       "median_calibration": dict(zip(["r_F", "a", "k", "sd_e", "sd_eta", "sd_u"], map(float, med))),
       "calibration_quartiles": np.percentile(cal, [25, 75], axis=0).tolist(),
       "D_by_reporting_noise_no_feedback": D_noise, "D_by_feedback_no_noise": {"f_of_stability_gap": D_feedback, "w_unit": float(wunit)},
       "observed_validation_D": 0.04045892959202791}
json.dump(res, open("p1t_confound_sizing.json", "w"), indent=1, default=float)
with zipfile.ZipFile("p1t_confound_sizing.zip", "w", zipfile.ZIP_DEFLATED) as z: z.write("p1t_confound_sizing.json")
import shutil; shutil.copy("p1t_confound_sizing.zip", os.path.join(ROOT, "p1t_confound_sizing.zip"))
print(json.dumps({k: v for k, v in res.items() if k.startswith("D_") or k == "median_calibration"}, indent=1, default=float))
try:
    from google.colab import files; files.download("p1t_confound_sizing.zip")
except Exception: print("saved p1t_confound_sizing.zip (also on Drive)")
'''
nb["cells"][1]["source"] = cell
nb["cells"][0]["source"] = ("# P1T exploratory: how large would reporting noise have to be?\n\n"
    "Calibrates a no-feedback, noisy-report economy and a feedback economy to Taiwan **development-period** data "
    "(2013–2016 only) and computes the forecast gain each would produce. No validation or holdout flows are read and no "
    "P1T statistic is computed on data. Run the single code cell once (a few minutes) and return `p1t_confound_sizing.zip`.")
for c in nb["cells"]:
    if c["cell_type"] == "code":
        c["outputs"] = []; c["execution_count"] = None
json.dump(nb, open("P1T_ConfoundSizing_Colab.ipynb", "w"), ensure_ascii=False, indent=1)
compile(cell, "cell", "exec")
print(sha)

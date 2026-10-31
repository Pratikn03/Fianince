# ============================================================================
# P11F: pre-specified CFTC tagged-flow test for Paper 1 (approved by the author on 2026-10-30).
# Specification: prereg_flow/P11F_cot_tagged_flow.json (SHA-256 checked below; committed before the run).
#
# Colab:  !git clone https://github.com/Pratikn03/Fianince.git
#         %cd Fianince/ceiling_suite/p11
#         %run tagged_flow_test.py
# Output: <BASE>/results/C5F_cot_tagged_flow.json and <BASE>/prereg/P11F_unlocks.json. Run it once.
# ============================================================================
import os, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
exec(open(os.path.join(HERE, "c0_setup.py")).read())        # MARKETS, END_DATE, record(), caches (registered setup)
exec(open(os.path.join(HERE, "c1_functions.py")).read())    # get_cot, weekly_panel, block_index

SPEC_PATH = os.path.join(HERE, "prereg_flow", "P11F_cot_tagged_flow.json")
SPEC_SHA256 = "052a63f20617e7e31753009b36ec7e63cf1375ec34f3d488c725a439b657e0ce"
assert hashlib.sha256(open(SPEC_PATH).read().encode()).hexdigest() == SPEC_SHA256, "specification changed"
SPEC = json.load(open(SPEC_PATH))
unlock = os.path.join(PREREG, "P11F_unlocks.json")
n_runs = json.load(open(unlock))["n"] + 1 if os.path.exists(unlock) else 1
json.dump({"n": n_runs, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": SPEC_SHA256},
          open(unlock, "w"), indent=2)
print("unlock count:", n_runs, "(should be 1)")


def flow_panel(mkt):
    D = weekly_panel(mkt).copy()
    for c in ("fast", "slow"):
        D[f"u_{c}"] = D[f"n_{c}"] - D[f"n_{c}_lag"]
        D[f"u_{c}_lag"] = D[f"u_{c}"].shift(1)
    D["ret_lag"] = D["ret"].shift(1)
    consecutive = (D["date"].diff().dt.days == 7)             # the previous row is the previous week
    return D[consecutive].dropna().reset_index(drop=True)


def iv_fit(D, c):
    y = D[f"u_{c}"].to_numpy(); one = np.ones(len(D))
    X = np.column_stack([one, D[f"u_{c}_lag"], D["ret"]]); Z = np.column_stack([one, D["ret_lag"], D["ret"]])
    b = np.linalg.solve(Z.T @ X, Z.T @ y)
    return b[1], b[2]


def ols_fit(D, c):
    X = np.column_stack([np.ones(len(D)), D[f"u_{c}_lag"], D["ret"]])
    b = np.linalg.lstsq(X, D[f"u_{c}"].to_numpy(), rcond=None)[0]
    return b[1], b[2]


def first_stage_F(D, c):
    y = D[f"u_{c}_lag"].to_numpy(); one = np.ones(len(D))
    Xr = np.column_stack([one, D["ret"]]); Xu = np.column_stack([one, D["ret"], D["ret_lag"]])
    rss = lambda X: float(np.sum((y - X @ np.linalg.lstsq(X, y, rcond=None)[0]) ** 2))
    r0, r1 = rss(Xr), rss(Xu)
    return (r0 - r1) / (r1 / (len(y) - Xu.shape[1]))


q = lambda v: [float(np.nanquantile(v, 0.025)), float(np.nanquantile(v, 0.975))]
res = {}
for mkt in MARKETS:
    D = flow_panel(mkt); T = len(D); R = np.random.default_rng(SPEC["seed"] + sum(map(ord, mkt)))
    est = {c: iv_fit(D, c) for c in ("fast", "slow")}
    boot = {c: [] for c in est}
    for b in range(2000):
        Db = D.iloc[block_index(T, 13, R)].reset_index(drop=True)
        for c in boot:
            try:
                boot[c].append(iv_fit(Db, c))
            except np.linalg.LinAlgError:
                boot[c].append((np.nan, np.nan))
    out = {"weeks": T, "first": str(D["date"].iloc[0].date()), "last": str(D["date"].iloc[-1].date())}
    for c in est:
        a = np.array(boot[c])
        out[c] = {"iv_r": float(est[c][0]), "iv_r_ci": q(a[:, 0]), "iv_w": float(est[c][1]), "iv_w_ci": q(a[:, 1]),
                  "ols_r": float(ols_fit(D, c)[0]), "ols_w": float(ols_fit(D, c)[1]), "first_stage_F": first_stage_F(D, c)}
    f = out["fast"]
    out["H1_width"] = f["iv_r_ci"][1] - f["iv_r_ci"][0]
    res[mkt] = out
    print(mkt, T, "IV r", round(f["iv_r"], 3), f["iv_r_ci"], "w", round(f["iv_w"], 4), f["iv_w_ci"], "F", round(f["first_stage_F"], 1))

h1 = int(sum(bool(res[m]["H1_width"] < 0.5) for m in res))
h2 = int(sum(bool(res[m]["fast"]["first_stage_F"] >= 10) for m in res))
h3 = int(sum(bool((res[m]["fast"]["iv_w_ci"][0] > 0) or (res[m]["fast"]["iv_w_ci"][1] < 0)) for m in res))
summary = {"H1": {"count": int(h1), "of": len(res), "pass": bool(h1 >= 6)}, "H2": {"count": int(h2), "of": len(res), "pass": bool(h2 >= 6)},
           "H3": {"count": int(h3), "of": len(res), "pass": bool(h3 >= 6)}, "unlock_count": n_runs, "spec_sha256": SPEC_SHA256}
record("C5F_cot_tagged_flow", summary["H1"]["pass"], "real data", {"summary": summary, "by_market": res},
       criterion=SPEC["hypotheses"]["H1_primary"])
print(json.dumps(summary, indent=1))

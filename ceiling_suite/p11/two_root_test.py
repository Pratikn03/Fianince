# ============================================================================
# P11M: pre-specified test (approved by the author on 2026-10-31): do CFTC class positions show a second, faster
# root? Specification: prereg_memory/P11M_two_root.json (SHA-256 checked below; committed before any run).
# Output: <BASE>/results/C6M_cot_two_root.json and <BASE>/prereg/P11M_unlocks.json. Run it once.
#
# Colab:                   !git clone https://github.com/Pratikn03/Fianince.git
#                          %cd Fianince/ceiling_suite/p11
#                          %run two_root_test.py
# ============================================================================
import os, json, time, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
SPEC_SHA256 = "e66335881e2c83333f928db7704d0cf723216d1921aeddb1cc75fc168886040c"


def two_root_fit(D, c):
    """OLS of n_t on (1, n_{t-1}, n_{t-2}, ret_t, ret_{t-1}); returns phi1, phi2, b0, b1 and the roots z1 >= z2
    (NaN if complex)."""
    y = D[f"n_{c}"].to_numpy()
    X = np.column_stack([np.ones(len(D)), D[f"n_{c}_lag"], D[f"n_{c}_lag2"], D["ret"], D["ret_lag"]])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    phi1, phi2 = b[1], b[2]
    disc = phi1 ** 2 + 4 * phi2
    if disc < 0:
        return phi1, phi2, b[3], b[4], np.nan, np.nan
    z1, z2 = (phi1 + np.sqrt(disc)) / 2, (phi1 - np.sqrt(disc)) / 2
    return phi1, phi2, b[3], b[4], z1, z2


def two_root_panel(D):
    D = D.copy()
    for c in ("fast", "slow"):
        D[f"n_{c}_lag2"] = D[f"n_{c}"].shift(2)
    D["ret_lag"] = D["ret"].shift(1)
    consecutive = (D["date"].diff().dt.days == 7) & (D["date"].diff(2).dt.days == 14)
    return D[consecutive].dropna().reset_index(drop=True)


def analyse_market(D, rng, B=2000, block=13):
    T = len(D)
    out = {"weeks": T}
    for c in ("fast", "slow"):
        est = two_root_fit(D, c)
        draws = []
        for _ in range(B):
            nb = int(np.ceil(T / block)); starts = rng.integers(0, T - block + 1, nb)
            idx = np.concatenate([np.arange(s, s + block) for s in starts])[:T]
            draws.append(two_root_fit(D.iloc[idx].reset_index(drop=True), c))
        a = np.array(draws)
        real = np.isfinite(a[:, 4])
        q = lambda v: [float(np.nanquantile(v, 0.025)), float(np.nanquantile(v, 0.975))]
        out[c] = {"phi1": est[0], "phi2": est[1], "b0": est[2], "b1": est[3], "z1": est[4], "z2": est[5],
                  "z2_ci": q(a[real, 5]), "gap_ci": q(a[real, 4] - a[real, 5]), "complex_share": float(1 - real.mean()),
                  "z2_halflife_weeks": float(np.log(0.5) / np.log(est[5])) if 0 < est[5] < 1 else None}
    f = out["fast"]
    out["H1"] = bool(np.isfinite(f["z2"]) and f["z2_ci"][0] > 0 and f["z2_ci"][1] < 0.9 and f["gap_ci"][0] > 0)
    out["H2"] = bool(f["z2_halflife_weeks"] is not None and f["z2_halflife_weeks"] < 13)
    out["H3"] = bool(np.isfinite(f["z2"]) and np.isfinite(out["slow"]["z2"]) and f["z2"] < out["slow"]["z2"])
    return out


if __name__ == "__main__":
    if SPEC_SHA256 is None:
        raise SystemExit("DRAFT: the specification has not been approved and registered; nothing was run.")
    spec_path = os.path.join(HERE, "prereg_memory", "P11M_two_root.json")
    assert hashlib.sha256(open(spec_path).read().encode()).hexdigest() == SPEC_SHA256, "specification changed"
    exec(open(os.path.join(HERE, "c0_setup.py")).read())
    exec(open(os.path.join(HERE, "c1_functions.py")).read())
    unlock = os.path.join(PREREG, "P11M_unlocks.json")
    n_runs = json.load(open(unlock))["n"] + 1 if os.path.exists(unlock) else 1
    json.dump({"n": n_runs, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": SPEC_SHA256},
              open(unlock, "w"), indent=2)
    print("unlock count:", n_runs, "(should be 1)")
    res = {}
    for mkt in MARKETS:
        D = two_root_panel(weekly_panel(mkt))
        res[mkt] = analyse_market(D, np.random.default_rng(20261101 + sum(map(ord, mkt))))
        print(mkt, {k: res[mkt][k] for k in ("H1", "H2", "H3")}, "z2", res[mkt]["fast"]["z2"], res[mkt]["fast"]["z2_ci"])
    summary = {h: {"count": int(sum(res[m][h] for m in res)), "of": len(res)} for h in ("H1", "H2", "H3")}
    summary["H1"]["pass"] = summary["H1"]["count"] >= 6
    summary["H2"]["pass"] = summary["H2"]["count"] >= 6
    summary["H3"]["pass"] = summary["H3"]["count"] >= 5
    record("C6M_cot_two_root", summary["H1"]["pass"], "real data", {"summary": summary, "by_market": res},
           criterion="smaller root of the fast class clearly inside (0, 0.9) and distinct from the larger, 6 of 8")
    print(json.dumps(summary, indent=1))

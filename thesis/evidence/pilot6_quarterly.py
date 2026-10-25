"""EXPLORATORY Pilot 6 on the spent C3 symbols (not a registered test; nothing here is confirmatory evidence).

Pilot 4 found that the standardized margin does not grow like the square root of the sample symbol by symbol, because
the estimated margin moves between 2025 and 2026. Pilot 6 asks whether certification holds on the time scale on which
these markets are stable: for each symbol and calendar quarter (2025Q1 to 2026Q3), with C3's estimator on that
quarter's valid days only (at least 30), is the margin decided, on which side, and do the quarterly intervals agree?
Readings: share of symbol-quarters decided; share decided safe; per symbol, the number of quarters decided and whether
any two decided quarters have non-overlapping intervals (drift); heterogeneity test of the quarterly margins
(chi-square of the inverse-variance-weighted deviations, using bootstrap standard errors).
Usage (Colab): pilot6_quarterly.run(cache_dir, out_json)        Local test: python pilot6_quarterly.py --selftest
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c2_margin_vs_identify as C2  # noqa: E402
import c3_margin_more_days as C3  # noqa: E402
import f1_flagship as F1  # noqa: E402

MIN_Q_DAYS = 30
B = 200
SEED = 20261106


def quarter(date):
    ts = pd.Timestamp(date); return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"


def quarter_stats(days, j, salt):
    rng = np.random.default_rng(SEED + 101 * j + salt); n = len(days)
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B)]).astype(float)
    pr, kx = C2.solve_w(S, "price", W), C2.solve_w(S, "k_x", W)
    M = -pr[:, 1] - pr[:, 0] * kx.sum(1)
    c = C2.ci(M[1:]); sd = float(np.nanstd(M[1:]))
    return {"n": n, "M": float(M[0]), "se": sd, "ci": c, "decided": bool(c[0] > 0 or c[1] < 0),
            "sign": "safe" if c[0] > 0 else "unsafe" if c[1] < 0 else "undecided"}


def analyse(per_symbol_days):
    out = {}
    for j, (s, days) in enumerate(per_symbol_days.items()):
        byq = {}
        for d in days:
            byq.setdefault(quarter(d["date"]), []).append(d)
        qs = {q: quarter_stats(v, j, i) for i, (q, v) in enumerate(sorted(byq.items())) if len(v) >= MIN_Q_DAYS}
        if len(qs) < 2:
            continue
        Ms = np.array([v["M"] for v in qs.values()]); ses = np.array([v["se"] for v in qs.values()])
        ok = ses > 0; w = 1 / ses[ok] ** 2; mbar = float((w * Ms[ok]).sum() / w.sum())
        chi2 = float((w * (Ms[ok] - mbar) ** 2).sum()); dof = int(ok.sum() - 1)
        dec = [v for v in qs.values() if v["decided"]]
        disjoint = any(a["ci"][1] < b["ci"][0] or b["ci"][1] < a["ci"][0] for i, a in enumerate(dec) for b in dec[i + 1:])
        out[s] = {"quarters": qs, "n_quarters": len(qs), "n_decided": len(dec),
                  "n_safe": sum(v["sign"] == "safe" for v in qs.values()), "drift_disjoint": bool(disjoint),
                  "heterogeneity_p": float(stats.chi2.sf(chi2, dof)) if dof > 0 else np.nan}
        print(f"  {s}: quarters={len(qs)} decided={len(dec)} safe={out[s]['n_safe']} disjoint={disjoint} "
              f"het p={out[s]['heterogeneity_p']:.3f}", flush=True)
    sq = [q for v in out.values() for q in v["quarters"].values()]
    summ = {"n_symbols": len(out), "symbol_quarters": len(sq), "decided": sum(q["decided"] for q in sq),
            "decided_safe": sum(q["sign"] == "safe" for q in sq), "decided_unsafe": sum(q["sign"] == "unsafe" for q in sq),
            "symbols_decided_every_quarter": sum(v["n_decided"] == v["n_quarters"] for v in out.values()),
            "symbols_with_disjoint_decided_quarters": sum(v["drift_disjoint"] for v in out.values()),
            "symbols_heterogeneous_p05": sum((v["heterogeneity_p"] or 1) < 0.05 for v in out.values())}
    return {"per_symbol": out, "summary": summ}


def run(cache_dir, out_json, symbols=None):
    symbols = symbols or json.loads((HERE / "C3_universe.json").read_text())["symbols"]
    per = F1.load(cache_dir, symbols, C3.dates())
    res = {"kind": "EXPLORATORY Pilot 6 (quarterly certification on the spent C3 symbols); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), **analyse(per)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps(res["summary"], indent=1))
    return res


def selftest():
    import pilot4_curve_and_risk as P4
    rng = np.random.default_rng(9); per = {}
    dates = [d for d in pd.date_range("2025-01-01", "2025-09-30").strftime("%Y-%m-%d") if int(d[-2:]) % 3]
    for j in range(3):
        days = []
        for d in dates:
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = P4.day_record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}))
            if r is not None:
                r["date"] = d; days.append(r)
        per[f"S{j}"] = days
    out = analyse(per)
    s = out["summary"]; print(json.dumps(s))
    assert s["n_symbols"] == 3 and s["symbol_quarters"] == 9
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()

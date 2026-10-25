"""Robustness analyses for the flagship paper, on the committed rows of Tests S1 and R1.

EXPLORATORY: these analyses were chosen after the registered results were known. They are reported to show how
fragile or stable the registered findings are, never as confirmatory evidence. Inputs: thesis/evidence/S1_rows.csv.gz and
R1_rows.csv.gz (committed with the tests' results). Output: robustness.json and robustness_numbers.tex next to this file.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
EV = HERE.parents[2] / "thesis" / "evidence"
sys.path.insert(0, str(EV))
import r1_absresp as R1  # noqa: E402

CONTROLS = ["log_rv_lag", "log_rv_trail"]


def pooled(d, y, x="M", share=0.6, cluster="date", wins=(0.05, 0.95), extra=()):
    """F1/S1's pooled out-of-sample design with a choice of clustering unit, training share and winsorization."""
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[y, x, *CONTROLS, *extra]).copy()
    d["n_sym"] = d.groupby("symbol")["t"].transform("count"); d["rk"] = d.groupby("symbol")["t"].rank(method="first")
    tr, te = d[d.rk <= share * d.n_sym].copy(), d[d.rk > share * d.n_sym].copy()
    if len(tr) < 100 or len(te) < 100 or tr.symbol.nunique() < 3:
        return None
    lo, hi = tr[x].quantile(wins[0]), tr[x].quantile(wins[1])
    tr["X"], te["X"] = tr[x].clip(lo, hi), te[x].clip(lo, hi)
    base = list(CONTROLS)
    for e in extra:
        a, b = tr[e].quantile(0.05), tr[e].quantile(0.95); tr[e + "_w"] = tr[e].clip(a, b); te[e + "_w"] = te[e].clip(a, b)
        base.append(e + "_w")

    def fit(cols):
        Z = tr[[y] + cols]; m = Z.groupby(tr.symbol).transform("mean")
        bb = np.linalg.lstsq((Z[cols] - m[cols]).to_numpy(), (Z[y] - m[y]).to_numpy(), rcond=None)[0]
        fe = (tr[y] - tr[cols].to_numpy() @ bb).groupby(tr.symbol).mean()
        return te.symbol.map(fe).to_numpy() + te[cols].to_numpy() @ bb, bb
    f0, _ = fit(base); f1, b1 = fit(base + ["X"]); yy = te[y].to_numpy()
    cw = pd.Series((yy - f0) ** 2 - ((yy - f1) ** 2 - (f0 - f1) ** 2), index=te.index)
    key = {"date": te.date, "week": pd.to_datetime(te.date).dt.strftime("%G-%V"), "symbol": te.symbol}[cluster]
    g = cw.groupby(key).mean()
    t = float(g.mean() / (g.std(ddof=1) / np.sqrt(len(g))))
    return {"coef": float(b1[-1]), "t": t, "p": float(stats.norm.sf(t)), "n_test": int(len(te)), "clusters": int(len(g))}


def main():
    s1 = pd.read_csv(EV / "S1_rows.csv.gz"); r1 = R1.add_logs(pd.read_csv(EV / "R1_rows.csv.gz"))
    out = {"note": "EXPLORATORY robustness on committed rows; chosen after the registered results were known"}
    # S1 Primary 2: next-day log(1+RV) on the 20-day margin
    v = {"baseline": pooled(s1, "log_rv"),
         "cluster_week": pooled(s1, "log_rv", cluster="week"), "cluster_symbol": pooled(s1, "log_rv", cluster="symbol"),
         "train_50": pooled(s1, "log_rv", share=0.5), "train_70": pooled(s1, "log_rv", share=0.7),
         "winsor_01_99": pooled(s1, "log_rv", wins=(0.01, 0.99)),
         "year_2025": pooled(s1[s1.date < "2026-01-01"], "log_rv"), "year_2026": pooled(s1[s1.date >= "2026-01-01"], "log_rv"),
         "without_oct_2025": pooled(s1[~s1.date.str.startswith("2025-10")], "log_rv")}
    med = s1.groupby("symbol").log_rv_trail.median(); hi = med[med >= med.median()].index
    v["high_vol_symbols"] = pooled(s1[s1.symbol.isin(hi)], "log_rv"); v["low_vol_symbols"] = pooled(s1[~s1.symbol.isin(hi)], "log_rv")
    loo = [pooled(s1[s1.symbol != s], "log_rv")["t"] for s in s1.symbol.unique()]
    v["leave_one_symbol_out"] = {"t_min": float(min(loo)), "t_max": float(max(loo)), "n": len(loo)}
    out["S1_P2_variance"] = v
    # R1 Primary 1: within-symbol IV elasticity of next-day log(1+MAE) on log Psi_H
    rr = {"baseline": R1.tsls(r1, "log_mae", "logPsi", "logPsi_lag"),
          "with_volatility_controls": R1.tsls(r1, "log_mae", "logPsi", "logPsi_lag", controls=("log_shock", *CONTROLS)),
          "year_2025": R1.tsls(r1[r1.date < "2026-01-01"], "log_mae", "logPsi", "logPsi_lag"),
          "year_2026": R1.tsls(r1[r1.date >= "2026-01-01"], "log_mae", "logPsi", "logPsi_lag")}
    r1 = r1.assign(log_kappa=np.log(np.where(r1.kappa > 0, r1.kappa, np.nan)),
                   log_kappa_lag=np.log(np.where(r1.kappa_lag > 0, r1.kappa_lag, np.nan)))
    r1["log_shock_kappa"] = r1.log_shock + r1.log_kappa
    rr["impact_alone"] = R1.tsls(r1, "log_mae", "log_kappa", "log_kappa_lag")
    rr["logS_pilot7_control"] = R1.tsls(r1, "log_mae", "logS", "logS_lag", controls=("log_shock_kappa",))
    rr["logS_shock_control"] = R1.tsls(r1, "log_mae", "logS", "logS_lag")
    loo = [R1.tsls(r1[r1.symbol != s], "log_mae", "logPsi", "logPsi_lag")["elasticity"] for s in r1.symbol.unique()]
    rr["leave_one_symbol_out"] = {"min": float(min(loo)), "max": float(max(loo)), "n": len(loo)}
    out["R1_P1_size"] = rr
    (HERE / "robustness.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    L = ["% generated by robustness.py (exploratory); do not edit"]
    nm = {"baseline": "Base", "cluster_week": "Week", "cluster_symbol": "Sym", "train_50": "TrFifty", "train_70": "TrSeventy",
          "winsor_01_99": "Wins", "year_2025": "YrA", "year_2026": "YrB", "without_oct_2025": "NoOct",
          "high_vol_symbols": "HiVol", "low_vol_symbols": "LoVol"}
    for k, s in nm.items():
        L.append("\\newcommand{\\RobS%sT}{%.2f}\\newcommand{\\RobS%sC}{%.2f}" % (s, v[k]["t"], s, v[k]["coef"]))
    L.append("\\newcommand{\\RobSLooMin}{%.2f}\\newcommand{\\RobSLooMax}{%.2f}" % (v["leave_one_symbol_out"]["t_min"], v["leave_one_symbol_out"]["t_max"]))
    nr = {"baseline": "Base", "with_volatility_controls": "Vol", "year_2025": "YrA", "year_2026": "YrB", "impact_alone": "Kappa",
          "logS_pilot7_control": "SPseven", "logS_shock_control": "SShock"}
    for k, s in nr.items():
        L.append("\\newcommand{\\RobR%sE}{%.2f}\\newcommand{\\RobR%sSE}{%.2f}" % (s, rr[k]["elasticity"], s, rr[k]["se"]))
    L.append("\\newcommand{\\RobRLooMin}{%.2f}\\newcommand{\\RobRLooMax}{%.2f}" % (rr["leave_one_symbol_out"]["min"], rr["leave_one_symbol_out"]["max"]))
    (HERE / "robustness_numbers.tex").write_text("\n".join(L) + "\n")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()

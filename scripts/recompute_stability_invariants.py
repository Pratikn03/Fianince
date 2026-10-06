"""Recompute and mechanically verify S and rho(J) for all 768 Binance asset-days,
5 FI-2010 stocks, and the BTC perpetual futures holdout.
Exports results/provenance/stability_invariants_table.csv and prints summary verification.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROV = ROOT / "results" / "provenance"

def run_stability_audit():
    # 1. Binance Panel
    with open(PROV / "binance_panel_results.json") as f:
        bp_data = json.load(f)
    
    records = []
    for r in bp_data["results"]:
        J11 = float(r["J11"])
        J12 = float(r["J12"])
        J21 = float(r["J21"])
        J22 = float(r["J22"])
        J = np.array([[J11, J12], [J21, J22]])
        eigs = np.linalg.eigvals(J)
        rho = float(np.max(np.abs(eigs)))
        denom = 1.0 - J22
        Q = (J12 * J21) / denom if abs(denom) > 1e-12 else np.nan
        S = J11 + Q
        sign_cond = bool(J11 >= 0 and J11 < 1 and J22 >= 0 and J22 < 1 and (J12 * J21) >= 0)
        
        # Build-time assertion: every observation declared stable has rho < 1
        assert rho < 1.0, f"Binance breach: {r['symbol']} {r['date']} rho={rho}"
        assert S < 1.0, f"Binance S breach: {r['symbol']} {r['date']} S={S}"
        
        records.append({
            "dataset": "Binance_Spot",
            "asset": r["symbol"],
            "date": r["date"],
            "J11": J11,
            "J12": J12,
            "J21": J21,
            "J22": J22,
            "Q": Q,
            "S": S,
            "rho": rho,
            "sign_cond": sign_cond
        })

    # 2. FI-2010 Equity Benchmark
    with open(PROV / "equity_benchmark_results.json") as f:
        eq_data = json.load(f)
    
    for s_name, res in eq_data["per_stock_results"].items():
        # In FI-2010, the estimated parameters:
        a_hat = res["a_hat"]
        lam_hat = res["lambda_hat"]
        c_hat = res["c_hat"]
        eta_hat = res["eta_hat"]
        # J = [[a, lam], [eta * c, 1 - eta + eta * lam * c]]
        J11 = a_hat
        J12 = lam_hat
        J21 = eta_hat * c_hat
        J22 = 1.0 - eta_hat + eta_hat * lam_hat * c_hat
        J = np.array([[J11, J12], [J21, J22]])
        eigs = np.linalg.eigvals(J)
        rho = float(np.max(np.abs(eigs)))
        Q = res["Q_hat"]
        S = res["S_hat"]
        
        assert rho < 1.0, f"FI-2010 breach: {s_name} rho={rho}"
        assert S < 1.0, f"FI-2010 S breach: {s_name} S={S}"
        
        records.append({
            "dataset": "FI-2010_Equity",
            "asset": s_name,
            "date": "2010-Panel",
            "J11": J11,
            "J12": J12,
            "J21": J21,
            "J22": J22,
            "Q": Q,
            "S": S,
            "rho": rho,
            "sign_cond": bool(J11 >= 0 and J11 < 1 and J22 >= 0 and J22 < 1 and (J12 * J21) >= 0)
        })

    # 3. BTC Holdout (January 2023)
    with open(PROV / "btc_jan2023_results.json") as f:
        ho_data = json.load(f)
    
    m1 = ho_data["method_1_direct_estimation"]
    a_ho = m1["a_hat"]
    lam_ho = m1["lambda_hat"]
    c_ho = m1["c_hat"]
    eta_ho = m1["eta_hat"]
    J11 = a_ho
    J12 = lam_ho
    J21 = eta_ho * c_ho
    J22 = 1.0 - eta_ho + eta_ho * lam_ho * c_ho
    J = np.array([[J11, J12], [J21, J22]])
    eigs = np.linalg.eigvals(J)
    rho = float(np.max(np.abs(eigs)))
    Q = m1["Q_hat"]
    S = m1["S_hat"]
    
    assert rho < 1.0, f"Holdout breach: rho={rho}"
    assert S < 1.0, f"Holdout S breach: S={S}"
    
    records.append({
        "dataset": "BTC_Holdout_Jan2023",
        "asset": "BTCUSDT_Perp",
        "date": "2023-01",
        "J11": J11,
        "J12": J12,
        "J21": J21,
        "J22": J22,
        "Q": Q,
        "S": S,
        "rho": rho,
        "sign_cond": bool(J11 >= 0 and J11 < 1 and J22 >= 0 and J22 < 1 and (J12 * J21) >= 0)
    })

    df = pd.DataFrame(records)
    out_csv = PROV / "stability_invariants_table.csv"
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df)} records to {out_csv}")

    # Print summary table requested by auditor
    print("\n" + "="*80)
    print("STABILITY INVARIANTS AUDIT SUMMARY")
    print("="*80)
    for ds in ["Binance_Spot", "FI-2010_Equity", "BTC_Holdout_Jan2023"]:
        sub = df[df["dataset"] == ds]
        print(f"Dataset: {ds:<22} | N = {len(sub):3d} | "
              f"Mean S = {sub['S'].mean():.4f} | Max S = {sub['S'].max():.4f} | "
              f"Mean rho = {sub['rho'].mean():.4f} | Max rho = {sub['rho'].max():.4f} | "
              f"Breaches (rho >= 1) = {(sub['rho'] >= 1.0).sum()}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_stability_audit()

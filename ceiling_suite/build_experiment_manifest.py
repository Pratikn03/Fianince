#!/usr/bin/env python3
"""
Builds ceiling_suite/EXPERIMENT_MANIFEST.csv mapping every mathematical theorem,
simulation script, and Colab protocol cell to its exact command, script SHA-256,
output file path, output SHA-256, seed, and manuscript claim/table/figure.
"""
import csv
import hashlib
from pathlib import Path

SUITE = Path(__file__).resolve().parent


def sha256(rel_path: str) -> str:
    p = SUITE / rel_path
    if not p.exists():
        return "EXTERNAL_COLAB_ARCHIVE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


EXPERIMENTS = [
    # Paper 1 Theory & Monte Carlo
    ("P1-THM-QUANTITY", "Paper 1", "papers/recompute_audit.py", "python3 papers/recompute_audit.py", "2,3",
     "recomputed/R_audit_oct2026.json", "Theorem thm:quantity (d_2 = -kappa^2 q delta^2, L1 bound K* delta^2 over 1,610 draws)"),
    ("P1-THM-TWOCOHORT", "Paper 1", "papers/recompute_audit.py", "python3 papers/recompute_audit.py", "symbolic",
     "recomputed/R_audit_oct2026.json", "Theorem thm:twocohort (exact moment matching m=0,1,2 and M_3 gap 4 tau p_- p_+ Delta^3)"),
    ("P1-THM-BLIND", "Paper 1", "papers/recompute_audit.py", "python3 papers/recompute_audit.py", "deterministic",
     "recomputed/R_audit_oct2026.json", "Theorem thm:blind & Prop prop:blind (gain 1.77 to 169.50 at fixed spectrum)"),
    ("P1-EXTRA-MC", "Paper 1", "papers/recompute_extra.py", "python3 papers/recompute_extra.py", "20261019",
     "recomputed/R_P1_extra.json", "Exact error formula MC, Prop prop:passive0 zero-quantity blocks, Gauss-Radau Table tab:radau, two-Kalman-desk worked example"),
    ("P1-THEORY-CONST", "Paper 1", "papers/recompute_theory.py", "python3 papers/recompute_theory.py", "deterministic",
     "recomputed/R_P1_theory_constants.json", "Theorems thm:spectral, thm:adaptive, Prop prop:tri (C*_det,quad, omega*, KL ratio, delta_min(3))"),
    ("P1-CAPITAL-LEDGER", "Paper 1", "papers/recompute_p1_capital.py", "python3 papers/recompute_p1_capital.py", "deterministic",
     "recomputed/R_P1_capital_ledger.json", "Theorem thm:capital & Table tab:capledger (funded probe capital ledger)"),
    ("P1-SPRT", "Paper 1", "papers/recompute_p1_sprt.py", "python3 papers/recompute_p1_sprt.py", "deterministic",
     "recomputed/R_P1_sprt.json", "Theorem thm:adaptive sequential Wald SPRT verification"),
    ("P1-CRB", "Paper 1", "papers/recompute_crb.py", "python3 papers/recompute_crb.py", "deterministic",
     "recomputed/R_P1_crb.json", "Proposition prop:crb Cramer-Rao benchmark and Sylvester determinant scaling"),
    ("P1-ESTIMATORS", "Paper 1", "papers/recompute_p1_estimators.py", "python3 papers/recompute_p1_estimators.py", "deterministic",
     "recomputed/R_P1_estimators.json", "Section 4 two-cohort estimator comparison against CRB"),
    ("P1-KCOHORT-UPPER", "Paper 1", "theory/kcohort_upper.py", "python3 theory/kcohort_upper.py", "0",
     "recomputed/R_P1_kcohort_upper.json", "Theorem prop:esprit & Table tab:kupper (Prony sample complexity slopes for K=2,3,4,5)"),
    ("P1-GENERAL-MINIMAX", "Paper 1", "theory/general_minimax.py", "python3 theory/general_minimax.py", "7",
     "theory/R_P1_general_minimax.json", "Lemma lem:altpair & Theorem thm:general & Table tab:general (Remez equioscillation pairs and 1/log N LP estimator)"),
    ("P1-LEMMA-CHECKS", "Paper 1", "theory/lemma_checks.py", "python3 theory/lemma_checks.py", "0",
     "recomputed/R_P1_general_kernel.json", "Theorem thm:general Chebyshev monomial coefficient bound B(rho) and series reciprocal 1/H"),
    ("P1-DISCLOSURE-VALUE", "Paper 1", "theory/disclosure_value.py", "python3 theory/disclosure_value.py", "deterministic",
     "recomputed/R_P1_disclosure_value.json", "Theorem thm:discvalue & Table tab:discvalue (price-only vs class-tagged sample ratio + calibrated BTC/ETH)"),
    ("P1-PROTOCOLS", "Paper 1", "papers/recompute_p1_protocols.py", "python3 papers/recompute_p1_protocols.py", "deterministic",
     "recomputed/R_P1_protocols.json", "Section 6 Binance 5-minute trader-position persistence and mechanical EMA filter"),
    ("P1-P11-CFTC-COT", "Paper 1", "p11/c4_test.py", "python3 p11/c4_test.py", "preregistered",
     "p11res/results/C4_cot_disclosure.json", "Section 6.2 & Table tab:cot (Pre-registered CFTC COT 8-contract class-tagged disclosure test)"),

    # Paper 2 Theory, Calibration & Empirical Protocols
    ("P2-KREISS-TABLE", "Paper 2", "papers/kreiss_table.py", "python3 papers/kreiss_table.py", "deterministic",
     "recomputed/R_P2_kreiss.json", "Theorem thm:radius & Table tab:kreiss (Safe radius and Kreiss bounds at fixed spectral radius 0.8)"),
    ("P2-OCT20-RERUNS", "Paper 2", "papers/recompute_oct20.py", "python3 papers/recompute_oct20.py", "20261020",
     "papers/recomputed/R_oct20_reruns.json", "Prop prop:invariance (1,000 cohort splittings), Prop prop:lucas (3,000 draws), Prop prop:multi network"),
    ("P2-T6M-SEARCH", "Paper 2", "theory/t6m_search4.py", "python3 theory/t6m_search4.py", "deterministic",
     "recomputed/R_audit_oct2026.json", "Theorems thm:t6, thm:nomom, thm:noover, Prop prop:t6m, Remark rem:counter"),
    ("P2-CALIB-GUARD", "Paper 2", "papers/calib_guard.py", "python3 papers/calib_guard.py", "deterministic",
     "recomputed/R_P2_calibrated_guard.json", "Section 5.5 & Table tab:calib & Fig fig:calib (Peak vs summed gain at calibrated BTCUSDT parameters)"),
    ("P2-EQUILIBRIUM", "Paper 2", "theory/equilibrium.py", "python3 theory/equilibrium.py", "0",
     "recomputed/R_P2_equilibrium.json", "Proposition prop:equil (N-dealer equilibrium under-supply of reversion and Pigouvian rebate)"),
    ("P2-DOLLAR-TRANS", "Paper 2", "papers/recompute_dollar.py", "python3 papers/recompute_dollar.py", "deterministic",
     "recomputed/R_P2_dollar_translation.json", "Section 7 economic magnitude translation in basis points and USD"),
    ("P2-P7-BYBIT-TRADES", "Paper 2", "p7res/prereg/P7_bybit.json", "Colab Protocol P7", "20261021",
     "p7res/results/W6_bybit_test.json", "Section 7.4 Pre-registered Bybit 40-symbol trade-only cross-venue test"),
    ("P2-P10-BYBIT-OB", "Paper 2", "p10b/cells/v6_test.py", "python3 p10b/cells/v6_test.py", "20261025",
     "p10res/results/V6_bybit_ob_test.json", "Section 7.4 & Table tab:bybitob Pre-registered Bybit 1% order-book depth test"),
    ("P2-P12-CERT-GUARD", "Paper 2", "p12/q6_test.py", "python3 p12/q6_test.py", "20261027",
     "p12res/results/Q6_certified_guard.json", "Section 7.5 & Table tab:certguard Pre-registered 3-day certified guard position-limit backtest"),
    ("P2-P12-OCT10-EVENT", "Paper 2", "p12/q7_event.py", "python3 p12/q7_event.py", "20261027",
     "p12res/results/Q7_oct10_event.json", "Section 7.3 & Fig fig:oct10 October 10, 2025 liquidation crash event study"),
    ("P2-P13-R1-THROTTLE", "Paper 2", "p13/r1_throttle.py", "python3 p13/r1_throttle.py", "20261028",
     "p13res/results/R1_guard_throttle.json", "Section 7.5 & Table tab:backtest Six-hour estimated guard throttle vs volatility limit"),
    ("P2-P13-R2-TERCILES", "Paper 2", "p13/r2_terciles.py", "python3 p13/r2_terciles.py", "20261028",
     "p13res/results/R2_terciles_gain_multiple.json", "Section 7 depth-tercile heterogeneity and gain multiple"),
    ("P2-P13-R3-BYBIT-BARS", "Paper 2", "p13/r3_bybit_bars.py", "python3 p13/r3_bybit_bars.py", "20261028",
     "p13res/results/R3_bybit_bar_diagnostics.json", "Section 7.4 Bybit vs Binance bar-level microstructure diagnostics"),
    ("P2-P13-R4-IV", "Paper 2", "p13/r4_iv.py", "python3 p13/r4_iv.py", "20261028",
     "p13res/results/R4_iv_C3.json", "Section 7 instrumental-variables / split-window robustness check for C3_hat"),
    ("P2-P13-R5-FIXEDGRID", "Paper 2", "p13/r5_fixedgrid.py", "python3 p13/r5_fixedgrid.py", "20261028",
     "p13res/results/R5_fixed_grid_depletion.json", "Section 6 fixed-price-grid book depletion vs recentered band depth"),
    ("P2-P13-R6-CFTC-BASIS", "Paper 2", "p13/r6_cftc.py", "python3 p13/r6_cftc.py", "20261028",
     "p13res/results/R6_cftc_basis_signature.json", "Paper 1 Section 6.2 leveraged-funds vs asset-manager CFTC persistence signature"),
    ("P2-P13-R7-CO-SPOT", "Paper 2", "p13/r7_co.py", "python3 p13/r7_co.py", "20261028",
     "p13res/results/R7_cochrane_orcutt_spot.json", "Section 7 Cochrane-Orcutt serial-correlation correction on spot panel"),
    ("P2-P13-R8-VPIN", "Paper 2", "p13/r8_vpin.py", "python3 p13/r8_vpin.py", "20261029",
     "p13res/results/R8_vpin.json", "Section 1 & Section 7 Post-hoc head-to-head comparison with 50-bucket VPIN (Delta R^2 +2.03 pp beyond baseline+VPIN)"),
    ("P2-P14-US-EQUITIES", "Paper 2", "p14/a5_test.py", "python3 p14/a5_test.py", "20261030",
     "p14res/results/A5_us_equity_test.json", "Section 7.4 & Table tab:stocks Pre-registered 60-stock US equities consolidated-trade test"),
]


def main():
    out_csv = SUITE / "EXPERIMENT_MANIFEST.csv"
    with out_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "experiment_id",
            "paper",
            "script_path",
            "script_sha256",
            "command",
            "seed_or_mode",
            "output_path",
            "output_sha256",
            "associated_paper_claims",
        ])
        for exp_id, paper, script, cmd, seed, out_p, claims in EXPERIMENTS:
            writer.writerow([
                exp_id,
                paper,
                script,
                sha256(script),
                cmd,
                seed,
                out_p,
                sha256(out_p),
                claims,
            ])
    print(f"[PASS] Wrote {len(EXPERIMENTS)} experiment lineage rows to {out_csv}")


if __name__ == "__main__":
    main()

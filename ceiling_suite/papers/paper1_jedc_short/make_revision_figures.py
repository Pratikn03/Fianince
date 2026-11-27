"""Generate publication-grade figures for Paper 1 JEDC Main (Fig 3) and Online Supplement (Figs S2-S4)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
})


def make_twse_sensitivity_figure():
    data = json.loads((ROOT / "ceiling_suite/p1_empirics/p1_round3_sensitivity_results.json").read_text())
    hold = data["p1t_updated_holdout"]
    reg = data["p1t_regime_split_20200323"]
    stab = hold["diagnostics"]["stability"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 2.45), constrained_layout=True)

    # Panel A: P1T Out-of-Sample Holdout & 23 March 2020 Regime Split
    labels = [
        "Pooled (2019-23)",
        "Pre-Mar 2020 (5s Call)",
        "Post-Mar 2020 (Cont.)",
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
        "Reverse Causality",
    ]
    entries = [
        hold["primary_block20"],
        reg["pre_20200323_call_auction_5s"]["Foreign_block20"],
        reg["post_20200323_continuous_matching"]["Foreign_block20"],
        stab["2019"],
        stab["2020"],
        stab["2021"],
        stab["2022"],
        stab["2023"],
        hold["diagnostics"]["reverse_causality"],
    ]
    y_pos = np.arange(len(labels))[::-1]
    ests = [e["D"] for e in entries]
    los = [e["D"] - e["ci95"][0] for e in entries]
    his = [e["ci95"][1] - e["D"] for e in entries]
    colors = [
        "#1f4e78", "#2e75b6", "#0b5394",
        "#4a7ebb", "#4a7ebb", "#4a7ebb", "#7f8c8d", "#7f8c8d",
        "#c0392b",
    ]

    ax1.axvline(0.0, color="#444444", linestyle="--", linewidth=0.9)
    for y, est, lo, hi, col in zip(y_pos, ests, los, his, colors):
        ax1.errorbar(
            est, y, xerr=[[lo], [hi]], fmt="o", color=col,
            ecolor=col, elinewidth=1.4, capsize=3, markersize=4.5,
        )
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels)
    ax1.set_xlabel(r"Out-of-sample Foreign forecast gain $\hat{D}$ (95% block CI)")
    ax1.set_title("Panel A: TWSE Holdout, Regime Split & Placebo")
    ax1.grid(axis="x", linestyle=":", alpha=0.5)

    # Panel B: P1M Specification Sensitivity (Memory Rates r_c)
    p1m_base = data["p1m_updated_panel"]
    p1m_lim = data["p1m_exclude_limits"]
    p1m_dx = data["p1m_price_diff"]

    classes = ["Foreign", "Trust", "Dealers"]
    x = np.arange(len(classes))
    w = 0.25

    r_base = p1m_base["theta"]["r"]
    r_base_ci = [p1m_base["bootstrap"]["ci"][f"r_{c}"]["ci95"] for c in classes]
    r_lim = p1m_lim["theta"]["r"]
    r_dx = [p1m_dx["flow_on_dx_rules"][c][0] for c in classes]
    r_dx_ci = [p1m_dx["bootstrap_ci"][f"r_{c}_dx"]["ci95"] for c in classes]

    ax2.bar(
        x - w, r_base, width=w, color="#1f4e78", label=r"Baseline ($\sum a_j=0.97$)",
        yerr=[[r_base[i] - r_base_ci[i][0] for i in range(3)], [r_base_ci[i][1] - r_base[i] for i in range(3)]],
        capsize=3, error_kw={"elinewidth": 1.1},
    )
    ax2.bar(
        x, r_lim, width=w, color="#5b9bd5", label=r"Excl. limits ($\hat\kappa=0.0041$)",
    )
    ax2.bar(
        x + w, r_dx, width=w, color="#ed7d31", label=r"First-diff $\Delta x$ ($\sum a_j=-0.11$)",
        yerr=[[r_dx[i] - r_dx_ci[i][0] for i in range(3)], [r_dx_ci[i][1] - r_dx[i] for i in range(3)]],
        capsize=3, error_kw={"elinewidth": 1.1},
    )
    ax2.set_xticks(x)
    ax2.set_xticklabels(classes)
    ax2.set_ylim(0, 0.56)
    ax2.set_ylabel(r"Estimated memory persistence $\hat{r}_c$")
    ax2.set_title("Panel B: Class Memory Stability Across Specifications")
    ax2.legend(frameon=False, loc="upper right", fontsize=7.3)
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    out_path = OUT_DIR / "fig_twse_sensitivity.pdf"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def make_fragility_figure():
    # Exact Theorem 4.2 one-cohort equilibrium branch:
    # A=0.5, sF=0.25, sXi=0.35, abar=0.3, r=0.5, w=1.0
    A, sF, sXi, abar, r, w = 0.5, 0.25, 0.35, 0.30, 0.50, 1.0
    D_min = abar + 2 * A * sF * sXi
    D_grid = np.linspace(max(D_min, r) + 1e-4, 1.0, 2000)
    disc = (D_grid - abar) ** 2 - 4 * (A ** 2) * (sF ** 2) * (sXi ** 2)
    kappa_minus = D_grid * ((D_grid - abar) - np.sqrt(disc)) / (2 * A * (sXi ** 2))
    S_M = w / (D_grid - r)
    lam_grid = (D_grid - abar) / (kappa_minus * S_M)

    idx_crit = int(np.argmax(lam_grid))
    lam_crit = lam_grid[idx_crit]
    D_crit = D_grid[idx_crit]

    # Stable upper branch D >= D_crit
    D_stab = D_grid[idx_crit:]
    lam_stab = lam_grid[idx_crit:]
    km_stab = kappa_minus[idx_crit:]
    depth_stab = D_stab / km_stab
    V_stab = (sF ** 2) + (km_stab / D_stab) ** 2 * (sXi ** 2)

    # Unstable lower branch D < D_crit
    D_unst = D_grid[:idx_crit + 1]
    lam_unst = lam_grid[:idx_crit + 1]
    km_unst = kappa_minus[:idx_crit + 1]
    depth_unst = D_unst / km_unst

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.2), constrained_layout=True)

    ax1.plot(lam_stab, depth_stab, color="#1f4e78", linewidth=1.8, label="Stable branch $D(\\lambda)/\\kappa(\\lambda)$")
    ax1.plot(lam_unst, depth_unst, color="#c0392b", linestyle="--", linewidth=1.3, label="Unstable branch")
    ax1.axvline(lam_crit, color="#444444", linestyle=":", linewidth=1.1)
    ax1.scatter([lam_crit], [D_crit / kappa_minus[idx_crit]], color="#c0392b", zorder=5, s=30,
                label=rf"Saddle-node fold $\lambda_{{\mathrm{{crit}}}}={lam_crit:.3f}$")
    ax1.set_xlabel(r"Feedback intensity scale $\lambda$")
    ax1.set_ylabel(r"Effective market depth $D / \kappa$")
    ax1.set_title("Panel A: Square-Root Liquidity Collapse (Theorem 4.2)")
    ax1.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax1.grid(True, linestyle=":", alpha=0.4)

    ax2.plot(lam_stab, V_stab, color="#1f4e78", linewidth=1.8, label=r"Equilibrium variance $V(\lambda)$")
    ax2.axhline(2 * (sF ** 2), color="#c0392b", linestyle="--", linewidth=1.2,
                label=rf"Vieta ceiling $2\sigma_F^2 = {2*sF**2:.3f}$")
    ax2.axvline(lam_crit, color="#444444", linestyle=":", linewidth=1.1)
    ax2.scatter([lam_crit], [V_stab[0]], color="#c0392b", zorder=5, s=30)
    ax2.set_xlabel(r"Feedback intensity scale $\lambda$")
    ax2.set_ylabel(r"Conditional variance $V(\lambda)$")
    ax2.set_title(r"Panel B: Finite Threshold Variance $V(\lambda_{\mathrm{crit}}) < 2\sigma_F^2$")
    ax2.legend(frameon=False, fontsize=7.5, loc="lower right")
    ax2.grid(True, linestyle=":", alpha=0.4)

    out_path = OUT_DIR / "fig_supp_fragility_equilibrium.pdf"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def make_surveillance_and_adaptive_figure():
    diag_path = ROOT / "research_extension/paper1_publication_revision/passive_tax_followup/passive_diagnostics.json"
    diag = json.loads(diag_path.read_text())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.2), constrained_layout=True)

    # Panel A: Proposition 7.11 Strategic Crowding Rates (n=4 benchmark)
    N = np.logspace(2, 6, 200)
    delta_1side = 0.25 * (N / 100.0) ** (-0.5)       # N^{-1/(n-2)} = N^{-1/2}
    delta_glrt = 0.25 * (N / 100.0) ** (-1.0 / 3.0)   # N^{-1/(n-1)} = N^{-1/3}
    J_1side = (N / 100.0) ** (-1.0)                   # N^{-2/(n-2)} = N^{-1}

    ax1.loglog(N, delta_1side, color="#1f4e78", linewidth=1.8, label=r"One-sided test: $\delta_N^* \asymp N^{-1/2}$")
    ax1.loglog(N, delta_glrt, color="#ed7d31", linewidth=1.6, linestyle="--", label=r"Composite GLRT: $\delta_N^* \asymp N^{-1/3}$")
    ax1.loglog(N, J_1side, color="#c0392b", linewidth=1.5, linestyle=":", label=r"KL divergence $J_N^* \asymp N^{-1} \to 0$")
    ax1.set_xlabel(r"Sample size $N$")
    ax1.set_ylabel("Equilibrium spacing / divergence")
    ax1.set_title("Panel A: Surveillance Paradox Crowding (Prop. 7.11)")
    ax1.legend(frameon=False, fontsize=7.3, loc="lower left")
    ax1.grid(True, which="both", linestyle=":", alpha=0.4)

    # Panel B: Section S23 Adaptive Passive Incidence RMSE (from passive_diagnostics.json)
    rows = diag["rows"]
    ns = [r["prices"] for r in rows]
    rmses = [r["rmse"] for r in rows]
    base_rows = diag["fixed_2logn_oracle_baseline_rows"]
    b_ns = [r["prices"] for r in base_rows]
    b_rmses = [r["rmse"] for r in base_rows]
    ref_line = [rmses[0] * (ns[0] / n) ** 0.5 for n in ns]

    ax2.loglog(ns, rmses, "o-", color="#1f4e78", linewidth=1.8, markersize=5, label="Adaptive truncation RMSE")
    ax2.loglog(b_ns, b_rmses, "s--", color="#c0392b", linewidth=1.4, markersize=4.5, label="Fixed-degree baseline (plateau)")
    ax2.loglog(ns, ref_line, ":", color="#7f8c8d", linewidth=1.2, label=r"$O(n^{-1/2})$ slope")
    ax2.set_xlabel(r"Passive sample size $n$")
    ax2.set_ylabel("Transfer-function RMSE")
    ax2.set_title("Panel B: Adaptive Passive Truncation (Sec. S23)")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax2.grid(True, which="both", linestyle=":", alpha=0.4)

    out_path = OUT_DIR / "fig_supp_surveillance_mpv.pdf"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    make_twse_sensitivity_figure()
    make_fragility_figure()
    make_surveillance_and_adaptive_figure()

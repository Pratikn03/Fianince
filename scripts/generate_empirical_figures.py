"""Generate publication-grade empirical visualizations for the 768-day Binance panel
and dual structural identification (SMM vs Rigobon).
Produces paper/figures/fig_binance_panel_and_identification.pdf and PNG preview.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DATA_FILE = ROOT / "results" / "provenance" / "binance_panel_results.json"
SUMMARY_FILE = ROOT / "results" / "provenance" / "binance_panel_summary.json"
FIG_DIR = ROOT / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- Styling
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "axes.labelsize": 9.5,
    "axes.titlesize": 10.0,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.0,
    "figure.titlesize": 11.5,
    "lines.linewidth": 1.4,
    "axes.linewidth": 0.8,
    "grid.linewidth": 0.5,
    "grid.alpha": 0.35,
    "axes.grid": True,
})

# Academic Palette
NAVY = "#1f4e79"
TEAL = "#008080"
CRIMSON = "#b22222"
FOREST = "#2e7d32"
AMBER = "#d35400"
SLATE = "#5a6b7c"


def build_figure():
    with open(DATA_FILE) as f:
        panel_data = json.load(f)
    with open(SUMMARY_FILE) as f:
        summary_data = json.load(f)

    results = panel_data["results"]
    results.sort(key=lambda r: (r["date"], r["symbol"]))

    fig = plt.figure(figsize=(10.5, 3.6), dpi=300)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.3, 1.0, 1.0], wspace=0.30,
                           left=0.06, right=0.98, top=0.88, bottom=0.16)

    # -----------------------------------------------------------------------
    # Panel (a): Multi-Year Dynamic Evolution: S and Q (2021-2024)
    # -----------------------------------------------------------------------
    ax_a = fig.add_subplot(gs[0, 0])
    
    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in results]
    s_vals = [r["S"] for r in results]
    q_vals = [r["Q"] for r in results]

    unique_dates = sorted(list(set(dates)))
    date_to_s = {d: [] for d in unique_dates}
    date_to_q = {d: [] for d in unique_dates}
    for d, s, q in zip(dates, s_vals, q_vals):
        date_to_s[d].append(s)
        date_to_q[d].append(q)

    med_s = [np.median(date_to_s[d]) for d in unique_dates]
    p25_s = [np.percentile(date_to_s[d], 25) for d in unique_dates]
    p75_s = [np.percentile(date_to_s[d], 75) for d in unique_dates]

    med_q = [np.median(date_to_q[d]) for d in unique_dates]

    # Plot S envelope
    ax_a.scatter(dates, s_vals, color=NAVY, alpha=0.15, s=6, label=r"Daily asset $\hat S$", rasterized=True)
    ax_a.plot(unique_dates, med_s, color=NAVY, lw=1.6, label=r"Median $\hat S$ across assets")
    ax_a.fill_between(unique_dates, p25_s, p75_s, color=NAVY, alpha=0.20, label=r"IQR ($25\%\text{--}75\%$)")

    # Critical boundary S = 1.0
    ax_a.axhline(1.0, color=CRIMSON, ls="--", lw=1.5, label=r"Instability boundary $S = 1.0$")

    # Inset for Q > 0 (positioned cleanly in lower left)
    ax_ins = ax_a.inset_axes([0.06, 0.16, 0.44, 0.36])
    ax_ins.scatter(dates, q_vals, color=FOREST, alpha=0.10, s=4, rasterized=True)
    ax_ins.plot(unique_dates, med_q, color=FOREST, lw=1.2)
    ax_ins.axhline(0.0, color="black", ls=":", lw=0.8)
    ax_ins.set_title(r"Feedback $\hat Q$ (Pooled $= +0.008$)", fontsize=7.0, pad=2, weight="bold")
    ax_ins.set_ylim(-0.015, 0.035)
    ax_ins.xaxis.set_major_formatter(mdates.DateFormatter("%y"))
    ax_ins.xaxis.set_major_locator(mdates.YearLocator())
    ax_ins.tick_params(labelsize=6)
    ax_ins.grid(True, alpha=0.25)

    ax_a.set_ylim(0.68, 1.05)
    ax_a.xaxis.set_major_locator(mdates.YearLocator())
    ax_a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax_a.set_ylabel(r"Closed-loop persistence $\hat S = a + \hat Q$", fontweight="bold")
    ax_a.set_title(r"(a) Persistence $\hat S$ Across 768 Asset-Days", loc="left", fontweight="bold")
    ax_a.legend(loc="upper right", framealpha=0.9, facecolor="white", edgecolor="none")

    # Annotate epochs along the bottom
    ax_a.text(datetime(2021, 7, 1), 0.70, "2021 Bull", fontsize=6.8, color=SLATE, ha="center", weight="bold")
    ax_a.text(datetime(2022, 7, 1), 0.70, "2022 Crash", fontsize=6.8, color=SLATE, ha="center", weight="bold")
    ax_a.text(datetime(2023, 7, 1), 0.70, "2023 Quiet", fontsize=6.8, color=SLATE, ha="center", weight="bold")
    ax_a.text(datetime(2024, 7, 1), 0.70, "2024 ETF", fontsize=6.8, color=SLATE, ha="center", weight="bold")

    # -----------------------------------------------------------------------
    # Panel (b): Asset-by-Asset Comparison: Q vs Q_30 (Memory Purged)
    # -----------------------------------------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])

    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT"]
    labels = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "LTC"]
    y_pos = np.arange(len(symbols))

    by_asset = summary_data["by_asset"]
    q_means = [by_asset[s]["Q"]["mean"] for s in symbols]
    q_cis = np.array([[by_asset[s]["Q"]["mean"] - by_asset[s]["Q"]["ci95"][0],
                       by_asset[s]["Q"]["ci95"][1] - by_asset[s]["Q"]["mean"]] for s in symbols]).T

    q30_means = [by_asset[s]["Q30"]["mean"] for s in symbols]
    q30_cis = np.array([[by_asset[s]["Q30"]["mean"] - by_asset[s]["Q30"]["ci95"][0],
                         by_asset[s]["Q30"]["ci95"][1] - by_asset[s]["Q30"]["mean"]] for s in symbols]).T

    offset = 0.16
    ax_b.errorbar(q_means, y_pos + offset, xerr=q_cis, fmt="o", color=NAVY,
                  capsize=3, capthick=0.8, elinewidth=1.2, ms=4.5, label=r"Baseline $\hat Q$ (OLS)")
    ax_b.errorbar(q30_means, y_pos - offset, xerr=q30_cis, fmt="s", color=TEAL,
                  capsize=3, capthick=0.8, elinewidth=1.2, ms=4.0, label=r"Purged $\hat Q_{30}$ (30s splitting lag)")

    ax_b.axvline(0.0, color="black", ls=":", lw=1.0)
    ax_b.set_yticks(y_pos)
    ax_b.set_yticklabels(labels, fontweight="bold")
    ax_b.invert_yaxis()
    ax_b.set_xlabel(r"Estimated feedback coefficient $Q$", fontweight="bold")
    ax_b.set_title(r"(b) Asset-Level Feedback & Memory Bias", loc="left", fontweight="bold")
    ax_b.legend(loc="lower right", framealpha=0.9, facecolor="white", edgecolor="none")
    ax_b.set_xlim(-0.002, 0.016)

    # -----------------------------------------------------------------------
    # Panel (c): Dual Structural Identification: Reduced-Form vs SMM vs Rigobon
    # -----------------------------------------------------------------------
    ax_c = fig.add_subplot(gs[0, 2])

    methods = [
        ("OLS\nReduced-Form", 0.00815, 0.00760, 0.00870, NAVY, "o"),
        ("MD\nLyapunov (C1)", 0.00861, 0.00750, 0.00972, FOREST, "^"),
        ("Rigobon (C2)\nHeteroskedastic", -0.01913, -0.02186, -0.01640, CRIMSON, "v"),
    ]

    x_c = np.arange(len(methods))
    for i, (m_label, val, low, high, col, marker) in enumerate(methods):
        err = np.array([[val - low], [high - val]])
        ax_c.errorbar(i, val, yerr=err, fmt=marker, color=col, ms=6.5,
                      capsize=4, capthick=1.0, elinewidth=1.6, lw=0)
        ax_c.text(i, val + (0.0025 if val > 0 else -0.0035), f"{val:+.4f}",
                  ha="center", va="bottom" if val > 0 else "top", fontsize=7.5, color=col, fontweight="bold")

    ax_c.axhline(0.0, color="black", ls=":", lw=1.0)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels([m[0] for m in methods], fontsize=8.0, fontweight="bold")
    ax_c.set_ylabel(r"Estimated feedback parameter $Q$", fontweight="bold")
    ax_c.set_title(r"(c) Dual Structural Identification", loc="left", fontweight="bold")
    ax_c.set_ylim(-0.028, 0.020)

    # Annotate economic mechanism contrast with clean text boxes
    ax_c.text(0.5, 0.0155, "Dynamic Momentum\n(Flow amplifies trend)",
              ha="center", va="center", fontsize=6.8, color=NAVY, weight="bold",
              bbox=dict(boxstyle="round,pad=0.25", fc="#e8f0fe", ec=NAVY, lw=0.6))

    ax_c.annotate("Contemporaneous Buffering\n(Liquidity provision absorbs shocks)",
                  xy=(2.0, -0.0191), xytext=(1.5, -0.009),
                  arrowprops=dict(arrowstyle="->", color=CRIMSON, lw=0.8),
                  ha="center", va="center", fontsize=6.8, color=CRIMSON, weight="bold",
                  bbox=dict(boxstyle="round,pad=0.25", fc="#fce8e6", ec=CRIMSON, lw=0.6))

    # Save outputs
    pdf_path = FIG_DIR / "fig_binance_panel_and_identification.pdf"
    png_path = FIG_DIR / "fig_binance_panel_and_identification.png"
    plt.savefig(pdf_path, bbox_inches="tight")
    plt.savefig(png_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated: {pdf_path}")
    print(f"Generated: {png_path}")

    # Generate Welfare Pareto Frontier figure
    try:
        from simulations.welfare_pareto_frontier import compute_welfare_pareto_frontier
        compute_welfare_pareto_frontier()
        print(f"Generated: {FIG_DIR / 'fig_welfare_pareto_frontier.pdf'}")
    except Exception as e:
        print(f"Note: welfare pareto frontier generation error: {e}")


if __name__ == "__main__":
    build_figure()


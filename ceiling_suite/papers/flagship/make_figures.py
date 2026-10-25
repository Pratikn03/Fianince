"""Figures for the flagship paper, drawn from committed result files (no new data). Writes fig_*.pdf next to this file."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402

HERE = Path(__file__).resolve().parent
TH = HERE.parents[2] / "thesis"
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "pdf.fonttype": 42})


def style(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.6); ax.set_axisbelow(True)


# Figure 1: certification comes with the record, identification does not (F1's registered secondary curve)
f1 = json.loads((TH / "evidence/F1_results.json").read_text())["evaluation"]; cv = f1["secondary"]["curve"]
keys = ["60", "120", "240", "all"]; n = f1["n_evaluable"]
xs = [60, 120, 240, 430]
dec = [100 * cv[k]["decided"] / n for k in keys]; idn = [100 * cv[k]["identified"] / n for k in keys]
fig, ax = plt.subplots(figsize=(4.6, 2.8)); style(ax)
ax.plot(xs, dec, color=BLUE, lw=2, marker="o", ms=5, label="Margin decided")
ax.plot(xs, idn, color=ORANGE, lw=2, marker="s", ms=5, label="Memories identified")
ax.text(xs[-1] + 8, dec[-1], "margin decided", color=INK, va="center", fontsize=8)
ax.text(xs[-1] + 8, idn[-1] + 4, "memories identified", color=INK, va="center", fontsize=8)
ax.set_xscale("log"); ax.set_xticks(xs); ax.set_xticklabels(["60", "120", "240", "all (430)"])
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_ylim(0, 100); ax.set_xlim(50, 900); ax.set_xlabel("Valid days used"); ax.set_ylabel("Share of markets (%)")
ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.45), fontsize=8)
fig.tight_layout(); fig.savefig(HERE / "fig_learning_curve.pdf"); plt.close(fig)

# Figure 2: the certificate's success depends on the margin only through T M / g(1) (simulation, Theorem uniform)
un = json.loads((TH / "checks/uniform_certification_numeric_check.json").read_text())["uniform_power"]
fig, ax = plt.subplots(figsize=(4.6, 2.8)); style(ax)
for g, col, lab in (("g_roots_2_-3", BLUE, "roots of g at 2 and $-3$"), ("g_roots_1.5pm_i", ORANGE, "roots of g at $1.5\\pm i$")):
    for T, ls in ((500, "--"), (2000, "-")):
        th = [0, 5, 10, 20, 40]; y = [100 * un[f"{g}|T={T}|c={c}"]["rate_certified_safe"] for c in th]
        ax.plot(th, y, color=col, lw=2 if T == 2000 else 1.4, ls=ls, marker="o", ms=4, label=f"{lab}, T={T}")
ax.axhline(5, color=MUTED, lw=0.8, ls=":"); ax.text(41, 5, "5% size", color=MUTED, fontsize=7, va="center")
ax.set_xlabel(r"$\theta = T M / g(1)$"); ax.set_ylabel("Certified safe (%)"); ax.set_ylim(0, 102)
ax.legend(fontsize=7, loc="lower right", bbox_to_anchor=(1.0, 0.1)); ax.set_xlim(-1, 47)
fig.tight_layout(); fig.savefig(HERE / "fig_uniform_power.pdf"); plt.close(fig)

# Figure 3: exploratory robustness of S1's variance forecast (t-statistics)
rb = json.loads((HERE / "robustness.json").read_text())["S1_P2_variance"]
lab = {"baseline": "Registered", "cluster_week": "Clustered by week", "cluster_symbol": "Clustered by market",
       "train_50": "Training share 50%", "train_70": "Training share 70%", "winsor_01_99": "Winsorized 1/99%",
       "year_2025": "2025 only", "year_2026": "2026 only", "without_oct_2025": "Without Oct 2025",
       "high_vol_symbols": "High-volatility markets", "low_vol_symbols": "Low-volatility markets"}
items = [(lab[k], rb[k]["t"]) for k in lab][::-1]
fig, ax = plt.subplots(figsize=(4.6, 3.0)); ax.grid(axis="x", color=GRID, linewidth=0.6); ax.set_axisbelow(True)
ax.scatter([t for _, t in items], range(len(items)), color=BLUE, s=28, zorder=3)
lo, hi = rb["leave_one_symbol_out"]["t_min"], rb["leave_one_symbol_out"]["t_max"]
ax.plot([lo, hi], [len(items)] * 2, color=BLUE, lw=2); ax.scatter([lo, hi], [len(items)] * 2, color=BLUE, s=14)
ax.set_yticks(list(range(len(items))) + [len(items)]); ax.set_yticklabels([n_ for n_, _ in items] + ["Leave one market out"], fontsize=7.5)
ax.axvline(1.645, color=MUTED, lw=0.8, ls=":"); ax.text(1.72, len(items) - 0.4, "one-sided 5%", color=MUTED, fontsize=7)
ax.set_xlim(0, 6.2); ax.set_xlabel("Clark–West t-statistic")
fig.tight_layout(); fig.savefig(HERE / "fig_robustness.pdf"); plt.close(fig)
print("figures written")

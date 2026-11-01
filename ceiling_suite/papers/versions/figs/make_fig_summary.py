"""Figure 1 of Paper 1: the paper in one figure. Reads registered result files only.
(a) schematic of the identification boundary and the supervisory separation;
(b) real-noise injection test (registered, I1): data needed against memory spacing, price-only vs tagged;
(c) CFTC class reports in price data (post hoc, C7): factor by which a price-only sample must grow."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
I1 = json.load(open(os.path.join(ROOT, "p1_injection", "results", "I1_injection_test.json")))["metrics"]["arms"]["real"]
C7 = json.load(open(os.path.join(ROOT, "p11res", "results", "C7_data_equivalence.json")))
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "serif"})
fig = plt.figure(figsize=(7.0, 2.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.0, 1.0], wspace=0.42)

# (a) schematic
ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
def box(x, y, w, h, text, fc="#f3f2ef", ec=INK2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15,rounding_size=0.3", fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7, color=INK)
def arrow(x0, y0, x1, y1, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=7, lw=0.8, color=INK2, ls=ls))
for k, (y, lab) in enumerate([(8.0, "fast"), (6.2, "medium"), (4.4, "slow")]):
    box(0.1, y, 2.6, 1.2, lab + "\ngroup")
    arrow(2.9, y + 0.6, 4.2, 6.8)
box(4.3, 6.1, 2.2, 1.4, "sum of\norders")
arrow(6.65, 6.8, 7.7, 6.8)
box(7.75, 6.1, 2.0, 1.4, "price")
ax.add_patch(FancyArrowPatch((8.75, 6.0), (1.4, 3.9), connectionstyle="arc3,rad=-0.35", arrowstyle="-|>",
                             mutation_scale=7, lw=0.8, color=INK2, ls="--"))
ax.text(5.0, 2.55, "prices feed back", fontsize=6.5, color=INK2, ha="center")
ax.text(0.1, 1.35, "Prices see only the sum:", fontsize=7, color=INK, fontweight="bold")
ax.text(0.1, 0.55, "market-wide measure: sized from prices", fontsize=6.5, color=INK)
ax.text(0.1, -0.25, "targeted measure: needs the groups", fontsize=6.5, color=INK)
ax.set_title("(a) What prices reveal", fontsize=8, loc="left", color=INK)

# (b) injection test
ax = fig.add_subplot(gs[1])
d2, p2, t2 = map(np.array, (I1["K2_d_eta"], I1["K2_price_N_star"], I1["K2_tagged_N_star"]))
d3, p3 = map(np.array, (I1["K3_d_eta"], I1["K3_price_N_star"]))
ax.loglog(d2, p2, color=BLUE, lw=2, marker="o", ms=4, label=f"prices, 2 groups (slope {I1['slope_K2_price']:.2f})")
ax.loglog(d3, p3, color=ORANGE, lw=2, marker="s", ms=4, label=f"prices, 3 groups (slope {I1['slope_K3_price']:.2f})")
ax.loglog(d2, t2, color=AQUA, lw=2, marker="^", ms=4, label="tagged records (flat)")
ax.set_xlabel(r"memory spacing $\Delta\eta$"); ax.set_ylabel("experiments needed")
ax.grid(True, which="major", color=GRID, lw=0.5)
ax.legend(frameon=False, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=1)
ax.set_xlim(min(d2.min(), d3.min()) / 1.3, max(d2.max(), d3.max()) * 1.3)
from matplotlib.ticker import FixedLocator, NullFormatter, FormatStrFormatter
ax.xaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.3, 0.5])); ax.xaxis.set_major_formatter(FormatStrFormatter("%g"))
ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_title("(b) Cost of learning the groups", fontsize=8, loc="left", color=INK)

# (c) data equivalence
ax = fig.add_subplot(gs[2])
rows = sorted(C7["rows"], key=lambda r: r["factor"])
y = np.arange(len(rows))
cols = [BLUE if r["set"] == "original" else ORANGE for r in rows]
ax.barh(y, [r["factor"] for r in rows], color=cols, height=0.7, edgecolor="#fcfcfb", lw=0.5)
NAMES = {"BTC": "Bitcoin", "ETH": "Ether", "ES": "S&P 500", "TY": "Treasury", "EUR": "Euro", "JPY": "Yen", "CL": "Crude oil",
         "NG": "Natural gas", "CT": "Cotton", "GBP": "Pound", "GC": "Gold", "HG": "Copper", "KC": "Coffee", "LE": "Cattle",
         "NQ": "Nasdaq-100", "SB": "Sugar", "SI": "Silver", "ZC": "Corn", "ZS": "Soybeans", "ZW": "Wheat"}
ax.set_xscale("log"); ax.set_yticks(y); ax.set_yticklabels([NAMES[r["market"]] for r in rows], fontsize=5.5)
ax.axvline(C7["median_factor"], color=INK2, lw=0.8, ls="--")
ax.set_ylim(-0.7, len(rows) + 0.8)
ax.text(C7["median_factor"] * 0.92, len(rows) - 0.1, f"median {C7['median_factor']:,.0f}", fontsize=6.5, color=INK, ha="right")
ax.set_xlabel("times more price data needed")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=BLUE, label="original 8 markets"), Patch(color=ORANGE, label="replication, 12 markets")],
          frameon=False, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=1)
ax.grid(True, axis="x", which="major", color=GRID, lw=0.5)
ax.set_title("(c) Class reports in price data", fontsize=8, loc="left", color=INK)
fig.savefig(os.path.join(HERE, "fig_summary.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(HERE, "fig_summary.png"), bbox_inches="tight", dpi=200)
print("written")

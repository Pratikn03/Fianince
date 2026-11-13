"""Figure for Paper 1 (core Proposition prop:nearcrit, note Proposition n:nearcrit): the passive barrier.

Panel (a): passive information per observation (Gaussian KL rate, Whittle) between the Gauss and Gauss-Radau
K-group populations at a common feedback budget S = 1 - 1e-6, against the spacing of memories, with the
(spacing)^(4K-2) reference slopes. Computed here.
Panel (b): the same information against the margin 1 - S, for the pair held at a common budget (bounded) and at a
common persistence a (grows without bound). Read from fragility_scan_matched_results.json and
fragility_scan_results.json (same parameters: rc = 0.5, spacing 0.1, W = 0.3, kappa = 0.5).
Run from this folder: python3 make_barrier_figure.py -> ../../ceiling_suite/papers/paper1_core/fig_barrier.pdf
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from fragility_scan import rules


def D(z, a, kappa, r, w):
    return z - a - kappa * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)


def kl_rate(K, dEta, eps, rc=0.5, W=0.3, kappa=0.5, n=400001):
    """Same computation as fragility_uniform_check.kl_rate (copied: that script runs on import)."""
    (xg, wg), (xr, wr) = rules(K)
    rA, wA, rB, wB = rc + dEta * xg, W * wg, rc + dEta * xr, W * wr
    aA = 1 - eps - kappa * np.sum(wA / (1 - rA)); aB = 1 - eps - kappa * np.sum(wB / (1 - rB))
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), n // 2)[::-1], np.logspace(-9, np.log10(np.pi), n // 2)])
    z = np.exp(1j * om)
    u = np.abs(D(z, aA, kappa, rA, wA)) ** 2 / np.abs(D(z, aB, kappa, rB, wB)) ** 2
    return float(np.trapezoid(u - 1 - np.log(u), om) / (4 * np.pi))


BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#222222", "#6b6b66"
spacings = np.array([0.2, 0.141, 0.1, 0.0707, 0.05, 0.0354, 0.025])
panel_a = {K: [kl_rate(K, s, 1e-6) for s in spacings] for K in (2, 3)}
fits = {K: float(np.polyfit(np.log(spacings), np.log(panel_a[K]), 1)[0]) for K in (2, 3)}
matched = json.load(open("fragility_scan_matched_results.json"))
common_a = json.load(open("fragility_scan_results.json"))

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.9))
for K, c, mk in ((2, BLUE, "o"), (3, ORANGE, "s")):
    y = np.array(panel_a[K])
    ax1.loglog(spacings, y, color=c, lw=2, marker=mk, ms=5, label=f"$K={K}$ (fitted slope {fits[K]:.2f})")
    ref = y[-1] * (spacings / spacings[-1]) ** (4 * K - 2)
    ax1.loglog(spacings, ref, color=MUTED, lw=1, ls=":")
    ax1.annotate(f"slope {4 * K - 2}", (spacings[2], ref[2]), textcoords="offset points", xytext=(6, -10),
                 color=MUTED, fontsize=8)
ax1.set_xlabel(r"spacing of memories $\Delta\eta$")
ax1.set_ylabel("passive information per observation")
ax1.set_title(r"(a) at $1-S=10^{-6}$", fontsize=9, color=INK, loc="left")
ax1.legend(frameon=False, fontsize=8, loc="lower right")
ax1.grid(True, which="major", color="#e6e6e3", lw=0.6)
ax1.set_xticks([0.025, 0.05, 0.1, 0.2]); ax1.set_xticklabels(["0.025", "0.05", "0.1", "0.2"])
ax1.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

for K, c, mk in (("2", BLUE, "o"), ("3", ORANGE, "s")):
    m = matched[K]["rows"]; g = common_a[K]["rows"]
    ax2.loglog([r["1-S"] for r in m], [r["passive_kl_rate"] for r in m], color=c, lw=2, marker=mk, ms=5)
    ax2.loglog([r["1-S"] for r in g], [r["passive_kl_rate"] for r in g], color=c, lw=1.5, ls="--", marker=mk,
               ms=5, mfc="white")
ax2.invert_xaxis()
ax2.set_xlabel(r"margin to instability $1-S$")
ax2.set_title(r"(b) at $\Delta\eta=0.1$", fontsize=9, color=INK, loc="left")
from matplotlib.lines import Line2D
hs = [Line2D([], [], color=BLUE, lw=2, marker="o", ms=5, label="$K=2$"),
      Line2D([], [], color=ORANGE, lw=2, marker="s", ms=5, label="$K=3$"),
      Line2D([], [], color=MUTED, lw=2, label="common budget $S$"),
      Line2D([], [], color=MUTED, lw=1.5, ls="--", marker="o", mfc="white", ms=5, label="common persistence $a$")]
ax2.legend(handles=hs, frameon=False, fontsize=7.5, loc="center", bbox_to_anchor=(0.5, 0.45), ncol=2)
ax2.set_xticks([0.2, 0.1, 0.05, 0.02, 0.01, 0.005]); ax2.set_xticklabels(["0.2", "0.1", "0.05", "0.02", "0.01", "0.005"])
ax2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax2.grid(True, which="major", color="#e6e6e3", lw=0.6)
fig.tight_layout()
out = "../../ceiling_suite/papers/paper1_core/fig_barrier.pdf"
fig.savefig(out); fig.savefig("fig_barrier.png", dpi=200)
json.dump({"spacings": spacings.tolist(), "panel_a_kl_rate": {str(k): v for k, v in panel_a.items()},
           "fitted_slopes": {str(k): v for k, v in fits.items()}}, open("make_barrier_figure_results.json", "w"), indent=1)
print("slopes", fits, "->", out)

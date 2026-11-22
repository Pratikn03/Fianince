"""Near instability with an admissible pair (21 November 2026, after the simulated referee reports).

The earlier scripts (fragility_uniform_check.py, make_barrier_figure.py, calibration_table.py, finite_sample_check.py)
held the two economies at a common feedback budget by giving them different persistences a. The paper's observer
knows a, so that pair is not admissible for it. Here both economies share a; economy B (Gauss--Radau) has its weights
rescaled by 1 + c, with c chosen so that both have the same feedback budget. Because the two normalized rules share
their moments of order 0..2K-2, c is of order (spacing)^(2K-1), and the largest weights still differ at order one.

Outputs: nearcrit_admissible_results.json and ../../ceiling_suite/papers/paper1_core/fig_barrier_admissible.pdf.
Run from this folder: python3 nearcrit_admissible.py
"""
import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.lines import Line2D

from scipy.linalg import cho_factor, cho_solve, solve_discrete_lyapunov, toeplitz
from fragility_scan import rules


def autocov(a, kappa, r, w, n):
    """As in finite_sample_check.py (copied: that script runs on import)."""
    eta = 1 - r; q = w / eta; K = len(r)
    A0 = np.zeros((K + 1, K + 1)); A0[0, 0] = a; A0[0, 1:] = kappa * q
    A = A0.copy()
    A[1:, :] = eta[:, None] * A0[0, :][None, :]
    A[1:, 1:] += np.diag(r)
    b = np.zeros(K + 1); b[0] = 1.0; b[1:] = eta
    P = solve_discrete_lyapunov(A, np.outer(b, b))
    g = np.empty(n); v = P[:, 0].copy()
    for h in range(n):
        g[h] = v[0]; v = A @ v
    return g


def kl_exact(gA, gB):
    SA, SB = toeplitz(gA), toeplitz(gB)
    cB = cho_factor(SB); M = cho_solve(cB, SA)
    _, ldA = np.linalg.slogdet(SA); _, ldB = np.linalg.slogdet(SB)
    return 0.5 * (np.trace(M) - len(gA) - (ldA - ldB))


def D(z, a, kappa, r, w):
    return z - a - kappa * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)


def pair(K, dEta, eps, rc=0.5, W=0.3, kappa=0.5, rescale=True):
    """Economies A (Gauss) and B (Gauss-Radau) with a common persistence a. With rescale=True, B's weights are
    scaled so that both budgets equal 1 - eps; with rescale=False, B keeps total weight W and its budget differs."""
    (xg, wg), (xr, wr) = rules(K)
    rA, wA, rB, wB = rc + dEta * xg, W * wg, rc + dEta * xr, W * wr
    c = np.sum(wA / (1 - rA)) / np.sum(wB / (1 - rB)) - 1
    if rescale:
        wB = wB * (1 + c)
    a = 1 - eps - kappa * np.sum(wA / (1 - rA))
    budgetB = a + kappa * np.sum(wB / (1 - rB))
    return (a, kappa, rA, wA), (a, kappa, rB, wB), {"c": float(c), "a": float(a), "budget_gap": float(budgetB - (1 - eps)),
                                                    "max_weight_A": float(wA.max() / wA.sum()),
                                                    "max_weight_B": float(wB.max() / wB.sum())}


def kl_rate(pA, pB, m=400001):
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), m // 2)[::-1], np.logspace(-9, np.log10(np.pi), m // 2)])
    z = np.exp(1j * om)
    u = np.abs(D(z, *pA)) ** 2 / np.abs(D(z, *pB)) ** 2          # f_B / f_A
    return float(np.trapezoid(u - 1 - np.log(u), om) / (4 * np.pi))


out = {"note": "common persistence a; B's weights rescaled by 1+c so that both budgets are 1-eps (admissible pair)"}

# 1. uniformity in the margin: rate / spacing^(4K-2)
uni = {}
for K in (2, 3):
    rows = []
    for dEta in (0.1, 0.05, 0.025):
        for eps in (1e-1, 1e-2, 1e-3, 1e-4, 1e-6):
            pA, pB, info = pair(K, dEta, eps)
            v = kl_rate(pA, pB)
            rows.append({"spacing": dEta, "margin": eps, "kl_rate": v, "scaled": v / dEta ** (4 * K - 2), **info})
    uni[str(K)] = rows
    print(f"K={K}: rate / spacing^(4K-2)")
    for dEta in (0.1, 0.05, 0.025):
        print("   spacing %.3f:" % dEta, "  ".join("%.0e -> %.4g" % (r["margin"], r["scaled"]) for r in rows if r["spacing"] == dEta),
              "  c=%.2e" % [r for r in rows if r["spacing"] == dEta][0]["c"])
out["uniform_check"] = uni

# 2. figure panel (a): at 1-S = 1e-6 against the spacing
spacings = np.array([0.2, 0.141, 0.1, 0.0707, 0.05, 0.0354, 0.025])
panel_a = {K: [kl_rate(*pair(K, s, 1e-6)[:2]) for s in spacings] for K in (2, 3)}
fits = {K: float(np.polyfit(np.log(spacings), np.log(panel_a[K]), 1)[0]) for K in (2, 3)}
print("panel (a) slopes", fits)

# 3. figure panel (b): at spacing 0.1 against the margin; admissible pair and the common-a pair without rescaling
margins = np.array([0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 1e-5, 1e-6])
panel_b = {}
for K in (2, 3):
    adm = [kl_rate(*pair(K, 0.1, e)[:2]) for e in margins]
    gap = pair(K, 0.1, 0.1, rescale=False)[2]["budget_gap"]
    noresc = [kl_rate(*pair(K, 0.1, e, rescale=False)[:2]) for e in margins]
    panel_b[str(K)] = {"margins": margins.tolist(), "admissible": adm, "common_a_unrescaled": noresc,
                       "budget_gap_unrescaled": gap}
    print(f"panel (b) K={K}: admissible {min(adm):.3e}..{max(adm):.3e}; unrescaled {noresc[0]:.3e} -> {noresc[-1]:.3e}"
          f" (budget gap {gap:.2e})")
out["figure"] = {"spacings": spacings.tolist(), "panel_a": {str(k): v for k, v in panel_a.items()},
                 "panel_a_slopes": {str(k): v for k, v in fits.items()}, "panel_b": panel_b}

# 4. Table 1: years of daily data, n >= ln 5 / KL (Bretagnolle-Huber, both errors 5%), 252 days a year;
#    kappa = 0.5, feedback share 0.3 (total weight of A 0.6 (1 - rc))
table = []
for K, rc, d in ((2, 0.5, 0.1), (2, 0.5, 0.05), (2, 0.8, 0.1), (2, 0.8, 0.05), (2, 0.9, 0.05), (2, 0.9, 0.025),
                 (3, 0.5, 0.1), (3, 0.5, 0.05)):
    row = {"K": K, "rc": rc, "spacing": d}
    for eps in (0.1, 1e-6):
        kl = kl_rate(*pair(K, d, eps, rc=rc, W=0.6 * (1 - rc))[:2])
        row[f"years_{eps:g}"] = float(np.log(5) / kl / 252)
    table.append(row)
    print("table", row)
out["table"] = table

# 5. finite samples: exact divergence of n stationary observations against n times the rate
fs = []
for K, d in ((2, 0.2), (2, 0.1)):
    for eps in (1e-1, 1e-2, 1e-3):
        pA, pB, _ = pair(K, d, eps)
        rate = kl_rate(pA, pB)
        for n in (250, 1000, 4000):
            kl = kl_exact(autocov(*pA, n), autocov(*pB, n))
            fs.append({"K": K, "spacing": d, "eps": eps, "n": n, "kl_exact": kl, "n_times_rate": n * rate,
                       "ratio": kl / (n * rate)})
out["finite_sample"] = fs
print("finite-sample ratios %.4f..%.4f" % (min(r["ratio"] for r in fs), max(r["ratio"] for r in fs)))

# 6. active probing near instability, admissible pair: squared distance between the two impulse responses
from fragility_scan import response
act = {}
for K in (2, 3):
    rows = []
    for gap in [0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125]:
        pA, pB, _ = pair(K, 0.1, gap)
        n = int(60 / gap) + 400
        hA = response(pA[0], pA[1], pA[2], pA[3], n); hB = response(pB[0], pB[1], pB[2], pB[3], n)
        rows.append({"1-S": gap, "active_sq_norm": float(np.sum((hA - hB) ** 2))})
    g = np.log([r["1-S"] for r in rows])
    act[str(K)] = {"rows": rows, "exponent_last4": float(np.polyfit(g[-4:], np.log([r["active_sq_norm"] for r in rows][-4:]), 1)[0])}
    print(f"active probing K={K}: squared response difference ~ (1-S)^{act[str(K)]['exponent_last4']:.2f}")
out["active_probing"] = act

# 7. finite samples: eigenvalues of T_n(f_A)^{-1} T_n(f_B) lie within 4 rho of one, and the divergence is below 16 n rho^2
from scipy.linalg import eigh
om = np.linspace(-np.pi, np.pi, 1 << 16, endpoint=False); zz = np.exp(1j * om)
band = []
for K, d in ((2, 0.2), (2, 0.1)):
    for eps in (1e-1, 1e-2, 1e-3):
        pA, pB, _ = pair(K, d, eps)
        rho = float(np.max(np.abs((D(zz, *pB) - D(zz, *pA)) / D(zz, *pA))))
        for n in (250, 1000, 4000):
            gA, gB = autocov(*pA, n), autocov(*pB, n)
            lam = eigh(toeplitz(gB), toeplitz(gA), eigvals_only=True)
            kl = kl_exact(gA, gB)
            band.append({"K": K, "spacing": d, "eps": eps, "n": n, "rho": rho, "max_abs_lambda_minus_1": float(np.max(np.abs(lam - 1))),
                         "in_band": bool(np.max(np.abs(lam - 1)) <= 4 * rho), "kl": kl, "bound": 16 * n * rho ** 2,
                         "below_bound": bool(kl <= 16 * n * rho ** 2)})
print("eigenvalue band holds in all cases:", all(b["in_band"] for b in band), "; divergence below bound in all:",
      all(b["below_bound"] for b in band), "; rho range %.3g..%.3g" % (min(b["rho"] for b in band), max(b["rho"] for b in band)))
out["finite_sample_band"] = band

json.dump(out, open("nearcrit_admissible_results.json", "w"), indent=1)

# figure
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#222222", "#6b6b66"
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
    pb = panel_b[K]
    ax2.loglog(pb["margins"], pb["admissible"], color=c, lw=2, marker=mk, ms=4)
    ax2.loglog(pb["margins"], pb["common_a_unrescaled"], color=c, lw=1.5, ls="--", marker=mk, ms=4, mfc="white")
ax2.invert_xaxis()
ax2.set_xlabel(r"margin to instability $1-S$")
ax2.set_title(r"(b) at $\Delta\eta=0.1$", fontsize=9, color=INK, loc="left")
hs = [Line2D([], [], color=MUTED, lw=2, label="same $a$, same budget"),
      Line2D([], [], color=MUTED, lw=1.5, ls="--", label="same $a$, budgets differ")]
ax2.legend(handles=hs, frameon=False, fontsize=7, loc="lower right", bbox_to_anchor=(1.0, 0.14), handlelength=2.2)
ax2.set_xticks([1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6])
ax2.grid(True, which="major", color="#e6e6e3", lw=0.6)
fig.tight_layout()
fig.savefig("../../ceiling_suite/papers/paper1_core/fig_barrier_admissible.pdf")
fig.savefig("fig_barrier_admissible.png", dpi=200)
print("figure written")

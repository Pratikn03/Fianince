"""Detection-forecast identity, matched upper bound for any memory shape, and the uniform irrelevance bound:
numerical checks (15 November 2026).

A. Identity. For two populations with aggregate flow maps F and F', Gaussian news of variance sigma^2 and any probe
   policy, KL(P || P') = sum_t V_t / (2 sigma^2), where V_t = kappa^2 E[(F - F')^2(h_t)] is the excess mean squared
   error at date t+1 of a forecaster who uses the wrong population. A test with both errors below 1/4 needs
   Lambda = sum_t V_t / sigma^2 > 1. We check the identity by Monte Carlo and plot the error of the likelihood-ratio
   test against Lambda for pairs from four families of memory, K = 2 and 3, matched and unmatched: one curve.
B. Matched upper bound. For a non-exponential family, the minimum-distance estimator from noisy reset impulse
   responses has weight error proportional to (noise) * Delta^-(2K-1).
C. Uniform irrelevance bound. A Bayesian autoregression of order L (prior N(0, I), known sigma) has cumulative excess
   log-loss over the composition observer at most
       S^2/2 + (L/2) log(1 + T/(1-S)^2) + T S^2 rbar^(2L) / (2 (1-S)^2),
   whatever the number of groups and the spacing of their memories.
Outputs: duality_results.json, fig_duality.pdf (written next to this script and copied to paper1_core/)."""
import json, math, os, shutil
import numpy as np
from numpy.polynomial import legendre as Lg
from scipy.optimize import least_squares
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261115)
M = 120                      # kernel taps kept
a, kappa, sigma = 0.3, 0.5, 1.0

def taps(fam, th, M=M):
    m = np.arange(M, dtype=float)
    if fam == "exponential": return (1 - th) * th ** m
    if fam == "power":       return (m + 1.0) ** (-th)
    if fam == "hump":        return (m + 1.0) * th ** m * (1 - th) ** 2
    if fam == "window":      return 1.0 / (1.0 + np.exp((m - th) / 1.5)) / th
    raise ValueError(fam)

CENTRE = {"exponential": 0.5, "power": 2.5, "hump": 0.5, "window": 8.0}
SCALE = {"exponential": 0.3, "power": 1.0, "hump": 0.2, "window": 3.0}

def gauss(K):
    x, w = Lg.leggauss(K); return x, w / 2
def radau(K):
    c = [0] * (K + 1); c[K - 1] = 1; c[K] = 1
    x = np.sort(np.real(Lg.legroots(c)))
    V = np.vander(x, K, increasing=True).T
    mom = np.array([(1 + (-1) ** j) / (2 * (j + 1)) for j in range(K)])
    return x, np.linalg.solve(V, mom)

def kernel(fam, nodes, wts, D, W):
    return sum(W * w * taps(fam, CENTRE[fam] + SCALE[fam] * D * s) for s, w in zip(nodes, wts))

def stable(k): return a + kappa * np.abs(k).sum() < 1

# ---------------------------------------------------------------- A. identity and one curve
def simulate(k_true, k_alt, A, T, n):
    """n paths of length T under k_true with random-sign probes of size A; returns the log likelihood ratio
    log dP_true/dP_alt and the pathwise sum of kappa^2 (F - F')^2."""
    X = np.zeros((n, T + M + 1)); llr = np.zeros(n); sV = np.zeros(n)
    kt, ka = k_true[::-1], k_alt[::-1]
    for t in range(M, T + M):
        hist = X[:, t - M + 1:t + 1]                    # x_{t-M+1..t}; reversed taps align tap m with x_{t-m}
        Ft, Fa = hist @ kt, hist @ ka
        v = A * rng.choice([-1.0, 1.0], size=n); eps = sigma * rng.standard_normal(n)
        base = a * X[:, t] + kappa * v
        X[:, t + 1] = base + kappa * Ft + eps
        d = kappa * (Ft - Fa)
        llr += (d * eps + 0.5 * d * d) / sigma ** 2      # log N(x; m, s^2) - log N(x; m', s^2)
        sV += d * d
    return llr, sV

W = 0.25
PAIRS = []
for fam, K, D in (("exponential", 2, 0.6), ("exponential", 3, 0.8), ("power", 2, 0.5), ("power", 3, 0.7),
                  ("hump", 2, 0.6), ("window", 2, 0.6)):
    gx, gw = gauss(K); rx, rw = radau(K)
    PAIRS.append((f"{fam}, K={K}, matched pair", fam, kernel(fam, gx, gw, D, W), kernel(fam, rx, rw, D, W)))
# unmatched pairs, including one across families
PAIRS.append(("exponential, one group against two", "exponential", W * taps("exponential", 0.5),
              W * 0.5 * (taps("exponential", 0.35) + taps("exponential", 0.65))))
PAIRS.append(("power against hump", "cross", W * taps("power", 2.5) / taps("power", 2.5).sum() * 1.2,
              W * taps("hump", 0.5) / taps("hump", 0.5).sum() * 1.2))
T, n = 160, 4000
out = {"identity": [], "pairs": [p[0] for p in PAIRS]}
for name, fam, k0, k1 in PAIRS:
    assert stable(k0) and stable(k1), name
    # calibrate the probe size: Lambda grows like A^2 for large A
    _, sv = simulate(k0, k1, 10.0, T, 400); lam10 = sv.mean() / sigma ** 2
    for target in (0.1, 0.3, 1.0, 2.0, 4.0, 8.0, 16.0, 30.0):
        A = 10.0 * math.sqrt(target / lam10)
        l0, s0 = simulate(k0, k1, A, T, n); l1, s1 = simulate(k1, k0, A, T, n)
        lam = 0.5 * (s0.mean() + s1.mean()) / sigma ** 2
        err = 0.5 * ((l0 < 0).mean() + (l1 < 0).mean())
        se = (l0.std(ddof=1) / math.sqrt(n))
        out["identity"].append({"pair": name, "family": fam, "probe": A, "Lambda": lam,
                                "KL_mc": float(l0.mean()), "half_sumV_over_s2": float(s0.mean() / (2 * sigma ** 2)),
                                "KL_se": float(se), "lr_test_error": float(err)})
dev = max(abs(r["KL_mc"] - r["half_sumV_over_s2"]) / r["KL_se"] for r in out["identity"])
out["identity_max_z"] = float(dev)
below = [r for r in out["identity"] if r["Lambda"] <= 1.0]
out["min_error_with_Lambda_at_most_1"] = float(min(r["lr_test_error"] for r in below))
gauss_curve = [abs(r["lr_test_error"] - norm.cdf(-math.sqrt(r["Lambda"]) / 2)) for r in out["identity"]]
out["max_gap_to_gaussian_curve"] = float(max(gauss_curve))

# ---------------------------------------------------------------- B. matched upper bound, non-exponential families
def response(k, T=40):
    h = np.zeros(T); h[0] = kappa
    for t in range(1, T):
        nn = min(t, len(k)); h[t] = a * h[t - 1] + kappa * np.dot(k[:nn], h[t - 1::-1][:nn])
    return h

def resp_param(fam, p, D, K):
    return response(sum(p[i] * taps(fam, CENTRE[fam] + SCALE[fam] * D * p[K + i], 60) for i in range(K)))

out["upper"] = {}
for fam in ("power", "hump"):
    K = 2; gx, gw = gauss(K); p0 = np.concatenate([W * gw, gx]); s = 1e-9
    Ds = np.array([0.4, 0.28, 0.2, 0.14, 0.1]); rm = []
    for D in Ds:
        h0 = resp_param(fam, p0, D, K); errs = []
        for _ in range(200):
            y = h0 + s * rng.standard_normal(h0.size)
            fit = least_squares(lambda p: (resp_param(fam, p, D, K) - y) / s, p0, jac="3-point", x_scale="jac", xtol=1e-15, ftol=1e-15, gtol=1e-15)
            errs.append(fit.x[:K] - p0[:K])
        rm.append(float(np.sqrt(np.mean(np.square(errs)))))
    slope = float(np.polyfit(np.log(Ds), np.log(rm), 1)[0])
    out["upper"][fam] = {"spreads": Ds.tolist(), "weight_rmse": rm, "slope": slope, "predicted": -(2 * K - 1), "noise": s}

# ---------------------------------------------------------------- C. uniform irrelevance bound (log loss)
def market(etas, qs, T, n):
    r = 1 - np.array(etas); q = np.array(qs)
    X = np.zeros((n, T + 1)); Y = np.zeros((n, len(etas))); M0 = np.zeros((n, T + 1))
    for t in range(T):
        m = a * X[:, t] + kappa * (Y @ q)
        M0[:, t + 1] = m
        X[:, t + 1] = m + sigma * rng.standard_normal(n)
        Y = Y * r + X[:, t + 1][:, None] * (1 - r)
    return X, M0

def bayes_ar_excess(X, M0, L):
    """Cumulative excess log-loss of the Bayesian AR(L) (prior N(0, I), known sigma) over the true conditional law."""
    n, T1 = X.shape; exc = np.zeros(n)
    for i in range(n):
        P = np.eye(L); phi = np.zeros(L); x = X[i]
        for t in range(1, T1):
            z = np.zeros(L); kk = min(L, t); z[:kk] = x[t - kk:t][::-1]          # z_j = x_{t-1-j}
            Pz = P @ z; s2 = sigma ** 2 * (1 + z @ Pz)                             # predictive variance
            pred = phi @ z; e = x[t] - pred
            exc[i] += (-0.5 * (x[t] - M0[i, t]) ** 2 / sigma ** 2) - (-0.5 * math.log(s2 / sigma ** 2) - 0.5 * e * e / s2)
            g = Pz / (1 + z @ Pz); phi = phi + g * e; P = P - np.outer(g, Pz)
    return exc

out["irrelevance"] = {}
Tc, nc = 4000, 60
for label, etas in (("wide (0.30, 0.60)", (0.30, 0.60)), ("close (0.44, 0.46)", (0.44, 0.46))):
    qs = (0.4, 0.4); S = a + kappa * sum(qs); rbar = 0.7          # one memory bound for the class, so one L for both
    L = math.ceil(math.log(Tc) / (2 * math.log(1 / rbar)))
    X, M0 = market(etas, qs, Tc, nc); exc = bayes_ar_excess(X, M0, L)
    bound = S ** 2 / 2 + (L / 2) * math.log(1 + Tc / (1 - S) ** 2) + Tc * S ** 2 * rbar ** (2 * L) / (2 * (1 - S) ** 2)
    out["irrelevance"][label] = {"T": Tc, "L": L, "S": S, "rbar": rbar, "cumulative_excess_logloss": float(exc.mean()),
                                 "se": float(exc.std(ddof=1) / math.sqrt(nc)), "bound": float(bound),
                                 "per_period": float(exc.mean() / Tc)}
out["ok"] = bool(out["identity_max_z"] < 4 and out["min_error_with_Lambda_at_most_1"] >= 0.25
                 and all(abs(v["slope"] - v["predicted"]) < 0.3 for v in out["upper"].values())
                 and all(v["cumulative_excess_logloss"] <= v["bound"] for v in out["irrelevance"].values()))
json.dump(out, open(os.path.join(HERE, "duality_results.json"), "w"), indent=1)

# ---------------------------------------------------------------- figure: one curve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SER = [("matched pairs, $K=2$", "#2a78d6", "o", lambda r: "K=2, matched" in r["pair"]),
       ("matched pairs, $K=3$", "#eb6834", "s", lambda r: "K=3, matched" in r["pair"]),
       ("unmatched pairs", "#1baf7a", "^", lambda r: "matched" not in r["pair"])]
fig, ax = plt.subplots(figsize=(5.3, 3.4))
lam = np.logspace(-1.15, 1.6, 300)
ax.plot(lam, norm.cdf(-np.sqrt(lam) / 2), color=INK, lw=1.2, zorder=2, label=r"$\Phi(-\sqrt{\Lambda}/2)$")
for lab, col, mk, sel in SER:
    pts = [r for r in out["identity"] if sel(r)]
    ax.scatter([r["Lambda"] for r in pts], [r["lr_test_error"] for r in pts], s=30, marker=mk, facecolor=col,
               edgecolor="white", linewidth=0.7, zorder=3, label=lab)
ax.axvline(1.0, color=MUTED, lw=0.8, ls=(0, (4, 3)), zorder=1)
ax.axhline(0.25, color=MUTED, lw=0.8, ls=(0, (4, 3)), zorder=1)
ax.text(0.93, 0.02, "no test has both errors\nbelow 1/4 left of this line", ha="right", va="bottom", fontsize=8, color=MUTED)
ax.set_xscale("log"); ax.set_xlim(0.07, 40); ax.set_ylim(0, 0.5)
ax.set_xlabel(r"cumulative forecast loss from confusing the two populations, $\Lambda=\sum_t V_t/\sigma^2$", fontsize=9, color=INK)
ax.set_ylabel("error of the likelihood-ratio test", fontsize=9, color=INK)
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"): ax.spines[sp].set_color(MUTED)
ax.tick_params(colors=MUTED, labelsize=8)
ax.legend(frameon=False, fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig_duality.pdf")); fig.savefig(os.path.join(HERE, "fig_duality.png"), dpi=150)
shutil.copy(os.path.join(HERE, "fig_duality.pdf"), os.path.join(HERE, "..", "..", "ceiling_suite", "papers", "paper1_core", "fig_duality.pdf"))
print(json.dumps({k: v for k, v in out.items() if k != "identity"}, indent=1))

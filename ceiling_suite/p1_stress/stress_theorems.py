"""Paper 1: numerical stress tests of results that are not machine-checked (31 October 2026).

These are numerical checks, not proofs and not pre-specified tests. Each part draws random parameter settings and
checks a theorem's prediction across them; failures are reported as they come out.

  P1  Theorem prop:esprit (Prony upper bound): for random separated rate configurations, the number of reset
      experiments Prony's method needs grows no faster than (Delta eta)^-(4K-2), uniformly over configurations.
  P2  Theorem prop:passive (passive data): the Whittle divergence rate between two moment-matched economies shrinks
      as (Delta eta)^(4K-2), computed exactly from the two price spectra (no simulation noise).
  P3  Lemma lem:altpair / Theorem thm:general (general memory): the alternation construction gives two n-atom
      memory distributions on [0, rho] with equal moments of order <= 2n-2, Wasserstein distance >= rho E_{2n-2}
      and kernel distance below 2 rho^(2n-1)/(1-rho), for random rho.
  P4  Theorem thm:discvalue (value of disclosure): with class-tagged flow the number of experiments stays bounded as
      the spacing shrinks, for K = 2, 3, 4, while the price-only requirement explodes.

Run:  python stress_theorems.py      (CPU, about 10-20 minutes)
Output: results/S1_stress_tests.json
"""
import os, sys, json, time, ast
import numpy as np
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "p1_injection"))
from injection_core import impulse, prony_weights, class_flows, tagged_weights, gauss_rule  # noqa: E402

SEED = 20261031
rng = np.random.default_rng(SEED)
GRID = 2.0 ** (np.arange(90) / 2)          # experiment counts 1, sqrt2, 2, ...
A_, KAPPA, SIGMA, SIGMA_F, REPS, EPS_REL, TARGET = 0.5, 0.8, 1e-3, 0.02, 200, 0.25, 0.25


def n_star(fail):
    """Smallest N on GRID with failure rate <= TARGET there and at the next grid point."""
    prev = None
    for N in GRID:
        f = fail(N)
        if prev is not None and prev[1] <= TARGET and f <= TARGET:
            return float(prev[0])
        prev = (N, f)
    return None


def prony_fail(K, r, w, N):
    T = 2 * K + 1
    h = impulse(A_, KAPPA, w, r, T)
    hbar = h + SIGMA / np.sqrt(N) * rng.standard_normal((REPS, T))
    hbar[:, 0] = KAPPA
    est = prony_weights(hbar, A_, KAPPA, K)
    bad = ~np.isfinite(est).all(axis=1) | (np.nanmax(np.abs(est - w), axis=1) > EPS_REL * w.min())
    return float(bad.mean())


def tagged_fail(K, r, w, N, taps=6):
    h = impulse(A_, KAPPA, w, r, taps)
    hbar = h + SIGMA / np.sqrt(N) * rng.standard_normal((REPS, taps))
    F = class_flows(w, r, h)
    fbar = F[None] + SIGMA_F / np.sqrt(N) * rng.standard_normal((REPS, K, taps))
    est = tagged_weights(fbar, hbar)
    bad = np.max(np.abs(est - w), axis=1) > EPS_REL * w.min()
    return float(bad.mean())


def slope(x, y):
    pts = [(np.log(a), np.log(b)) for a, b in zip(x, y) if b is not None]
    if len(pts) < 3:
        return None
    X, Y = np.array(pts).T
    return float(np.polyfit(X, Y, 1)[0])


def separated_nodes(K, gap):
    while True:
        s = np.sort(rng.uniform(-1, 1, K))
        if K == 1 or np.min(np.diff(s)) >= gap:
            return s


out = {"kind": "numerical stress tests (not proofs, not pre-specified)", "seed": SEED,
       "settings": {"a": A_, "kappa": KAPPA, "sigma": SIGMA, "sigma_f": SIGMA_F, "reps": REPS,
                    "accuracy": "every weight within 25% of the smallest true weight", "target_failure": TARGET}}
t0 = time.time()

# ---------------- P1: Prony upper bound, random separated configurations ----------------
P1 = {}
for K, grid, ncfg in ((2, [0.35, 0.28, 0.22, 0.18, 0.14], 15), (3, [0.35, 0.28, 0.22, 0.18], 12)):
    rows = []
    for c in range(ncfg):
        rc = rng.uniform(0.42, 0.45)
        s = separated_nodes(K, 0.5)
        om = rng.uniform(0.2, 1.0, K); om = om / om.sum()
        w = 0.08 * om
        ns = []
        for d in grid:
            r = rc + d * s
            ns.append(n_star(lambda N: prony_fail(K, r, w, N)))
        const = [None if n is None else n * d ** (4 * K - 2) / SIGMA ** 2 for n, d in zip(ns, grid)]
        rows.append({"rc": rc, "nodes": s.tolist(), "weights": w.tolist(), "N_star": ns, "slope": slope(grid, ns),
                     "N_star_times_d^(4K-2)_over_sigma2": const})
        print(f"P1 K={K} cfg {c}: slope {rows[-1]['slope']}", flush=True)
    sl = [r_["slope"] for r_ in rows if r_["slope"] is not None]
    allc = [v for r_ in rows for v in r_["N_star_times_d^(4K-2)_over_sigma2"] if v is not None]
    trend = [r_["N_star_times_d^(4K-2)_over_sigma2"][-1] / r_["N_star_times_d^(4K-2)_over_sigma2"][0]
             for r_ in rows if None not in (r_["N_star_times_d^(4K-2)_over_sigma2"][0], r_["N_star_times_d^(4K-2)_over_sigma2"][-1])]
    P1[f"K{K}"] = {"d_grid": grid, "configs": rows, "theory_slope": -(4 * K - 2),
                   "slope_min": min(sl), "slope_max": max(sl), "slope_median": float(np.median(sl)),
                   "n_failed_configs": int(sum(r_["slope"] is None for r_ in rows)),
                   "constant_min": min(allc), "constant_max": max(allc),
                   "constant_ratio_smallest_over_largest_d_median": float(np.median(trend)),
                   "constant_ratio_smallest_over_largest_d_max": float(np.max(trend))}
out["P1_prony_upper_bound"] = P1


# ---------------- P2: passive data, exact Whittle divergence rate ----------------
def grid_pair(K, W):
    n = 2 * K - 1
    from math import comb
    s = np.array([2 * k / n - 1 for k in range(n + 1)])
    wts = np.array([comb(n, k) for k in range(n + 1)], float) / 2 ** (n - 1) * W
    return (s[1::2], wts[1::2]), (s[0::2], wts[0::2])


def spectrum(om, a, kappa, w, r):
    z = np.exp(1j * om)
    G = np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)
    H = kappa * z / (z - a - kappa * G)
    return np.abs(H / kappa) ** 2


def whittle_kl(fA, fB):
    u = (fA - fB) / fB
    small = np.abs(u) < 1e-3
    val = np.where(small, u ** 2 / 2 - u ** 3 / 3 + u ** 4 / 4, u - np.log1p(np.where(small, 0, u)))
    return float(np.mean(val) / 2)          # (1/4pi) * integral over [-pi, pi] = mean / 2


om = np.linspace(-np.pi, np.pi, 2 ** 15, endpoint=False)
P2 = {}
for K in (2, 3, 4):
    rows = []
    for c in range(10):
        rc, a, kappa, W = rng.uniform(0.4, 0.5), rng.uniform(0.2, 0.6), rng.uniform(0.5, 1.0), rng.uniform(0.04, 0.1)
        (sA, wA), (sB, wB) = grid_pair(K, W)
        ds = np.geomspace(0.3, 0.05, 8)
        kls = []
        for d in ds:
            fA = spectrum(om, a, kappa, wA, rc + d * sA)
            fB = spectrum(om, a, kappa, wB, rc + d * sB)
            kls.append(whittle_kl(fA, fB))
        rows.append({"rc": rc, "a": a, "kappa": kappa, "W": W, "d": ds.tolist(), "whittle_kl_rate": kls,
                     "slope": slope(ds, kls)})
    sl = [r_["slope"] for r_ in rows]
    P2[f"K{K}"] = {"configs": rows, "theory_slope": 4 * K - 2, "slope_min": min(sl), "slope_max": max(sl)}
    print(f"P2 K={K}: slopes {min(sl):.3f}..{max(sl):.3f} (theory {4*K-2})", flush=True)
out["P2_passive_whittle"] = P2

# ---------------- P3: general memory, alternation construction at random rho ----------------
src = open(os.path.join(ROOT, "theory", "general_minimax.py")).read()
tree = ast.parse(src)
ns_ = {"np": np, "mp": mp}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ("remez_sqrt", "alternation_pair", "moments", "w1",
                                                            "kernel_dist"):
        exec(compile(ast.Module([node], []), "general_minimax", "exec"), ns_)
mp.mp.dps = 60
P3 = []
for rho in rng.uniform(0.3, 0.99, 12):
    for n in (2, 3, 4, 5, 6):
        A, B, E = ns_["alternation_pair"](n, mp.mpf(float(rho)))
        mA, mB = ns_["moments"](A, 2 * n), ns_["moments"](B, 2 * n)
        low = max(abs(mA[j] - mB[j]) for j in range(2 * n - 1))
        W1 = ns_["w1"](A, B); kd = ns_["kernel_dist"](A, B)
        bound = 2 * mp.mpf(float(rho)) ** (2 * n - 1) / (1 - mp.mpf(float(rho)))
        P3.append({"rho": float(rho), "n": n, "atoms": [len(A), len(B)], "max_low_moment_gap": float(low),
                   "W1": float(W1), "rho_E": float(mp.mpf(float(rho)) * E), "kernel_l2": float(kd),
                   "kernel_bound": float(bound),
                   "pass": bool(len(A) == n and len(B) == n and low < 1e-30 and W1 >= mp.mpf(float(rho)) * E * (1 - 1e-20)
                                and kd <= bound)})
out["P3_general_memory_altpair"] = {"cases": P3, "n_cases": len(P3), "n_pass": int(sum(c["pass"] for c in P3))}
print(f"P3: {out['P3_general_memory_altpair']['n_pass']}/{len(P3)} pass", flush=True)

# ---------------- P4: value of disclosure, tagged requirement stays bounded ----------------
P4 = {}
for K, grid in ((2, [0.5, 0.4, 0.32, 0.25, 0.2, 0.16, 0.125]), (3, [0.6, 0.5, 0.4, 0.32, 0.25]),
                (4, [0.6, 0.5, 0.4, 0.32, 0.25])):
    s, om_ = gauss_rule(K)
    rc = 0.5 if K > 2 else 0.6
    w = 0.08 * om_
    tag, price = [], []
    for d in grid:
        r = rc + d * s
        tag.append(n_star(lambda N: tagged_fail(K, r, w, N)))
        price.append(n_star(lambda N: prony_fail(K, r, w, N)) if K <= 3 else None)
    tg = [x for x in tag if x is not None]
    P4[f"K{K}"] = {"d_grid": grid, "tagged_N_star": tag, "price_N_star": price,
                   "tagged_max_over_min": (max(tg) / min(tg)) if len(tg) == len(tag) else None,
                   "price_slope": slope(grid, price), "tagged_slope": slope(grid, tag)}
    print(f"P4 K={K}: tagged {tag} max/min {P4[f'K{K}']['tagged_max_over_min']}; price slope {P4[f'K{K}']['price_slope']}",
          flush=True)
out["P4_disclosure_tagged"] = P4
out["runtime_seconds"] = time.time() - t0

os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "S1_stress_tests.json"), "w"), indent=1, default=float)
print("saved results/S1_stress_tests.json", f"({out['runtime_seconds']:.0f} s)")

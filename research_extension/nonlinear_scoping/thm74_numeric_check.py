"""Numerical check of Theorem 7.4 (core version of Paper 1): stress identifies the signed capacity measure.

Simulation only; no market data. Five checks, each recorded as it comes out:
  T1  populations with the same signed measure mu~ = sum c_i sgn(l_i) delta_(r_i,|l_i|) give identical responses
      to every probe (tanh and hard limit), including after splitting traders and adding offsetting pairs;
  T2  populations with the same kernel but different mu~: identical below the first band edge (hard limit), then
      separated; under tanh, the first-tap gap scales like A^3;
  T3  constructive recovery under the hard limit: steer the price with probes, read the date-2 flow map along two
      directions, locate kinks and slope jumps, and recover every atom (r, |l|, net capacity) of mu~;
  T4  the Taylor route for tanh: the odd Taylor coefficients of the small-probe flow map are tau_{2n-1} sum d s^{2n-1};
      checked by comparing the cubic coefficient with its prediction;
  T5  why part (ii) was reworded: a group can be detected before its own band edge is reached, through the kernel
      constraint, when another group of the same memory saturates first.
Usage: python3 thm74_numeric_check.py [seed]   (writes thm74_numeric_check_results.json)
"""
import json, sys
import numpy as np

a, kappa = 0.5, 0.8
SHAPES = {"tanh": np.tanh, "clip": lambda u: np.clip(u, -1.0, 1.0)}


def respond(pop, v, psi):
    """Price response of the probing experiment: x_t = a x_{t-1} + kappa (sum_i c_i psi(l_i m_{i,t}) + v_t)."""
    r = np.array([p[0] for p in pop]); c = np.array([p[1] for p in pop]); l = np.array([p[2] for p in pop])
    m = np.zeros(len(pop)); x = np.zeros(len(v)); xp = 0.0
    for t in range(len(v)):
        x[t] = a * xp + kappa * (np.sum(c * psi(l * m)) + v[t])
        m = r * m + x[t]; xp = x[t]
    return x


def flow_map_date2(pop, x0, x1, psi):
    """Steer the price to (x0, x1) with probes, then read the date-2 aggregate flow from the response."""
    r = np.array([p[0] for p in pop]); c = np.array([p[1] for p in pop]); l = np.array([p[2] for p in pop])
    v0 = x0 / kappa
    m = r * 0.0 + x0                                    # m_1 = x_0
    F1 = np.sum(c * psi(l * m))
    v1 = (x1 - a * x0) / kappa - F1                     # probe that realises x1
    x1_real = a * x0 + kappa * (F1 + v1)
    m = r * m + x1_real                                 # m_2 = r x_0 + x_1
    F2 = np.sum(c * psi(l * m))
    x2 = a * x1_real + kappa * F2                       # v_2 = 0
    return (x2 - a * x1_real) / kappa                   # read back F_2 from the response


def mu_tilde(pop, nd=10):
    out = {}
    for r, c, l in pop:
        if l == 0: continue
        k = (round(r, nd), round(abs(l), nd)); out[k] = out.get(k, 0.0) + c * np.sign(l)
    return {k: v for k, v in out.items() if abs(v) > 1e-12}


def random_population(rng, n_atoms):
    rates = rng.choice([0.2, 0.4, 0.6, 0.8], size=n_atoms)
    lev = rng.choice([0.05, 0.08, 0.12, 0.2, 0.3], size=n_atoms)
    pop = []
    for r, lam in zip(rates, lev):
        c = float(rng.uniform(0.2, 1.5)); sgn = 1.0 if rng.random() < 0.8 else -1.0
        pop.append((float(r), c, sgn * float(lam)))
    return pop


def stable(pop):
    return a + kappa * sum(c * abs(l) / (1 - r) for r, c, l in pop) < 1


def main(seed=20261108):
    rng = np.random.default_rng(seed); out = {"seed": seed}
    # T1: same mu~, different decompositions
    gaps = {k: 0.0 for k in SHAPES}; n1 = 0
    while n1 < 40:
        P = random_population(rng, 4)
        if not stable(P): continue
        Q = []
        for r, c, l in P:                               # split each trader and add an offsetting pair
            f = rng.uniform(0.2, 0.8); e = rng.uniform(0.05, 0.3)
            Q += [(r, f * c, l), (r, (1 - f) * c + e, l), (r, e, -l)]
        for name, psi in SHAPES.items():
            for _ in range(5):
                v = rng.normal(0, 20, 30)
                gaps[name] = max(gaps[name], float(np.max(np.abs(respond(P, v, psi) - respond(Q, v, psi)))))
        n1 += 1
    out["T1_same_mu_tilde_max_gap"] = gaps
    out["T1_pass"] = all(g < 1e-9 for g in gaps.values())
    # T2: same kernel, different mu~ (two groups at memory 0.7)
    P = [(0.7, 1.0, 0.1)]; Pp = [(0.7, 0.25, 0.2), (0.7, 1.0, 0.05)]
    rows = []
    for A in [0.5, 1, 2, 4, 5, 6, 8, 12]:
        v = np.zeros(30); v[0] = A
        rows.append({"A": A, "gap_clip": float(np.max(np.abs(respond(P, v, SHAPES["clip"]) - respond(Pp, v, SHAPES["clip"])))),
                     "gap_tanh_tap1": float(abs(respond(P, v, np.tanh)[1] - respond(Pp, v, np.tanh)[1]))})
    out["T2_rows"] = rows
    small = [rw for rw in rows if rw["A"] <= 1]
    out["T2_tanh_tap1_slope_small_A"] = float(np.polyfit(np.log([rw["A"] for rw in small]), np.log([rw["gap_tanh_tap1"] for rw in small]), 1)[0])
    first = next(rw["A"] for rw in rows if rw["gap_clip"] > 0)
    out["T2_clip_zero_below"] = first
    out["T2_pass"] = all(rw["gap_clip"] == 0 for rw in rows if rw["A"] < first) and first > 4
    # T3: constructive recovery under the hard limit, random populations, two directions
    results = []
    n3 = 0
    while n3 < 25:
        P = random_population(rng, int(rng.integers(2, 5)))
        if not stable(P): continue
        truth = mu_tilde(P)
        rec = {}
        for th in (0.3, 0.9):
            us = np.linspace(0, 120, 120001)
            g = np.array([flow_map_date2(P, th * u, u, SHAPES["clip"]) for u in us])
            sl = np.diff(g) / np.diff(us); jumps = np.where(np.abs(np.diff(sl)) > 1e-7)[0]
            kinks = []
            for j in jumps:
                uk = us[j + 1]
                if kinks and uk - kinks[-1][0] < 0.01: continue
                d = 0.002
                sL = (flow_map_date2(P, th * (uk - d), uk - d, SHAPES["clip"]) - flow_map_date2(P, th * (uk - 2 * d), uk - 2 * d, SHAPES["clip"])) / d
                sR = (flow_map_date2(P, th * (uk + 2 * d), uk + 2 * d, SHAPES["clip"]) - flow_map_date2(P, th * (uk + d), uk + d, SHAPES["clip"])) / d
                kinks.append((uk, sR - sL))
            rec[th] = [(1 / uk, -jump * uk) for uk, jump in kinks]          # (s_k, d_k)
        # match the two directions by net capacity d (direction-free), solve for (r, lambda)
        got = {}
        for s1, d1 in rec[0.3]:
            cand = min(rec[0.9], key=lambda sd: abs(sd[1] - d1)) if rec[0.9] else None
            if cand is None: continue
            s2 = cand[0]; q = s1 / s2
            r = (q - 1) / (0.9 * 0 + 0.3 - q * 0.9) if abs(0.3 - q * 0.9) > 1e-12 else np.nan
            lam = s1 / (r * 0.3 + 1)
            got[(round(float(r), 3), round(float(lam), 3))] = round(float(d1), 3)
        tr = {(round(k[0], 3), round(k[1], 3)): round(v, 3) for k, v in truth.items()}
        # match atoms with a tolerance set by the kink grid (step 0.001 in u)
        def near(k1, k2): return abs(k1[0] - k2[0]) <= 5e-3 and abs(k1[1] - k2[1]) <= 5e-3
        ok = len(tr) == len(got) and all(any(near(k, g) and abs(tr[k] - got[g]) < 5e-3 for g in got) for k in tr)
        results.append({"truth": {str(k): v for k, v in tr.items()}, "recovered": {str(k): v for k, v in got.items()}, "match": ok})
        n3 += 1
    out["T3_recovery"] = results
    out["T3_matches"] = sum(r_["match"] for r_ in results); out["T3_cases"] = len(results)
    # T4: Taylor route for tanh: cubic coefficient of the date-2 flow map along a direction
    P = [(0.7, 1.0, 0.1)]; Pp = [(0.7, 0.25, 0.2), (0.7, 1.0, 0.05)]; th = 0.5
    us = np.linspace(-0.3, 0.3, 61)
    gdiff = np.array([flow_map_date2(P, th * u, u, np.tanh) - flow_map_date2(Pp, th * u, u, np.tanh) for u in us])
    coef = np.polyfit(us, gdiff, 7)                     # highest power first
    def mu_list(pop): return [(c * np.sign(l), abs(l) * (r * th + 1)) for r, c, l in pop]
    pred3 = -1 / 3 * (sum(d * s ** 3 for d, s in mu_list(P)) - sum(d * s ** 3 for d, s in mu_list(Pp)))
    out["T4_cubic_coef_fit"] = float(coef[-4]); out["T4_cubic_coef_pred"] = float(pred3)
    out["T4_linear_coef_fit"] = float(coef[-2])
    out["T4_pass"] = abs(coef[-4] - pred3) < 1e-6 * max(1, abs(pred3)) + 1e-9 and abs(coef[-2]) < 1e-9
    # T5: indirect detection before a group's own band edge
    P = [(0.7, 1.0, 0.1), (0.7, 1.0, 0.4)]              # kernel weight at 0.7: 0.1 + 0.4 = 0.5 ... (stability below)
    Pp = [(0.7, 2.0, 0.1), (0.7, 0.75, 0.4)]            # 0.2 + 0.3 = 0.5: same kernel, differs at both atoms
    th = 0.5; s_hi, s_lo = 0.4 * 1.35, 0.1 * 1.35
    u_mid = 0.5 * (1 / s_hi + 1 / s_lo)                 # beyond the high-leverage edge, before the low-leverage edge
    out["T5_u_edges"] = [1 / s_hi, 1 / s_lo]
    out["T5_gap_inside_all_bands"] = float(abs(flow_map_date2(P, th * 1.0, 1.0, SHAPES["clip"]) - flow_map_date2(Pp, th * 1.0, 1.0, SHAPES["clip"])))
    out["T5_gap_between_edges"] = float(abs(flow_map_date2(P, th * u_mid, u_mid, SHAPES["clip"]) - flow_map_date2(Pp, th * u_mid, u_mid, SHAPES["clip"])))
    out["T5_note"] = ("The populations differ at the low-leverage atom too, but the difference is already visible once only the "
                      "high-leverage group has saturated: with the kernel fixed, a change at one atom forces a change elsewhere.")
    out["ALL_PASS"] = bool(out["T1_pass"] and out["T2_pass"] and out["T3_matches"] == out["T3_cases"] and out["T4_pass"]
                           and out["T5_gap_inside_all_bands"] == 0 and out["T5_gap_between_edges"] > 0)
    return out


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261108
    res = main(seed)
    json.dump(res, open("thm74_numeric_check_results.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("T3_recovery", "T2_rows")}, indent=1, default=str))

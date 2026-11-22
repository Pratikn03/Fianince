"""P1M-A1: the two analyses the simulated referees asked for (protocol P1M_A1_protocol.md).

Taiwan development period 2013-01-02 to 2016-12-30 only, as in P1M. Builds on p1m_core.py, which is imported
unchanged.

Part A (no new data; input is the P1M estimate stored in results/p1m_results.json)
    Q2 and Q3 of P1M recomputed on classes of compositions that the paper's theory covers. The memories r'_c lie in
    [0, 0.99]. The weights w'_c carry signs:
      variant "P": every weight is nonnegative, which is the positive class of the lower bounds;
      variant "T": each weight has the sign of its tagged estimate (Foreign and Trust nonnegative, Dealers nonpositive).
    The memories are at least gamma apart. The indistinguishable set, the boxes and the stationarity requirement are
    those of P1M.
Part B (the TWSE panel; run in Colab)
    Decoupled rules: u_{c,t} = sum_{j=1..J} beta_{c,j} x_{t-j} + e_{c,t}, with AR(p) non-feedback flow
    e_{c,t} = sum_l phi_{c,l} e_{c,t-l} + eta_{c,t}. The feedback kernel no longer decays at the persistence of the
    class's own flow. Stock fixed effects; iterated Cochrane-Orcutt in moment form; the price equation of P1M; a joint
    stationary date bootstrap with the same dates for every equation.
    H_c = kappa * sum_j beta_{c,j}.
"""
from __future__ import annotations

import itertools

import numpy as np

import p1m_core as pm

CLASSES = pm.CLASSES
# ---- Part A --------------------------------------------------------------------------------------------------------
VARIANTS = {"P": (1, 1, 1), "T": (1, 1, -1)}     # +1: weight >= 0, -1: weight <= 0 (Foreign, Trust, Dealers)
GAMMAS = (0.0, 0.01, 0.02, 0.05, 0.10)
R_MIN = 0.0
SCAN_GAMMAS = (0.0, 0.05)
SCAN_FACTORS = (1.0, 5.0, 10.0)                  # times max_c |H_c|; 2 (tight box) and the primary box are in the grid
TOL_CONS = 1e-12
TOL_BOUND = 1e-10
# ---- Part B --------------------------------------------------------------------------------------------------------
B_RUNS = (("primary", 10, 2), ("J5", 5, 2), ("J20", 20, 2), ("AR1", 10, 1))    # (label, J lags of x, AR order)
CO_TOL = 1e-12
CO_MAXIT = 500
MIN_ROWS = 50


# =====================================================================================================================
# Part A: ranges over a constrained class of compositions
# =====================================================================================================================

def _signs(variant):
    return np.array(VARIANTS[variant], float)


def _project(r, w, variant, gamma):
    """Clip to the bounds and spread the sorted memories so that neighbours are at least gamma apart."""
    s = _signs(variant)
    w = np.where(s > 0, np.maximum(w, 0.0), np.minimum(w, 0.0))
    r = np.clip(np.asarray(r, float), R_MIN, pm.R_MAX)
    order = np.argsort(r, kind="stable")
    rs = r[order].copy()
    for k in range(1, 3):
        rs[k] = max(rs[k], rs[k - 1] + gamma)
    if rs[2] > pm.R_MAX:
        rs -= rs[2] - pm.R_MAX
    rs = np.maximum(rs, R_MIN)
    out = np.empty(3)
    out[order] = rs
    return out, w, order


def in_class(r, w, variant, gamma, hbar, kappa, tol=TOL_BOUND):
    s = _signs(variant)
    r, w = np.asarray(r, float), np.asarray(w, float)
    if np.any(r < R_MIN - tol) or np.any(r > pm.R_MAX + tol) or np.any(s * w < -tol):
        return False
    rs = np.sort(r)
    if np.any(np.diff(rs) < gamma - tol):
        return False
    H = kappa * w / (1 - r)
    return bool(np.all(np.abs(H) <= hbar + tol))


def _constraint_fns(th, n_rec, hbar, gamma, order, A1, with_kl):
    kap = th["kappa"]

    def sep(v):
        r = v[:3]
        return np.array([r[order[1]] - r[order[0]] - gamma, r[order[2]] - r[order[1]] - gamma])

    def box(v):
        r, w = v[:3], v[3:]
        H = kap * w / (1 - r)
        return np.r_[hbar - H, hbar + H] / max(hbar, 1e-12)

    def kl(v):
        return np.array([(pm.J0 - n_rec * pm.kl_rate(th, v[:3], v[3:], A1)) / pm.J0])

    cons = [{"type": "ineq", "fun": sep}, {"type": "ineq", "fun": box}]
    if with_kl:
        cons.append({"type": "ineq", "fun": kl})
    return cons, sep, box, kl


def _bounds(variant):
    s = _signs(variant)
    return [(R_MIN, pm.R_MAX)] * 3 + [((0.0, None) if si > 0 else (None, 0.0)) for si in s]


def _feasible(th, v, variant, gamma, hbar, n_rec, A1, order):
    r, w = v[:3], v[3:]
    if not in_class(r, w, variant, gamma, hbar, th["kappa"]):
        return False
    if n_rec * pm.kl_rate(th, r, w, A1) > pm.J0 * (1 + TOL_CONS):
        return False
    return pm.stationary(th, r, w)[0]


def _starts(th, variant, gamma, seed, n_random):
    """The estimate's six relabelings and n_random random rules, projected onto the class (P1M's start design)."""
    rng = np.random.default_rng(seed)
    pts = []
    for perm in itertools.permutations(range(3)):
        pts.append((th["r"][list(perm)], th["w"][list(perm)]))
    wscale = np.maximum(np.abs(th["w"]), 1e-6).max()
    for _ in range(n_random):
        r = np.clip(th["r"] + rng.normal(0, 0.3, 3), -0.95, 0.95)
        w = th["w"] + rng.normal(0, 1, 3) * wscale
        pts.append((r, w))
    out = []
    for r, w in pts:
        r2, w2, order = _project(r, w, variant, gamma)
        out.append((np.r_[r2, w2], order))
    return out


def relabelings_in_class(th, variant, gamma, hbar):
    """Halt effects of the estimate's relabelings that lie in the class. Their divergence rate is exactly 0, so they lie
    in the indistinguishable set at every record length (the exact barrier within the class)."""
    vals = set()
    H = pm.effects(th)["H"]
    for perm in itertools.permutations(range(3)):
        r, w = th["r"][list(perm)], th["w"][list(perm)]
        if in_class(r, w, variant, gamma, hbar, th["kappa"]):
            vals.add(float(th["kappa"] * w[0] / (1 - r[0])))
    return sorted(vals), bool(in_class(th["r"], th["w"], variant, gamma, hbar, th["kappa"])), H.tolist()


def constrained_ranges(th, n_rec, hbar, variant, gamma, seed=pm.SEED, n_random=pm.N_RANDOM_STARTS):
    """Min and max of H'_Foreign and of U' = sum_c H'_c over compositions theta' in the class (variant, gamma) with
    n_rec * rate(theta, theta') <= J0, |H'_c| <= hbar and a stationary price process.

    Phase 1 from every start: minimise the divergence within the class (bounds, separation in the start's ordering of
    memories, box). Starts that reach the indistinguishable set are kept. Phase 2 from each kept start: SLSQP for each
    extreme with all constraints. Returns the extremes found; the true range contains them. If no start reaches the set,
    the set is reported empty together with the smallest n * rate found (the true set may still be nonempty)."""
    from scipy.optimize import minimize
    A1 = pm.A_of(th)
    kap = th["kappa"]
    bnds = _bounds(variant)
    feasible_starts = []
    best_phase1 = np.inf
    for v0, order in _starts(th, variant, gamma, seed, n_random):
        cons1, sep, box, kl = _constraint_fns(th, n_rec, hbar, gamma, order, A1, with_kl=False)
        obj = lambda v: n_rec * pm.kl_rate(th, v[:3], v[3:], A1) / pm.J0
        try:
            res = minimize(obj, v0, method="SLSQP", bounds=bnds, constraints=cons1,
                           options={"maxiter": 500, "ftol": 1e-16})
            v1 = res.x
        except Exception:
            continue
        val = n_rec * pm.kl_rate(th, v1[:3], v1[3:], A1)
        if np.all(sep(v1) >= -TOL_BOUND) and np.all(box(v1) >= -TOL_BOUND) and in_class(v1[:3], v1[3:], variant, gamma, hbar, kap):
            best_phase1 = min(best_phase1, val)
            if _feasible(th, v1, variant, gamma, hbar, n_rec, A1, order):
                feasible_starts.append((v1, order))

    def HF(v):
        return float(kap * v[3] / (1 - v[0]))

    def UU(v):
        return float(np.sum(kap * v[3:] / (1 - v[:3])))

    out = {"variant": variant, "gamma": gamma, "hbar": float(hbar), "n_rec": float(n_rec), "J0": pm.J0,
           "n_starts": 6 + n_random, "n_feasible_starts": len(feasible_starts),
           "smallest_n_rate_phase1": float(best_phase1)}
    rel, est_in, _ = relabelings_in_class(th, variant, gamma, hbar)
    out["relabeling_values_H_Foreign_in_class"] = rel
    out["estimate_in_class"] = est_in
    if not feasible_starts:
        out["empty"] = True
        return out
    out["empty"] = False
    # every feasible point visited (the kept starts and every feasible SLSQP outcome of either search) is pooled, and
    # both effects are extremised over the pool: each point is a member of the set, so the pool's extremes are found
    # values of the true range
    pool = [v for v, _ in feasible_starts]
    for name, f in (("H_Foreign", HF), ("U", UU)):
        for v0, order in feasible_starts:
            cons2, sep, box, kl = _constraint_fns(th, n_rec, hbar, gamma, order, A1, with_kl=True)
            for sgn in (1, -1):
                try:
                    res = minimize(lambda q: sgn * f(q) / max(hbar, 1e-12), v0, method="SLSQP", bounds=bnds,
                                   constraints=cons2, options={"maxiter": 500, "ftol": 1e-14})
                    cand = res.x
                except Exception:
                    continue
                if _feasible(th, cand, variant, gamma, hbar, n_rec, A1, order):
                    pool.append(cand)
    out["n_pool"] = len(pool)
    for name, f in (("H_Foreign", HF), ("U", UU)):
        vals = np.array([f(v) for v in pool])
        rec = {}
        for key, k in (("min", int(np.argmin(vals))), ("max", int(np.argmax(vals)))):
            v = pool[k]
            rec[key] = float(vals[k])
            rec[key + "_rules"] = {"r": v[:3].tolist(), "w": v[3:].tolist(),
                                   "n_rate": float(n_rec * pm.kl_rate(th, v[:3], v[3:], A1))}
        out[name] = rec
    return out


def part_a_configs(th, records, hbar_primary, hbar_tight):
    """The pre-specified configurations (protocol section 3)."""
    n_panel, n_stock = records["pooled_stock_days"], records["median_stock_days"]
    hmax = float(np.max(np.abs(pm.effects(th)["H"])))
    cfg = []
    for variant in ("P", "T"):
        for gamma in GAMMAS:
            for box_name, hb in (("primary", hbar_primary), ("tight", hbar_tight)):
                cfg.append({"key": f"{variant}_g{gamma:.2f}_{box_name}_panel", "variant": variant, "gamma": gamma,
                            "box": box_name, "hbar": hb, "record": "whole_panel", "n_rec": n_panel})
    for gamma in SCAN_GAMMAS:
        for f in SCAN_FACTORS:
            cfg.append({"key": f"T_g{gamma:.2f}_x{f:g}_panel", "variant": "T", "gamma": gamma, "box": f"{f:g}xmaxH",
                        "hbar": f * hmax, "record": "whole_panel", "n_rec": n_panel})
    for variant in ("P", "T"):
        cfg.append({"key": f"{variant}_g0.00_primary_stock", "variant": variant, "gamma": 0.0, "box": "primary",
                    "hbar": hbar_primary, "record": "one_stock", "n_rec": n_stock})
    return cfg


# =====================================================================================================================
# Part B: decoupled rules
# =====================================================================================================================

def decoupled_moments(prep, mask, flow, J, p_ar, delay=pm.DELAY):
    """Per-date cross moments of z_t = (u_t, u_{t-1..t-p}, x_{t-delay}, ..., x_{t-delay-(J+p-1)}), within-stock
    demeaned over the rows where every component is finite (stock means over the full sample; fixed effects are not
    re-estimated within bootstrap draws, as in P1M)."""
    x = prep["x"]
    N, T = x.shape
    base = prep["usable"] & pm.universe_mask(prep, T) & mask[None, :]
    comps = [pm.lag(flow, k) for k in range(p_ar + 1)] + [pm.lag(x, delay + j) for j in range(J + p_ar)]
    Z = np.stack(comps, -1)
    ok = base & np.isfinite(Z).all(-1)
    cnt = ok.sum(1)
    ok &= (cnt >= MIN_ROWS)[:, None]
    cnt = ok.sum(1)
    c = np.maximum(cnt, 1)
    Zm = np.where(ok[..., None], Z, 0.0).sum(1) / c[:, None]
    Zd = np.where(ok[..., None], Z - Zm[:, None, :], 0.0)
    M = np.einsum("itk,itl->tkl", Zd, Zd)
    return {"M": M, "n": ok.sum(0), "n_stocks": int((cnt > 0).sum()), "J": J, "p": p_ar, "k": Z.shape[-1]}


def _cu(k, p, phi):
    v = np.zeros(k)
    v[0] = 1.0
    v[1:p + 1] = -phi
    return v


def _cx(k, p, phi, j):
    """Quasi-differenced x_{t-j} (j = 1..J): x_{t-j} - sum_l phi_l x_{t-j-l}."""
    v = np.zeros(k)
    b = p + 1 + (j - 1)
    v[b] = 1.0
    for l in range(1, p + 1):
        v[b + l] -= phi[l - 1]
    return v


def _ce(k, p, J, beta, l):
    """e_{t-l} = u_{t-l} - sum_j beta_j x_{t-j-l}."""
    v = np.zeros(k)
    v[l] = 1.0
    for j in range(1, J + 1):
        v[p + 1 + (j - 1) + l] -= beta[j - 1]
    return v


def co_fit(M, J, p, phi0=None, tol=CO_TOL, maxit=CO_MAXIT):
    """Iterated Cochrane-Orcutt for u = beta(L) x + e, phi(L) e = eta, from the summed moment matrix M."""
    k = M.shape[0]
    phi = np.zeros(p) if phi0 is None else np.array(phi0, float)
    converged = False
    it = 0
    for it in range(1, maxit + 1):
        Cx = np.stack([_cx(k, p, phi, j) for j in range(1, J + 1)], 1)
        beta = np.linalg.solve(Cx.T @ M @ Cx, Cx.T @ M @ _cu(k, p, phi))
        D = np.stack([_ce(k, p, J, beta, l) for l in range(1, p + 1)], 1)
        d0 = _ce(k, p, J, beta, 0)
        phi_new = np.linalg.solve(D.T @ M @ D, D.T @ M @ d0)
        if np.max(np.abs(phi_new - phi)) < tol:
            phi = phi_new
            converged = True
            break
        phi = phi_new
    Cx = np.stack([_cx(k, p, phi, j) for j in range(1, J + 1)], 1)
    beta = np.linalg.solve(Cx.T @ M @ Cx, Cx.T @ M @ _cu(k, p, phi))
    resid = _cu(k, p, phi) - Cx @ beta
    ssr = float(resid @ M @ resid)
    return beta, phi, ssr, it, converged


def decoupled(prep, mask, J, p_ar, dealer="DealerTotal", B_=pm.B, mean_block=pm.MEAN_BLOCK, seed=pm.SEED, label=""):
    """Point estimates and the joint stationary date bootstrap of beta_c, phi_c, kappa, H_c = kappa sum_j beta_{c,j}
    and U = sum_c H_c. The price equation is P1M's (p = 5 lags, impact on U_{t-1})."""
    flows = pm.class_flows(prep, dealer)
    eqs = pm.build_equations(prep, mask, pm.DELAY, pm.P_LAGS, dealer)
    price = eqs["price"]
    kappa = float(pm.ols_from(price)[0][pm.P_LAGS])
    mom = {c: decoupled_moments(prep, mask, flows[c], J, p_ar) for c in CLASSES}
    point = {}
    for c in CLASSES:
        M = mom[c]["M"].sum(0)
        beta, phi, ssr, it, conv = co_fit(M, J, p_ar)
        n = int(mom[c]["n"].sum())
        point[c] = {"beta": beta.tolist(), "sum_beta": float(beta.sum()), "phi": phi.tolist(),
                    "sigma2_eta": ssr / max(n - J - p_ar - mom[c]["n_stocks"], 1), "rows": n,
                    "stocks": mom[c]["n_stocks"], "iterations": it, "converged": conv}
    H = np.array([kappa * point[c]["sum_beta"] for c in CLASSES])
    T = len(price["n"])
    for c in CLASSES:
        assert mom[c]["M"].shape[0] == T
    rng = np.random.default_rng(seed)
    draws, n_fail = [], 0
    for _ in range(B_):
        idx = pm.stationary_indices(T, mean_block, rng)
        try:
            kb = float(pm.ols_from(price, idx)[0][pm.P_LAGS])
            sb = []
            for c in CLASSES:
                beta, phi, _, _, conv = co_fit(mom[c]["M"][idx].sum(0), J, p_ar, phi0=point[c]["phi"])
                sb.append(beta.sum())
                sb.append(phi[0])
            sb = np.array(sb)
        except np.linalg.LinAlgError:
            n_fail += 1
            continue
        Hb = kb * sb[0::2]
        draws.append(np.r_[sb[0::2], sb[1::2], kb, Hb, Hb.sum()])
    draws = np.array(draws)
    names = [f"sum_beta_{c}" for c in CLASSES] + [f"phi1_{c}" for c in CLASSES] + ["kappa"] + \
            [f"H_{c}" for c in CLASSES] + ["U"]
    ptv = np.r_[[point[c]["sum_beta"] for c in CLASSES], [point[c]["phi"][0] for c in CLASSES], kappa, H, H.sum()]
    ci = {nm: {"est": float(v), "ci95": [float(np.percentile(draws[:, j], 2.5)), float(np.percentile(draws[:, j], 97.5))],
               "se": float(np.std(draws[:, j]))} for j, (nm, v) in enumerate(zip(names, ptv))}
    return {"label": label, "J": J, "ar_order": p_ar, "dealer_series": dealer, "kappa": kappa, "rules": point,
            "H": H.tolist(), "U": float(H.sum()), "bootstrap": {"B_used": len(draws), "failed": n_fail,
                                                                "mean_block": mean_block, "seed": seed, "ci": ci}}

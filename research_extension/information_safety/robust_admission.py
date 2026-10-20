"""Robust pre-trade admission (Paper 2, Theorem thm:robustguard, Proposition prop:venue, Theorem thm:venuebb; blueprint D3, D7;
tests T06 and T13).

Dealer/venue throttle in the cohort economy: admitting a fraction alpha of algorithmic flow scales the merged measure by alpha,
so S(alpha) = kappa / (1 - a - kappa alpha Phi). Worst-case loss over an unbounded horizon for inventory I and per-period shocks
|u| <= ubar is |I| ubar S(alpha) (all h_t >= 0).

Venue mode with action-dependent dynamics:Venue-mode admission with action-dependent dynamics (blueprint D7; Paper 2, Proposition prop:venue and Theorem thm:venuebb).

Two models.

1. Cohort economy with admitted liquidity (closed form). Admitting a fraction alpha of a participant class scales the
   feedback weight to alpha*Phi, deepens the book (impact kappa0/(1 + delta alpha)) and speeds reversion (1 - a0 + rho alpha):
       S(alpha) = kappa0 / D(alpha),  D(alpha) = (1 + delta alpha)(1 - a0 + rho alpha) - kappa0 Phi alpha.
   D is a convex quadratic, so the safe set {alpha : |I| ubar S(alpha) <= B} is [0,1] minus an open interval.

2. Three-state book (Section 4's depletion model) with admission-dependent parameters and no closed form:
       kappa(alpha) = kappa0/(1 + delta alpha^2), q(alpha) = alpha q0, r(alpha) = r0 + rho alpha^2,
   and an uncertainty box for (phi, kappa0, q0, delta, rho). The robust safe set is certified by interval branch and
   bound with outward rounding (interval.py): finite-horizon interval enclosure of the summed absolute response plus a
   rigorous tail bound from a contraction certificate.
"""
import itertools
import numpy as np
from interval import IV, matvec, matmul, norm_inf_upper
from model_contracts import closed_loop_matrix


def alpha_star(a, kappa, Phi_up, I, ubar, B):
    """Largest alpha in [0,1] safe for every Phi <= Phi_up; None if even alpha = 0 is unsafe (halt, reduce inventory)."""
    if abs(I) * ubar * kappa / (1 - a) > B:
        return None
    if Phi_up <= 0:
        return 1.0
    return float(min(1.0, max(0.0, (1 - a - kappa * abs(I) * ubar / B) / (kappa * Phi_up))))


def S_alpha(a, kappa, Phi, alpha):
    den = 1 - a - kappa * alpha * Phi
    return np.inf if den <= 0 else kappa / den


def Phi_from_S(a, kappa, S):
    return (1 - a - kappa / S) / kappa


# ------------------------------------------------------------------------------------------------
# 1. closed form
# ------------------------------------------------------------------------------------------------
def cohort_D(alpha, kappa0, a0, Phi, delta, rho):
    return (1 + delta * alpha) * (1 - a0 + rho * alpha) - kappa0 * Phi * alpha


def cohort_safe_set(kappa0, a0, Phi, delta, rho, I, ubar, B):
    """Exact safe set in [0,1] for one economy: list of closed intervals. Safe iff D(alpha) >= kappa0 |I| ubar / B."""
    tau = kappa0 * abs(I) * ubar / B
    A2 = delta * rho
    A1 = delta * (1 - a0) + rho - kappa0 * Phi
    A0 = (1 - a0) - tau
    if A2 == 0:
        if A1 == 0:
            return [(0.0, 1.0)] if A0 >= 0 else []
        root = -A0 / A1
        if A1 > 0:
            lo = max(0.0, root)
            return [(lo, 1.0)] if lo <= 1 else []
        hi = min(1.0, root)
        return [(0.0, hi)] if hi >= 0 else []
    disc = A1 * A1 - 4 * A2 * A0
    if disc <= 0:
        return [(0.0, 1.0)]
    r1 = (-A1 - np.sqrt(disc)) / (2 * A2); r2 = (-A1 + np.sqrt(disc)) / (2 * A2)
    out = []
    if r1 >= 0:
        out.append((0.0, min(1.0, r1)))
    if r2 <= 1:
        out.append((max(0.0, r2), 1.0))
    return [iv for iv in out if iv[0] <= iv[1]]


def cohort_worst_corner(box):
    """For alpha >= 0, D - kappa0*tau is increasing in delta and rho and decreasing in kappa0, a0 and Phi, so the worst economy
    of a box is the same corner for every alpha."""
    return {"kappa0": box["kappa0"][1], "a0": box["a0"][1], "Phi": box["Phi"][1], "delta": box["delta"][0], "rho": box["rho"][0]}


# ------------------------------------------------------------------------------------------------
# 2. three-state book: point evaluation and interval enclosure
# ------------------------------------------------------------------------------------------------
FIXED = {"a": 0.80, "r0": 0.15, "eps": 0.40, "eta": 0.30}


def book_matrices(alpha, th, fx=FIXED):
    k = th["kappa0"] / (1 + th["delta"] * alpha ** 2); q = alpha * th["q0"]; r = fx["r0"] + th["rho"] * alpha ** 2
    a, eps, eta, phi = fx["a"], fx["eps"], fx["eta"], th["phi"]
    J = np.array([[a + k * eta * q, phi, k * (1 - eta)], [eps * eta * q, 1 - r, eps * (1 - eta)], [eta * q, 0.0, 1 - eta]])
    return J, np.array([k, eps, 0.0])


def book_S(alpha, th, T=6000, fx=FIXED):
    J, v = book_matrices(alpha, th, fx)
    if max(abs(np.linalg.eigvals(J))) >= 1:
        return np.inf
    s = 0.0
    for _ in range(T):
        s += abs(v[0]); v = J @ v
    return s


def book_S_exact(alpha, th, fx=FIXED):
    """All entries of J and s0 are nonnegative here, so h_t >= 0 and S = e1' (I - J)^{-1} s0 when rho(J) < 1."""
    J, s0 = book_matrices(alpha, th, fx)
    if max(abs(np.linalg.eigvals(J))) >= 1:
        return np.inf
    return float(np.linalg.solve(np.eye(3) - J, s0)[0])


def book_S_interval(alo, ahi, th_lo, th_hi, T=80, fx=FIXED):
    """Interval enclosure [Slo, Shi] of S over alpha in [alo, ahi] and theta in the box [th_lo, th_hi] (arrays: a batch of
    boxes). Shi = +inf when no contraction certificate is found. Slo uses the finite horizon only (a valid lower bound)."""
    al = IV(alo, ahi)
    P = {k: IV(th_lo[k], th_hi[k]) for k in th_lo}
    a, r0, eps, eta = (IV.enclose(fx[k]) for k in ("a", "r0", "eps", "eta"))
    al2 = al.sq()
    k = P["kappa0"] / (1 + P["delta"] * al2)
    q = al * P["q0"]
    r = r0 + P["rho"] * al2
    one = IV.enclose(1.0); zero = IV(np.zeros_like(np.asarray(alo, float)))
    J = [[a + k * eta * q, P["phi"], k * (one - eta)],
         [eps * eta * q, one - r, eps * (one - eta)],
         [eta * q, zero, one - eta]]
    v = [k, eps * (zero + one), zero]
    Ppow = [[one * (zero + 1.0) if i == j else zero for j in range(3)] for i in range(3)]
    s = IV(np.zeros_like(np.asarray(alo, float)))
    norm_sum = np.zeros_like(np.asarray(alo, float))
    for _ in range(T):
        s = s + v[0].abs()
        norm_sum = np.nextafter(norm_sum + norm_inf_upper(Ppow), np.inf)
        v = matvec(J, v)
        Ppow = matmul(J, Ppow)
    lam = norm_inf_upper(Ppow)                                  # ||J^T||_inf upper bound
    vmag = np.maximum.reduce([x.mag() for x in v])               # ||J^T s0||_inf upper bound
    with np.errstate(divide="ignore", invalid="ignore"):
        tail = np.where(lam < 1, np.nextafter(vmag * norm_sum / np.nextafter(1 - lam, -np.inf), np.inf), np.inf)
    return s.lo, np.nextafter(s.hi + tail, np.inf)


# ------------------------------------------------------------------------------------------------
# interval branch and bound over the admission level
# ------------------------------------------------------------------------------------------------
def _split_box(box, K):
    names = sorted(box)
    grids = {n: np.linspace(box[n][0], box[n][1], K + 1) for n in names}
    lo, hi = {n: [] for n in names}, {n: [] for n in names}
    for idx in itertools.product(range(K), repeat=len(names)):
        for n, i in zip(names, idx):
            lo[n].append(grids[n][i]); hi[n].append(grids[n][i + 1])
    return {n: np.array(v) for n, v in lo.items()}, {n: np.array(v) for n, v in hi.items()}


def _samples(box):
    names = sorted(box)
    pts = [dict(zip(names, c)) for c in itertools.product(*[box[n] for n in names])]
    pts.append({n: 0.5 * (box[n][0] + box[n][1]) for n in names})
    return pts


def certify_admission(box, s_budget, tol=1e-3, K_levels=(1, 2, 3), T=80, fx=FIXED):
    """Classify [0,1] into certified-safe, certified-unsafe and undecided intervals for the robust condition
    sup_{theta in box} S(alpha, theta) <= s_budget. Returns dict with lists of intervals and certified brackets for the
    largest safe level and the largest level reachable by ramping from 0 through safe levels only."""
    samples = _samples(box)
    th_s_lo = {n: np.array([p[n] for p in samples]) for n in box}
    queue = [(0.0, 1.0)]; safe, unsafe, undecided = [], [], []
    n_eval = 0
    while queue:
        a0, a1 = queue.pop()
        # lower bound of the robust risk: max over sample economies of the interval lower bound over [a0, a1]
        lo_s, _ = book_S_interval(np.full(len(samples), a0), np.full(len(samples), a1), th_s_lo, th_s_lo, T=T, fx=fx)
        n_eval += len(samples)
        if np.max(lo_s) > s_budget:
            unsafe.append((a0, a1)); continue
        decided = False
        for K in K_levels:
            tl, th = _split_box(box, K)
            m = len(next(iter(tl.values())))
            _, hi_s = book_S_interval(np.full(m, a0), np.full(m, a1), tl, th, T=T, fx=fx)
            n_eval += m
            if np.max(hi_s) <= s_budget:
                safe.append((a0, a1)); decided = True; break
        if decided:
            continue
        if a1 - a0 > tol:
            mid = 0.5 * (a0 + a1); queue += [(mid, a1), (a0, mid)]
        else:
            undecided.append((a0, a1))
    merge = lambda L: _merge(sorted(L))
    safe, unsafe, undecided = merge(safe), merge(unsafe), merge(undecided)
    a_max_lo = max((b for _, b in safe), default=None)
    a_max_hi = max([b for _, b in safe] + [b for _, b in undecided], default=None)
    ramp = 0.0 if safe and safe[0][0] == 0.0 else None
    if ramp is not None:
        ramp = safe[0][1]
    return {"safe": safe, "unsafe": unsafe, "undecided": undecided, "alpha_max_bracket": [a_max_lo, a_max_hi],
            "alpha_ramp_lower": ramp, "undecided_length": float(sum(b - a for a, b in undecided)), "interval_evaluations": n_eval}


def _merge(L):
    out = []
    for a, b in L:
        if out and abs(out[-1][1] - a) < 1e-15:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def bisection_alpha(theta, s_budget, iters=40, fx=FIXED):
    """The monotone-risk shortcut (assumes S increasing in alpha): largest alpha with S(alpha) <= budget by bisection on [0,1]."""
    if book_S(1.0, theta, fx=fx) <= s_budget:
        return 1.0
    lo, hi = 0.0, 1.0
    if book_S(0.0, theta, fx=fx) > s_budget:
        return None
    for _ in range(iters):
        m = 0.5 * (lo + hi)
        if book_S(m, theta, fx=fx) <= s_budget:
            lo = m
        else:
            hi = m
    return lo


DEMO_BOX = {"phi": (0.075, 0.085), "kappa0": (0.97, 1.03), "q0": (0.115, 0.125), "delta": (3.8, 4.2), "rho": (0.28, 0.32)}


def run_optimizer_check():
    rng = np.random.default_rng(6); mism = 0; nonint = 0; cases = 0; infeas = 0
    for trial in range(500):
        K = rng.integers(1, 4); eta = rng.uniform(0.05, 0.95, K); aa = rng.uniform(0, 0.8); kk = rng.uniform(0.2, 1.5)
        Phi_ = rng.uniform(0.1, 2.0) * (1 - aa) / kk; q = rng.dirichlet(np.ones(K)) * Phi_
        I, ub, Bb = rng.uniform(0.5, 2), rng.uniform(0.01, 0.3), 1.0
        ast = alpha_star(aa, kk, Phi_, I, ub, Bb)
        grid = np.linspace(0, 1, 1001)
        safe = []
        for al in grid:
            Jm = closed_loop_matrix(aa, kk, al * q, eta); bvec = kk * np.r_[1.0, eta]
            if max(abs(np.linalg.eigvals(Jm))) >= 1:
                safe.append(False); continue
            Smat = np.linalg.solve(np.eye(K + 1) - Jm, bvec)[0]
            safe.append(I * ub * Smat <= Bb * (1 + 1e-9))
        safe = np.array(safe)
        cases += 1
        if ast is None:
            infeas += 1; mism += safe.any(); continue
        bf = grid[safe].max() if safe.any() else None
        mism += bf is None or abs(bf - ast) > 1.5e-3
        first_unsafe = np.argmax(~safe) if (~safe).any() else len(safe)
        nonint += safe[first_unsafe:].any()
    return {"cases": cases, "mismatches": int(mism), "non_interval_safe_sets": int(nonint), "infeasible_states": infeas,
                          "pass": mism == 0 and nonint == 0}



def run_venue_mode():
    """Test T13 (Proposition prop:venue, Theorem thm:venuebb): (a) the closed-form cohort venue model has a non-interval safe set
    and a worst-case corner; (b) in the three-state book with admission-dependent impact, refill and feedback, interval branch and
    bound certifies the robust safe set; checked against a dense sampled truth; (c) the monotone shortcut fails."""
    # (a) closed form, checked against a dense grid
    box = {"kappa0": (0.98, 1.02), "a0": (0.58, 0.6), "Phi": (2.3, 2.4), "delta": (2.9, 3.1), "rho": (0.58, 0.62)}
    I, ub, B = 1.0, 0.37, 1.0
    th = cohort_worst_corner(box)
    exact = cohort_safe_set(th["kappa0"], th["a0"], th["Phi"], th["delta"], th["rho"], I, ub, B)
    grid = np.linspace(0, 1, 2001); R = np.random.default_rng(13)
    pts = [dict(zip(sorted(box), c)) for c in itertools.product(*[box[n] for n in sorted(box)])]
    pts += [{n: R.uniform(*box[n]) for n in box} for _ in range(300)]
    def safe_all(al):
        for p in pts:
            D = cohort_D(al, p["kappa0"], p["a0"], p["Phi"], p["delta"], p["rho"])
            if D <= 0 or p["kappa0"] * I * ub / D > B:
                return False
        return True
    sampled = np.array([safe_all(a) for a in grid])
    in_exact = np.array([any(lo - 1e-12 <= a <= hi + 1e-12 for lo, hi in exact) for a in grid])
    closed = {"box": box, "worst_corner": th, "exact_safe_set": exact, "agree_with_sampled_grid": int((sampled == in_exact).sum()),
              "grid_points": len(grid), "safe_set_is_interval": len(exact) == 1 and exact[0][0] == 0.0}
    # (b) three-state book, branch and bound vs sampled truth
    bb = {}
    pts2 = _samples(DEMO_BOX) + [{n: R.uniform(*DEMO_BOX[n]) for n in DEMO_BOX} for _ in range(400)]
    grid2 = np.linspace(0, 1, 1001)
    Ssup = np.array([max(book_S_exact(a, p) for p in pts2) for a in grid2])
    for s_b in (6.3, 6.5):
        res = certify_admission(DEMO_BOX, s_b, tol=2e-3)
        viol = int(sum(1 for a, s in zip(grid2, Ssup) if any(lo <= a <= hi for lo, hi in res["safe"]) and s > s_b))
        wrong_unsafe = int(sum(1 for a, s in zip(grid2, Ssup) if any(lo <= a <= hi for lo, hi in res["unsafe"]) and s <= s_b))
        nominal = {n: 0.5 * (DEMO_BOX[n][0] + DEMO_BOX[n][1]) for n in DEMO_BOX}
        shortcut_ok = book_S_exact(1.0, nominal) <= s_b         # monotone shortcut: certify alpha = 1, hence all of [0, 1]
        bb[str(s_b)] = {**res, "sampled_violations_of_certified_safe": viol, "certified_unsafe_but_sampled_safe": wrong_unsafe,
                        "sampled_sup_S_at_0_0.1_0.2_1": [float(Ssup[0]), float(Ssup[100]), float(Ssup[200]), float(Ssup[-1])],
                        "monotone_shortcut_claims_all_of_0_1_safe": bool(shortcut_ok),
                        "unsafe_levels_admitted_by_shortcut": float(sum(b - a for a, b in res["unsafe"])) if shortcut_ok else 0.0}
    ok = closed["agree_with_sampled_grid"] == len(grid) and all(v["sampled_violations_of_certified_safe"] == 0 and v["certified_unsafe_but_sampled_safe"] == 0 for v in bb.values())
    return {"closed_form": closed, "book_branch_and_bound": bb, "pass": bool(ok)}

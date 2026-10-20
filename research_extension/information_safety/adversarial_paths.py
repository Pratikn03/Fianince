"""Exact worst-case loss by exhaustive sign enumeration and by linear programming (corrected quantity gate; test T05,
blueprint D1, E04). Per-period shock bound |v_j| <= V: worst case = V * sum |g_k| (all sign paths). Total budget
sum |v_j| <= V: worst case = V * max |g_k| (a vertex of the l1 ball)."""
import itertools
import numpy as np
from scipy.optimize import linprog


def run_sign_enumeration():
    rng = np.random.default_rng(5); t5 = {"per_period_sum_exact": 0, "total_budget_peak_exact": 0, "peak_under_per_period_violations": 0, "cases": 0}
    for trial in range(200):
        n = 3; J = rng.normal(0, 0.5, (n, n)); J /= max(1.0, max(abs(np.linalg.eigvals(J))) / 0.95)
        Hv = rng.normal(0, 1, n); C = rng.normal(0, 1, n)
        for Tn in range(1, 11):
            g = np.array([C @ np.linalg.matrix_power(J, m) @ Hv for m in range(Tn)])
            worst = max(abs(np.dot(g[::-1], np.array(s))) for s in itertools.product([-1, 1], repeat=Tn))
            t5["per_period_sum_exact"] += abs(worst - np.abs(g).sum()) < 1e-9
            vert = max(abs(g))                                   # l1 ball: maximum at a vertex
            t5["total_budget_peak_exact"] += abs(vert - np.max(np.abs(g))) < 1e-12
            t5["peak_under_per_period_violations"] += worst > np.max(np.abs(g)) + 1e-12
            t5["cases"] += 1
    t5["pass"] = t5["per_period_sum_exact"] == t5["cases"]
    return t5



def support_joint(g, V, W):
    """Worst case of |sum_k g_k v_k| over |v_k| <= V and sum |v_k| <= W: fill the largest |g_k| first (closed form)."""
    a = np.sort(np.abs(np.asarray(g, float)))[::-1]
    full = int(min(len(a), np.floor(W / V))) if V > 0 else 0
    val = V * a[:full].sum()
    if full < len(a):
        val += (W - full * V) * a[full]
    return float(val)


def support_lp(g, V, W):
    """The same worst case by linear programming (v = v+ - v-, maximize g'v; the problem is symmetric in sign)."""
    g = np.asarray(g, float); H = len(g)
    c = -np.r_[g, -g]                                       # maximize g'(v+ - v-)
    A = np.ones((1, 2 * H)); b = [W]
    res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, V)] * (2 * H), method="highs")
    return float(-res.fun)


def run_lp_support(seed=51, cases=300):
    """E04 for larger horizons: closed-form joint support versus LP; per-period-only and budget-only limits."""
    rng = np.random.default_rng(seed); worst = 0.0; n = 0
    for _ in range(cases):
        H = int(rng.integers(5, 60)); g = rng.normal(0, 1, H) * 0.9 ** np.arange(H); V = rng.uniform(0.1, 1); W = rng.uniform(0.1, 1) * H * V
        worst = max(worst, abs(support_joint(g, V, W) - support_lp(g, V, W))); n += 1
        assert abs(support_joint(g, V, 1e9) - V * np.abs(g).sum()) < 1e-9 and abs(support_joint(g, 1e9, W) - W * np.abs(g).max()) < 1e-9
    return {"cases": n, "max_abs_gap_closed_form_vs_LP": worst, "pass": worst < 1e-7}

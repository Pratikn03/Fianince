"""Theorem thm:robustguard (closed form vs state matrices), Proposition prop:venue (non-interval safe set, worst corner) and
Theorem thm:venuebb (interval branch and bound is sound), plus the interval arithmetic it relies on."""
import itertools
import numpy as np
from model_contracts import closed_loop_matrix
from robust_admission import (alpha_star, cohort_D, cohort_safe_set, cohort_worst_corner, certify_admission, book_S_exact,
                              book_S_interval, DEMO_BOX)
from interval import IV


def test_robust_guard_matches_state_matrix():
    rng = np.random.default_rng(6)
    for _ in range(40):
        K = 2; eta = rng.uniform(.1, .9, K); a = rng.uniform(0, .6); ka = rng.uniform(.3, 1.2)
        Phi = rng.uniform(.2, 1.5) * (1 - a) / ka; q = rng.dirichlet(np.ones(K)) * Phi
        ast = alpha_star(a, ka, Phi, 1.0, .1, 1.0)
        if ast is None or ast >= 1:
            continue
        for al, safe in [(ast * .999, True), (min(1, ast * 1.001), False)]:
            J = closed_loop_matrix(a, ka, al * q, eta); S = np.linalg.solve(np.eye(K + 1) - J, ka * np.r_[1.0, eta])[0]
            assert (.1 * S <= 1 + 1e-9) == safe


def test_venue_closed_form_nonconvex_and_corner():
    box = {"kappa0": (0.98, 1.02), "a0": (0.58, 0.6), "Phi": (2.3, 2.4), "delta": (2.9, 3.1), "rho": (0.58, 0.62)}
    th = cohort_worst_corner(box); S = cohort_safe_set(th["kappa0"], th["a0"], th["Phi"], th["delta"], th["rho"], 1, .37, 1)
    assert len(S) == 2 and S[0][0] == 0.0 and S[1][1] == 1.0
    rng = np.random.default_rng(0)
    for al in np.linspace(0, 1, 201):
        worst = min(cohort_D(al, *(rng.uniform(*box[n]) for n in ("kappa0", "a0", "Phi", "delta", "rho"))) for _ in range(50))
        assert cohort_D(al, th["kappa0"], th["a0"], th["Phi"], th["delta"], th["rho"]) - th["kappa0"] * .37 <= worst - 0.98 * .37 + 1e-12


def test_interval_encloses_point_values():
    rng = np.random.default_rng(1)
    for _ in range(20):
        a0 = rng.uniform(0, .9); a1 = min(1, a0 + rng.uniform(0, .05))
        lo = {n: np.array([DEMO_BOX[n][0]]) for n in DEMO_BOX}; hi = {n: np.array([DEMO_BOX[n][1]]) for n in DEMO_BOX}
        Slo, Shi = book_S_interval(np.array([a0]), np.array([a1]), lo, hi)
        for _ in range(20):
            th = {n: rng.uniform(*DEMO_BOX[n]) for n in DEMO_BOX}; al = rng.uniform(a0, a1)
            s = book_S_exact(al, th)
            assert Shi[0] >= s and (Slo[0] <= s)


def test_branch_and_bound_sound():
    res = certify_admission(DEMO_BOX, 6.5, tol=8e-3)
    rng = np.random.default_rng(3)
    pts = [dict(zip(sorted(DEMO_BOX), c)) for c in itertools.product(*[DEMO_BOX[n] for n in sorted(DEMO_BOX)])]
    pts += [{n: rng.uniform(*DEMO_BOX[n]) for n in DEMO_BOX} for _ in range(60)]
    for lo, hi in res["safe"]:
        for al in np.linspace(lo, hi, 7):
            assert max(book_S_exact(al, p) for p in pts) <= 6.5
    assert len(res["safe"]) >= 2 and res["unsafe"]                       # non-interval safe set found


def test_interval_ops_contain_exact():
    rng = np.random.default_rng(2)
    for _ in range(500):
        x, y = rng.normal(0, 3, 2); X, Y = IV.enclose(x), IV.enclose(y)
        for f, F in [(lambda u, v: u + v, lambda U, V: U + V), (lambda u, v: u * v, lambda U, V: U * V),
                     (lambda u, v: u - v, lambda U, V: U - V)]:
            Z = F(X, Y); assert Z.lo <= f(x, y) <= Z.hi
        if abs(y) > 1e-3:
            Z = X / Y; assert Z.lo <= x / y <= Z.hi

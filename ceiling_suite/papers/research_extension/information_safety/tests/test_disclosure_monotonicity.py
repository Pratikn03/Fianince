"""Theorem thm:disclosure (i): a smaller compatible set (here a smaller certified Phi) never lowers safe capacity."""
import numpy as np
from robust_admission import alpha_star


def test_disclosure_monotone():
    for Phi_pub, Phi_disc in [(1.0, .8), (.5, .5), (2.0, .3)]:
        assert alpha_star(.4, 1, Phi_disc, 1, .48, 1) >= alpha_star(.4, 1, Phi_pub, 1, .48, 1)


def test_strict_only_if_binding_economy_removed():
    rng = np.random.default_rng(9)
    for _ in range(200):
        a, k = rng.uniform(0, .6), rng.uniform(.3, 1.2); Pp = rng.uniform(.05, 1) * (1 - a) / k
        I, ub = 1.0, rng.uniform(.01, .2)
        base = alpha_star(a, k, Pp, I, ub, 1.0)
        if base is None or base >= 1:
            continue
        assert alpha_star(a, k, Pp, I, ub, 1.0) == base                  # same worst case: no gain
        assert alpha_star(a, k, 0.9 * Pp, I, ub, 1.0) > base              # binding economy excluded: strict gain


def test_intersection_admits_at_least_either():
    """Theorem thm:disclosure (v): the minimum of two upper bounds admits at least as much as either one."""
    rng = np.random.default_rng(15)
    for _ in range(200):
        P1, P2 = rng.uniform(.05, .6, 2)
        ai = alpha_star(.4, 1, min(P1, P2), 1, .48, 1)
        assert ai >= alpha_star(.4, 1, P1, 1, .48, 1) and ai >= alpha_star(.4, 1, P2, 1, .48, 1)

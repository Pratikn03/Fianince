"""Fast unit tests for the information-safety extension (pytest -q). Each mirrors a statement in Paper 2."""
import itertools, os, sys
from fractions import Fraction as Fr
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_contracts import impulse, impulse_exact, impulse_from_kernel, kernel, moments_from_impulse, summed_response, closed_loop_matrix
from markov_krein import phi_bounds, check_rep, best_approx_error_formula
from certificate import certificate, lam_bar, T_for
from robust_admission import alpha_star


def test_witness_exact():                       # Example ex:witness
    a, k = Fr(2, 5), Fr(1)
    hA = impulse_exact(a, k, [Fr(8, 100)], [Fr(1, 2)], 5)
    hB = impulse_exact(a, k, [Fr(2, 100) / Fr(95, 100), Fr(2, 100) / Fr(5, 100)], [Fr(95, 100), Fr(5, 100)], 5)
    assert hA[:3] == hB[:3] and hA[3] != hB[3]


def test_recursions_agree():
    rng = np.random.default_rng(1)
    for _ in range(50):
        K = rng.integers(1, 4); a = rng.uniform(0, .8); ka = rng.uniform(.2, 1.5); eta = rng.uniform(.05, .95, K)
        q = rng.dirichlet(np.ones(K)) * rng.uniform(.05, .95) * (1 - a) / ka
        h = impulse(a, ka, q, eta, 80)
        assert np.allclose(h, impulse_from_kernel(a, ka, kernel(q, eta, 80), 80), atol=1e-12)
        assert np.allclose(moments_from_impulse(a, ka, h, 20), kernel(q, eta, 20), atol=1e-9)


def test_convolution_gain_exact():              # corrected quantity gate, test T05
    rng = np.random.default_rng(2)
    for _ in range(30):
        g = rng.normal(0, 1, 8)
        worst = max(abs(np.dot(g, s)) for s in itertools.product([-1, 1], repeat=8))
        assert abs(worst - np.abs(g).sum()) < 1e-9


def test_markov_krein_brackets_truth():         # Theorem thm:window (i)-(ii)
    rng = np.random.default_rng(3)
    for _ in range(20):
        K = 4; r = rng.uniform(0, .9, K); w = rng.uniform(.1, 1, K)
        for d in range(1, 2 * K - 1):
            c = [float(np.sum(w * r ** j)) for j in range(d + 1)]
            lo, up, L, U = phi_bounds(c, .9)
            assert check_rep(L, c, .9)[0] and check_rep(U, c, .9)[0]
            true = float(np.sum(w / (1 - r)))
            assert lo <= true + 1e-9 <= up + 2e-9
            assert up - lo <= 2 * c[0] * best_approx_error_formula(d, .9) * (1 + 1e-9)


def test_certificate_coverage():                # Theorem thm:certcost (i), test T04
    rng = np.random.default_rng(4); miss = 0; reps = 400
    for _ in range(reps):
        a, ka = .3, .8; eta = np.array([.3, .7]); q = np.array([.2, .2]); h = impulse(a, ka, q, eta, 600)
        T = T_for(.05 * h.sum(), ka, .7, .7); hb = h + rng.normal(0, .04 / np.sqrt(100), 600)
        miss += certificate(hb, .04, 100, ka, .7, .7, T, .05) < h.sum()
    assert miss / reps <= .05 + .03


def test_robust_guard_matches_state_matrix():   # Theorem thm:robustguard (i), test T06
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


def test_disclosure_monotone():                 # Theorem thm:disclosure (i)
    for Phi_pub, Phi_disc in [(1.0, .8), (.5, .5), (2.0, .3)]:
        assert alpha_star(.4, 1, Phi_disc, 1, .48, 1) >= alpha_star(.4, 1, Phi_pub, 1, .48, 1)

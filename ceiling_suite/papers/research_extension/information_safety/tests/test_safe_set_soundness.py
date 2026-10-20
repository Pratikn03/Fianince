"""Lemma lem:sound and Lemma lem:certnum: compatible-set guards are sound with the set's coverage; certified window
endpoints contain the exact Markov-Krein interval."""
import numpy as np
from data_compatibility import phi_bounds, check_rep, best_approx_error_formula, certified_phi_bounds
from robust_admission import alpha_star
from model_contracts import summed_response


def test_markov_krein_brackets_truth():
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


def test_certified_endpoints_contain_exact_interval():
    rng = np.random.default_rng(8)
    for _ in range(8):
        K = 3; r = rng.uniform(0, .9, K); w = rng.uniform(.1, 1, K)
        for n in (3, 4, 5):
            k = [float(np.sum(w * r ** j)) for j in range(n)]
            c = certified_phi_bounds(k, .9)
            assert c["Phi_lo_cert"] <= c["Phi_lo_hp"] and c["Phi_hi_cert"] >= c["Phi_hi_hp"]
            assert c["Phi_hi_cert"] - c["Phi_hi_hp"] < 1e-6 * c["Phi_hi_hp"]
            assert c["Phi_lo_cert"] <= float(np.sum(w / (1 - r))) <= c["Phi_hi_cert"]


def test_compatible_set_guard_sound():
    """If the true Phi is below the certified Phi_up, every admitted level is safe for the true economy."""
    rng = np.random.default_rng(10)
    for _ in range(500):
        a, k = rng.uniform(0, .6), rng.uniform(.3, 1.2); Phi = rng.uniform(.05, .95) * (1 - a) / k
        Phi_up = Phi * rng.uniform(1, 1.5); ub = rng.uniform(.01, .3)
        ast = alpha_star(a, k, Phi_up, 1.0, ub, 1.0)
        if ast is None:
            continue
        for al in np.linspace(0, ast, 5):
            assert ub * summed_response(a, k, al * Phi) <= 1 + 1e-9

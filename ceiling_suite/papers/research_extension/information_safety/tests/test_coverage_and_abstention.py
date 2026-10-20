"""Theorem thm:certcost (i) and Proposition prop:hotelling: coverage of the certificates; abstention when infeasible."""
import numpy as np
from model_contracts import impulse
from uncertainty_calibration import (certificate, T_for, t_certificate, hotelling_upper, z_certificate_O1, noise_ar_taps)
from robust_admission import alpha_star


def test_certificate_coverage():
    rng = np.random.default_rng(4); miss = 0; reps = 400
    for _ in range(reps):
        a, ka = .3, .8; eta = np.array([.3, .7]); q = np.array([.2, .2]); h = impulse(a, ka, q, eta, 600)
        T = T_for(.05 * h.sum(), ka, .7, .7); hb = h + rng.normal(0, .04 / np.sqrt(100), 600)
        miss += certificate(hb, .04, 100, ka, .7, .7, T, .05) < h.sum()
    assert miss / reps <= .05 + .03


def test_t_certificate_exact_with_correlated_taps():
    rng = np.random.default_rng(11); h = 0.8 * 0.6 ** np.arange(10); S = h.sum(); g = noise_ar_taps(0.05, 0.8)
    cov_t = cov_z = cov_h = 0; reps = 1500
    for _ in range(reps):
        H = h + g(rng, 40, 10)
        cov_t += t_certificate(H) >= S; cov_z += z_certificate_O1(H, 0.05) >= S; cov_h += hotelling_upper(H, np.ones(10)) >= S
    assert cov_t / reps >= 0.93 and cov_h / reps >= 0.95 and cov_z / reps < 0.85


def test_abstains_when_infeasible():
    assert alpha_star(0.5, 1.0, 0.3, I=10.0, ubar=1.0, B=1.0) is None

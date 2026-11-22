import math
import unittest

import numpy as np

from instrument_incidence import (
    ar1_filter_moments,
    kink_checks,
    optimal_activity,
    optimizer_check,
    quadratic_coefficients,
    quadrature_pair,
)


class InstrumentIncidenceTests(unittest.TestCase):
    def test_filter_against_direct_covariance(self):
        r, p, variance = .6, -.25, .8
        indices = np.arange(150)
        lags = indices[:, None] - indices[None, :]
        coefficients = (1-r) * r**indices
        variance_direct = coefficients @ (variance * p**abs(lags)) @ coefficients
        for h in [1, 2, 5]:
            v, d = ar1_filter_moments(r, p, variance, h)
            covariance = coefficients @ (variance * p**abs(lags + h)) @ coefficients
            self.assertAlmostEqual(v, variance_direct)
            self.assertAlmostEqual(d, 2*(variance_direct-covariance))

    def test_white_noise_proportional_tax_exit(self):
        for r in [.2, .5, .8]:
            v, d = ar1_filter_moments(r, 0., 1.)
            tau = math.sqrt(math.pi / (4 * 1.5))
            self.assertAlmostEqual(optimal_activity(v, d, tax=tau),
                                   max(0., 1-math.sqrt((1+r)/1.5)))

    def test_turnover_cap_and_revision(self):
        r = .7
        v, d = ar1_filter_moments(r, 0., 1., 3)
        volume = math.sqrt(2*d/math.pi)/3
        self.assertAlmostEqual(optimal_activity(v, d, h=3, cap=.2*volume), .2)
        self.assertAlmostEqual(optimal_activity(v, d, h=3, decay=.5), (1+.5+.25)/3)

    def test_quadratic_series(self):
        for r in [.1, .8]:
            v, d = ar1_filter_moments(r, .35, 1.)
            q = optimal_activity(v, d, quadratic=.2)
            c = quadratic_coefficients(.35, 1., .2, 70)
            self.assertAlmostEqual(c @ (r**np.arange(len(c))), (1-q)/(1-r))

    def test_moment_pair_and_exit(self):
        for k in (2, 3, 4):
            a, b = quadrature_pair(k)
            for j in range(2*k-1):
                self.assertAlmostEqual(a[1] @ a[0]**j, b[1] @ b[0]**j)
        for k, result in kink_checks().items():
            self.assertAlmostEqual(result["tap_slope"], 2*int(k)-1)
            for row in result["rows"]:
                self.assertEqual((row["gauss_exits"], row["radau_exits"]), (0, 1))
                self.assertGreater(row["budget_gap"], 0.)

    def test_closed_form_matches_optimizer(self):
        self.assertLess(optimizer_check(), 1.e-6)


if __name__ == "__main__":
    unittest.main()

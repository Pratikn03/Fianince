import unittest

import numpy as np

from passive_incidence import (
    fit_bounded_polynomial,
    fitted_spectrum,
    impact_weighted_taps,
    model_spectrum,
    quadratic_weight,
    sample_covariances,
    simulation,
)


class PassiveCertificateTests(unittest.TestCase):
    def test_covariance_padding(self):
        x = np.array([1., -3., 2., 0., 5.])
        np.testing.assert_allclose(sample_covariances(x, 4), [
            np.mean(x*x), *(np.mean(x[j:]*x[:-j]) for j in range(1, 5))
        ])

    def test_factor_recovers_taps_without_innovation_scale(self):
        r = np.array([.2, .55, .75])
        w = np.array([.08, .10, .12])
        kappa, a = .5, .2
        f = 3.7*model_spectrum(r, w, a, kappa)
        expected = kappa*w @ (r[:, None]**np.arange(12))
        np.testing.assert_allclose(impact_weighted_taps(f, a, 12), expected, atol=1.e-11)

    def test_spectrum_floor(self):
        np.testing.assert_allclose(fitted_spectrum([1., .5], 8, .1)[:3],
                                   [2., 1+2**(-.5), 1.])

    def test_white_noise_quadratic_weight(self):
        r = np.array([0., .2, .65, .79])
        g = quadratic_weight([1., 0.], r, .17, 1.2, .1)
        np.testing.assert_allclose(g, .34/(1.2+.34*(1-r)))

    def test_bounded_polynomial_fixture(self):
        grid = np.linspace(0, .8, 25)
        c = fit_bounded_polynomial(grid, 1.-.45*grid, 5, 1.08, 2.)
        self.assertLessEqual(np.abs(c) @ 1.08**np.arange(len(c)), 2.00000001)
        np.testing.assert_allclose(np.polynomial.polynomial.polyval(grid, c), 1.-.45*grid,
                                   atol=1.e-9)

    def test_passive_end_to_end(self):
        receipt = simulation(repetitions=4, sample_sizes=(512, 2048))
        self.assertTrue(all(np.isfinite(r["rmse"]) for r in receipt["rows"]))
        self.assertGreater(receipt["truth"], 0)


if __name__ == "__main__":
    unittest.main()

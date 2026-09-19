"""Deterministic algebra checks for the Machine Markets working paper.
These are NOT calibrated markets, agent experiments, or empirical evidence.
Requires Python 3 and NumPy. Run: python verify_math.py
"""
import json
import numpy as np


def spectral_radius(matrix):
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Expected a square matrix")
    if not np.isfinite(matrix).all():
        raise ValueError("Nonfinite matrix entry")
    return float(np.max(np.abs(np.linalg.eigvals(matrix))))


def scalar_matrix(a, g, eta, kappa=1.0):
    if not (0 <= a < 1 and 0 < eta <= 1 and g >= 0 and kappa >= 0):
        raise ValueError("Parameters violate the proposition assumptions")
    return np.array([[a, g], [eta * kappa, 1 - eta]])


def rho_formula(a, g, eta, kappa=1.0):
    return float((a + 1 - eta + np.sqrt((a - 1 + eta)**2
                 + 4 * g * eta * kappa)) / 2)


def main():
    rows = []
    for label, g, eta in [
        ("stable feedback", 0.30, 0.20),
        ("boundary", 0.60, 0.20),
        ("unstable feedback", 0.90, 0.20),
        ("same unstable gain, slower learning", 0.90, 0.05),
        ("same unstable gain, faster learning", 0.90, 0.80),
        ("baseline before action gate", 0.45, 0.20),
        ("gate, depth unchanged", 0.225, 0.20),
        ("gate, depth reduced to one quarter", 0.90, 0.20),
    ]:
        radius = spectral_radius(scalar_matrix(0.4, g, eta))
        assert abs(radius - rho_formula(0.4, g, eta)) < 1e-12
        rows.append(dict(case=label, a=0.4, g=g, eta=eta, kappa=1.0,
                         radius=radius))

    # A deterministic Cartesian grid, not a Monte Carlo experiment.
    scalar_checks = 0
    max_error = 0.0
    for a in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for eta in [0.05, 0.2, 0.5, 0.8, 1.0]:
            for g in [0.07, 0.17, 0.37, 0.67, 1.07]:
                for kappa in [0.15, 0.45, 0.85, 1.25, 1.75]:
                    radius = spectral_radius(scalar_matrix(a, g, eta, kappa))
                    max_error = max(max_error,
                        abs(radius - rho_formula(a, g, eta, kappa)))
                    assert abs(g * kappa - (1 - a)) > 1e-8
                    assert (radius < 1) == (g * kappa < 1 - a)
                    scalar_checks += 1

    # Independent network formula checks with a fixed seed.
    rng = np.random.default_rng(20260918)
    network_checks = 0
    max_network_error = 0.0
    for _ in range(250):
        d, n = 3, 4
        B = rng.uniform(0, 1, (d, n)) / n
        C = rng.uniform(0, 1, (n, d)) / d
        a = float(rng.uniform(0.05, 0.95))
        eta = float(rng.uniform(0.05, 1.0))
        g = float(rng.uniform(0.01, 4.0))
        J = np.block([[a*np.eye(d), g*B],
                      [eta*C, (1-eta)*np.eye(n)]])
        nu = spectral_radius(B @ C)
        radius = spectral_radius(J)
        pred = rho_formula(a, g, eta, nu)
        max_network_error = max(max_network_error, abs(radius - pred))
        assert abs(radius - pred) < 1e-10
        assert abs(g*nu - (1-a)) > 1e-8
        assert (radius < 1) == (g*nu < 1-a)
        network_checks += 1

    # Frozen eigenvalues do not certify an arbitrarily switched system.
    J1 = np.array([[0.5, 2.0], [0.0, 0.5]])
    J2 = J1.T
    switch_radius = spectral_radius(J2 @ J1)
    assert spectral_radius(J1) == 0.5
    assert spectral_radius(J2) == 0.5
    assert switch_radius > 1

    # Stable eigenvalues can coexist with large finite-horizon gain.
    J = np.array([[0.8, 4.0], [0.0, 0.8]])
    gains = [float(np.linalg.norm(np.linalg.matrix_power(J, h), 2))
             for h in range(51)]
    peak_h = int(np.argmax(gains))
    assert spectral_radius(J) < 1 and max(gains) > 8

    # A Gram concentration score loses the direction of action alignment.
    r = np.array([1.0, 0.0])
    same = np.stack([r, r])
    opposite = np.stack([r, -r])
    def adc(R):
        return float(np.linalg.eigvalsh(R.T @ R / len(R))[-1])
    assert adc(same) == adc(opposite) == 1.0
    assert np.linalg.norm(same.mean(axis=0)) == 1.0
    assert np.linalg.norm(opposite.mean(axis=0)) == 0.0

    out = dict(scalar_cases=rows, scalar_grid_checks=scalar_checks,
               max_scalar_formula_error=max_error,
               network_checks=network_checks,
               max_network_formula_error=max_network_error,
               switching_product_radius=switch_radius,
               switching_per_step_growth=np.sqrt(switch_radius),
               nonnormal_radius=0.8, nonnormal_peak_h=peak_h,
               nonnormal_peak_gain=max(gains),
               concentration_same=adc(same),
               concentration_opposite=adc(opposite),
               numpy_version=np.__version__)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()

"""Passive price certificate for the quadratic-cost benchmark.

The input is the centered pricing signal of the stationary model. The known
anchor is a model input. No registered data or direct kernel taps are used.
"""

import json
import math

import numpy as np
from scipy import optimize, signal


def sample_covariances(x, max_lag):
    price = np.asarray(x, dtype=float)
    if price.ndim != 1 or not np.isfinite(price).all() or not 0 <= max_lag < len(price):
        raise ValueError("Expected one finite price sequence longer than max_lag")
    grid = 2 ** (2 * len(price) - 1).bit_length()
    cross = np.fft.irfft(abs(np.fft.rfft(price, n=grid))**2, n=grid)[:max_lag + 1]
    return cross / (len(price) - np.arange(max_lag + 1))


def fitted_spectrum(covariances, grid_size, floor):
    covariance = np.asarray(covariances, dtype=float)
    if covariance.ndim != 1 or not len(covariance) or 2 * len(covariance) > grid_size or floor <= 0:
        raise ValueError("Invalid spectrum grid or floor")
    grid = np.zeros(grid_size)
    lags = np.arange(1, len(covariance))
    grid[0] = covariance[0]
    grid[lags] = grid[-lags] = covariance[1:]
    return np.maximum(np.fft.fft(grid).real, floor)


def impact_weighted_taps(spectrum, anchor, depth):
    """Recover the first depth coefficients of (1-Q(z))/z - anchor."""
    spectrum = np.asarray(spectrum, dtype=float)
    if depth < 1 or 2 * depth >= len(spectrum) or np.any(spectrum <= 0):
        raise ValueError("Expected a positive spectrum grid with resolution above depth")
    cepstrum = np.fft.fft(np.log(spectrum)).real[:depth + 1] / len(spectrum)
    taps = np.zeros(depth + 1)
    taps[0] = 1.
    for j in range(1, depth + 1):
        k = np.arange(1, j + 1)
        taps[j] = -np.dot(k * cepstrum[k], taps[j - k]) / j
    recovered = -taps[1:]
    recovered[0] -= anchor
    return recovered


def quadratic_weight(covariance, memories, quadratic, risk, denominator_floor):
    """Evaluate the fixed-memory quadratic-cost g on a real memory grid."""
    gamma = np.asarray(covariance, dtype=float)
    r = np.asarray(memories, dtype=float)
    shifted = np.r_[gamma[1:], 0.]
    b = np.polynomial.polynomial.polyval(r, np.r_[gamma[0], 2*gamma[1:]])
    b1_coefficients = np.r_[shifted[0], shifted[1:] + gamma[:-1], gamma[-1]]
    b1 = np.polynomial.polynomial.polyval(r, b1_coefficients)
    c1 = 2 * (b - b1) / (1-r)
    return quadratic*c1 / np.maximum(risk*b + quadratic*(1-r)*c1, denominator_floor)


def fit_bounded_polynomial(memory_grid, pilot, depth, radius, bound):
    """Fit on the supplied mesh with a certified weighted coefficient L1 bound."""
    if radius <= 1. or bound <= 0 or depth < 1:
        raise ValueError("Expected a radius above one, a positive bound and depth")
    j = np.arange(depth)
    powers = (np.asarray(memory_grid)[:, None] / radius)**j
    one = np.ones((len(powers), 1))
    inequalities = np.vstack([
        np.hstack([powers, -powers, -one]),
        np.hstack([-powers, powers, -one]),
        np.r_[np.ones(2 * depth), 0.],
    ])
    targets = np.r_[pilot, -pilot, bound]
    objective = np.r_[np.zeros(2 * depth), 1.]
    for method in ("highs-ipm", "highs-ds"):
        fit = optimize.linprog(objective, A_ub=inequalities, b_ub=targets, method=method)
        if fit.success:
            break
    else:
        raise RuntimeError(f"Polynomial fit failed: {fit.message}")
    coefficients = (fit.x[:depth]-fit.x[depth:2*depth]) / radius**j
    norm = np.abs(coefficients) @ radius**j
    return coefficients * min(1., bound / norm) if norm else coefficients


def estimate(x, *, anchor, max_memory, quadratic, risk, cov_lag,
             depth, radius, coefficient_bound, spectrum_lower):
    """Compute the point estimate. The coefficient and spectrum bounds are inputs."""
    if not 0 < max_memory < 1 or risk <= 0 or quadratic < 0 or cov_lag < 1:
        raise ValueError("Invalid memory or quadratic desk parameters")
    covariance = sample_covariances(x, cov_lag)
    mesh = np.linspace(0, max_memory, math.ceil(math.sqrt(len(x))) + 1)
    pilot = quadratic_weight(covariance, mesh, quadratic, risk, risk*spectrum_lower/2)
    fitted_weight = fit_bounded_polynomial(mesh, pilot, depth, radius, coefficient_bound)
    grid_size = 2 ** max(9, (2*max(len(x), depth, cov_lag)).bit_length())
    spectrum = fitted_spectrum(covariance, grid_size, spectrum_lower/2)
    taps = impact_weighted_taps(spectrum, anchor, depth)
    return max(0., float(fitted_weight @ taps))


def model_spectrum(nodes, weights, anchor, impact, grid_size=8192):
    """Synthetic Gaussian closed-loop model with unit innovation variance."""
    omega = 2*np.pi*np.arange(grid_size) / grid_size
    z = np.exp(-1j*omega)
    kernel = np.sum(np.asarray(weights)[:, None] / (1-np.asarray(nodes)[:, None]*z), axis=0)
    return abs(1-anchor*z-impact*z*kernel)**(-2)


def synthetic_observations(nodes, weights, anchor, impact, length, rng):
    # Evaluate the exact rational transfer using a finite polynomial denominator.
    factors = [np.array([1., -r]) for r in nodes]
    numerator = np.array([1.])
    for factor in factors:
        numerator = np.polynomial.polynomial.polymul(numerator, factor)
    denominator = np.polynomial.polynomial.polymul([1., -anchor], numerator)
    for j, weight in enumerate(weights):
        other = np.array([1.])
        for i, factor in enumerate(factors):
            if i != j:
                other = np.polynomial.polynomial.polymul(other, factor)
        denominator[1:len(other)+1] -= impact * weight * other
    return signal.lfilter(numerator, denominator, rng.normal(size=length+300))[300:]


def adaptive_hyperparameters(x, *, max_memory, quadratic, risk):
    """Data-driven lag/polynomial truncation L_n = ceil(c_log * log n), Bartlett PSD floor, and 2-fold CV bound."""
    price = np.asarray(x, dtype=float)
    n = len(price)
    if n < 64 or not 0 < max_memory < 1 or risk <= 0 or quadratic < 0:
        raise ValueError("Expected n >= 64 and valid memory/desk parameters")
    b_lag = max(8, math.ceil(1.5 * math.log(n)))
    gam_init = sample_covariances(price, b_lag)
    k_idx = np.arange(1, len(gam_init))
    bartlett_cov = np.r_[gam_init[0], gam_init[1:] * (1.0 - k_idx / (b_lag + 1.0))]
    f_bart = fitted_spectrum(bartlett_cov, 1024, max(1.e-6, gam_init[0] / n))
    spec_lower = max(2.0 * gam_init[0] / math.sqrt(n), float(np.min(f_bart)))

    ac1 = abs(gam_init[1]) / max(gam_init[0], 1.e-12)
    rho_hat = float(np.clip(max(max_memory, ac1 ** 0.5), 0.55, 0.90))
    c_log = float(np.clip(0.65 / (-math.log(rho_hat)), 3.2, 5.5))
    L_n = min(n // 5, math.ceil(c_log * math.log(n)))
    radius = 1.0 + 0.20 * (1.0 - max_memory)

    half = n // 2
    lag_cv = min(L_n, half // 5)
    cov1 = sample_covariances(price[:half], lag_cv)
    cov2 = sample_covariances(price[half:2 * half], lag_cv)
    mesh_cv = np.linspace(0, max_memory, 33)
    pilot1 = quadratic_weight(cov1, mesh_cv, quadratic, risk, risk * spec_lower / 2.0)
    pilot2 = quadratic_weight(cov2, mesh_cv, quadratic, risk, risk * spec_lower / 2.0)
    scale0 = max(0.5, float(np.max(np.abs(pilot1))))
    best_B, best_err = 4.0 * scale0, float("inf")
    d_cv = min(L_n, 20)
    for mult in (1.5, 2.5, 4.0, 8.0, 16.0):
        B_cand = mult * scale0
        try:
            c1 = fit_bounded_polynomial(mesh_cv, pilot1, d_cv, radius, B_cand)
            err = float(np.max(np.abs(np.polynomial.polynomial.polyval(mesh_cv, c1) - pilot2)))
            if err < best_err - 1.e-9:
                best_err, best_B = err, B_cand
        except Exception:
            continue
    return {"cov_lag": L_n, "depth": L_n, "radius": radius,
            "coefficient_bound": best_B, "spectrum_lower": spec_lower}


def estimate_adaptive(x, *, anchor, max_memory, quadratic, risk):
    """Fully data-driven passive incidence estimator requiring no oracle spectral or polynomial bounds."""
    hp = adaptive_hyperparameters(x, max_memory=max_memory, quadratic=quadratic, risk=risk)
    return estimate(x, anchor=anchor, max_memory=max_memory, quadratic=quadratic, risk=risk, **hp)


def simulation(repetitions=96, sample_sizes=(512, 2048, 8192, 32768), seed=924):
    rng = np.random.default_rng(seed)
    nodes, weights = np.array([.2, .55, .75]), np.array([.08, .10, .12])
    anchor, impact, friction = .2, .5, .1
    covariance = np.fft.ifft(model_spectrum(nodes, weights, anchor, impact)).real[:500]
    true_weight = quadratic_weight(covariance, nodes, friction, 1., .1)
    truth = float(impact*weights @ true_weight)
    rows = []
    fixed_rows = []
    for n in sample_sizes:
        estimates = []
        fixed_estimates = []
        for _ in range(repetitions):
            x = synthetic_observations(nodes, weights, anchor, impact, n, rng)
            estimates.append(estimate_adaptive(
                x, anchor=anchor, max_memory=.8, quadratic=friction, risk=1.,
            ))
            fixed_estimates.append(estimate(
                x, anchor=anchor, max_memory=.8, quadratic=friction, risk=1.,
                cov_lag=math.ceil(2*math.log(n)), depth=math.ceil(math.log(n))+4,
                radius=1.04, coefficient_bound=4., spectrum_lower=.3,
            ))
        errors = np.asarray(estimates) - truth
        fixed_errors = np.asarray(fixed_estimates) - truth
        rows.append({"prices": n, "rmse": float(np.sqrt(np.mean(errors**2))),
                     "bias": float(np.mean(errors))})
        fixed_rows.append({"prices": n, "rmse": float(np.sqrt(np.mean(fixed_errors**2))),
                           "bias": float(np.mean(fixed_errors))})
    slope = np.polyfit(np.log(sample_sizes), np.log([r["rmse"] for r in rows]), 1)[0]
    tail_ratio = float(rows[-2]["rmse"] / rows[-1]["rmse"]) if len(rows) >= 2 else float("nan")
    return {"seed": seed, "repetitions_per_size": repetitions, "truth": truth,
            "rows": rows, "log_rmse_slope": float(slope),
            "tail_4x_rmse_ratio": tail_ratio,
            "fixed_2logn_oracle_baseline_rows": fixed_rows}


if __name__ == "__main__":
    print(json.dumps(simulation(), indent=2))

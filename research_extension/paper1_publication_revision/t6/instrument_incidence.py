"""Synthetic incidence checks and a scenario using archived P1M coefficients.

This script does not fit or rerun an empirical test. Its only empirical input is
the committed P1M primary parameter vector. It prints a fresh diagnostic JSON.
"""

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.signal import lfilter
from scipy.special import eval_legendre, ndtri, roots_jacobi, roots_legendre


def ar1_filter_moments(memory, persistence, variance, h=1):
    """Variance of the normalized filter and variance of an h-step change."""
    if not 0 <= memory < 1 or not -1 < persistence < 1 or variance <= 0 or h < 1:
        raise ValueError("Invalid stationary AR(1) filter parameters")
    filtered_variance = (
        variance * (1 - memory) / (1 + memory)
        * (1 + memory * persistence) / (1 - memory * persistence)
    )
    if h == 1:
        change_variance = (
            2 * filtered_variance * (1 - memory) * (1 - persistence)
            / (1 + memory * persistence)
        )
    else:
        cross = (1 - memory) * variance / (1 + memory)
        bilateral = (persistence**h + sum(
            memory**j * (persistence ** abs(h - j) + persistence ** (h + j))
            for j in range(1, h + 1)
        ) + (memory**(h + 1) * persistence + memory**(h + 1) * persistence**(2*h + 1))
            / (1 - memory * persistence))
        change_variance = 2 * (filtered_variance - cross * bilateral)
    return filtered_variance, change_variance


def optimal_activity(variance, change_variance, *, alpha=1.0, risk=1.0,
                     quadratic=0.0, tax=0.0, cap=math.inf, h=1, decay=1.0):
    """Optimal nonnegative response scale under the stated per-date objective."""
    if (variance <= 0 or change_variance <= 0 or alpha <= 0 or risk <= 0
            or quadratic < 0 or tax < 0 or cap < 0 or h < 1 or not 0 <= decay <= 1):
        raise ValueError("Invalid trading problem")
    gain = alpha * variance * sum(decay**j for j in range(h)) / h
    turnover = math.sqrt(2 * change_variance / math.pi) / h
    curvature = risk * variance + quadratic * change_variance / h
    return min(cap / turnover, max(0.0, (gain - tax * turnover) / curvature))


def quadratic_coefficients(persistence, risk, quadratic, depth):
    """Taylor coefficients for the h=1 quadratic-cost incidence under AR(1)."""
    adjustment = 2 * quadratic * (1 - np.asarray(persistence))
    intercept = risk + adjustment
    ratio = (adjustment - risk * persistence) / intercept
    return (adjustment / intercept)[..., None] * ratio[..., None] ** np.arange(depth)


def quadrature_pair(k):
    gauss, weights = roots_legendre(k)
    interior, _ = roots_jacobi(k - 1, 0, 1)
    radau = np.r_[-1., interior]
    radau_weights = np.r_[1/k**2, (1-interior)/(2*k**2 * eval_legendre(k-1, interior)**2)]
    return (gauss, weights/2), (radau, radau_weights)


def optimizer_check():
    errors = []
    for r in [.1, .4, .8]:
        for h in [1, 4]:
            v, d = ar1_filter_moments(r, -.25, 1., h)
            for tax, cap in [(0., math.inf), (.3, .15), (4., .15)]:
                q = optimal_activity(v, d, quadratic=.23, tax=tax, cap=cap, h=h, decay=.85)
                volume = math.sqrt(2 * d / math.pi) / h
                gain = v * np.mean(.85 ** np.arange(h))
                curvature = v + .23 * d / h
                limit = min(2., cap / volume)
                numerical = minimize_scalar(
                    lambda x: .5 * curvature * x*x - (gain - tax*volume)*x,
                    method="bounded", bounds=(0., limit), options={"xatol": 1.e-12},
                )
                errors.append(abs(q - numerical.x))
    return max(errors)


def smooth_simulation():
    rng = np.random.default_rng(712)
    persistence = .35
    quadratic = .2
    nodes, weights = np.array([.25, .6, .8]), np.array([.12, .18, .26])
    truth = weights @ np.sum(
        quadratic_coefficients(persistence, 1., quadratic, 80) * nodes[:, None]**np.arange(80), axis=1,
    )
    rows = []
    samples = np.array([256, 1024, 4096, 16384])
    for n in samples:
        x = lfilter([1.], [1., -persistence], rng.normal(size=(320, n+128)), axis=1)[:, 128:]
        fitted = np.clip(
            np.sum(x[:, 1:] * x[:, :-1], axis=1) / np.sum(x[:, :-1]**2, axis=1),
            -.9, .9,
        )
        depth = math.ceil(math.log(n) / (2 * math.log(1/.8))) + 4
        taps = weights @ (nodes[:, None]**np.arange(depth))
        noise = rng.normal(scale=.25/np.sqrt(n), size=(len(x), depth))
        estimated = np.sum(quadratic_coefficients(fitted, 1., quadratic, depth) * (taps + noise), axis=1)
        rows.append({"n": int(n), "rmse": float(np.sqrt(np.mean((estimated-truth)**2)))})
    slope = np.polyfit(np.log(samples), np.log([x["rmse"] for x in rows]), 1)[0]
    return {"repetitions": 320, "rows": rows, "rmse_slope": float(slope)}


def kink_checks():
    threshold = .5
    spreads = np.array([.01, .005, .0025, .00125])
    all_rows = {}
    for k in [2, 3]:
        gauss, radau = quadrature_pair(k)
        shift = (1 + max(gauss[0]))/2
        rows = []
        for spread in spreads:
            analogues = []
            for nodes, weights in (gauss, radau):
                memories = threshold - spread * (nodes + shift)
                g = np.minimum(1., np.sqrt((1+memories)/(1+threshold))) / (1-memories)
                budget = weights @ g
                analogues.append((budget, memories, weights))
            left, right = analogues
            # Compute the tap differences from centered moments to avoid
            # cancellation of both measures' common lower moments.
            first = 2*k-1
            depth = 40
            center = threshold - spread*shift
            centered = np.array([
                gauss[1] @ gauss[0]**j - radau[1] @ radau[0]**j
                for j in range(depth)
            ])
            gap = np.array([
                sum(math.comb(m, j) * center**(m-j) * (-spread)**j * centered[j]
                    for j in range(first, m+1))
                for m in range(first, depth)
            ])
            # Exact equal-error likelihood rule for this direct Gaussian tap
            # experiment, with unit per-tap variance.
            repetitions = math.ceil((2*ndtri(.75)/np.linalg.norm(gap))**2)
            rows.append({"spread": float(spread), "budget_gap": float(abs(right[0]-left[0])),
                         "first_tap_gap": float(abs(gap[0])), "testing_repetitions": repetitions,
                         "gauss_exits": int(sum(left[1] >= threshold)),
                         "radau_exits": int(sum(right[1] >= threshold))})
        all_rows[str(k)] = {
            "rows": rows,
            "budget_slope": float(np.polyfit(np.log(spreads), np.log([x["budget_gap"] for x in rows]), 1)[0]),
            "tap_slope": float(np.polyfit(np.log(spreads), np.log([x["first_tap_gap"] for x in rows]), 1)[0]),
            "testing_slope": float(np.polyfit(np.log(spreads), [math.log(x["testing_repetitions"]) for x in rows], 1)[0]),
        }
    return all_rows


def taiwan_scenario(path):
    theta = json.loads(path.read_text())["runs"]["primary"]["theta"]
    normalized_tax = .1
    cases = []
    for name, r, w in zip(("Foreign", "Trust"), theta["r"][:2], theta["w"][:2]):
        share = min(1., normalized_tax * math.sqrt(1+r))
        cases.append({"class": name, "attenuation": share,
                      "feedback_reduction": theta["kappa"] * w * share / (1-r)})
    return {"normalized_tax": normalized_tax, "rows": cases,
            "feedback_reduction": sum(x["feedback_reduction"] for x in cases)}


def main():
    root = Path(__file__).resolve().parents[3]
    result = {
        "optimizer_max_abs_difference": optimizer_check(),
        "smooth": smooth_simulation(),
        "kink": kink_checks(),
        "taiwan_scenario": taiwan_scenario(root / "ceiling_suite/p1_empirics/results/p1m_results.json"),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

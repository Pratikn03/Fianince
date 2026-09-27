"""Inference regressions: independent episodes, terminal timing, and honest pivots."""
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import t as student_t

from research_extension.mm_revision.decisions import DecisionLabel
from research_extension.mm_revision.inference.audited_terminal import (
    construct_audited_regressors,
    fit_audited_terminal_regression,
)
from studies.audited_constraints.src.inference import (
    reconstruct_terminal,
    terminal_interval,
)
from studies.audited_constraints.src.linear import simulate_linear


@pytest.mark.parametrize("function", [construct_audited_regressors, fit_audited_terminal_regression])
@pytest.mark.parametrize("path", [np.zeros(20), np.arange(20.0)])
def test_single_trajectory_cannot_issue_an_exact_terminal_pivot(function, path):
    with pytest.raises(ValueError, match="independent.*episodes|episode.*matrix"):
        function(path, [.5])


def test_terminal_row_has_intercept_and_only_preterminal_memory():
    prices = np.array([[2., 3., 5., 7.], [4., 8., 16., 32.]])
    X, y = construct_audited_regressors(prices, [.5, 1.])
    np.testing.assert_array_equal(X, [[1., 5., 2., 3.], [1., 16., 5., 8.]])
    np.testing.assert_array_equal(y, [7., 32.])
    changed = prices.copy()
    changed[:, -1] += 1000
    XX, yy = construct_audited_regressors(changed, [.5, 1.])
    np.testing.assert_array_equal(XX, X)
    np.testing.assert_array_equal(yy, y + 1000)
    y[:] = -1
    np.testing.assert_array_equal(prices[:, -1], [7., 32.])


@pytest.mark.parametrize("rates", [[], .5, [[.5]], [0.], [-.1], [1.01], [np.nan], [np.inf]])
def test_invalid_rates_rejected_before_reconstruction(rates):
    with pytest.raises(ValueError, match="rates"):
        construct_audited_regressors(np.ones((12, 5)), rates)


@pytest.mark.parametrize("prices", [
    np.empty((0, 4)), np.ones((12, 2)), np.ones((12, 4, 1)),
    np.full((12, 4), np.nan), np.full((12, 4), np.inf),
])
def test_invalid_episode_matrix_rejected(prices):
    with pytest.raises(ValueError, match="episode.*matrix"):
        construct_audited_regressors(prices, [.5])


@pytest.mark.parametrize("alpha", [0., 1., -.1, np.nan, np.inf, [.05]])
def test_invalid_confidence_level_rejected(alpha):
    prices = np.random.default_rng(6).normal(size=(12, 5))
    with pytest.raises(ValueError, match="alpha"):
        fit_audited_terminal_regression(prices, [.5], alpha)


@pytest.mark.parametrize("noise_model", ["student_t", "heteroskedastic", "sensor_noise", "unknown", None])
def test_unsupported_noise_cannot_use_gaussian_student_reference(noise_model):
    prices = np.random.default_rng(6).normal(size=(12, 5))
    with pytest.raises(ValueError, match="noise_model"):
        fit_audited_terminal_regression(prices, [.5], noise_model=noise_model)


@pytest.mark.parametrize("prices,rates", [
    (np.zeros((20, 8)), [.5]),
    (np.ones((20, 8)), [.5]),
    (np.tile(np.arange(8.), (20, 1)), [.5]),
    (np.random.default_rng(4).normal(size=(20, 8)), [.5, .5]),
    (np.random.default_rng(4).normal(size=(20, 3)), [.5, .1]),
    (np.random.default_rng(4).normal(size=(3, 8)), [.5]),
    (np.random.default_rng(4).normal(size=(2, 8)), [.5]),
])
def test_unidentified_or_exhausted_design_abstains_with_unbounded_interval(prices, rates):
    result = fit_audited_terminal_regression(prices, rates)
    assert result["status"] == "invalid_design"
    assert result["decision"] == DecisionLabel.ABSTAIN
    assert not result["is_definite"] and not result["is_conflict"]
    assert result["S_lower"] == -np.inf and result["S_upper"] == np.inf
    assert np.isnan(result["S_hat"]) and result["se_S"] == np.inf
    assert result["reference_distribution"] is None


@pytest.mark.parametrize("q,label", [(.5, DecisionLabel.STABLE), (.8, DecisionLabel.UNSTABLE), (.6, DecisionLabel.ABSTAIN)])
def test_intercept_excluded_from_gain_and_legacy_slope_fields(q, label):
    prefix = np.random.default_rng(12).normal(size=(80, 2))
    # At T=3 and eta=.5, memory at T-1 is .5*x_1, not .5*x_2.
    y = 5. + .4 * prefix[:, 1] + q * .5 * prefix[:, 0]
    result = fit_audited_terminal_regression(np.column_stack([prefix, y]), [.5])
    assert result["intercept_hat"] == pytest.approx(5.)
    assert result["a_hat"] == pytest.approx(.4)
    assert result["q_hat"] == pytest.approx([q])
    assert result["gamma_hat"] == pytest.approx([.4, q])
    assert result["coefficient_estimates"] == pytest.approx([5., .4, q])
    assert result["S_hat"] == pytest.approx(.4 + q)
    assert result["decision"] == label
    assert result["df"] == 77
    assert result["S_lower"] < result["S_hat"] < result["S_upper"]


def test_gaussian_terminal_noise_matches_independent_svd_student_reference():
    rng = np.random.default_rng(718)
    prefix = rng.normal(size=(60, 2))
    X = np.column_stack([np.ones(60), prefix[:, 1], .5 * prefix[:, 0]])
    y = X @ [1.25, .4, .3] + rng.normal(0, .2, 60)
    # Independent SVD reference (the primary inference implementation uses QR).
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    beta = Vt.T @ ((U.T @ y) / s)
    sigma = np.linalg.norm(y - X @ beta) / np.sqrt(57)
    se = sigma * np.linalg.norm((Vt @ [0., 1., 1.]) / s)
    estimate = beta[1:].sum()
    radius = student_t.ppf(.975, 57) * se + 1e-12
    result = fit_audited_terminal_regression(
        np.column_stack([prefix, y]), [.5], noise_model="iid_gaussian",
    )
    assert result["status"] == "ok"
    assert result["reference_distribution"] == "student_t"
    assert result["df"] == 57
    assert result["coefficient_estimates"] == pytest.approx(beta)
    assert result["sigma_hat"] == pytest.approx(sigma)
    assert result["se_S"] == pytest.approx(se)
    assert result["S_lower"] == pytest.approx(estimate - radius)
    assert result["S_upper"] == pytest.approx(estimate + radius)


@pytest.mark.parametrize("rates", [[.5, .002], [.5, .1], [1.], [1e-12]])
def test_noisy_episode_fit_matches_correct_primary_endpoint(rates):
    q = np.full(len(rates), .4 / len(rates))
    prices = simulate_linear(.4, q, rates, .02, 128, 64, 701, "impulse")["prices"]
    X, y = reconstruct_terminal(prices, rates)
    expected = terminal_interval(X, y, alpha=.1)
    result = fit_audited_terminal_regression(prices, rates, alpha=.1)
    actual_X, actual_y = construct_audited_regressors(prices, rates)
    np.testing.assert_array_equal(actual_X, X)
    np.testing.assert_array_equal(actual_y, y)
    assert result["df"] == 128 - len(rates) - 2
    for actual_key, expected_key in [("S_hat", "estimate"), ("se_S", "se"), ("S_lower", "lower"), ("S_upper", "upper")]:
        assert result[actual_key] == pytest.approx(expected[expected_key], rel=1e-12)
    assert result["coefficient_estimates"] == pytest.approx(expected["coefficient_estimates"])
    assert result["condition_number_scaled"] == pytest.approx(expected["condition_number_scaled"])
    labels = {"stable": DecisionLabel.STABLE, "unstable": DecisionLabel.UNSTABLE, "inconclusive": DecisionLabel.ABSTAIN}
    assert result["decision"] == labels[expected["label"]]


def test_archived_public_paths_reproduce_primary_interval_without_rewriting_outputs():
    root = Path(__file__).resolve().parents[2]
    path = root / "studies/audited_constraints/data/linear_public_0_impulse.npz"
    with np.load(path) as data:
        prices, rates = data["prices"], data["rates"]
    expected = terminal_interval(*reconstruct_terminal(prices, rates))
    result = fit_audited_terminal_regression(prices, rates)
    assert result["S_hat"] == pytest.approx(expected["estimate"], abs=1e-13)
    assert result["S_lower"] == pytest.approx(expected["lower"], abs=1e-13)
    assert result["S_upper"] == pytest.approx(expected["upper"], abs=1e-13)


def test_finite_but_overflowing_input_fails_closed():
    prices = np.random.default_rng(22).uniform(.5, 1., size=(20, 4)) * 1e308
    with np.errstate(over="raise", invalid="raise"):
        result = fit_audited_terminal_regression(prices, [.5])
    assert result["status"] == "numerical_failure"
    assert result["decision"] == DecisionLabel.ABSTAIN
    assert result["S_lower"] == -np.inf and result["S_upper"] == np.inf
    assert not result["is_definite"]
    assert result["reference_distribution"] is None

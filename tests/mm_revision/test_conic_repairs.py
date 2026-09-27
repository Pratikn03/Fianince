"""Regressions for calibration and deliberately uncertified numerical endpoints."""
import numpy as np
import pytest
from scipy.optimize import linprog
from scipy.stats import chi2, f

from research_extension.mm_revision.decisions import DecisionLabel
from research_extension.mm_revision.inference import conic_certificate as conic


def panel():
    return dict(beta_hat=np.array([1., .4, .16]), covariance=np.eye(3) * 1e-8,
                df=30, eta_floor=1., bins=1)


@pytest.mark.parametrize("fit", [conic.fit_conic_certificate, conic.fit_box_lp])
@pytest.mark.parametrize("covariance", [np.zeros((3, 3)), np.diag([1., 0., 1.]),
    np.diag([1., -1., 1.]), np.array([[1., .2, 0.], [0., 1., 0.], [0., 0., 1.]]),
    np.diag([1., np.nan, 1.]), np.diag([1., np.inf, 1.]), np.eye(2)])
def test_invalid_covariance_rejected_without_ridge(fit, covariance):
    args = panel()
    args['covariance'] = covariance
    with pytest.raises(ValueError):
        fit(**args)


@pytest.mark.parametrize("field,value", [
    ('beta_hat', [1., .4]), ('beta_hat', [[1., .4, .16]]),
    ('beta_hat', [1., np.nan, .16]), ('alpha', 0.), ('alpha', 1.),
    ('alpha', np.nan), ('eta_floor', 0.), ('eta_floor', 1.1),
    ('eta_floor', np.nan), ('bins', 0), ('bins', 1.5), ('bins', True),
    ('df', 2), ('df', 3.5), ('df', np.inf), ('a_bar', -1.), ('a_bar', np.inf)])
@pytest.mark.parametrize("fit", [conic.fit_conic_certificate, conic.fit_box_lp])
def test_invalid_inputs_rejected(fit, field, value):
    args = panel()
    args[field] = value
    with pytest.raises(ValueError):
        fit(**args)


@pytest.mark.parametrize('limit', [0, -1, 1.5, True])
def test_invalid_solve_budget_rejected(limit):
    with pytest.raises(ValueError):
        conic.fit_conic_certificate(**panel(), max_cuts=limit)


@pytest.mark.parametrize('fit', [conic.fit_conic_certificate, conic.fit_box_lp])
def test_calibration_known_and_estimated_and_unknown_mode(fit):
    args = panel()
    estimated = fit(**args)
    known = fit(**args, covariance_mode='known')
    assert estimated['covariance_mode'] == 'estimated'
    assert estimated['radius_distribution'] == 'F'
    assert estimated['radius_squared'] == pytest.approx(90 / 28 * f.ppf(.95, 3, 28))
    assert known['covariance_mode'] == 'known'
    assert known['radius_distribution'] == 'chi2'
    assert known['radius_squared'] == pytest.approx(chi2.ppf(.95, 3))
    assert estimated['radius_squared'] > known['radius_squared']
    assert fit(**{**args, 'df': None}, covariance_mode='known')['radius_squared'] == known['radius_squared']
    with pytest.raises(ValueError):
        fit(**args, covariance_mode='diagonal')


@pytest.mark.parametrize('fit', [conic.fit_conic_certificate, conic.fit_box_lp])
def test_decisive_numerical_interval_cannot_issue_certificate(fit):
    result = fit(**panel())
    assert result['S_upper'] < 1.
    assert result['numerical_decision'] == DecisionLabel.STABLE
    assert result['decision'] == DecisionLabel.ABSTAIN
    assert result['certified'] is False
    assert result['certification_status'] == 'unverified_constraint_rounding'
    assert result['status'] == 'numerical_candidate'
    assert not result['is_definite']


def literal_cut_lp(sense, max_cuts):
    # Base interval [0,2]; radius-one ellipsoid (x-1)^2/.25 <= 1
    # adds x >= .5 for min and x <= 1.5 for max. Exact optima .5, 1.5.
    solve = getattr(conic, '_solve_with_cuts', None)
    assert callable(solve), 'cut solver must retain the solved matrices and duals'
    return solve(c=np.array([sense]), A_ub=np.array([[1.]]), b_ub=np.array([2.]),
                 A_eq=None, b_eq=None, bounds=[(0., 2.)],
                 beta_hat=np.array([1.]), covariance=np.array([[.25]]),
                 k2=1., beta_indices=np.array([0]), max_cuts=max_cuts)


@pytest.mark.parametrize('sense,expected', [(1., .5), (-1., -1.5)])
def test_both_duals_include_active_added_cut(sense, expected):
    result = literal_cut_lp(sense, 2)
    assert result['termination_status'] == 'converged'
    assert result['lp_solves'] == 2
    assert result['cuts'] == 1
    assert result['dual_lower_bound'] == pytest.approx(expected, abs=1e-13)
    assert result['A_ub'].shape == (2, 1)
    assert len(result['result'].ineqlin.marginals) == 2
    assert abs(result['result'].ineqlin.marginals[-1]) > 0
    # Omitting the cut loses its active multiplier and gives the base-box bound.
    assert result['dual_lower_bound'] > (0. if sense > 0 else -2.)


def test_budget_exhaustion_does_not_claim_unsolved_cut_or_convergence():
    result = literal_cut_lp(1., 1)
    assert result['result'].success
    assert result['termination_status'] == 'max_cuts_reached'
    assert result['lp_solves'] == 1
    assert result['cuts'] == 0
    assert result['A_ub'].shape == (1, 1)
    assert result['ellipsoid_violation'] == pytest.approx(3.)
    assert result['dual_lower_bound'] == pytest.approx(0.)


def test_numeric_dual_repairs_stationarity_residual_for_both_senses():
    # Literal LP .5 <= x <= 1.5, and x+y=2, in the box [0,2]^2.
    A = np.array([[-1., 0.], [1., 0.]])
    b = np.array([-.5, 1.5])
    eq = np.array([[1., 1.]])
    for sense, optimum in [(1., .5), (-1., -1.5)]:
        c = np.array([sense, 0.])
        res = linprog(c, A_ub=A, b_ub=b, A_eq=eq, b_eq=[2.], bounds=[(0., 2.)]*2)
        y = -res.ineqlin.marginals + np.array([.01, -.02])
        lower = conic.residual_corrected_dual_lower_bound(
            c, A, b, eq, np.array([2.]), [(0., 2.)]*2, y, np.array([.03]))
        assert lower <= optimum
        assert lower > optimum - .2


def test_conic_reports_each_cut_termination_separately_from_solver_success():
    args = dict(beta_hat=np.array([1., .4, .2]), covariance=np.eye(3)*1e-3,
                df=30, eta_floor=.1, bins=2)
    result = conic.fit_conic_certificate(**args, max_cuts=1)
    assert result['solver_success']
    assert 'max_cuts_reached' in (result['termination_min'], result['termination_max'])
    assert result['lp_solves_min'] == result['lp_solves_max'] == 1
    assert result['cuts_min'] == result['cuts_max'] == 0
    assert result['S_lower'] == result['dual_lower_bound']
    assert result['S_upper'] == -result['dual_lower_bound_negative_objective']
    assert result['endpoint_bound_status'] == 'numerically_corrected_dual'


@pytest.mark.parametrize('mode', ['known', 'estimated'])
def test_box_comparison_uses_identical_calibration(mode):
    args = panel()
    result = conic.fit_conic_certificate(**args, covariance_mode=mode)
    box = conic.fit_box_lp(**args, covariance_mode=mode)
    assert result['box_lower'] == pytest.approx(box['S_lower'])
    assert result['box_upper'] == pytest.approx(box['S_upper'])
    assert result['box_comparison_status'] == 'computed_numerically'


def test_no_weak_dominance_claim_when_no_comparison_was_computed():
    args = panel()
    args['covariance'] = np.eye(3)
    result = conic.fit_conic_certificate(**args)
    assert result['status'] == 'insufficient_initial_impact'
    assert result['weak_dominance_over_box'] is None
    assert result['box_comparison_status'] == 'not_computed'
    assert result['certified'] is False


@pytest.mark.parametrize('p,R,alpha', [(0, 20, .05), (2.5, 20, .05),
    (3, 4, .05), (3, 30.5, .05), (3, 30, 0.), (3, 30, np.nan)])
def test_hotelling_rejects_invalid_calibration(p, R, alpha):
    with pytest.raises(ValueError):
        conic.hotelling_f_critical_value(p, R, alpha)

"""Regression checks for response alignment and honest interval summaries."""
import numpy as np
import pytest

from research_extension.mm_revision import decisions
from research_extension.mm_revision.studies import synthetic_recovery as study


def test_panel_regresses_post_probe_response_not_initial_state(monkeypatch):
    # With a=.4, eta=.5, Q=.42, kappa=1 the first coefficients are
    # 1, .4, .4**2 + .5*.42 = .37. Including x0 shifts these by one.
    observed = {}
    original = study.response_intervals

    def record_real_regression(*args, **kwargs):
        result = original(*args, **kwargs)
        observed.update(result)
        return result

    monkeypatch.setattr(study, 'response_intervals', record_real_regression)
    study.run_single_synthetic_panel(.82, .5, H=4, n_episodes=12,
                                     noise_sigma=0, seed=41, eta_floor=.5)
    np.testing.assert_allclose(observed['estimate'][:3], [1., .4, .37], atol=1e-12)
    assert observed['estimate'].shape == (5,)


@pytest.mark.parametrize('lo,hi,expected', [
    (0., np.inf, True), (np.nan, np.nan, False), (None, None, False),
    (np.nan, 2., False), (0., None, False), (2., 1., False),
    (.7, .9, True), (.9, 1., False),
])
def test_missing_or_invalid_endpoints_never_count_as_coverage(lo, hi, expected):
    assert callable(getattr(decisions, 'interval_contains', None)), 'explicit interval validation required'
    assert decisions.interval_contains(lo, hi, .82) is expected


def test_unbounded_width_is_not_reported_as_zero():
    assert callable(getattr(decisions, 'summarize_interval_widths', None))
    out = decisions.summarize_interval_widths([
        {'lower': 0., 'upper': np.inf}, {'lower': None, 'upper': None}])
    assert out['finite_intervals'] == 0
    assert out['unbounded_intervals'] == 1
    assert out['invalid_intervals'] == 1
    assert out['mean_interval_width'] is None
    assert out['finite_mean_interval_width'] is None


def test_finite_width_denominator_is_explicit():
    assert callable(getattr(decisions, 'summarize_interval_widths', None))
    out = decisions.summarize_interval_widths([
        {'lower': 1., 'upper': 3.}, {'lower': 0., 'upper': 4.},
        {'lower': 0., 'upper': np.inf}])
    assert out['finite_intervals'] == 2
    assert out['finite_mean_interval_width'] == 3.
    assert out['mean_interval_width'] is None


@pytest.mark.parametrize('lo,hi', [(np.nan, 2.), (0., np.nan), (None, None)])
def test_invalid_interval_is_conflict_not_abstention(lo, hi):
    assert decisions.classify_interval(lo, hi) == decisions.DecisionLabel.CONFLICT


def test_fitter_exception_is_retained_not_counted_as_coverage(monkeypatch):
    def failed_fit(*args, **kwargs):
        raise RuntimeError('deliberate fitting failure')
    monkeypatch.setattr(study, 'fit_covariance_output_error', failed_fit)
    out = study.run_single_synthetic_panel(.82, .5, H=4, n_episodes=12,
                                           noise_sigma=.1, seed=42)
    assert not out['output_error']['is_covered']
    assert out['output_error']['is_conflict']
    assert out['output_error']['error'] == 'RuntimeError: deliberate fitting failure'


def test_adapter_preserves_genuine_unbounded_interval():
    from research_extension.mm_revision.inference.recurrence_adapter import fit_recurrence_interval
    out = fit_recurrence_interval(np.array([-1., -.4, -.2]), np.array([1., .4, .2]))
    assert out['S_lower'] == 0.
    assert out['S_upper'] == np.inf


def test_panel_retains_observed_inputs_separate_from_oracle():
    out = study.run_single_synthetic_panel(.82, .5, H=4, n_episodes=12,
                                           noise_sigma=.1, seed=42)
    assert 'observation' in out and 'oracle_diagnostics' in out
    assert np.asarray(out['observation']['covariance']).shape == (5, 5)
    assert out['observation']['df'] == 10
    assert out['observation']['price_indices'] == 'x1..x(H+1)'
    assert out['seed'] == 42


def test_unavailable_fit_fallback_is_not_successful_interval_coverage(monkeypatch):
    from research_extension.mm_revision.inference.covariance_output_error import fit_covariance_output_error
    unavailable = fit_covariance_output_error(1.2*.35**np.arange(13), np.eye(13)*1e-5)
    assert unavailable.ci_type == 'unavailable'
    monkeypatch.setattr(study, 'fit_covariance_output_error', lambda *a, **k: unavailable)
    out = study.run_single_synthetic_panel(.82, .5, H=4, n_episodes=12,
                                           noise_sigma=.1, seed=42)['output_error']
    assert out['lower'] is None and out['upper'] is None
    assert not out['is_covered']
    assert out['inference_available'] is False


def test_nonconverged_point_fit_is_unavailable(monkeypatch):
    import observable
    monkeypatch.setattr(observable, 'recurrence_point', lambda *a, **k:
                        {'status': 'solver_failure', 'gain': .7})
    out = study.run_single_synthetic_panel(.82, .5, H=4, n_episodes=12, seed=42)['naive_point_fit']
    assert not out['is_covered'] and not out['is_issued']
    assert out['lower'] is None and out['upper'] is None
    assert 'solver_failure' in out['error']
    assert out['diagnostics']['status'] == 'solver_failure'

"""Regression tests for local, asymptotic output-error interval repairs."""
from types import SimpleNamespace
from collections import Counter
from contextlib import contextmanager
import io
import json
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from research_extension.mm_revision.inference import covariance_output_error as oe
from research_extension.mm_revision.studies import output_error_misspecification_diagnostic as diagnostic


def analytic_response(theta, horizon=12):
    """Independent scalar recurrence and exact parameter sensitivities."""
    a, eta, q, kappa = theta
    x, y = 1.0, 0.0
    dx, dy = np.zeros(4), np.zeros(4)
    beta, jac = [], []
    for _ in range(horizon + 1):
        beta.append(kappa * x)
        jac.append(kappa * dx + np.array([0, 0, 0, x]))
        dx, dy = (a * dx + dy + np.array([x, 0, 0, 0]),
                  eta * q * dx + (1 - eta) * dy
                  + np.array([0, q * x - y, eta * x, 0]))
        x, y = a * x + y, eta * q * x + (1 - eta) * y
    return np.asarray(beta), np.asarray(jac)


def profile_helper():
    helper = getattr(oe, "_profile_interval", None)
    assert callable(helper), "Profile endpoints need a bracketed, outward solver"
    return helper


@pytest.mark.parametrize("level", [0.8, 0.95, 0.99])
def test_quadratic_profile_never_rounds_crossings_inward(level):
    center, scale = 0.83, 0.0137
    cutoff = stats.chi2.ppf(level, 1)
    interval, status = profile_helper()(
        lambda s: ((s - center) / scale) ** 2,
        center, cutoff, 0.0, 1.495, initial_step=0.007,
    )
    radius = scale * np.sqrt(cutoff)
    assert interval[0] <= center - radius
    assert interval[1] >= center + radius
    np.testing.assert_allclose(interval, [center - radius, center + radius], atol=2e-7, rtol=0)
    assert status == ("crossing", "crossing")


def test_no_profile_crossing_returns_actual_parameter_bounds():
    visited = []

    def flat_profile(s):
        visited.append(s)
        return 0.0

    interval, status = profile_helper()(flat_profile, 0.8, 3.84, 0.0, 1.195, initial_step=0.01)
    assert interval == (0.0, 1.195)
    assert status == ("parameter_bound", "parameter_bound")
    assert min(visited) >= 0 and max(visited) <= 1.195


def test_failed_profile_evaluation_cannot_be_treated_as_rejection():
    interval, status = profile_helper()(
        lambda s: 0.0 if s == 0.8 else np.nan,
        0.8, 3.84, 0.0, 1.495, initial_step=0.01,
    )
    assert interval == (0.0, 1.495)
    assert status == ("unavailable", "unavailable")


def test_unavailable_lower_profile_skips_unnecessary_upper_search():
    visited = []

    def profile(s):
        visited.append(s)
        return 0.0 if s == 0.8 else np.nan

    interval, status = profile_helper()(profile, 0.8, 3.84, 0.0, 1.495, initial_step=0.01)
    assert interval == (0.0, 1.495)
    assert status == ("unavailable", "unavailable")
    # Once the lower search makes the entire profile unavailable, further
    # costly nuisance optimization cannot alter either endpoint or status.
    assert len(visited) == 2
    assert visited[0] == 0.8 and visited[1] < 0.8


@pytest.mark.parametrize("reg_lambda", [0.0, 2000.0])
def test_real_fit_sandwich_matches_independent_analytic_derivatives(reg_lambda):
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    # Deliberate model residuals rule out residual-scaled inverse information.
    beta += np.array([0, .001, -.003, .004, -.002, .003, -.004, .002, -.003, .004, -.002, .003, -.003])
    sd = np.linspace(0.0003, 0.001, len(beta))
    cov = np.outer(sd, sd) * 0.4 ** np.abs(np.subtract.outer(np.arange(len(beta)), np.arange(len(beta))))
    result = oe.fit_covariance_output_error(beta, cov, reg_lambda=reg_lambda,
                                             compute_profile=False, confidence_level=0.8)
    assert result.diagnostics.optimizer_success
    _, jac = analytic_response([result.a, result.eta, result.Q, result.kappa])
    weight = np.linalg.inv(cov + 1e-6 * np.trace(cov) / len(cov) * np.eye(len(cov)))
    # The objective is r'Wr + lambda(a^2+Q^2): half its GN Hessian is A.
    bread = np.linalg.inv(jac.T @ weight @ jac + reg_lambda * np.diag([1, 0, 1, 0]))
    contrast = np.array([1, 0, 1, 0])
    variance = contrast @ bread @ jac.T @ weight @ cov @ weight @ jac @ bread.T @ contrast
    assert result.se_S == pytest.approx(np.sqrt(variance), rel=2e-4)
    radius = stats.norm.ppf(0.9) * np.sqrt(variance)
    np.testing.assert_allclose(result.sandwich_interval,
                               [max(0, result.S_model - radius), min(4.995, result.S_model + radius)], rtol=2e-5)
    assert result.decision_interval == result.sandwich_interval
    assert result.profile_interval is None


def test_small_legitimate_standard_error_is_not_replaced():
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-12, compute_profile=False)
    assert result.diagnostics.optimizer_success
    assert 0 < result.se_S < 1e-4


@pytest.mark.parametrize("bad_cov", [np.eye(3), np.diag([1, 1, 1, -1]),
                                      np.full((4, 4), np.nan),
                                      np.array([[1, .2, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])])
def test_invalid_covariance_is_rejected(bad_cov):
    with pytest.raises(ValueError, match="covariance"):
        oe.fit_covariance_output_error([1, .5, .3, .2], bad_cov, compute_profile=False)


@pytest.mark.parametrize("reg_lambda,q_max", [(0.0, 4.0), (1.0, 0.0)])
def test_singular_identification_abstains_even_with_regularization(reg_lambda, q_max):
    # Q = 0 makes eta unidentifiable; penalization cannot create information.
    beta = 1.2 * 0.35 ** np.arange(13)
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-5,
                                             reg_lambda=reg_lambda, q_max=q_max, compute_profile=True)
    assert result.ci_type == "unavailable"
    assert np.isnan(result.se_S)
    assert result.sandwich_interval is None and result.profile_interval is None
    assert result.decision_interval == (0.0, np.inf)
    assert result.diagnostics.weak_identification
    assert "rank" in result.inference_status


def test_failed_optimizer_cannot_issue_precision(monkeypatch):
    # Inject optimizer failure only; keep response, interval, and diagnostics code real.
    def failed_optimizer(fun, x0, **kwargs):
        return SimpleNamespace(x=np.asarray(x0), fun=fun(x0), success=False,
                               status=1, message="iteration limit", nit=0, nfev=1)

    monkeypatch.setattr(oe, "minimize", failed_optimizer)
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-4)
    assert result.ci_type == "unavailable"
    assert not result.diagnostics.optimizer_success
    assert result.decision_interval == (0.0, np.inf)
    assert np.isnan(result.se_S)


def test_optimizer_numerical_failure_abstains(monkeypatch):
    def numerical_failure(*args, **kwargs):
        raise np.linalg.LinAlgError("numerical optimizer failure")

    monkeypatch.setattr(oe, "minimize", numerical_failure)
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-4)
    assert result.ci_type == "unavailable"
    assert result.decision_interval == (0.0, np.inf)
    assert not result.diagnostics.optimizer_success


def test_nonfinite_optimizer_result_is_not_success(monkeypatch):
    def nonfinite_result(fun, x0, **kwargs):
        return SimpleNamespace(x=np.asarray(x0), fun=np.nan, success=True,
                               status=0, message="nominal success", nit=1, nfev=1)

    monkeypatch.setattr(oe, "minimize", nonfinite_result)
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-4)
    assert not result.diagnostics.optimizer_success
    assert result.ci_type == "unavailable"
    assert result.decision_interval == (0.0, np.inf)


def test_failed_profile_optimizer_keeps_sandwich_but_abstains(monkeypatch):
    real_minimize = oe.minimize

    def fail_nuisance_optimizer(fun, x0, **kwargs):
        if len(x0) == 3:
            raise np.linalg.LinAlgError("numerical nuisance failure")
        return real_minimize(fun, x0, **kwargs)

    monkeypatch.setattr(oe, "minimize", fail_nuisance_optimizer)
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-4, q_max=.6)
    assert result.ci_type == "unavailable"
    assert result.sandwich_interval is not None
    assert result.profile_interval == (0.0, 1.595)
    assert result.profile_status == ("unavailable", "unavailable")
    assert result.decision_interval == (0.0, np.inf)


def test_real_profile_and_sandwich_are_separately_reported():
    beta, _ = analytic_response([0.35, 0.3, 0.4, 1.2])
    result = oe.fit_covariance_output_error(beta, np.eye(len(beta)) * 1e-4,
                                             q_max=0.6, confidence_level=0.8)
    assert result.profile_interval is not None
    assert getattr(result, "sandwich_interval", None) is not None
    assert result.decision_interval == result.profile_interval
    assert 0 <= result.S_lower <= result.S_model <= result.S_upper <= 1.595
    assert "local" in result.inference_status and "asymptotic" in result.inference_status
    assert len(result.profile_status) == 2


@pytest.mark.parametrize("level", [0, 1, np.nan])
def test_invalid_confidence_level_rejected(level):
    with pytest.raises(ValueError, match="confidence_level"):
        oe.fit_covariance_output_error([1, .5, .3, .2], np.eye(4), confidence_level=level, compute_profile=False)


def test_diagnostic_real_h6_two_panels_records_six_attempts_and_separate_coverage(monkeypatch):
    calls = []
    real_fit = diagnostic.fit_covariance_output_error
    real_minimize = oe.minimize

    def record_fit(beta, covariance, **kwargs):
        calls.append((beta.copy(), covariance.copy()))
        if len(calls) == 1:
            # Keep a real fitted sandwich while making this profile unavailable.
            def unavailable_profile(fun, x0, **options):
                if len(x0) == 3:
                    raise np.linalg.LinAlgError("injected nuisance failure")
                return real_minimize(fun, x0, **options)
            with monkeypatch.context() as patch:
                patch.setattr(oe, "minimize", unavailable_profile)
                return real_fit(beta, covariance, **kwargs)
        return real_fit(beta, covariance, **kwargs)

    monkeypatch.setattr(diagnostic, "fit_covariance_output_error", record_fit)
    report = diagnostic.run_output_error_diagnostic(n_panels=2, H=6)
    assert len(calls) == 6  # C1/C3 once, C2/C4 twice each; not eight fits.
    assert report["total_attempted"] == 6
    assert report["seed"] == 20260924 and report["R"] == 1024 and report["H"] == 6
    rows = report["panel_records"]
    assert Counter(r["condition"] for r in rows) == {
        "C1_matched_noiseless": 1, "C2_matched_noisy": 2,
        "C3_misspec_noiseless": 1, "C4_misspec_noisy": 2,
    }
    for row in rows:
        for field in ("se_S", "ci_type", "inference_status", "profile_status", "bound_hits",
                      "optimizer_success", "optimizer_status", "optimizer_message",
                      "profile_interval", "sandwich_interval", "profile_covered", "sandwich_covered"):
            assert field in row
    unavailable = next(r for r in rows if r["condition"] == "C1_matched_noiseless")
    assert unavailable["ci_type"] == "unavailable"
    assert unavailable["primary_covered"] is None and unavailable["profile_covered"] is None
    assert unavailable["fallback_interval"] == [0.0, "Infinity"]
    assert unavailable["fallback_contains_truth"] is True
    assert unavailable["sandwich_available"] and isinstance(unavailable["sandwich_covered"], bool)
    summary = report["summary"]["C1_matched_noiseless"]
    assert summary["attempted_count"] == 1 and summary["available_count"] == 0
    assert summary["coverage_denominator"] == 0 and summary["coverage_pct"] is None
    assert summary["sandwich_coverage_denominator"] == 1
    assert summary["fallback_count"] == 1 and summary["nonconverged_count"] == 0
    assert summary["coverage_kind"] == "deterministic_containment_not_sampling_coverage"
    # Preserve the original interleaved C2/C4 Gaussian draws and known covariance.
    rng = np.random.default_rng(20260924)
    for row in [r for r in rows if r["case_kind"] == "noisy_known_covariance"]:
        condition = row["condition"]
        exact = diagnostic.simulate_impulse_response(.4, [.05] if condition.startswith("C2") else [.2,.02],
                                                     [.42] if condition.startswith("C2") else [.252,.168], 1., 6)
        noise = rng.normal(0, .05 / np.sqrt(1024), 7)
        beta, covariance = calls[row["attempt_index"]]
        np.testing.assert_array_equal(beta, exact + noise)
        np.testing.assert_array_equal(covariance, np.eye(7) * (.05 ** 2 / 1024))
        assert row["covariance_kind"] == "known_gaussian_covariance"
    for condition, summary in report["summary"].items():
        condition_rows = [r for r in rows if r["condition"] == condition]
        valid = [r for r in condition_rows if r["primary_available"]]
        assert summary["coverage_denominator"] == len(valid)
        assert summary["coverage_pct"] == (100 * sum(r["primary_covered"] for r in valid) / len(valid) if valid else None)
        assert all(field in summary for field in ("mean_bias", "rmse", "fit_available_count", "nonconverged_count"))
    json.dumps(report, allow_nan=False)


def test_diagnostic_retains_exceptions_with_zero_valid_denominators(monkeypatch):
    calls = []

    def fail_fit(*args, **kwargs):
        calls.append(1)
        raise RuntimeError("injected fit failure")

    monkeypatch.setattr(diagnostic, "fit_covariance_output_error", fail_fit)
    report = diagnostic.run_output_error_diagnostic(n_panels=2, H=6)
    assert len(calls) == len(report["panel_records"]) == 6
    for row in report["panel_records"]:
        assert row["exception_type"] == "RuntimeError"
        assert row["exception_message"] == "injected fit failure"
        assert row["ci_type"] == "unavailable" and row["se_S"] is None
        assert row["primary_covered"] is None and row["fallback_interval"] is None
    for summary in report["summary"].values():
        assert summary["nonconverged_count"] == summary["exception_count"] == summary["attempted_count"]
        assert summary["available_count"] == summary["fit_available_count"] == 0
        assert summary["coverage_denominator"] == summary["profile_coverage_denominator"] == summary["sandwich_coverage_denominator"] == 0
        assert summary["mean_bias"] is None and summary["rmse"] is None
        assert summary["coverage_pct"] is None
    json.dumps(report, allow_nan=False)


def diagnostic_cli():
    main = getattr(diagnostic, "main", None)
    assert callable(main), "Diagnostic CLI must require an explicit new output path"
    return main


def test_diagnostic_cli_requires_output_and_refuses_existing_before_fitting(monkeypatch):
    def must_not_run(**kwargs):
        pytest.fail("Output guard must execute before any diagnostic fits")

    monkeypatch.setattr(diagnostic, "run_output_error_diagnostic", must_not_run)
    with pytest.raises(SystemExit) as missing:
        diagnostic_cli()([])
    assert missing.value.code == 2
    with pytest.raises(SystemExit) as existing:
        diagnostic_cli()(["--output", str(Path(__file__).resolve())])
    assert existing.value.code == 2


def test_diagnostic_cli_exclusive_creation_without_writing_results(monkeypatch):
    output = Path(__file__).resolve().parent / "unwritten_output_error_fixture.json"
    stream = io.StringIO()
    seen = []

    @contextmanager
    def memory_open(path, mode, **kwargs):
        assert path == output and mode == "x"
        seen.append(path)
        yield stream

    def tiny_report(**kwargs):
        assert kwargs == {"n_panels": 2, "H": 6, "R": 1024, "seed": 20260924}
        return {"summary": {}, "panel_records": [], "total_attempted": 0}

    monkeypatch.setattr(diagnostic, "run_output_error_diagnostic", tiny_report)
    monkeypatch.setattr(Path, "open", memory_open)
    diagnostic_cli()(["--output", str(output), "--n-panels", "2", "--H", "6"])
    assert seen == [output]
    assert json.loads(stream.getvalue())["total_attempted"] == 0
    assert not output.exists()

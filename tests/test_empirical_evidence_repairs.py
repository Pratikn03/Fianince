"""Regression protection for the bounded, offline empirical evidence repairs."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scipy import stats

from research_extension import binance_multi_epoch_study as binance
from research_extension.mm_revision.studies import empirical


ROOT = Path(__file__).resolve().parents[1]
PARAMS = np.array([0.4, 0.2, 0.3, 0.5])


def matrix_response(params, flow):
    """Independent closed-form state transition oracle (no production helper)."""
    a, eta, q, kappa = params
    transition = np.array([[a, 1.0], [eta * q, 1.0 - eta]])
    impulse = np.array([kappa, 0.0])
    return np.array([
        sum((np.linalg.matrix_power(transition, t - j) @ impulse)[0] * flow[j]
            for j in range(t + 1))
        for t in range(len(flow))
    ])


def fixed_optimizer(monkeypatch, *, success=True, invalid=False):
    """Force a known optimizer outcome while exercising the real objective."""
    objectives = []

    def optimize(fun, x0, **kwargs):
        objectives.append(float(fun(PARAMS)))
        return SimpleNamespace(
            x=np.full(4, np.nan) if invalid else PARAMS.copy(),
            fun=objectives[-1], success=success, status=0 if success else 1,
            message="fixture convergence" if success else "iteration limit",
            nit=1, nfev=1,
        )

    monkeypatch.setattr(binance, "minimize", optimize)
    return objectives


def path_fixture():
    flow = np.linspace(-1.0, 2.0, 41)
    # Small outcome variance exposes the previous artificial R² floor at -1.
    prices = 100.0 + np.r_[0.0, np.cumsum(0.01 + 0.001 * np.sin(np.arange(40)))]
    return prices, flow


def panels_fixture():
    rng = np.random.default_rng(712)
    return {
        f"asset-{i}": {
            "closes": (100 * np.exp(np.r_[0, np.cumsum(rng.normal(0, .005, 79))])).tolist(),
            "signed_flow": rng.normal(size=80).tolist(),
            "signed_flow_alignment": "closes",
            "rel_spread_bps": float(i * i + 1),
        }
        for i in range(7)
    }


def test_response_retains_feedback_memory_beyond_fifteen_lags():
    flow = np.r_[2.0, np.zeros(25)]
    response = binance.simulate_model_response(PARAMS, flow)
    np.testing.assert_allclose(response[:4], [1.0, .4, .22, .16], atol=1e-14)
    np.testing.assert_allclose(response, matrix_response(PARAMS, flow), atol=1e-14)


def test_response_can_continue_from_training_state():
    flow = np.array([2., -1., 3., 0., 1.])
    first, state = binance.simulate_model_response(PARAMS, flow[:3], return_state=True)
    second = binance.simulate_model_response(PARAMS, flow[3:], initial_state=state)
    np.testing.assert_allclose(np.r_[first, second], matrix_response(PARAMS, flow))


def test_every_epoch_uses_the_complete_contiguous_training_path(monkeypatch):
    objectives = fixed_optimizer(monkeypatch)
    prices, flow = path_fixture()
    binance.train_single_seed(prices, flow, seed=42, n_epochs=3)
    n_train = 28  # floor(0.70 * 40 transitions), not floor(0.70 * 41 prices).
    expected = np.mean((np.diff(prices)[:n_train] - matrix_response(PARAMS, flow[:n_train]))**2)
    expected += .01 * PARAMS[2]**2
    np.testing.assert_allclose(objectives, [expected] * 3, rtol=1e-12)


def test_validation_carries_state_and_preserves_negative_r2(monkeypatch):
    fixed_optimizer(monkeypatch)
    prices, flow = path_fixture()
    result = binance.train_single_seed(prices, flow, seed=42, n_epochs=1)
    expected = matrix_response(PARAMS, flow[:-1])[28:]
    actual = np.diff(prices)[28:]
    assert result["val_loss_final"] == pytest.approx(np.mean((actual - expected)**2))
    expected_r2 = 1 - np.sum((actual - expected)**2) / np.sum((actual - np.mean(actual))**2)
    assert expected_r2 < -1
    assert result["oos_r2"] == pytest.approx(expected_r2)
    assert result["temporal_split"]["train_transition_indices"] == [0, 28]
    assert result["temporal_split"]["validation_transition_indices"] == [28, 40]


@pytest.mark.parametrize("success,invalid", [(False, False), (True, True)])
def test_invalid_optimizer_result_is_rejected(monkeypatch, success, invalid):
    fixed_optimizer(monkeypatch, success=success, invalid=invalid)
    with pytest.raises((ValueError, RuntimeError), match="(?i)optimizer|finite"):
        binance.train_single_seed(*path_fixture(), seed=42, n_epochs=1)


@pytest.mark.parametrize("ratio", [0.0, 1.0, -0.1, float("nan")])
def test_invalid_temporal_split_is_rejected(ratio):
    with pytest.raises(ValueError, match="train_ratio"):
        binance.train_single_seed(*path_fixture(), seed=42, train_ratio=ratio)


def test_validation_outcomes_cannot_change_fitted_parameters():
    prices, flow = path_fixture()
    altered = prices.copy()
    altered[29:] += np.linspace(5, 100, 12)
    first = binance.train_single_seed(prices, flow, seed=42, n_epochs=2)
    second = binance.train_single_seed(altered, flow, seed=42, n_epochs=2)
    for key in ("a", "eta", "Q", "kappa", "train_loss_final"):
        assert first[key] == second[key]
    assert first["val_loss_final"] != second["val_loss_final"]


def test_period_b_regression_losses_are_explicitly_in_sample():
    result = empirical.evaluate_two_layer_temporal_split(panels_fixture())
    assert result.get("evaluation_type") == "in_sample_explanatory"
    assert result.get("out_of_sample") is False
    assert result["outcome_used_to_fit_slopes"] is True
    assert "paired_loss_evaluation" not in result
    comparison = result["in_sample_loss_comparison"]["F"]
    assert comparison["interpretation"] == "descriptive_nested_model_residual_reduction"
    assert comparison["mean_residual_loss_reduction"] >= -1e-14


def test_failed_structural_fit_never_substitutes_proxy_f(monkeypatch):
    def failed_fit(*args, **kwargs):
        raise ValueError("controlled fit failure")

    monkeypatch.setattr(empirical, "fit_observational_structural_model", failed_fit)
    result = empirical.evaluate_two_layer_temporal_split(panels_fixture())
    assert all(r["S_model"] is None for r in result["records"])
    assert all(r["S_model_status"] == "fit_failed" for r in result["records"])
    assert result["specifications"]["full_model_S_model"]["status"] == "unavailable"
    assert result["in_sample_loss_comparison"]["S_model"]["status"] == "unavailable"


def test_tick_flow_is_not_silently_paired_with_candle_prices():
    panels = panels_fixture()
    for panel in panels.values():
        del panel["signed_flow_alignment"]
    result = empirical.evaluate_two_layer_temporal_split(panels)
    assert all(r["S_model"] is None for r in result["records"])
    assert all(r["S_model_status"] == "unavailable_unaligned_flow" for r in result["records"])
    assert result["n_markets"] == len(panels)


def test_missing_prices_are_reported_as_exclusions():
    panels = panels_fixture()
    panels["invalid"] = {"closes": [1., 0., 2.]}
    result = empirical.evaluate_two_layer_temporal_split(panels)
    assert result["excluded_assets"][0]["symbol"] == "invalid"
    assert result["n_markets"] == 7


@pytest.mark.parametrize("X,y", [
    ([[1., 1.], [1., 1.], [1., 1.]], [1., 2., 4.]),
    ([[1., 1.], [1., 2.]], [1., 2.]),
    ([[1., 1.], [1., float("nan")], [1., 3.]], [1., 2., 4.]),
])
def test_invalid_ols_cannot_emit_valid_looking_statistics(X, y):
    with pytest.raises(ValueError):
        empirical.run_ols_regression(X, y)


def test_serialized_rows_reproduce_their_actual_bivariate_not_legacy_claim():
    rows = json.loads((ROOT / "research_extension/outputs/empirical_results.json").read_text())["asset_table"]
    x = np.array([r["s_hat_A"] for r in rows])
    y = np.array([r["rho1_B"] for r in rows])
    result = empirical.run_ols_regression(np.column_stack([np.ones(len(x)), x]), y)
    independent = stats.linregress(x, y)
    assert result["t_stats"][1] == pytest.approx(1.9015882671447775, abs=1e-12)
    assert result["p_values"][1] == pytest.approx(0.09373829283337161, abs=1e-12)
    assert result["r2"] == pytest.approx(0.3112970151374501, abs=1e-12)
    assert result["beta"][1] == pytest.approx(independent.slope)
    assert result["p_values"][1] == pytest.approx(independent.pvalue)


def test_cached_price_proxy_uses_only_period_a():
    panels = panels_fixture()
    changed = copy.deepcopy(panels)
    for d in changed.values():
        d["closes"][56:] = (np.asarray(d["closes"][56:]) * np.linspace(1.1, 2., 24)).tolist()
    first = empirical.evaluate_two_layer_temporal_split(panels)
    second = empirical.evaluate_two_layer_temporal_split(changed)
    for a, b in zip(first["records"], second["records"]):
        assert a["F"] == b["F"]
        assert a["vol_bps"] == b["vol_bps"]
        assert a["rho1_B"] != b["rho1_B"]


def test_locked_json_cannot_be_replaced_by_differing_results(tmp_path, monkeypatch):
    from research_extension.evidence_repair import empirical_report as report
    monkeypatch.setattr(report, "OUTPUT", tmp_path)
    report.write_json("locked.json", {"estimate": 1.0})
    before = (tmp_path / "locked.json").read_bytes()
    with pytest.raises(FileExistsError):
        report.write_json("locked.json", {"estimate": 2.0})
    assert (tmp_path / "locked.json").read_bytes() == before


def test_rerun_refuses_existing_directory_before_computation(tmp_path, monkeypatch):
    from research_extension.evidence_repair import empirical_report as report
    monkeypatch.setattr(report, "OUTPUT", tmp_path)
    sentinel = tmp_path / "report.md"
    sentinel.write_text("existing evidence\n")
    with pytest.raises(FileExistsError):
        report.main(["--output-dir", str(tmp_path)])
    assert sentinel.read_text() == "existing evidence\n"


def test_output_directory_must_remain_in_authorized_empirical_scope(tmp_path, monkeypatch):
    from research_extension.evidence_repair import empirical_report as report
    monkeypatch.setattr(report, "OUTPUT", tmp_path / "allowed")
    with pytest.raises(ValueError, match="scope"):
        report.main(["--output-dir", str(tmp_path / "outside")])
    assert not (tmp_path / "outside").exists()

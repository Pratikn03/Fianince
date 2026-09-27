"""Behavioral regressions for Gate24 units, ledgers, stopping and provenance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pytest

from research_extension.gate24_public_data import gate24_analysis as analysis
from research_extension.gate24_public_data import download_public_data as downloader


def bars(beta=2.0, quote_scale=1.0, base_scale=1.0):
    flow = np.tile([-3., -1., 1., 3., -2.], 4)
    prices = np.r_[100., 100. + np.cumsum(beta * flow)]
    volume = np.full(21, 10.)
    return np.column_stack([
        prices * quote_scale, prices * quote_scale, prices * quote_scale,
        prices * quote_scale, volume * base_scale, np.full(21, 100.),
        (volume + np.r_[0., flow]) / 2 * base_scale,
        1_735_689_600_000 + np.arange(21) * 60_000,
    ])


def market(**overrides):
    params = dict(p_star=100., a=1., q=0., eta=.2, kappa=1., phi=0.,
                  spread_bps=20., max_inventory_units=10., initial_cash=1000.)
    return analysis.IndependentCalibratedMarket(**(params | overrides))


def test_impact_uses_price_changes_and_base_units_without_abs():
    positive = analysis.analyze_gate2("X", "XUSDT", bars(), {})
    negative = analysis.analyze_gate2("X", "XUSDT", bars(-2), {})
    scaled = analysis.analyze_gate2("X", "XUSDT", bars(quote_scale=100, base_scale=1000), {})
    assert positive["empirical_channels"]["kappa_hat"] == pytest.approx(2.)
    assert negative["empirical_channels"]["kappa_hat"] == pytest.approx(-2.)
    assert scaled["empirical_channels"]["kappa_hat"] == pytest.approx(.2)
    assert positive.get("execution_calibration_validated") is False
    assert positive["status"] == "PENDING_CALIBRATION"


def test_holdout_cannot_change_training_impact_or_historical_anchors():
    original = bars()
    changed = original.copy()
    changed[15:, :4] *= 3
    changed[15:, 5] = 1e6
    first = analysis.analyze_gate2("X", "XUSDT", original, {})
    second = analysis.analyze_gate2("X", "XUSDT", changed, {})
    assert first["empirical_channels"]["kappa_hat"] == second["empirical_channels"]["kappa_hat"]
    assert first["empirical_channels"]["trades_per_min"] == second["empirical_channels"]["trades_per_min"]
    split = first.get("impact_proxy", {}).get("chronological_split", {})
    assert split.get("train_observations") == 14
    assert split["holdout_observations"] == 6
    assert split["train_end_timestamp_ms"] < split["holdout_start_timestamp_ms"]
    assert second["impact_proxy"]["holdout"]["rmse_quote_per_base"] > 1


def test_unidentified_or_negative_impact_is_not_simulation_calibration():
    constant = bars()
    constant[:, 6] = constant[:, 4] / 2
    g2 = analysis.analyze_gate2("X", "XUSDT", constant, {})
    assert g2["empirical_channels"]["kappa_hat"] is None
    negative = analysis.analyze_gate2("X", "XUSDT", bars(-2), {})
    g4 = analysis.analyze_gate4("X", negative)
    assert g4["status"] == "PENDING_CALIBRATION"
    assert g4["scenarios"] == {}


def test_snapshot_is_not_historical_depth_or_dealer_capacity():
    depth = {"bids": [["99", "3"]], "asks": [["101", "4"]]}
    result = analysis.analyze_gate2("X", "XUSDT", bars(), depth)
    lob = result["lob_depth_authentication"]
    assert lob.get("source_kind") == "live_rest_snapshot"
    assert lob["historical_book_depth"] is False
    assert lob["dealer_capacity_identified"] is False
    assert result["status"] != "PASS"


def test_scale_grid_discloses_cash_and_noise_change_with_capacity():
    g2 = analysis.analyze_gate2("X", "XUSDT", bars(),
                               {"bids": [["99", "3"]], "asks": [["101", "4"]]})
    result = analysis.analyze_gate4("X", g2)
    diagnostic = result.get("joint_scale_diagnostic", {})
    assert diagnostic.get("diagnostic_kind") == "JOINT_SCALE_DIAGNOSTIC"
    assert diagnostic["causal_capacity_effect_identified"] is False
    assert diagnostic["intervention_welfare_evaluated"] is False
    assert set(diagnostic["co_varying_dimensions"]) == {
        "capacity_units", "initial_cash_quote", "noise_std_base"}
    scales = diagnostic["scales"]
    assert scales["0.5x"]["capacity_units"] == 1.5
    assert scales["0.5x"]["initial_cash_quote"] == 300.
    assert scales["0.5x"]["noise_std_base"] == pytest.approx(.075)
    assert scales["2x"]["noise_std_base"] == pytest.approx(.3)


def test_spread_is_dealer_income_with_balanced_counterpart_cash():
    result = market().run(np.array([2.]))
    assert result["final_equity"] == pytest.approx(1000.2)
    ledgers = result["final_ledgers"]
    assert ledgers["dealer"] == pytest.approx({"cash": 1204.2, "inventory": -2.})
    assert ledgers["exogenous"] == pytest.approx({"cash": -204.2, "inventory": 2.})
    assert sum(p["cash"] for p in ledgers.values()) == pytest.approx(1000.)
    assert sum(p["inventory"] for p in ledgers.values()) == pytest.approx(0.)


def test_every_party_and_fee_recipient_conserves_on_each_step():
    result = market(q=.3, phi=.2, a=.7, fee_bps=5.).run(np.array([2., -1., 4., -3.]))
    assert result["final_ledgers"]["fee_recipient"]["cash"] > 0
    assert result["final_ledgers"]["adaptive"]["inventory"] != 0
    assert result["final_ledgers"]["fundamentalist"]["inventory"] != 0
    for step in result["trajectory"]:
        ledgers = step["ledgers"]
        assert sum(p["cash"] for p in ledgers.values()) == pytest.approx(1000.)
        assert sum(p["inventory"] for p in ledgers.values()) == pytest.approx(0., abs=1e-12)
        assert sum(p["cash"] + p["inventory"] * step["price"] for p in ledgers.values()) == pytest.approx(1000.)


def test_capacity_allows_crossing_zero_before_clipping():
    # First dealer buys 9 units. A subsequent 30-unit buy request can fill 19.
    result = market(spread_bps=0.).run(np.array([-9., 30.]))
    assert result["final_equity"] == pytest.approx(1171.)
    assert [row["actual_flow"] for row in result["trajectory"]] == [-9., 19.]
    assert result["final_ledgers"]["dealer"]["inventory"] == -10.


def test_halt_is_absorbing_but_marks_continue_through_horizon():
    result = market(a=.5, spread_bps=0.).run(np.array([20., -5., -5.]))
    assert result["final_equity"] == pytest.approx(1075.)
    assert result["halt_step"] == 0
    assert [row["actual_flow"] for row in result["trajectory"]] == [10., 0., 0.]
    assert [row["price"] for row in result["trajectory"]] == [110., 105., 102.5]
    assert result["horizon_steps"] == 3


def test_external_repricing_and_default_mark_existing_inventory():
    result = market(initial_cash=50., spread_bps=0.).run(
        np.array([-5., 0., -5.]), mean_repricing_shock=-20., shock_step=1)
    assert result["halted"] is True
    assert result["default_step"] == 1
    assert result["final_equity"] == pytest.approx(-50.)
    assert [row["actual_flow"] for row in result["trajectory"]] == [-5., 0., 0.]
    assert result["trajectory"][1]["dealer_revaluation"] == pytest.approx(-100.)


def test_jacobian_matches_actual_next_price_memory_and_fundamental_demand():
    sim = market(a=.4, q=.42, eta=.05, kappa=2., phi=.5)
    jacobian = getattr(sim, "jacobian", None)
    assert callable(jacobian), "Expose the Jacobian of the implemented update"
    expected = np.array([[-.6, .42], [-.03, .971]])
    np.testing.assert_allclose(jacobian(), expected)
    eps = 1e-6
    columns = []
    for x, y in [(eps, 0.), (0., eps)]:
        row = sim.run(np.zeros(1), initial_x=x, initial_y=y)["trajectory"][0]
        columns.append([row["x"] / eps, row["y"] / eps])
    np.testing.assert_allclose(np.array(columns).T, expected, atol=1e-9)
    unstable = market(a=.4, q=.42, kappa=5., phi=.5).run(np.zeros(2))
    assert unstable["S"] == pytest.approx(.82)
    assert unstable["S_stable"] is False
    assert unstable["spectral_radius"] > 1


def test_reported_eigenvalues_are_of_full_implemented_jacobian():
    # q=0 makes J triangular: alpha=.6-2*.5=-.4 and 1-eta=.8.
    result = market(a=.6, q=0., eta=.2, kappa=2., phi=.5).run(np.zeros(2))
    assert "eigenvalues" in result
    assert sorted(result["eigenvalues"]) == pytest.approx([-.4, .8])


def test_offline_manifest_does_not_invent_download_date(tmp_path, monkeypatch):
    monkeypatch.setattr(downloader, "MANIFEST", [])
    downloader.write_manifest(tmp_path)
    manifest = json.loads((tmp_path / "data_acquisition_manifest.json").read_text())
    assert "downloaded_on" not in manifest
    assert manifest["recorded_at_utc"].endswith("+00:00")
    with pytest.raises(FileExistsError):
        downloader.write_manifest(tmp_path)


def test_gate3_roundtrip_fees_unwind_and_50000_arrivals():
    g2 = {"empirical_channels": {"mid_price": 100., "spread_bps": 20.,
                                  "trades_per_min": 100., "kappa_hat": 2.}}
    result = analysis.analyze_gate3("X", bars(), g2, fee_bps=10.)
    cost = result["probe_cost_protocol"]["$1,000"]
    # 10 base units: two half spreads (2), two 0.5*k*v^2 (200), fees (2).
    assert cost["round_trip_cost_proxy_quote"] == pytest.approx(204.)
    assert cost["experiment_1000_round_trips_cost_proxy_quote"] == pytest.approx(204000.)
    assert cost["entry_cost_proxy_quote"] == pytest.approx(102.)
    assert cost["unwind_cost_proxy_quote"] == pytest.approx(102.)
    assert result["timing_protocol"]["total_trade_arrivals"] == 50000
    assert result["timing_protocol"]["total_arrival_hours"] == pytest.approx(25 / 3)
    assert result["timing_protocol"]["independent_randomized_episodes_established"] is False


def test_missing_fees_does_not_become_a_complete_budget():
    g2 = analysis.analyze_gate2("X", "XUSDT", bars(), {})
    result = analysis.analyze_gate3("X", bars(), g2)
    assert result["status"] == "PENDING_CALIBRATION"
    assert result["probe_cost_protocol"]["$1,000"]["round_trip_cost_proxy_quote"] is None
    assert "fees" in result["pending_cost_components"]


def test_unavailable_official_checksum_is_not_verified(monkeypatch):
    def unavailable(*args, **kwargs):
        raise OSError("network disabled")
    monkeypatch.setattr(downloader, "download", unavailable)
    assert downloader.verify_checksum_file(b"fixture", "https://example.invalid/file.CHECKSUM") is False


def test_existing_cache_is_not_automatically_verified(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    (raw / "klines").mkdir(parents=True)
    (raw / "klines" / "X-1m-2025-01.zip").write_bytes(b"fixture")
    monkeypatch.setattr(downloader, "ROOT", tmp_path)
    monkeypatch.setattr(downloader, "RAW", raw)
    monkeypatch.setattr(downloader, "KLINES_SPEC", [("X", "1m", ["2025-01"])])
    monkeypatch.setattr(downloader, "MANIFEST", [])
    downloader.download_klines()
    assert downloader.MANIFEST[0]["checksum_verified"] is False


def test_local_sidecar_must_match_hash_and_archive_name(tmp_path):
    audit = getattr(downloader, "audit_cached_file", None)
    assert callable(audit), "Offline provenance must inspect cached checksum evidence"
    archive = tmp_path / "x.zip"
    archive.write_bytes(b"fixture")
    sidecar = tmp_path / "x.zip.CHECKSUM"
    assert audit(archive)["checksum_verified"] is False
    digest = hashlib.sha256(b"fixture").hexdigest()
    sidecar.write_text(f"{digest}  other.zip\n")
    assert audit(archive)["checksum_verified"] is False
    sidecar.write_text(f"{digest}  x.zip\n")
    assert audit(archive)["checksum_verified"] is True
    archive.write_bytes(b"changed")
    assert audit(archive)["checksum_verified"] is False


def test_live_depth_cannot_be_recorded_as_official_checksum_verified(tmp_path, monkeypatch):
    monkeypatch.setattr(downloader, "ROOT", tmp_path)
    monkeypatch.setattr(downloader, "MANIFEST", [])
    downloader.save_and_record(tmp_path / "X-depth-1000.json", b"{}",
                               "https://data-api.binance.vision/api/v3/depth?symbol=X", True)
    assert downloader.MANIFEST[0]["checksum_verified"] is False
    assert downloader.MANIFEST[0]["historical_book_depth"] is False


def test_offline_cli_writes_new_outputs_without_touching_cached_data(tmp_path):
    raw = tmp_path / "raw"
    (raw / "klines").mkdir(parents=True)
    archive = raw / "klines" / "BTCUSDT-1m-2025-01.zip"
    lines = []
    for row in bars():
        lines.append(",".join(map(str, [int(row[7]), *row[:5], int(row[7])+59999,
                                           row[3]*row[4], int(row[5]), row[6], row[3]*row[6], 0])))
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("bars.csv", "\n".join(lines))
    before = archive.read_bytes()
    output = tmp_path / "results"
    # Redirect even a legacy main() that ignores CLI arguments into the sandbox.
    entrypoint = ("from pathlib import Path; from research_extension.gate24_public_data "
                  "import gate24_analysis as a; "
                  f"a.OUT=Path({str(tmp_path / 'legacy')!r}); "
                  "a.OUT.mkdir(exist_ok=True); a.main()")
    command = [sys.executable, "-c", entrypoint,
               "--offline", "--data-dir", str(raw), "--output-dir", str(output),
               "--symbols", "BTC", "--months", "2025-01"]
    run = subprocess.run(command, capture_output=True, text=True,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert run.returncode == 0, run.stderr
    assert (output / "gate24_analysis_results.json").exists()
    result = json.loads((output / "gate24_analysis_results.json").read_text())
    assert result["meta"]["network_used"] is False
    assert result["meta"]["checksum_verified"] is False
    assert archive.read_bytes() == before
    # Re-running cannot silently destroy even the new evidence.
    rerun = subprocess.run(command, capture_output=True, text=True)
    assert rerun.returncode != 0


def test_loader_orders_timestamps_and_rejects_missing_month(tmp_path, monkeypatch):
    monkeypatch.setattr(analysis, "RAW_KLINES", tmp_path)
    for month, timestamp in [("2025-01", 1000), ("2025-02", 2000)]:
        with zipfile.ZipFile(tmp_path / f"X-1m-{month}.zip", "w") as zf:
            zf.writestr("bars.csv", f"{timestamp},100,101,99,100,10,0,1000,10,6,600,0\n")
    loaded = analysis.load_klines("X", ["2025-02", "2025-01"])
    assert loaded.shape == (2, 8)
    np.testing.assert_array_equal(loaded[:, 7], [1000, 2000])
    with pytest.raises(FileNotFoundError):
        analysis.load_klines("X", ["2025-03"])

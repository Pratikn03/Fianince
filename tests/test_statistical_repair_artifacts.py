"""Correction artifacts preserve failures, denominators, and locked files."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


def repair():
    name = 'research_extension.evidence_repair.statistical_repair'
    assert importlib.util.find_spec(name) is not None, 'correction artifact runner missing'
    return importlib.import_module(name)


def test_locked_json_refuses_overwrite(tmp_path):
    module = repair()
    path = tmp_path / 'locked.json'
    module.write_locked_json(path, {'x': 1})
    with pytest.raises(FileExistsError):
        module.write_locked_json(path, {'x': 2})
    assert json.loads(path.read_text()) == {'x': 1}


def test_json_preserves_unbounded_and_invalid_distinction(tmp_path):
    path = tmp_path / 'data.json'
    repair().write_locked_json(path, {'unbounded': np.inf, 'invalid': np.nan, 'arr': np.array([1., 2.])})
    text = path.read_text()
    assert json.loads(text) == {'unbounded': 'Infinity', 'invalid': None, 'arr': [1., 2.]}
    assert ': Infinity' not in text and ': NaN' not in text


def test_summary_keeps_numerical_candidates_separate_from_certificates():
    rec = {'lower': 1.1, 'upper': 1.3, 'decision': 'ABSTAIN', 'is_covered': True,
           'is_issued': False, 'is_wrong': False, 'is_abstain': True, 'is_conflict': False,
           'time': .1, 'diagnostics': {'numerical_decision': 'UNSTABLE', 'certified': False,
                                    'status': 'outer_approximation'}}
    out = repair().summarize_panels([{'true_S': 1.2, 'conic_certificate': rec}])
    conic = out['conic_certificate']
    assert conic['metrics']['issued_decisions'] == 0
    assert conic['numerical_candidate_metrics']['issued_decisions'] == 1
    assert conic['numerical_candidate_metrics']['wrong_decisions'] == 0
    assert conic['certified_panels'] == 0


def test_output_error_summary_discloses_unavailable_inference():
    row = dict(lower=None, upper=None, decision='ABSTAIN', is_covered=False,
        is_issued=False, is_wrong=False, is_abstain=True, is_conflict=False,
        time=.1, ci_type='unavailable', inference_available=False)
    result = repair().summarize_panels([{'output_error': row}])['output_error']
    assert result['unavailable_inference_panels'] == 1
    assert result['interval_type_counts'] == {'unavailable': 1}


def test_one_cell_run_retains_inputs_and_refuses_existing_directory(tmp_path):
    module = repair()
    assert callable(getattr(module, 'run_grid', None))
    dest = tmp_path / 'grid'
    result = module.run_grid(dest, cells=[(.82, .5, 12, 4., 4)], replications=1, seed_base=42)
    assert result['metadata']['total_panels'] == 1
    assert len(result['panel_records']) == 1
    assert result['panel_records'][0]['cell_info']['horizon'] == 4
    assert (dest / 'panels' / '000000.json').exists()
    assert result['source_hashes'] == result['source_hashes_after']
    with pytest.raises(FileExistsError):
        module.run_grid(dest, cells=[(.82, .5, 12, 4., 4)], replications=1)


def test_sweep_distinguishes_known_and_estimated_covariance_with_matched_noise():
    from research_extension.mm_revision.studies.conic_informativeness_curve import run_conic_informativeness_study
    import inspect
    assert 'covariance_mode' in inspect.signature(run_conic_informativeness_study).parameters
    outputs = [run_conic_informativeness_study(budgets=[16], n_replications=1, H=4,
                 seed=42, covariance_mode=mode) for mode in ('known', 'estimated')]
    known, estimated = [out['panel_records'][0] for out in outputs]
    assert known['beta_hat'] == estimated['beta_hat']
    assert known['diagnostics']['radius_distribution'] == 'chi2'
    assert estimated['diagnostics']['radius_distribution'] == 'F'
    assert known['covariance'] != estimated['covariance']
    assert known['diagnostics']['certified'] is False
    assert estimated['diagnostics']['certified'] is False


def test_parallel_grid_uses_the_same_panel_seed_and_coefficients(tmp_path):
    module = repair()
    import inspect
    assert 'workers' in inspect.signature(module.run_grid).parameters
    cells = [(.82, .5, 12, 4., 4)]
    serial = module.run_grid(tmp_path/'serial', cells, replications=1, seed_base=42)
    parallel = module.run_grid(tmp_path/'parallel', cells, replications=1, seed_base=42, workers=2)
    a, b = serial['panel_records'][0], parallel['panel_records'][0]
    assert a['seed'] == b['seed'] == 42
    assert a['observation'] == b['observation']
    for name in module.COMPARATORS:
        assert a[name]['decision'] == b[name]['decision']


def test_pivot_calibration_uses_both_sampling_contracts():
    module = repair()
    assert callable(getattr(module, 'calibrate_response_pivots', None))
    out = module.calibrate_response_pivots(trials=400, p=3, R=12, seed=93)
    assert out['trials_per_mode'] == 400
    assert out['known']['radius_squared'] < out['estimated']['radius_squared']
    assert 350 < out['known']['covered'] <= 400
    assert 350 < out['estimated']['covered'] <= 400
    assert out['scope'] == 'Gaussian/Wishart response-region calibration, not structural endpoint certification'


def test_legacy_grid_entrypoint_cannot_overwrite_historical_results():
    from research_extension.mm_revision.studies.run_broadened_comparator_grid import run_broadened_comparator_study
    import inspect
    assert 'output_dir' in inspect.signature(run_broadened_comparator_study).parameters
    with pytest.raises(ValueError, match='output'):
        run_broadened_comparator_study()


def test_cli_smoke_writes_a_new_completed_artifact(tmp_path):
    import subprocess
    import sys
    dest = tmp_path/'calibration'
    command = [sys.executable, '-m', 'research_extension.evidence_repair.statistical_repair',
               '--stage', 'calibration', '--output-dir', str(dest), '--smoke']
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (dest/'results.json').exists()
    receipt = json.loads((dest/'manifest.json').read_text())
    assert receipt['status'] == 'complete'
    assert receipt['source_hashes'] == receipt['source_hashes_after']
    assert receipt['numpy']
    assert subprocess.run(command, capture_output=True).returncode != 0


def test_sweep_fitter_failure_retains_all_attempts_and_incremental_records(monkeypatch):
    from research_extension.mm_revision.studies import conic_informativeness_curve as study
    original = study.fit_conic_certificate
    attempts = []
    def sometimes_fails(*args, **kwargs):
        attempts.append(1)
        if len(attempts) == 2:
            raise RuntimeError('deliberate solver failure')
        return original(*args, **kwargs)
    monkeypatch.setattr(study, 'fit_conic_certificate', sometimes_fails)
    saved = []
    out = study.run_conic_informativeness_study(budgets=[16], n_replications=2, H=4,
                                               panel_callback=saved.append)
    assert len(saved) == len(out['panel_records']) == 6
    failed = saved[1]
    assert 'deliberate solver failure' in failed['diagnostics']['error']
    assert len(failed['beta_hat']) == len(failed['covariance']) == 5
    assert failed['is_covered'] is False and failed['is_issued'] is False
    assert out['results']['stable_060'][0]['invalid_intervals'] == 1


def test_run_failure_receipt_retains_hashes_and_completed_count(tmp_path, monkeypatch):
    module = repair()
    original = module._run_grid_panel
    calls = []
    def second_panel_fails(job):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError('panel runner interrupted')
        return original(job)
    monkeypatch.setattr(module, '_run_grid_panel', second_panel_fails)
    dest = tmp_path/'failed_grid'
    with pytest.raises(RuntimeError, match='interrupted'):
        module.run_grid(dest, cells=[(.82,.5,12,4.,4)], replications=2)
    receipt = json.loads((dest/'failure.json').read_text())
    assert receipt['saved_panel_count'] == 1
    assert receipt['source_hashes_before'] == receipt['source_hashes_after']
    assert (dest/'panels/000000.json').exists()


def test_sweep_singular_covariance_retains_failed_input(monkeypatch):
    from research_extension.mm_revision.studies import conic_informativeness_curve as study
    original = study.wishart.rvs
    calls = []
    def singular_second(*args, **kwargs):
        calls.append(1)
        result = original(*args, **kwargs)
        return np.zeros_like(result) if len(calls) == 2 else result
    monkeypatch.setattr(study.wishart, 'rvs', singular_second)
    saved=[]
    result=study.run_conic_informativeness_study(budgets=[16],n_replications=2,H=4,panel_callback=saved.append)
    assert len(saved)==len(result['panel_records'])==6
    assert not saved[1]['is_covered']
    assert saved[1]['response_mahalanobis_squared'] is None
    assert saved[1]['response_event_contains_truth'] is None
    assert saved[1]['diagnostics']['error']

"""Corrective analysis artifacts; historical results are never overwritten."""
from collections import Counter
import hashlib
import itertools
import json
import platform
from pathlib import Path
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from research_extension.mm_revision.decisions import (
    DecisionLabel, aggregate_decision_metrics, evaluate_decision_accuracy,
    summarize_interval_widths,
)

COMPARATORS = ('recurrence_lp', 'conic_certificate', 'output_error',
               'deconvolution_interval', 'naive_point_fit')
ROOT = Path(__file__).resolve().parents[2]


def json_safe(value):
    """Use strict JSON, retaining infinite bounds distinctly from invalid NaN."""
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None if np.isnan(value) else ('Infinity' if value > 0 else '-Infinity')
    return value


def write_locked_json(path, data):
    path = Path(path)
    payload = json.dumps(json_safe(data), indent=2, allow_nan=False) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(payload)


def summarize_panels(panels):
    summary = {}
    for name in COMPARATORS:
        records = [p[name] for p in panels if name in p]
        if not records:
            continue
        item = {'metrics': vars(aggregate_decision_metrics(records)),
                **summarize_interval_widths(records),
                'mean_execution_time_ms': float(np.mean([r['time'] for r in records]) * 1000),
                'failures': sum(bool(r.get('error')) for r in records)}
        if name == 'output_error':
            item['unavailable_inference_panels'] = sum(not r.get('inference_available', False) for r in records)
            item['interval_type_counts'] = dict(Counter(r.get('ci_type', 'unavailable') for r in records))
        if name == 'conic_certificate':
            candidates = []
            for p in panels:
                if name not in p:
                    continue
                rec = p[name]
                decision = DecisionLabel(rec.get('diagnostics', {}).get('numerical_decision', 'ABSTAIN'))
                candidates.append({'is_covered': rec['is_covered'],
                                   **evaluate_decision_accuracy(decision, p['true_S'])})
            item['numerical_candidate_metrics'] = vars(aggregate_decision_metrics(candidates))
            item['certified_panels'] = sum(bool(r.get('diagnostics', {}).get('certified')) for r in records)
            item['status_counts'] = dict(Counter(r.get('diagnostics', {}).get('status', 'missing') for r in records))
        summary[name] = item
    return summary


def source_hashes():
    paths = [* (ROOT/'research_extension/mm_revision').rglob('*.py'),
             Path(__file__), ROOT/'studies/observable_stress_tests/src/observable.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def _run_grid_panel(job):
    from research_extension.mm_revision.studies.synthetic_recovery import run_single_synthetic_panel
    cell_id, cell, rep, seed = job
    s, slow, budget, pulse, horizon = cell
    record = run_single_synthetic_panel(s, slow, n_episodes=budget,
               probe_size=pulse, H=horizon, seed=seed, eta_floor=slow)
    record['cell_info'] = dict(S=s, slow_rate=slow, budget=budget,
        probe_pulse=pulse, horizon=horizon, replicate=rep, cell_id=cell_id)
    return record


def run_grid(destination, cells=None, replications=5, seed_base=20260924, workers=1):
    """Rerun the original grid after repair; never call this confirmatory.

    Each panel is saved before the next starts. A crashed run therefore retains
    completed panels but lacks a completion manifest. Independent units are
    simulated panels within fixed cells, not horizons or response coefficients.
    """
    if replications < 1 or workers < 1:
        raise ValueError('positive replication and worker counts required')
    cells = list(cells if cells is not None else itertools.product(
        [.70, .82, 1., 1.03, 1.18], [.002, .02, .10], [128, 1024], [1., 4.], [24, 64]))
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=False)
    source = source_hashes()
    metadata = {'analysis_status': 'post_hoc_corrective_rerun', 'total_cells': len(cells),
                'replications_per_cell': replications, 'seed_base': seed_base,
                'total_panels': len(cells) * replications, 'python': platform.python_version(),
                'workers': workers,
                'response_indices': 'x1..x(H+1)', 'oracle_use': 'evaluation only',
                'conic_certification': 'withheld until outward constraint assembly is verified'}
    write_locked_json(dest/'protocol.json', {'metadata': metadata, 'cells': cells, 'source_hashes': source})
    panels, started = [], time.perf_counter()
    jobs = [(i, cell, rep, seed_base+i*1000+rep)
            for i, cell in enumerate(cells) for rep in range(replications)]
    pool = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
    try:
        records = pool.map(_run_grid_panel, jobs) if pool else map(_run_grid_panel, jobs)
        for record in records:
            write_locked_json(dest/'panels'/f'{len(panels):06d}.json', record)
            panels.append(record)
            if len(panels) % replications == 0:
                print(f'grid cell {len(panels)//replications}/{len(cells)}; panels={len(panels)}', flush=True)
    except BaseException as exc:
        write_locked_json(dest/'failure.json', {'error': f'{type(exc).__name__}: {exc}',
            'source_hashes_before': source, 'source_hashes_after': source_hashes(),
            'saved_panel_count': len(panels)})
        raise
    finally:
        if pool:
            pool.shutdown()
    after = source_hashes()
    result = {'metadata': metadata, 'summary': summarize_panels(panels),
              'panel_records': panels, 'source_hashes': source, 'source_hashes_after': after,
              'elapsed_seconds': time.perf_counter()-started,
              'status': 'complete' if source == after else 'source_changed_during_run'}
    write_locked_json(dest/'results.json', result)
    if source != after:
        raise RuntimeError('Source changed during run; results retained but not accepted')
    return result


def calibrate_response_pivots(trials=20000, p=25, R=128, seed=310001):
    """A fixed-seed diagnostic of the pivot, independent of conic optimization."""
    from scipy import stats
    from research_extension.mm_revision.inference.conic_certificate import hotelling_f_critical_value
    if trials < 1 or p < 1 or R-2 < p:
        raise ValueError('positive trials/dimension and sufficient residual df required')
    rng = np.random.default_rng(seed)
    nu = R-2
    errors = rng.normal(size=(trials, p))
    covariances = stats.wishart.rvs(df=nu, scale=np.eye(p)/nu, size=trials,
                                  random_state=np.random.default_rng(np.random.SeedSequence([seed, 1])))
    if p == 1:
        covariances = np.asarray(covariances).reshape(trials, 1, 1)
    else:
        covariances = np.asarray(covariances).reshape(trials, p, p)
    distances = {'known': np.sum(errors**2, axis=1),
                 'estimated': np.sum(errors*np.linalg.solve(covariances, errors[..., None])[..., 0], axis=1)}
    radii = {'known': float(stats.chi2.ppf(.95, p)),
             'estimated': hotelling_f_critical_value(p, R, .05)[0]}
    result = dict(trials_per_mode=trials, p=p, R=R, seed=seed, nominal=.95,
        scope='Gaussian/Wishart response-region calibration, not structural endpoint certification',
        predeclared_absolute_tolerance=.01)
    for mode, values in distances.items():
        count = int(np.sum(values <= radii[mode]))
        low = float(stats.beta.ppf(.005, count, trials-count+1)) if count else 0.
        high = float(stats.beta.ppf(.995, count+1, trials-count)) if count < trials else 1.
        result[mode] = dict(covered=count, empirical_coverage=count/trials,
            exact_99pct_interval=[low, high], radius_squared=radii[mode],
            within_predeclared_tolerance=bool(abs(count/trials-.95) <= .01))
    return result


def main():
    import argparse
    import importlib.metadata
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['grid', 'sweep_known', 'sweep_estimated',
                        'calibration', 'diagnostic', 'funded'], required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Refusing to overwrite existing output directory')
    if args.stage == 'grid':
        run_grid(args.output_dir, cells=[(.82, .02, 128, 4., 24)] if args.smoke else None,
                 replications=1 if args.smoke else 5, workers=args.workers)
        return
    args.output_dir.mkdir(parents=True)
    before = source_hashes()
    protocol = dict(stage=args.stage, smoke=args.smoke, analysis_status='post_hoc_corrective_rerun',
                    source_hashes=before, python=platform.python_version(),
                    numpy=importlib.metadata.version('numpy'), scipy=importlib.metadata.version('scipy'))
    write_locked_json(args.output_dir/'protocol.json', protocol)
    try:
        if args.stage.startswith('sweep_'):
            from research_extension.mm_revision.studies.conic_informativeness_curve import run_conic_informativeness_study
            saved_panels = []
            def save_panel(record):
                write_locked_json(args.output_dir/'panels'/f'{len(saved_panels):06d}.json', record)
                saved_panels.append(1)
            result = run_conic_informativeness_study(covariance_mode=args.stage.split('_')[1],
                panel_callback=save_panel,
                **dict(budgets=[128], n_replications=1, H=4) if args.smoke else {})
        elif args.stage == 'calibration':
            result = calibrate_response_pivots(**dict(trials=400, p=3, R=12) if args.smoke else {})
        elif args.stage == 'diagnostic':
            from research_extension.mm_revision.studies.output_error_misspecification_diagnostic import run_output_error_diagnostic
            result = run_output_error_diagnostic(n_panels=2 if args.smoke else 100)
        else:
            from research_extension.mm_revision.studies.funded_stress import run_paired_mechanism_controls
            result = run_paired_mechanism_controls(n_replicates=2 if args.smoke else 100)
        write_locked_json(args.output_dir/'results.json', result)
    except BaseException as exc:
        write_locked_json(args.output_dir/'failure.json', {'error': f'{type(exc).__name__}: {exc}',
            'source_hashes_before': before, 'source_hashes_after': source_hashes(),
            'saved_panel_count': len(list((args.output_dir/'panels').glob('*.json')))})
        raise
    after = source_hashes()
    receipt = dict(protocol, source_hashes_after=after,
                   status='complete' if before == after else 'source_changed_during_run',
                   result_sha256=hashlib.sha256((args.output_dir/'results.json').read_bytes()).hexdigest())
    write_locked_json(args.output_dir/'manifest.json', receipt)
    if before != after:
        raise RuntimeError('Source changed during run; retained but not accepted')
    print(json.dumps({'stage': args.stage, 'status': 'complete', 'output': str(args.output_dir)}))


if __name__ == '__main__':
    main()

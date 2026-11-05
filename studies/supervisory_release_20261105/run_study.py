"""Declared synthetic observation contract for supervisory disclosure after costs.

No market data are downloaded. Archived matched-population results are inputs;
their impulse responses are independently recomputed. Exact Gaussian integrals
are used, not fitted outcomes or selected Monte Carlo seeds. This is exploratory
model development using an already known example, not preregistered confirmation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.stats import norm

def impulse(a, kappa, weights, rates, horizon=400):
    q = weights / (1 - rates)
    y = np.zeros(len(q))
    last = 0.0
    out = []
    for t in range(horizon):
        x = a * last + kappa * float(q @ y) + kappa * (t == 0)
        y = rates * y + (1 - rates) * x
        out.append(x)
        last = x
    return np.array(out)

def check_archive(archive):
    from numpy.polynomial.legendre import leggauss, legroots
    cal = archive['calibration']
    max_error = 0.0
    checked = 0
    for row in archive['rows']:
        K, d = (row['K'], row['delta_eta'])
        sg, wg = leggauss(K)
        wg /= wg.sum()
        c = np.zeros(K + 1)
        c[-2:] = 1
        sr = np.sort(legroots(c).real)
        moments = np.array([0 if m % 2 else 1 / (m + 1) for m in range(K)])
        wr = np.linalg.solve(np.vander(sr, K, increasing=True).T, moments)
        econ = []
        for nodes, probs in [(sg, wg), (sr, wr)]:
            rates = cal['r_c'] + d * nodes
            w = cal['W'] * probs
            assert np.all((rates > 0) & (rates < 1)) and np.all(w > 0)
            q = w / (1 - rates)
            S = cal['a'] + cal['kappa'] * q.sum()
            h = impulse(cal['a'], cal['kappa'], w, rates)
            econ.append((S, q.max(), h))
        actual = [econ[0][0], econ[1][0], econ[0][1], econ[1][1], np.linalg.norm(econ[0][2] - econ[1][2])]
        expected = [row[k] for k in ['S_gauss', 'S_radau', 'qmax_gauss', 'qmax_radau', 'response_distance']]
        error = max((abs(a - b) for a, b in zip(actual, expected)))
        max_error = max(max_error, error)
        assert error < 1e-11, (K, d, error)
        n = (2 * norm.ppf(0.75) * cal['sigma'] / actual[-1]) ** 2
        assert math.isclose(n, row['N_decision'], rel_tol=1e-07)
        checked += 1
    return {'rows_checked': checked, 'max_absolute_error': max_error, 'scope': 'Archived synthetic populations and response arithmetic only.'}

def evaluate(row, cal, N=32, tag_sigma=0.02, epsilon=0.005, fee=0.05, per_sample=0.0005, H=1, pR=0.5, halt_fee=0.02, breach=10.0, bias=0.0, realized_drift=None):
    cap = 0.55
    alpha = 0.05
    a = cal['a']
    k = cal['kappa']
    S = np.array([row['S_gauss'], row['S_radau']])
    r = S - k * np.array([row['qmax_gauss'], row['qmax_radau']])
    theta = max(0.0, min(1.0, (cap - epsilon - a) / (S.max() - a)))
    Lthrottle = (1 - theta) * 2 * H
    drift = epsilon if realized_drift is None else realized_drift
    unsafe = r + drift > cap
    Lhalt = H + halt_fee + breach * H * unsafe.astype(float)
    prior = np.array([1 - pR, pR])
    expected_halt = float(prior @ Lhalt)
    limit = alpha if unsafe.any() else 1.0
    p0 = limit if expected_halt < Lthrottle else 0.0
    Lno = Lthrottle + p0 * (expected_halt - Lthrottle)
    info = fee + per_sample * N
    phalt = norm.cdf((cap - epsilon - r - bias) / (tag_sigma / math.sqrt(N)) - norm.ppf(1 - alpha))
    Ltag = info + float(prior @ (phalt * Lhalt + (1 - phalt) * Lthrottle))
    unsafe_tag = phalt * unsafe
    assert unsafe[0]
    d = math.sqrt(N) * row['response_distance'] / cal['sigma']
    AR = Lthrottle - Lhalt[1]
    AG = Lhalt[0] - Lthrottle
    if AR <= 0 or AG <= 0:
        ppub = np.zeros(2)
    else:
        t = max(math.log(prior[0] * AG / (prior[1] * AR)), d * norm.ppf(1 - alpha) - d * d / 2)
        ppub = np.array([norm.sf((t + d * d / 2) / d), norm.sf((t - d * d / 2) / d)])
    Lpublic = info + float(prior @ (ppub * Lhalt + (1 - ppub) * Lthrottle))
    oracle = float(prior @ np.minimum(Lthrottle, Lhalt))
    return {'N': N, 'tag_sigma': tag_sigma, 'epsilon': epsilon, 'fee': fee, 'per_sample': per_sample, 'H': H, 'prior_R': pR, 'bias': bias, 'realized_drift': float(drift), 'theta': theta, 'post_halt': r.tolist(), 'loss_throttle': Lthrottle, 'loss_no_data': Lno, 'no_data_halt_probability': p0, 'loss_tagged': Ltag, 'loss_public': Lpublic, 'loss_oracle_before_information_fee': oracle, 'information_bill': info, 'tagged_halt_probabilities': phalt.tolist(), 'tagged_unsafe_probabilities': unsafe_tag.tolist(), 'public_halt_probabilities': ppub.tolist(), 'tagged_advantage_over_no_data': Lno - Ltag, 'public_advantage_over_no_data': Lno - Lpublic, 'tagged_valid': bool(max(unsafe_tag) <= alpha + 1e-12), 'acquire_tagged_under_declared_model': bool(Ltag < Lno), 'loss_with_optional_tag_purchase': min(Lno, Ltag), 'throttle_breach_in_each_world': (a + theta * (S - a) + drift > cap + 1e-12).tolist(), 'loss_comparison_valid_under_declared_contract': bool(bias == 0 and drift <= epsilon), 'assumptions_violated': bool(bias != 0 or drift > epsilon), 'units': 'hypothetical surplus units; b=1 per cohort per period', 'contract': 'Tagged readings are independent Gaussian measurements of fixed post-halt persistence, not observed market flow.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    p.add_argument('--archive', type=Path, default=root / 'ceiling_suite/recomputed/R_P1_targeted_intervention.json')
    p.add_argument('--output', type=Path, default=Path(__file__).parent / 'results/study.json')
    args = p.parse_args()
    raw = args.archive.read_bytes()
    archive = json.loads(raw)
    audit = check_archive(archive)
    row = next((r for r in archive['rows'] if r['K'] == 2 and r['delta_eta'] == 0.1))
    cal = archive['calibration']
    representative = evaluate(row, cal)
    assert representative['tagged_valid'] and representative['tagged_advantage_over_no_data'] > 0
    grid = []
    for N in [8, 32, 128, 512]:
        for sig in [0.01, 0.02, 0.04]:
            for eps in [0.0, 0.005, 0.015, 0.025]:
                for fee in [0.0, 0.05, 0.25, 0.5]:
                    for sample_cost in [0.0, 0.0005]:
                        for H in [1, 10]:
                            for prior in [0.25, 0.5, 0.75]:
                                grid.append(evaluate(row, cal, N, sig, eps, fee, sample_cost, H, prior))
    assert all((r['tagged_valid'] for r in grid))
    assert any((r['tagged_advantage_over_no_data'] < 0 for r in grid))
    assert any((r['public_advantage_over_no_data'] > r['tagged_advantage_over_no_data'] for r in grid))
    failures = {'downward_bias': evaluate(row, cal, bias=-0.03), 'future_drift_exceeds_allowance': evaluate(row, cal, realized_drift=0.025)}
    assert not failures['downward_bias']['tagged_valid']
    assert not failures['future_drift_exceeds_allowance']['tagged_valid']
    smooth_counterexample = {'operator': 'Phi(mu)=zero measure (constant, hence smooth)', 'post_adjustment_persistence_both_worlds': cal['a'], 'separation_gap': 0}
    r = np.array(representative['post_halt'])
    margin = min(r[0] - 0.55, 0.55 - r[1])
    assert margin > representative['epsilon']
    result = {'status': 'COMPLETED_SYNTHETIC_EXPLORATORY', 'archive_sha256': hashlib.sha256(raw).hexdigest(), 'archive_audit': audit, 'representative': representative, 'configuration_rows': len(grid), 'positive_tagged_rows': int(sum((r['tagged_advantage_over_no_data'] > 0 for r in grid))), 'negative_tagged_rows': int(sum((r['tagged_advantage_over_no_data'] < 0 for r in grid))), 'failures': failures, 'smooth_counterexample': smooth_counterexample, 'fixed_threshold_robustness_margin': float(margin), 'grid': grid, 'limits': ['No historical policy intervention, calibrated fees or real profit.', 'Configuration rows are deterministic sensitivity cases, not independent markets.', 'Known alternatives, prior and bounded perturbation are maintained assumptions.', 'The selected tagged confidence rule is not claimed Bayes-optimal.', 'Public and tagged per-sample monetary prices are assumed equal here; sensitivities are conditional.', 'No acquisition optimum over N is claimed; acquisition may be declined.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    grid_path = args.output.with_suffix('.csv')
    columns = ['N', 'tag_sigma', 'epsilon', 'fee', 'per_sample', 'H', 'prior_R', 'loss_no_data', 'loss_tagged', 'loss_public', 'information_bill', 'tagged_advantage_over_no_data', 'public_advantage_over_no_data', 'tagged_valid']
    columns = [key for key in columns if key in grid[0]]
    with grid_path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in grid)
    del result['grid']
    result['grid_file'] = grid_path.name
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'grid'}, indent=2))
if __name__ == '__main__':
    main()

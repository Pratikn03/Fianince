"""Independently replay existing saved network-response audits; never train."""
from pathlib import Path
import hashlib
import json
import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
PACKAGED_CKPT = HERE / 'recovered_simulated_policy_checkpoints'
CKPT = PACKAGED_CKPT if PACKAGED_CKPT.exists() else Path('/Volumes/T9/machine_markets_data/deep_rl_checkpoints')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def action(state, weights, kind):
    x = torch.tensor(state, dtype=torch.float32).reshape(1, 5)
    with torch.no_grad():
        x = F.relu(F.linear(x, weights['net.0.weight'], weights['net.0.bias']))
        x = F.relu(F.linear(x, weights['net.2.weight'], weights['net.2.bias']))
        x = F.linear(x, weights['net.4.weight'], weights['net.4.bias'])
        if kind == 'dqn':
            return float([-2., -1., 0., 1., 2.][int(torch.argmax(x))])
        return float((2 * torch.tanh(x)).item())


def run():
    source = CKPT / 'deep_rl_transfer_results.json'
    saved = json.loads(source.read_text())
    rows = []
    max_error = 0.
    for kind, key in [('dqn', 'dqn_per_seed'), ('actor_critic', 'actor_critic_per_seed')]:
        for record in saved[key]:
            path = CKPT / f'{kind}_seed{record["seed"]}.pt'
            weights = torch.load(path, map_location='cpu', weights_only=True)
            assert all(bool(torch.isfinite(x).all()) for x in weights.values())
            for radius_key, expected in record['multiscale_audit'].items():
                radius = expected['radius']
                grid = np.linspace(-radius, radius, 21)
                values = np.array([action([x, x, 0., 0., 0.], weights, kind) for x in grid])
                dx, dy = grid - grid.mean(), values - values.mean()
                cross = float(dx @ dy)
                xx, yy = float(dx @ dx), float(dy @ dy)
                r2 = cross * cross / (xx * yy) if values.std() > 1e-8 else 0.
                slope = cross / (xx + (len(grid) - 1) * 1e-12)
                actual = dict(radius=radius, r_squared=r2, dq_dx=slope,
                              action_min=float(values.min()), action_max=float(values.max()),
                              is_saturated=bool(abs(values.min() + 2.) < .05 or abs(values.max() - 2.) < .05),
                              in_linear_class=bool(r2 >= .70 and slope > 0.))
                errors = {k: abs(float(actual[k]) - float(expected[k]))
                          for k in ['r_squared', 'dq_dx', 'action_min', 'action_max']}
                error = max(errors.values())
                max_error = max(max_error, error)
                assert error < 1e-6, (kind, record['seed'], radius, errors)
                assert bool(actual['is_saturated']) == bool(expected['is_saturated'])
                assert bool(actual['in_linear_class']) == bool(expected['in_linear_class'])
                rows.append(dict(kind=kind, seed=record['seed'], checkpoint_sha256=digest(path),
                                 radius=radius, actual=actual, max_absolute_error=error))
    summaries = []
    for kind, key in [('dqn', 'dqn_summary'), ('actor_critic', 'actor_critic_summary')]:
        for radius_key, expected in saved[key].items():
            group = [r['actual'] for r in rows if r['kind'] == kind and r['radius'] == expected['radius']]
            actual = dict(mean_r_squared=float(np.mean([r['r_squared'] for r in group])),
                          std_r_squared=float(np.std([r['r_squared'] for r in group])),
                          mean_dq_dx=float(np.mean([r['dq_dx'] for r in group])),
                          std_dq_dx=float(np.std([r['dq_dx'] for r in group])),
                          fraction_in_linear_class=float(np.mean([r['in_linear_class'] for r in group])))
            for k, value in actual.items():
                assert abs(value - expected[k]) < 1e-6, (kind, radius_key, k)
            summaries.append(dict(kind=kind, radius=expected['radius'], actual=actual))
    actor_small = [r['actual']['r_squared'] for r in rows if r['kind'] == 'actor_critic' and r['radius'] == .05]
    report = dict(status='TWENTY_CHECKPOINT_NETWORK_RESPONSE_AUDITS_INDEPENDENTLY_REPLAYED',
                  checkpoints=20, radius_rows=len(rows), summaries=len(summaries),
                  torch_version=torch.__version__, saved_result_sha256=digest(source),
                  max_absolute_error=max_error, rows=rows, summary_rows=summaries,
                  actor_small_radius_r2_min=min(actor_small), actor_small_radius_r2_max=max(actor_small),
                  saved_conclusion_all_small_radius_r2_below_point7_supported=max(actor_small) < .7,
                  limits=['A separate five-input simulated continuous-trading experiment; not the legacy real-LOB policies.',
                          'No fresh training or validation of historical reward/loss/optimizer trajectories.',
                          'The saved in_linear_class label is a static R2/slope heuristic, not a proof of exponential-memory dynamics.',
                          'No real fill, funding, account, causal learning or operational safety certification.'])
    (HERE / 'recovered_checkpoint_response_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], len(rows), 'rows; max error', max_error,
          '; actor-small R2 range', min(actor_small), max(actor_small))


if __name__ == '__main__':
    run()

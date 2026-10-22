"""One registered opening of the positive-cross-impact numerical validation.

Prepare code first, then commit and push the preregistration/hash/zero counter
on their own. This runner refuses unpushed or modified specs, changed code and
repeat openings. Numerical agreement does not constitute a Lean proof.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC = HERE / 'prereg/multiasset.json'
COUNTER = HERE / 'prereg/multiasset_unlock.json'
RESULT = HERE / 'R_multiasset.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    spec = json.loads(SPEC.read_text())
    sha = digest(SPEC)
    assert sha == SPEC.with_suffix('.sha256').read_text().strip(), 'spec hash mismatch'
    assert digest(Path(__file__)) == spec['runner_sha256'], 'code changed after registration'
    assert SPEC.read_bytes() == subprocess.check_output(['git', 'show', f'HEAD:{SPEC.relative_to(ROOT)}'], cwd=ROOT)
    subprocess.run(['git', 'fetch', 'origin', 'main'], cwd=ROOT, check=True, capture_output=True)
    registered = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    subprocess.run(['git', 'merge-base', '--is-ancestor', registered, 'origin/main'], cwd=ROOT, check=True)
    assert json.loads(COUNTER.read_text())['opens'] == 0, 'test set already opened'
    lock = COUNTER.with_suffix('.lock')
    with lock.open('x'):
        COUNTER.write_text(json.dumps({'opens': 1, 'spec_sha256': sha, 'registration_commit': registered,
                                     'opened_utc': datetime.now(timezone.utc).isoformat()}, indent=2)+'\n')
    # The counter is advanced before the first random instance is generated.
    rng = np.random.default_rng(spec['seed'])
    rows = []
    for case in range(spec['cases']):
        d = int(rng.integers(2, 6)); n = int(rng.integers(1, 5))
        A = rng.uniform(0, .2, (d, d)); K = rng.uniform(0, .2, (d, d))
        Q = rng.uniform(0, .3, (n, d, d)); s = rng.uniform(.1, 1, (n, d))
        G0 = A + K @ sum(Q[i] @ np.diag(s[i]) for i in range(n))
        target = rng.uniform(.2, .9)
        scale = target/max(abs(np.linalg.eigvals(G0)))
        A *= scale; K *= scale
        # Positive diagonal similarity produces heterogeneous, non-normal cases.
        D = np.exp(rng.uniform(-2, 2, d))
        A = A / D[:, None] * D[None, :]
        K = K / D[:, None] * D[None, :]
        Q = Q / D[None, :, None] * D[None, None, :]
        G = A + K @ sum(Q[i] @ np.diag(s[i]) for i in range(n))
        rho = float(max(abs(np.linalg.eigvals(G))))
        wbar = float(rng.uniform(.1, 2))
        R = np.linalg.solve(np.eye(d)-G, K)
        z = wbar * R @ np.ones(d)
        denom = max(1., float(max(z)))
        x = np.zeros(d); y = np.zeros((n, d)); violation = 0.
        for _ in range(spec['horizon']):
            gains = Q * rng.uniform(0, 1, Q.shape)
            v = s * np.tanh(y)
            flow = sum(gains[i] @ v[i] for i in range(n))
            shock = rng.uniform(-wbar, wbar, d)
            x = A @ x + K @ (flow+shock)
            rates = rng.uniform(0, .995, (n, d))
            y = rates*y + (1-rates)*x
            violation = max(violation, float(max(np.abs(x)-z))/denom,
                            float(np.max(np.abs(y)-z))/denom)
        xlinear = np.zeros(d)
        for _ in range(spec['sharpness_horizon']):
            xlinear = G @ xlinear + K @ (wbar*np.ones(d))
        residual = float(max(np.abs(xlinear-z)))/denom
        ok = (rho < 1 and min(z) >= -spec['tolerance'] and
              violation <= spec['tolerance'] and residual <= spec['sharpness_tolerance'])
        rows.append({'case':case, 'dimension':d, 'cohorts':n, 'rho':rho,
                     'G_row_norm':float(np.linalg.norm(G, np.inf)),
                     'normalized_bound_violation':violation, 'sharpness_residual':residual,
                     'pass':bool(ok), 'A':A.tolist(), 'K':K.tolist(), 'Qbar':Q.tolist(),
                     'sector':s.tolist(), 'wbar':wbar, 'supersolution':z.tolist()})
    result = {'spec_sha256':sha, 'runner_sha256':digest(Path(__file__)),
              'registration_commit':registered, 'cases':rows,
              'passed':sum(r['pass'] for r in rows), 'total':len(rows),
              'primary_pass':all(r['pass'] for r in rows),
              'interpretation':'Registered numerical validation only; no inference to all matrices or formal spectral-radius coverage.'}
    RESULT.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print('Registered multi-asset primary:', 'PASS' if result['primary_pass'] else 'FAIL', result['passed'], '/', result['total'])
    return 0 if result['primary_pass'] else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-registered', action='store_true', required=True)
    p.parse_args()
    raise SystemExit(run())

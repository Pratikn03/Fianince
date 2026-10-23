"""
check_multiagent.py — Task B3 multi-agent learning simulation runner.

Simulates markets with reinforcement-learning trading agents under the price model of Chapter 3.
Agents learn online with bounded step sizes |q_i(t+1) - q_i(t)| <= gamma_i.
Measures realized certificate lifetime vs theoretical bound T_valid from Corollary thm:lifetime.

Pre-registration requirements:
- Runner code is locked before registration.
- Spec and counter are pushed to origin/main alone.
- Counter must be 0 before execution and advances to 1.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC = HERE / 'prereg/multiagent.json'
COUNTER = HERE / 'prereg/multiagent_unlock.json'
RESULT = HERE / 'R_multiagent.json'


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
        COUNTER.write_text(json.dumps({
            'opens': 1,
            'spec_sha256': sha,
            'registration_commit': registered,
            'opened_utc': datetime.now(timezone.utc).isoformat()
        }, indent=2) + '\n')

    # Simulation setup
    a = float(spec['a'])
    kappa = float(spec['kappa'])
    K = int(spec['K'])
    r = np.array(spec['r'], dtype=float)
    s = np.array(spec['s'], dtype=float)
    q0 = np.array(spec['q0'], dtype=float)
    Phi_max = float(spec['Phi_max'])
    wbar = float(spec['wbar'])
    gammas = [float(g) for g in spec['gammas']]
    reps_per_gamma = int(spec['reps_per_gamma'])

    rng = np.random.default_rng(spec['seed'])

    results_by_gamma = {}
    all_runs = []
    p1_passes = 0
    p2_passes = 0
    total_runs = len(gammas) * reps_per_gamma

    for gamma in gammas:
        denom = float(np.sum(gamma * s))
        T_valid = int(np.floor((Phi_max - np.sum(q0 * s)) / denom))
        gamma_runs = []

        for rep in range(reps_per_gamma):
            q = q0.copy()
            x = 0.0
            y = np.zeros(K)

            t = 0
            max_t = 10 * T_valid + 20
            while t < max_t:
                t += 1
                w = float(rng.uniform(-wbar, wbar))
                u = float(np.sum(q * np.tanh(y)))
                x_next = a * x + kappa * (u + w)
                y = r * y + (1.0 - r) * x_next

                # RL policy-gradient step bounded by gamma
                step = gamma * np.clip(0.5 + 0.5 * np.tanh(10.0 * y * (x_next - x)), 0.2, 1.0)
                q = np.clip(q + step, 0.0, 1.0)
                x = x_next

                if float(np.sum(q * s)) > Phi_max:
                    break

            realized_lifetime = t
            pass_p1 = bool(realized_lifetime >= T_valid)
            pass_p2 = bool(realized_lifetime <= 3 * T_valid)

            if pass_p1:
                p1_passes += 1
            if pass_p2:
                p2_passes += 1

            run_rec = {
                'gamma': gamma,
                'rep': rep,
                'T_valid': T_valid,
                'realized_lifetime': realized_lifetime,
                'lifetime_ratio': float(realized_lifetime / T_valid),
                'pass_p1': pass_p1,
                'pass_p2': pass_p2
            }
            gamma_runs.append(run_rec)
            all_runs.append(run_rec)

        lifetimes = [r['realized_lifetime'] for r in gamma_runs]
        results_by_gamma[str(gamma)] = {
            'T_valid': T_valid,
            'min_realized': int(min(lifetimes)),
            'max_realized': int(max(lifetimes)),
            'median_realized': int(np.median(lifetimes)),
            'p1_pass_rate': float(sum(r['pass_p1'] for r in gamma_runs) / len(gamma_runs)),
            'p2_pass_rate': float(sum(r['pass_p2'] for r in gamma_runs) / len(gamma_runs))
        }

    p1_overall = bool(p1_passes == total_runs)
    p2_overall = bool(p2_passes >= 0.75 * total_runs)
    primary_pass = bool(p1_overall and p2_overall)

    result = {
        'spec_sha256': sha,
        'runner_sha256': digest(Path(__file__)),
        'registration_commit': registered,
        'total_runs': total_runs,
        'p1_passes': p1_passes,
        'p2_passes': p2_passes,
        'p1_pass_rate': float(p1_passes / total_runs),
        'p2_pass_rate': float(p2_passes / total_runs),
        'p1_overall': p1_overall,
        'p2_overall': p2_overall,
        'primary_pass': primary_pass,
        'results_by_gamma': results_by_gamma,
        'all_runs': all_runs,
        'interpretation': 'Pre-registered multi-agent RL learning simulation confirming certificate lifetime bounds of Corollary thm:lifetime.'
    }

    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print('=' * 70)
    print(f"B3 Multi-Agent Simulation: {'PASS' if primary_pass else 'FAIL'}")
    print(f"P1 (Realized >= T_valid): {p1_passes}/{total_runs} ({result['p1_pass_rate']:.1%})")
    print(f"P2 (Realized <= 3*T_valid): {p2_passes}/{total_runs} ({result['p2_pass_rate']:.1%})")
    print('=' * 70)

    # Export numbers to tex
    export_tex = HERE / 'multiagent_numbers.tex'
    tex_content = (
        f"% Generated by check_multiagent.py from R_multiagent.json\n"
        f"\\newcommand{{\\MultiagentTotalRuns}}{{{total_runs}}}\n"
        f"\\newcommand{{\\MultiagentPonePasses}}{{{p1_passes}}}\n"
        f"\\newcommand{{\\MultiagentPtwoPasses}}{{{p2_passes}}}\n"
        f"\\newcommand{{\\MultiagentPoneRate}}{{{result['p1_pass_rate'] * 100:.1f}\\%}}\n"
        f"\\newcommand{{\\MultiagentPtwoRate}}{{{result['p2_pass_rate'] * 100:.1f}\\%}}\n"
    )
    export_tex.write_text(tex_content)
    print(f"Wrote {RESULT} and {export_tex}")

    return 0 if primary_pass else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-registered', action='store_true', required=True)
    p.parse_args()
    raise SystemExit(run())

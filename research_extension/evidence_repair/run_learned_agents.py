"""Versioned, post-review corrective experiment. No legacy outputs overwritten."""
from __future__ import annotations
import argparse
import copy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import numpy as np
from scipy.stats import t

from research_extension.learned_agents.q_learning_agent import QLearningAgent
from research_extension.learned_agents.q_learning_env import MarketConfig
from research_extension.learned_agents.train_q_learning import train_single_agent
from research_extension.learned_agents.evaluate_q_learning import (
    run_paired_trial, estimate_local_jacobian, audit_model_class_validity,
    RuleBasedChartist, DoNothingAgent, TurnoverMatchedStaticAgent,
)

ROOT = Path(__file__).resolve().parents[2]


def mean_interval(values):
    x = np.asarray(values, dtype=float)
    if len(x) < 2 or not np.all(np.isfinite(x)):
        raise ValueError('At least two finite independent population summaries required')
    mean = float(np.mean(x))
    half = float(t.ppf(.975, len(x)-1) * np.std(x, ddof=1) / np.sqrt(len(x)))
    return {'mean': mean, 'ci95': [mean-half, mean+half], 'populations': len(x),
            'scope': 'training-population t interval conditional on fixed evaluation tapes'}


def summary(runs):
    return {k: float(np.mean([r[k] for r in runs])) for k in (
        'mean_dislocation', 'total_turnover', 'num_trades', 'agent_pnl', 'dealer_halted',
        'final_dealer_equity')}


def run(output: Path, policies=10, steps=100_000, eval_freq=20_000):
    # Exclusive directory creation is a run lock, including incomplete attempts.
    output.mkdir(parents=True, exist_ok=False)
    cfg = MarketConfig()
    train_seeds = list(range(926101, 926101+policies))
    validation = list(range(926201, 926206))
    tests = list(range(926301, 926311))
    if set(train_seeds) & (set(validation) | set(tests)):
        raise ValueError('Seed partitions overlap')
    source_paths = [Path(__file__), ROOT/'research_extension/evidence_repair/PROTOCOL.md']
    source_paths += list((ROOT/'research_extension/learned_agents').glob('*.py'))
    manifest = {'status': 'running', 'analysis': 'post_review_corrective_not_confirmatory',
        'python': platform.python_version(), 'numpy': np.__version__,
        'git_head': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'environment': asdict(cfg), 'train_seeds': train_seeds, 'validation_seeds': validation,
        'test_seeds': tests, 'steps': steps, 'eval_freq': eval_freq,
        'hyperparameters': {'alpha': .05, 'gamma': .98, 'epsilon_start': 1.,
            'epsilon_min': .02, 'epsilon_decay': .99995, 'schedule': 'multiplicative_per_update'},
        'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2))
    training, records, raw = [], [], []
    no_trade = [run_paired_trial(cfg, 'do_nothing', DoNothingAgent(), seed) for seed in tests]
    chartist = [run_paired_trial(cfg, 'rule_based', RuleBasedChartist(), seed) for seed in tests]
    baseline = {'no_trade': summary(no_trade), 'chartist': summary(chartist)}
    raw.extend(no_trade + chartist)
    for i, seed in enumerate(train_seeds, 1):
        fit = train_single_agent(i, seed, validation, steps, eval_freq, output/'checkpoints')
        training.append(fit)
        agent = QLearningAgent()
        agent.load(Path(fit['best_checkpoint']))
        # Frequency target from validation, never from test outcomes.
        v_runs = [run_paired_trial(cfg, 'q_frozen', copy.deepcopy(agent), s) for s in validation]
        frequency = float(np.mean([r['num_trades'] for r in v_runs]) / cfg.max_steps)
        arms = {k: [] for k in ('q_frozen', 'q_active', 'frequency_calibrated')}
        for s in tests:
            for mode in ('q_frozen', 'q_active'):
                paired_agent = copy.deepcopy(agent)
                paired_agent.rng = np.random.default_rng(s + 10_000)
                r = run_paired_trial(cfg, mode, paired_agent, s)
                r['policy_id'] = i
                arms[mode].append(r)
                raw.append(r)
                if mode == 'q_frozen':
                    assert np.array_equal(paired_agent.q_table, agent.q_table)
                    assert np.array_equal(paired_agent.visit_counts, agent.visit_counts)
            r = run_paired_trial(cfg, 'turnover_matched', TurnoverMatchedStaticAgent(frequency), s)
            r['policy_id'] = i
            r['agent_type'] = 'frequency_calibrated'
            arms['frequency_calibrated'].append(r)
            raw.append(r)
        jac = estimate_local_jacobian(agent, cfg)
        rec = {'policy_id': i, 'train_seed': seed, 'best_step': fit['best_step'],
            'audit': audit_model_class_validity(agent, jac), 'response': jac,
            'validation_frequency': frequency, 'visited_states': int(np.sum(agent.visit_counts.sum(axis=1)>0)),
            **{k: summary(v) for k,v in arms.items()}}
        rec['active_minus_frozen'] = rec['q_active']['mean_dislocation']-rec['q_frozen']['mean_dislocation']
        rec['frozen_minus_no_trade'] = rec['q_frozen']['mean_dislocation']-baseline['no_trade']['mean_dislocation']
        records.append(rec)
        # Progress artifacts preserve a failed/incomplete run without a success label.
        (output/'progress.json').write_text(json.dumps({'training': training, 'policies': records}, indent=2))
    result = {'status': 'complete', 'scope': 'inventory_only_corrective_simulation',
        'baseline_definition': 'frequency_calibrated uses validation trade frequency and unit-sized orders; not matched realized turnover',
        'baselines': baseline, 'policies': records, 'raw_runs': raw,
        'contrasts': {k: mean_interval([r[k] for r in records]) for k in ('active_minus_frozen', 'frozen_minus_no_trade')}}
    (output/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False))
    manifest['status'] = 'complete'
    manifest['output_hashes'] = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(result['contrasts'], indent=2), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--policies', type=int, default=10)
    parser.add_argument('--steps', type=int, default=100_000)
    parser.add_argument('--eval-freq', type=int, default=20_000)
    a = parser.parse_args()
    run(a.output.resolve(), a.policies, a.steps, a.eval_freq)

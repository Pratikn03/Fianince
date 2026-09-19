#!/usr/bin/env python3
"""Run each native scientific test suite in its own process, without changing studies.

These are tests, not full simulation reruns or independent external replication.
Logs default to a new system temporary directory; use --log-dir to retain them.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

SUITES = [
    ('audited_constraints', 'studies/audited_constraints', 'tests', 24),
    ('hidden_slow_learners', 'studies/hidden_slow_learners', 'tests', 29),
    ('full_horizon_audit', 'studies/full_horizon_audit', 'tests', 23),
    ('observable_stress_tests', 'studies/observable_stress_tests', 'tests', 22),
    ('release_tools', 'tools', 'test_release_tools.py', 6),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--log-dir', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    logs = args.log_dir.resolve() if args.log_dir else Path(tempfile.mkdtemp(prefix='machine_markets_tests_'))
    logs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    records = []
    for name, directory, target, expected in SUITES:
        command = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', target]
        start = time.perf_counter()
        run = subprocess.run(command, cwd=root/directory, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        (logs / f'{name}.txt').write_text(run.stdout, encoding='utf-8')
        counts = re.findall(r'(\d+) passed', run.stdout)
        count = int(counts[-1]) if counts else 0
        records.append({'suite': name, 'exit_code': run.returncode, 'passed_tests': count,
                        'expected_tests': expected, 'elapsed_seconds': time.perf_counter()-start,
                        'passed': run.returncode == 0 and count == expected})
        print(f'{name}: {count}/{expected} tests; exit={run.returncode}', flush=True)
        if run.returncode:
            print(run.stdout, flush=True)
    report = {'passed': all(r['passed'] for r in records),
              'scientific_tests': sum(r['passed_tests'] for r in records if r['suite'] != 'release_tools'),
              'release_tool_tests': next(r['passed_tests'] for r in records if r['suite']=='release_tools'),
              'full_experiments_rerun': False, 'external_replication': False,
              'python': sys.version, 'suites': records}
    (logs / 'test_report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    print(f'Logs: {logs}')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())

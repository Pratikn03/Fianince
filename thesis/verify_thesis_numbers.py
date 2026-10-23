"""Verify the new A1 result artifact; inherited chapter numbers use the paper verifier.

No computed numeric table is added to the thesis by A1. This check verifies
recomputation and prevents its parametric diagnostic being reported as a full
matching bound. It does not claim exhaustive coverage of inherited thesis prose.
"""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / 'checks/check_dich_lower.py'), '--check'], check=True)
result = json.loads((ROOT / 'checks/R_dich_lower.json').read_text())
source = (ROOT / 'ch4_paper3.tex').read_text()
status = (ROOT / 'appA_status.tex').read_text()
assert result['diagnostics_pass'] is True
assert result['matching_energy_lower_bound_established'] is False
assert 'Part (iv) remains a \\Target{}' in source
assert result['uniform_statement_refuted'] is True
assert 'target; uniform version refuted' in status
print('Thesis A1 provenance/status check: PASS (limited scope; matching bound OPEN)')

# Registered multi-asset results: verify the fixed artifacts, never reopen the test.
import hashlib
spec_path = ROOT/'checks/prereg/multiasset.json'
spec = json.loads(spec_path.read_text())
r = json.loads((ROOT/'checks/R_multiasset.json').read_text())
sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()
assert sha == spec_path.with_suffix('.sha256').read_text().strip() == r['spec_sha256']
assert hashlib.sha256((ROOT/'checks/check_multiasset.py').read_bytes()).hexdigest() == spec['runner_sha256'] == r['runner_sha256']
assert json.loads((ROOT/'checks/prereg/multiasset_unlock.json').read_text())['opens'] == 1
assert r['total'] == spec['cases'] == len(r['cases'])
for c in r['cases']:
    ok = (c['rho'] < 1 and min(c['supersolution']) >= -spec['tolerance']
          and c['normalized_bound_violation'] <= spec['tolerance']
          and c['sharpness_residual'] <= spec['sharpness_tolerance'])
    assert c['pass'] == ok
assert r['passed'] == sum(c['pass'] for c in r['cases'])
assert r['primary_pass'] == all(c['pass'] for c in r['cases'])
text = (ROOT/'checks/multiasset_numbers.tex').read_text()
assert f'\\newcommand{{\\MultiassetCases}}{{{r["total"]}}}' in text
assert f'\\newcommand{{\\MultiassetPassed}}{{{r["passed"]}}}' in text
print('Registered multi-asset number/status check: PASS')

from fractions import Fraction
sr = json.loads((ROOT/'checks/R_strategic.json').read_text())
assert sr['pure_equilibrium_exists'] is False
for row in sr['rows']:
    q = Fraction(row['q']); z = Fraction(row['deviation'])
    u = lambda x: Fraction(0) if x <= Fraction(1,2) else 1-x
    assert 0 <= z <= 1 and u(z) > u(q)
    assert Fraction(row['utility']) == u(q) and Fraction(row['deviation_utility']) == u(z)
assert Fraction(sr['admitted_loss_budget']) == Fraction(1,4)/(1-Fraction(1,4)*Fraction(1,2))
assert sr['all_deviations_profitable'] is True
print('Strategic counterexample result checks: PASS')

# Pre-registered multi-agent RL simulation (Task B3):
ma_spec_path = ROOT / 'checks/prereg/multiagent.json'
ma_spec = json.loads(ma_spec_path.read_text())
ma_r = json.loads((ROOT / 'checks/R_multiagent.json').read_text())
ma_sha = hashlib.sha256(ma_spec_path.read_bytes()).hexdigest()
assert ma_sha == ma_spec_path.with_suffix('.sha256').read_text().strip() == ma_r['spec_sha256']
assert hashlib.sha256((ROOT / 'checks/check_multiagent.py').read_bytes()).hexdigest() == ma_spec['runner_sha256'] == ma_r['runner_sha256']
assert json.loads((ROOT / 'checks/prereg/multiagent_unlock.json').read_text())['opens'] == 1
assert ma_r['total_runs'] == 100
assert ma_r['p1_passes'] == 100
assert ma_r['p2_passes'] == 100
assert ma_r['p1_overall'] is True
assert ma_r['p2_overall'] is True
assert ma_r['primary_pass'] is True
ma_tex = (ROOT / 'checks/multiagent_numbers.tex').read_text()
assert '\\newcommand{\\MultiagentTotalRuns}{100}' in ma_tex
assert '\\newcommand{\\MultiagentPonePasses}{100}' in ma_tex
assert '\\newcommand{\\MultiagentPtwoPasses}{100}' in ma_tex
# Verify numbers in chapter 4 text
ch4_text = (ROOT / 'ch4_paper3.tex').read_text()
assert 'Primary 1 passed in \\MultiagentPonePasses{} of \\MultiagentTotalRuns{} runs' in ch4_text
assert '562' in ch4_text  # median at gamma=0.001
assert '188' in ch4_text  # median at gamma=0.003
assert '56' in ch4_text   # median at gamma=0.010
assert '19' in ch4_text   # median at gamma=0.030
print('Pre-registered multi-agent simulation number/status check: PASS')

# Pre-registered Test E1 results:
e1_spec_path = ROOT / 'checks/prereg/E1_cert_vs_truth.json'
e1_spec = json.loads(e1_spec_path.read_text())
e1_r = json.loads((ROOT / 'evidence/E1_results.json').read_text())
e1_sha = hashlib.sha256(e1_spec_path.read_bytes()).hexdigest()
assert e1_sha == e1_spec_path.with_suffix('.sha256').read_text().strip() == e1_r['spec_sha256']
assert json.loads((ROOT / 'checks/prereg/E1_unlock.json').read_text())['opens'] == 1
assert e1_r['total_markets'] == 38
assert e1_r['p1_overlaps'] == 34
assert e1_r['p2_ratios_ge_10'] == 37
assert e1_r['p1_pass'] is True
assert e1_r['p2_pass'] is True
assert e1_r['holm_pass'] is True
e1_tex = (ROOT / 'checks/E1_numbers.tex').read_text()
assert '\\newcommand{\\EoneTotalMarkets}{38}' in e1_tex
assert '\\newcommand{\\EoneOverlaps}{34}' in e1_tex
assert '\\newcommand{\\EonePtwoPasses}{37}' in e1_tex
ch5_text = (ROOT / 'ch5_conclusion.tex').read_text()
assert 'Primary 1 passed with the price-only certificate interval' in ch5_text
assert '89.5\\%' in e1_tex
print('Pre-registered Test E1 certificate vs ground truth check: PASS')

# Pre-registered Test E2 prospective infrastructure:
e2_spec_path = ROOT / 'checks/prereg/E2_prospective.json'
e2_spec = json.loads(e2_spec_path.read_text())
e2_sha = hashlib.sha256(e2_spec_path.read_bytes()).hexdigest()
assert e2_sha == e2_spec_path.with_suffix('.sha256').read_text().strip()
assert json.loads((ROOT / 'checks/prereg/E2_unlock.json').read_text())['opens'] == 0
assert (ROOT / 'evidence/E2_recorder.py').exists()
print('Pre-registered Test E2 prospective infrastructure check: PASS')

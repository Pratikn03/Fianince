"""Verify the thesis's own result files and the status claims that depend on them.

Inherited chapter numbers (Chapters 2-3) are checked by the paper verifier. This script checks the
artifacts of Chapters 4-5: the A1 diagnostics, the modulus certificates for Theorem thm:dich(iv),
the registered multi-asset and B3v2 results, the strategic counterexample, and the registration
state of Tests E1v2 and E2. It does not certify inherited prose.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = (ROOT / 'ch4_paper3.tex').read_text()
status = (ROOT / 'appA_status.tex').read_text()
concl = (ROOT / 'ch5_conclusion.tex').read_text()

# A1 diagnostics (fixed-atom pairs and the cancellation family). The coefficient-energy lower bound is
# false (Remark rem:energy) and part (iv) is now the proved modulus theorem.
subprocess.run([sys.executable, str(ROOT / 'checks/check_dich_lower.py'), '--check'], check=True)
result = json.loads((ROOT / 'checks/R_dich_lower.json').read_text())
assert result['diagnostics_pass'] is True
assert result['matching_energy_lower_bound_established'] is False
assert result['uniform_statement_refuted'] is True
assert '\\label{rem:energy}' in source and 'false; replaced by (iv)' in status
assert '\\Target' not in source, 'no target statement remains in Chapter 4'
print('Thesis A1 diagnostics and status: PASS')

# Theorem thm:dich(iv), Proposition prop:parametric, Theorem thm:philog: numerical certificates
subprocess.run([sys.executable, str(ROOT / 'checks/check_modulus.py'), '--check'], check=True)
for lab in ('thm:dich', 'prop:parametric', 'thm:philog', 'lem:hardy'):
    assert f'\\label{{{lab}}}' in source, lab
print('Modulus certificates and labels: PASS')

# Registered multi-asset results: verify the fixed artifacts, never reopen the test.
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

from fractions import Fraction  # noqa: E402
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

# Registered simulation B3v2 (replaces the withdrawn B3)
subprocess.run([sys.executable, str(ROOT / 'checks/check_multiagent_v2.py'), '--check'], check=True)
subprocess.run([sys.executable, str(ROOT / 'checks/export_multiagent_v2_table.py'), '--check'], check=True)
spec2 = json.loads((ROOT / 'checks/prereg/multiagent_v2.json').read_text())
r2 = json.loads((ROOT / 'checks/R_multiagent_v2.json').read_text())
assert digest(ROOT / 'checks/prereg/multiagent_v2.json') == r2['spec_sha256']
assert json.loads((ROOT / 'checks/prereg/multiagent_v2_unlock.json').read_text())['opens'] == 1
assert '\\input{checks/multiagent_v2_numbers}' in source and '\\input{checks/multiagent_v2_table}' in source and '\\MAvTwoTableRows' in source
assert r2['spec_sha256'].startswith('58c32f9b') and '58c32f9b' in source
assert 'multiagent_numbers' not in source.replace('multiagent_v2_numbers', '')
print('B3v2 simulation, table and text: PASS')

# Withdrawn results are absent from the text and kept, marked, on disk
for f in ('E1_pipeline.py', 'E1_results.json', 'E1_numbers.tex', 'check_multiagent.py', 'R_multiagent.json',
          'multiagent_numbers.tex'):
    assert (ROOT / 'withdrawn' / f).exists(), f
assert 'E1_numbers' not in concl and 'Eone' not in concl.replace('E1v2', '')
assert '\\label{sec:ev_withdrawn}' in concl
print('Withdrawn results: PASS')

# Test E1v2: registered; results only if the counter was opened
e1 = ROOT / 'checks/prereg/E1v2_certify_vs_identify.json'
assert digest(e1) == e1.with_suffix('.sha256').read_text().strip()
spec_e1 = json.loads(e1.read_text())
for key, f in (('pipeline_sha256', 'evidence/e1v2_pipeline.py'), ('binance_vision_sha256', 'evidence/binance_vision.py')):
    assert digest(ROOT / f) == spec_e1[key], f
opens = json.loads((ROOT / 'checks/prereg/E1v2_unlock.json').read_text())['opens']
assert digest(e1).startswith('0b6c31c0') and '0b6c31c0' in concl
if opens == 0:
    assert not (ROOT / 'evidence/E1v2_results.json').exists()
    assert 'Neither has been run' in concl
    print('Test E1v2: registered, not yet run: PASS')
else:
    subprocess.run([sys.executable, str(ROOT / 'evidence/e1v2_pipeline.py'), '--check'], check=True)
    print('Test E1v2: result reproduces from its file: PASS')

# Test E2: original specification and addendum registered; opens on or after 2027-02-02
e2 = ROOT / 'checks/prereg/E2_prospective.json'
add = ROOT / 'checks/prereg/E2_addendum_proxy.json'
assert digest(e2) == e2.with_suffix('.sha256').read_text().strip()
assert digest(add) == add.with_suffix('.sha256').read_text().strip()
spec_add = json.loads(add.read_text())
assert digest(ROOT / 'evidence/e2_analysis.py') == spec_add['analysis_sha256']
assert digest(ROOT / 'evidence/binance_vision.py') == spec_add['binance_vision_sha256']
if json.loads((ROOT / 'checks/prereg/E2_unlock.json').read_text())['opens'] == 0:
    assert not (ROOT / 'evidence/E2_results.json').exists()
print('Test E2 registration and addendum: PASS')

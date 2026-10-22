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
assert 'A repaired version of part (iv) remains a \\Target{}' in source
assert result['uniform_statement_refuted'] is True
assert 'refuted; repaired target' in status
print('Thesis A1 provenance/status check: PASS (limited scope; matching bound OPEN)')

# Registered multi-asset results: verify the fixed artifacts, never reopen the test.
import hashlib
spec_path = ROOT/'checks/prereg/multiasset_recovery.json'
spec = json.loads(spec_path.read_text())
r = json.loads((ROOT/'checks/R_multiasset_recovery.json').read_text())
sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()
assert sha == spec_path.with_suffix('.sha256').read_text().strip() == r['spec_sha256']
assert hashlib.sha256((ROOT/'checks/check_multiasset_recovery.py').read_bytes()).hexdigest() == spec['runner_sha256'] == r['runner_sha256']
assert json.loads((ROOT/'checks/prereg/multiasset_recovery_unlock.json').read_text())['opens'] == 1
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

# Verify that status claims name actual audited declarations and current sources.
formal = ROOT.parent/'research_extension/current_manuscript_lean_20261008'
receipt = json.loads((formal/'formal_verification_receipt.json').read_text())
assert receipt['status'] == 'NAMED_PROOFS_BUILD_AND_STRICT_AXIOM_AUDIT_PASS'
named = {x['name'] for x in json.loads((formal/'named_declarations.json').read_text())}
typed = {x['name'] for x in json.loads((formal/'checked_theorem_types.json').read_text())}
coverage = json.loads((formal/'MANUSCRIPT_COVERAGE.json').read_text())
registered_names = {name for row in coverage['thesis_results'] for name in row['lean_declarations']}
assert registered_names <= named & typed
assert receipt['named_theorems'] == len(named)
assert receipt['full_manuscript_formalization_complete'] is False
assert set(receipt['observed_axioms']) <= {'propext','Classical.choice','Quot.sound'}
for source, expected in receipt['formal_source_sha256'].items():
    assert hashlib.sha256((formal/source).read_bytes()).hexdigest() == expected, source
for source, expected in receipt['manuscript_source_sha256'].items():
    assert hashlib.sha256((ROOT.parent/source).read_bytes()).hexdigest() == expected, source
print('Thesis proof-status/source provenance check: PASS')

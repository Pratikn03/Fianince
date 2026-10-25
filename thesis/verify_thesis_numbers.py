"""Verify the thesis's own result files and the status claims that depend on them.

Inherited chapter numbers (Chapters 2-3) are checked by the paper verifier. This script checks the
artifacts of Chapters 4-5: the A1 diagnostics, the modulus certificates for Theorem thm:dich(iv),
the registered multi-asset and B3v2 results, the strategic counterexample, and the registration
state and results of Tests E1v2, D1, G1, V1 and E2, and the exploratory pilot. It does not certify inherited prose.
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
subprocess.run([sys.executable, str(ROOT / 'checks/export_philog_constants.py'), '--check'], check=True)
subprocess.run([sys.executable, str(ROOT / 'checks/check_examples.py')], check=True)
for lab in ('prop:nonlinear', 'cor:peak', 'sec:examples', 'sec:fw_literature'):
    assert f'\\label{{{lab}}}' in source, lab
assert '\\input{checks/philog_constants}' in source and '\\input{checks/examples_table}' in source
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
assert '\\input{checks/E1_numbers}' not in concl and '\\input{checks/E1v2_numbers}' in concl
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
    assert 'None has been run' in concl
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

# Tests D1, G1, V1: registered before data; results only after the single opening
for tid, spec, keys in (("D1", "D1_tagging_scaling", ("d1_sha256", "e1v2_pipeline_sha256", "binance_vision_sha256")),
                        ("G1", "G1_stress_guard", ("g1_sha256", "e2_analysis_sha256", "binance_vision_sha256")),
                        ("V1", "V1_kraken_venue", ("v1_sha256",))):
    sp = ROOT / f'checks/prereg/{spec}.json'
    assert digest(sp) == sp.with_suffix('.sha256').read_text().strip(), tid
    js = json.loads(sp.read_text())
    files = {"d1_sha256": "d1_tagging_scaling.py", "e1v2_pipeline_sha256": "e1v2_pipeline.py",
             "binance_vision_sha256": "binance_vision.py", "g1_sha256": "g1_stress_guard.py",
             "e2_analysis_sha256": "e2_analysis.py", "v1_sha256": "v1_kraken_venue.py"}
    for k in keys:
        assert digest(ROOT / 'evidence' / files[k]) == js[k], (tid, k)
    c = json.loads((ROOT / f'checks/prereg/{tid}_unlock.json').read_text())
    if c['opens'] == 0:
        assert not (ROOT / f'evidence/{tid}_results.json').exists()
    else:
        res = json.loads((ROOT / f'evidence/{tid}_results.json').read_text())
        assert res['spec_sha256'] == digest(sp) == c['spec_sha256'], tid
        assert f'\\input{{checks/{tid}_numbers}}' in concl, tid
    assert f'{tid}:' in concl
print('Tests D1, G1, V1 registrations: PASS')

# Results of D1, G1 and V1 reproduce from their files (D1 by its own check; G1 and V1 by recomputing verdict and numbers)
sys.path.insert(0, str(ROOT / 'evidence'))
subprocess.run([sys.executable, str(ROOT / 'evidence/d1_tagging_scaling.py'), '--check'], check=True)
import g1_stress_guard as G1mod  # noqa: E402
import v1_kraken_venue as V1mod  # noqa: E402
g1res = json.loads((ROOT / 'evidence/G1_results.json').read_text())
g1ev = g1res.get('evaluation', g1res)
assert G1mod.numbers_tex(g1ev) == (ROOT / 'checks/G1_numbers.tex').read_text()
assert g1ev['G1_pass'] == (max(g1ev['stress']['amp_vol']['ci']) < 0 and g1ev['p_holm'][0] < 0.05)
assert g1ev['G2_pass'] == (max(g1ev['stress']['guard']['ci']) < 0 and g1ev['p_holm'][1] < 0.05)
v1res = json.loads((ROOT / 'evidence/V1_results.json').read_text())
assert V1mod.verdict(v1res['evaluation']) == v1res['verdict']
assert V1mod.numbers_tex(v1res['evaluation'], v1res['verdict']) == (ROOT / 'checks/V1_numbers.tex').read_text()
print('Tests D1, G1, V1: results reproduce from their files: PASS')

# Test C2: registration, counter, and the evaluation recomputed from its per-symbol results
import c2_margin_vs_identify as C2mod  # noqa: E402
c2spec = ROOT / 'checks/prereg/C2_margin_vs_identify.json'
c2c = json.loads((ROOT / 'checks/prereg/C2_unlock.json').read_text())
c2res = json.loads((ROOT / 'evidence/C2_results.json').read_text())
assert c2c['opens'] == 1 and c2res['spec_sha256'] == digest(c2spec) == c2c['spec_sha256']
assert (ROOT / 'checks/prereg/C2_margin_vs_identify.sha256').read_text().strip() == digest(c2spec)
assert json.loads(c2spec.read_text())['c2_sha256'] == digest(ROOT / 'evidence/c2_margin_vs_identify.py')
re_ev = C2mod.evaluate(c2res['per_symbol'])
for k in ('decided', 'identified', 'mcnemar_b', 'mcnemar_c', 'P1_pass', 'P2_pass', 'P3_tagged_tighter', 'P3_pass'):
    assert re_ev[k] == c2res['evaluation'][k], ('C2', k)
assert C2mod.numbers_tex(c2res['evaluation']) == (ROOT / 'checks/C2_numbers.tex').read_text()
assert '\\input{checks/C2_numbers}' in concl and 'C2:' in concl
print('Test C2: registration and results reproduce from their files: PASS')

# Test O1: registration, counter, verdict and numbers recomputed from its result file
import o1_release_overshoot as O1mod  # noqa: E402
o1spec = ROOT / 'checks/prereg/O1_release_overshoot.json'
o1c = json.loads((ROOT / 'checks/prereg/O1_unlock.json').read_text())
o1res = json.loads((ROOT / 'evidence/O1_results.json').read_text())
assert o1c['opens'] == 1 and o1res['spec_sha256'] == digest(o1spec) == o1c['spec_sha256']
assert (ROOT / 'checks/prereg/O1_release_overshoot.sha256').read_text().strip() == digest(o1spec)
o1j = json.loads(o1spec.read_text())
assert o1j['o1_sha256'] == digest(ROOT / 'evidence/o1_release_overshoot.py')
assert o1j['pilot2b_sha256'] == digest(ROOT / 'evidence/pilot2b_announcements.py')
pr = o1res['primary']; va = o1res['validity']
assert pr['pass'] == (va['V1_ok'] and va['V2_ok'] and pr['upper95_one_sided'] < 0)
assert abs(pr['Abar_120'] - sum(v['A']['120'] for v in o1res['per_symbol'].values()) / len(o1res['per_symbol'])) < 1e-9
assert O1mod.numbers_tex(o1res) == (ROOT / 'checks/O1_numbers.tex').read_text()
assert '\\input{checks/O1_numbers}' in concl and 'O1:' in concl
print('Test O1: registration and results reproduce from their files: PASS')

# Test C3: registration, counter, and the evaluation recomputed from its per-symbol results
import c3_margin_more_days as C3mod  # noqa: E402
c3spec = ROOT / 'checks/prereg/C3_margin_more_days.json'
c3c = json.loads((ROOT / 'checks/prereg/C3_unlock.json').read_text())
c3res = json.loads((ROOT / 'evidence/C3_results.json').read_text())
assert c3c['opens'] == 1 and c3res['spec_sha256'] == digest(c3spec) == c3c['spec_sha256']
assert (ROOT / 'checks/prereg/C3_margin_more_days.sha256').read_text().strip() == digest(c3spec)
assert json.loads(c3spec.read_text())['c3_sha256'] == digest(ROOT / 'evidence/c3_margin_more_days.py')
re3 = C3mod.evaluate(c3res['per_symbol'])
for k in ('n_evaluable', 'decided', 'identified', 'mcnemar_b', 'mcnemar_c', 'P1_pass', 'P2_pass'):
    assert re3[k] == c3res['evaluation'][k], ('C3', k)
assert C3mod.numbers_tex(c3res['evaluation']) == (ROOT / 'checks/C3_numbers.tex').read_text()
assert '\\input{checks/C3_numbers}' in concl and 'C3:' in concl
print('Test C3: registration and results reproduce from their files: PASS')

# Chapter 5 extra numbers and the exploratory pilot (labelled exploratory, never confirmatory)
subprocess.run([sys.executable, str(ROOT / 'checks/export_results_extra.py'), '--check'], check=True)
pilot = json.loads((ROOT / 'evidence/pilot_after_e1v2_results.json').read_text())
assert pilot['kind'].startswith('EXPLORATORY')
assert '\\label{sec:ev_explore}' in concl and 'Nothing in this subsection is confirmatory evidence' in concl
print('Exploration after the tests: labelled exploratory: PASS')

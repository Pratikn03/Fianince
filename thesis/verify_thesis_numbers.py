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

# Test F1: registration, addendum A1, counter, and the evaluation recomputed from its per-symbol results
import f1_flagship as F1mod  # noqa: E402
from scipy import stats as _st  # noqa: E402
f1spec = ROOT / 'checks/prereg/F1_flagship.json'
f1c = json.loads((ROOT / 'checks/prereg/F1_unlock.json').read_text())
f1res = json.loads((ROOT / 'evidence/F1_results.json').read_text())
assert f1c['opens'] == 1 and f1res['spec_sha256'] == digest(f1spec) == f1c['spec_sha256']
assert (ROOT / 'checks/prereg/F1_flagship.sha256').read_text().strip() == digest(f1spec)
f1j = json.loads(f1spec.read_text())
for key, f in (('f1_sha256', 'f1_flagship.py'), ('c3_sha256', 'c3_margin_more_days.py'), ('c2_sha256', 'c2_margin_vs_identify.py'),
               ('pilot4_sha256', 'pilot4_curve_and_risk.py'), ('binance_vision_sha256', 'binance_vision.py')):
    assert f1j[key] == digest(ROOT / 'evidence' / f), ('F1', key)
a1 = ROOT / 'checks/prereg/F1_addendum_A1.json'; a1j = json.loads(a1.read_text())
assert (ROOT / 'checks/prereg/F1_addendum_A1.sha256').read_text().strip() == digest(a1)
assert a1j['f1_spec_sha256'] == digest(f1spec) and a1j['f1_addendum_sha256'] == digest(ROOT / 'evidence/f1_addendum.py')
assert all(sym.isascii() for sym in f1res['symbols']) and len(f1res['symbols']) == 30
fe = f1res['evaluation']; ev1 = {k: v for k, v in f1res['per_symbol'].items() if v.get('n_days', 0) >= 200 and 'M' in v}
dec1 = sum(v['decided'] for v in ev1.values()); b1 = sum(v['decided'] and not v['identified'] for v in ev1.values())
c1 = sum(v['identified'] and not v['decided'] for v in ev1.values())
assert (len(ev1), dec1, b1, c1) == (fe['n_evaluable'], fe['decided'], fe['mcnemar_b'], fe['mcnemar_c'])
assert abs(float(_st.binom.sf(dec1 - 1, len(ev1), 0.5)) - fe['p_raw'][0]) < 1e-12
assert abs(float(_st.binom.sf(b1 - 1, b1 + c1, 0.5)) - fe['p_raw'][1]) < 1e-12
assert fe['P1_pass'] == (dec1 >= fe['threshold_count'] and fe['p_holm'][0] < 0.05)
assert fe['P2_pass'] == (b1 > c1 and fe['p_holm'][1] < 0.05)
assert fe['P3_pass'] == (fe['p_holm'][2] < 0.05 and fe['risk']['coef_X'] < 0) and fe['risk']['p'] == fe['p_raw'][2]
assert F1mod.numbers_tex(fe) == (ROOT / 'checks/F1_numbers.tex').read_text()
assert '\\input{checks/F1_numbers}' in concl and 'F1:' in concl
print('Test F1: registration, addendum and results reproduce from their files: PASS')

# Test S1: registered before its data; until its result is committed, the counter must still be at 0 or 1 and the
# pipeline must match the registered hashes
s1spec = ROOT / 'checks/prereg/S1_fragility.json'; s1j = json.loads(s1spec.read_text())
assert (ROOT / 'checks/prereg/S1_fragility.sha256').read_text().strip() == digest(s1spec)
for key, f in (('s1_sha256', 's1_fragility.py'), ('c3_sha256', 'c3_margin_more_days.py'), ('c2_sha256', 'c2_margin_vs_identify.py'),
               ('pilot4_sha256', 'pilot4_curve_and_risk.py'), ('binance_vision_sha256', 'binance_vision.py')):
    assert s1j[key] == digest(ROOT / 'evidence' / f), ('S1', key)
s1c = json.loads((ROOT / 'checks/prereg/S1_unlock.json').read_text())
if (ROOT / 'evidence/S1_results.json').exists():
    import pandas as _pd  # noqa: E402
    import s1_fragility as S1mod  # noqa: E402
    s1res = json.loads((ROOT / 'evidence/S1_results.json').read_text())
    assert s1c['opens'] == 1 and s1res['spec_sha256'] == digest(s1spec) == s1c['spec_sha256']
    assert s1res['registration_commit'] == s1c['registration_commit']
    s1u = json.loads((ROOT / 'evidence/S1_universe.json').read_text()); assert s1u['symbols'] == s1res['symbols'] and s1u['seed'] == 20261107
    s1e = s1res['evaluation']
    re_s1 = S1mod.evaluate(_pd.read_csv(ROOT / 'evidence/S1_rows.csv.gz'), s1e['n_evaluable'])   # rows saved at 6 significant digits
    for k in ('stress_days', 'P1_pass', 'P2_pass', 'P3_pass', 'P4_pass'):
        assert re_s1[k] == s1e[k], ('S1', k)
    assert all(abs(a - b) < 0.005 for a, b in zip(re_s1['p_raw'], s1e['p_raw']))
    assert s1e['n_evaluable'] == sum('excluded' not in v for v in s1res['per_symbol'].values())
    assert S1mod.numbers_tex(s1e) == (ROOT / 'checks/S1_numbers.tex').read_text()
    assert '\\input{checks/S1_numbers}' in concl and 'S1: does the margin measure fragility?' in concl
else:
    assert s1c['opens'] in (0, 1) and 'S1: does the margin measure fragility? (registered, not yet run)' in concl
print('Test S1: registration and pipeline hashes: PASS')

# Test B1 (registered simulation): registration, counter, and the evaluation recomputed from its runs
import b1_ailoop as B1mod  # noqa: E402
b1spec = ROOT / 'checks/prereg/B1_ailoop.json'; b1j = json.loads(b1spec.read_text())
assert (ROOT / 'checks/prereg/B1_ailoop.sha256').read_text().strip() == digest(b1spec)
assert b1j['b1_sha256'] == digest(ROOT / 'evidence/b1_ailoop.py') and b1j['sim_sha256'] == digest(ROOT / 'evidence/ailoop_sim.py')
b1c = json.loads((ROOT / 'checks/prereg/B1_unlock.json').read_text())
if (ROOT / 'evidence/B1_results.json').exists():
    b1r = json.loads((ROOT / 'evidence/B1_results.json').read_text())
    assert b1c['opens'] == 1 and b1r['spec_sha256'] == digest(b1spec) == b1c['spec_sha256'] and b1r['seeds'] == [1001, 1100]
    re_b1 = B1mod.evaluate(b1r['runs'])
    for k in ('P1', 'P2', 'P3', 'P4'):
        assert re_b1[k]['pass'] == b1r['evaluation'][k]['pass'], ('B1', k)
    assert B1mod.numbers_tex(b1r['evaluation']) == (ROOT / 'checks/B1_numbers.tex').read_text()
print('Test B1: registration and results reproduce from their files: PASS')

import importlib.util as _ilu0  # noqa: E402
# Test B2 (registered, language-model desks): registration, counter, the evaluation recomputed from its runs, and the text
import b2_llm as B2mod  # noqa: E402
b2spec = ROOT / 'checks/prereg/B2_llm.json'; b2j = json.loads(b2spec.read_text())
assert (ROOT / 'checks/prereg/B2_llm.sha256').read_text().strip() == digest(b2spec)
for _k, _f in (('b2_sha256', 'b2_llm.py'), ('llm_sha256', 'llm_ailoop.py'), ('sim_sha256', 'ailoop_sim.py'), ('b1_sha256', 'b1_ailoop.py')):
    assert b2j[_k] == digest(ROOT / 'evidence' / _f), ('B2 pipeline changed', _f)
b2c = json.loads((ROOT / 'checks/prereg/B2_unlock.json').read_text())
if (ROOT / 'evidence/B2_results.json').exists():
    b2r = json.loads((ROOT / 'evidence/B2_results.json').read_text())
    assert b2c['opens'] == 1 and b2r['spec_sha256'] == digest(b2spec) == b2c['spec_sha256']
    _m = b2r['meta']
    re_b2 = B2mod.evaluate(b2r['runs'], b2r['twins'], _m['parse_failures'] / _m['llm_calls'] > 0.05)
    for k in ('P1', 'P2', 'P3', 'P4'):
        assert re_b2[k]['pass'] == b2r['evaluation'][k]['pass'], ('B2', k)
    assert B2mod.numbers_tex(b2r['evaluation'], _m) == (ROOT / 'checks/B2_numbers.tex').read_text()
    _spec2 = _ilu0.spec_from_file_location("b2_extra", ROOT / "checks/b2_extra_numbers.py")
    _b2x = _ilu0.module_from_spec(_spec2); _spec2.loader.exec_module(_b2x)
    assert _b2x.numbers_tex(b2r) == (ROOT / 'checks/B2_extra.tex').read_text(), 'B2 extra macros differ from the result file'
    _ai = (ROOT / 'ch4b_aiagents.tex').read_text()
    assert '\\input{checks/B2_numbers}' in _ai and '\\input{checks/B2_extra}' in _ai and 'pending' not in _ai.split('sec:ai_b2')[1].split('sec:ai_limits')[0]
else:
    assert b2c['opens'] == 0
print('Test B2: registration and results reproduce from their files: PASS')

# Tests R1 and H1: registered before their data; pipeline hashes, counters and the text's status
for name, specf, keys, counter, res, para in (
        ('R1', 'R1_absresp', (('r1_sha256', 'r1_absresp.py'), ('s1_sha256', 's1_fragility.py'), ('c3_sha256', 'c3_margin_more_days.py'),
                              ('c2_sha256', 'c2_margin_vs_identify.py'), ('pilot4_sha256', 'pilot4_curve_and_risk.py'),
                              ('binance_vision_sha256', 'binance_vision.py')), 'R1_unlock', 'R1_results', 'R1: does the absolute response measure risk? (registered, not yet run)'),
        ('H1', 'H1_hyperliquid', (('h1_sha256', 'h1_hyperliquid.py'), ('c3_sha256', 'c3_margin_more_days.py'),
                                  ('c2_sha256', 'c2_margin_vs_identify.py'), ('pilot4_sha256', 'pilot4_curve_and_risk.py')),
         'H1_unlock', 'H1_results', 'H1: real agents (prospective, opens 10 December 2026)')):
    sp = ROOT / f'checks/prereg/{specf}.json'; sj = json.loads(sp.read_text())
    assert (ROOT / f'checks/prereg/{specf}.sha256').read_text().strip() == digest(sp), name
    for key, f in keys:
        assert sj[key] == digest(ROOT / 'evidence' / f), (name, key)
    cj = json.loads((ROOT / f'checks/prereg/{counter}.json').read_text())
    if (ROOT / f'evidence/{res}.json').exists():
        rj = json.loads((ROOT / f'evidence/{res}.json').read_text())
        assert cj['opens'] == 1 and rj['spec_sha256'] == digest(sp) == cj['spec_sha256'], name
        assert rj['registration_commit'] == cj['registration_commit'], name
        if name == 'R1':
            import pandas as _pd  # noqa: E402
            import r1_absresp as R1mod  # noqa: E402
            s1syms = set(json.loads((ROOT / 'evidence/S1_universe.json').read_text())['symbols'])
            assert not (set(rj['symbols']) & s1syms), 'R1 and S1 share symbols'
            re_r1 = R1mod.evaluate(_pd.read_csv(ROOT / 'evidence/R1_rows.csv.gz'), rj['evaluation']['n_evaluable'])
            for k in ('P1_pass', 'P2_pass', 'P3_pass'):
                assert re_r1[k] == rj['evaluation'][k], ('R1', k)
            assert all(abs(a - b) < 0.005 for a, b in zip(re_r1['p_raw'], rj['evaluation']['p_raw']))
            assert R1mod.numbers_tex(rj['evaluation']) == (ROOT / 'checks/R1_numbers.tex').read_text()
            assert '\\input{checks/R1_numbers}' in concl and 'R1: does the absolute response measure risk?' in concl
    else:
        assert cj['opens'] in (0, 1) and para in concl, name
    print(f'Test {name}: registration and pipeline hashes: PASS')

# Chapter 5 extra numbers and the exploratory pilot (labelled exploratory, never confirmatory)
subprocess.run([sys.executable, str(ROOT / 'checks/export_results_extra.py'), '--check'], check=True)
pilot = json.loads((ROOT / 'evidence/pilot_after_e1v2_results.json').read_text())
assert pilot['kind'].startswith('EXPLORATORY')
assert '\\label{sec:ev_explore}' in concl and 'Nothing in this subsection is confirmatory evidence' in concl
print('Exploration after the tests: labelled exploratory: PASS')

# Section "Agents who game the monitor": the printed macros are regenerated from the result file
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("antigaming_check", ROOT / "checks/antigaming_numeric_check.py")
_ag = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_ag)
_agres = json.loads((ROOT / "checks/antigaming_numeric_check.json").read_text())
assert _ag.numbers_tex(_agres) == (ROOT / "checks/antigaming_numbers.tex").read_text(), "antigaming macros differ from their result file"
assert _agres["part2_throttle_equilibrium"]["M_equilibrium"] > _agres["part2_throttle_equilibrium"]["M_min"]
assert "\\input{checks/antigaming_numbers}" in (ROOT / "ch4_paper3.tex").read_text()
print("Agents who game the monitor: numbers reproduce from their file: PASS")


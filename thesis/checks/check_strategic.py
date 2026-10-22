"""Exact rational diagnostics for the written strategic counterexample.
No empirical data or simulation; the universal claim is checked separately in Lean.
"""
from fractions import Fraction as F
import json
from pathlib import Path


def utility(q):
    admitted = F(1) if q <= F(1, 2) else F(0)
    return (1-admitted)*(1-q)


rows = []
for j in range(17):
    q = F(j, 16)
    deviation = F(3, 4) if q <= F(1, 2) else (q+F(1, 2))/2
    ok = 0 <= deviation <= 1 and utility(deviation) > utility(q)
    assert ok
    rows.append({'q':str(q), 'deviation':str(deviation), 'utility':str(utility(q)),
                 'deviation_utility':str(utility(deviation)), 'profitable':ok})
r = {'interpretation':'Exact diagnostic witnesses; the Lean theorem supplies the universal quantifier.',
     'threshold':'1/2', 'impact':'1/4', 'shock_bound':'1', 'admitted_loss_budget':'2/7',
     'cost':'0 (convex)', 'all_deviations_profitable':all(x['profitable'] for x in rows),
     'pure_equilibrium_exists':False, 'rows':rows}
Path(__file__).with_name('R_strategic.json').write_text(json.dumps(r, indent=2)+'\n')
print('Strategic counterexample rational diagnostics: PASS')

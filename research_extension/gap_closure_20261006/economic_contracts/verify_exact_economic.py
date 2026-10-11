"""Exact symbolic Schur identities and rational in-model risk counterexample."""
from pathlib import Path
import sympy as sp,json
HERE=Path(__file__).resolve().parent

def run():
    k,phi,q,eta=sp.symbols('k phi q eta',real=True)
    J=sp.Matrix([[1-k*phi,k*q],[eta*(1-k*phi),1-eta+eta*k*q]])
    T=sp.trace(J);d=J.det()
    expected=[k*eta*(phi-q),4-2*eta-k*((2-eta)*phi-eta*q),eta+(1-eta)*k*phi]
    assert all(sp.expand(x-y)==0 for x,y in zip([1-T+d,1+T+d,1-d],expected))
    low=J.subs({k:sp.Rational(1,10),phi:1,q:sp.Rational(1,10),eta:sp.Rational(9,10)})
    high=J.subs({k:1,phi:1,q:sp.Rational(1,10),eta:sp.Rational(9,10)})
    low_column=(low[:,0].T*low[:,0])[0];high_squared=sum(v*v for v in high)
    assert low_column==sp.Rational(14661,10000)>1
    assert high_squared==sp.Rational(461,10000)<1 and high[:,0]==sp.zeros(2,1)
    checks={}
    for label,mat in [('lower_impact',low),('higher_impact',high)]:
        tr=sp.trace(mat);det=mat.det();conditions=[1-tr+det,1+tr+det,1-det]
        assert all(v>0 for v in conditions);checks[label]=[str(v) for v in conditions]
    result={'scope':'Exact rational constructed counterexample and symbolic identities; no market calibration','jury_identities':[str(v) for v in expected],'low_impact_matrix':[[str(v) for v in row] for row in low.tolist()],'high_impact_matrix':[[str(v) for v in row] for row in high.tolist()],'low_column_squared_norm':str(low_column),'high_operator_squared_norm':str(high_squared),'jury_positive_exact':checks,'low_peak_lower_bound':'sqrt(14661)/100 > 1','high_peak_exact':'1, by operator contraction at every positive power and identity at t=0'}
    (HERE/'exact_economic_witnesses.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: symbolic Jury identities and exact rational stable amplification reversal')
if __name__=='__main__':run()

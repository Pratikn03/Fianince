"""Exact rational infinite-tail certificates for constructed scalar-output examples."""
from pathlib import Path
import json,math
import sympy as sp
HERE=Path(__file__).resolve().parent

def certificate(J,C,N=150):
    power=sp.eye(J.rows);rows=[];h=None;frobenius=None
    for t in range(N+512):
        row=C*power;squared=sum(v*v for v in row);rows.append(squared)
        if t>0 and h is None:
            norm_squared=sum(v*v for v in power)
            if norm_squared<1:h=t;frobenius=norm_squared
        if h is not None and t>=N+h-1:break
        power=power*J
    if h is None:raise ValueError('No rational block certificate found')
    peak=max(rows[:N]);index=rows[:N].index(peak);tail=max(rows[N:N+h])
    if tail>peak:raise ValueError('Prefix peak is not certified')
    def fraction(x):return {'numerator':str(sp.numer(x)),'denominator':str(sp.denom(x))}
    return {'peak_step':index,'peak_squared':fraction(peak),'tail_squared':fraction(tail),'block_frobenius_squared':fraction(frobenius),'block_h':h,'prefix_N':N,'exact_inequalities_verified':True,'M_C':float(sp.sqrt(peak)),'tail_upper':float(sp.sqrt(tail)),'block_norm_upper':float(sp.sqrt(frobenius))}

def run():
    result=json.loads((HERE/'risk_results.json').read_text());certificates={};R=sp.Rational
    for key in ['hedged_portfolio','structural_market_family','symmetric_impact_family']:
        family=[]
        for row in result[key]:
            theta=R(str(row['theta']))
            if key=='hedged_portfolio':
                J=sp.Matrix([[R(17,20),2,0],[0,R(17,20),0],[0,theta,R(17,20)]]);C=sp.Matrix([[1,0,-1]])
            elif key=='structural_market_family':
                J=sp.Matrix([[R(1,2),R(1,5),0,0],[R(1,10),R(21,25),0,0],[0,theta/5,R(1,2),R(1,5)],[0,theta/25,R(1,10),R(21,25)]]);C=sp.Matrix([[0,0,1,0]])
            else:
                J=sp.Matrix([[R(1,2),R(1,5),0,1/(10*theta)],[R(1,10),R(21,25),0,1/(50*theta)],[0,theta/10,R(1,2),R(1,5)],[0,theta/50,R(1,10),R(21,25)]]);C=sp.Matrix([[0,0,1,0]])
            exact=certificate(J,C)
            assert math.isclose(row['M_C'],exact['M_C'],rel_tol=1e-12,abs_tol=1e-12)
            row['exact_tail_certificate']=exact
            row.update(M_C=exact['M_C'],peak_step=exact['peak_step'],safe_radius_B1=1/exact['M_C'],tail_upper=exact['tail_upper'],block_h=exact['block_h'],block_norm=exact['block_norm_upper'])
            family.append(dict(theta=str(theta),**exact))
        certificates[key]=family
    (HERE/'exact_tail_certificates.json').write_text(json.dumps({'scope':'Exact rational matrix/row-square comparisons certify the constructed examples; empirical floating-point matrices and unknown parameters need their own roundoff/model bounds','families':certificates},indent=2)+'\n')
    (HERE/'risk_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Fifteen exact rational prefix/block/tail certificates passed')
if __name__=='__main__':run()

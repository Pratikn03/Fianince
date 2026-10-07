"""Exact symbolic witnesses for bounded-cohort audited-state identification.
Uses established Hankel/annihilating-filter algebra; not a new Prony algorithm.
"""
from pathlib import Path
import json
import sympy as sp
HERE=Path(__file__).resolve().parent

def deconvolve(x,u):
    if len(x)!=len(u) or x[0]==0:raise ValueError('Need equal-length exact sequences and nonzero first input')
    moments=[]
    for n in range(len(x)):
        moments.append(sp.cancel((u[n]-sum(moments[k]*x[n-k] for k in range(n)))/x[0]))
    return moments

def recover(moments,Kmax):
    if len(moments)<2*Kmax:raise ValueError('Insufficient exact moments')
    H=sp.Matrix(Kmax,Kmax,lambda i,j:moments[i+j]);K=H.rank()
    if K==0:return {'K':0,'rates':[],'coefficients':[],'weights':[],'annihilator':[sp.Integer(1)]}
    small=sp.Matrix(K,K,lambda i,j:moments[i+j]);rhs=sp.Matrix([-moments[K+i] for i in range(K)])
    coefficients=list(small.inv()*rhs);r=sp.symbols('r');polynomial=sp.Poly(r**K+sum(coefficients[i]*r**i for i in range(K)),r)
    roots=sp.polys.polytools.ground_roots(polynomial)
    if len(roots)!=K or any(v!=1 for v in roots.values()):raise ValueError('This witness implementation requires distinct rational roots; theorem covers exact real roots')
    memory=sorted(roots);V=sp.Matrix(K,K,lambda i,j:memory[j]**i);c=list(V.inv()*sp.Matrix(moments[:K]));rates=[1-r for r in memory];weights=[sp.cancel(v/eta) for v,eta in zip(c,rates)]
    return {'K':K,'rates':rates,'coefficients':c,'weights':weights,'annihilator':coefficients+[sp.Integer(1)]}

def witness(cohorts,Kmax):
    a=sp.Rational(1,2);kappa=sp.Rational(1);ys=[sp.Integer(0)]*len(cohorts);x=[];u=[];xp=sp.Integer(0);up=sp.Integer(0)
    for t in range(1,2*Kmax+1):
        shock=sp.Rational((-1)**t*(t+1),2*t+1);xp=a*xp+kappa*up+shock
        ys=[(1-eta)*y+eta*xp for y,(eta,q) in zip(ys,cohorts)];up=sum(q*y for y,(eta,q) in zip(ys,cohorts));x.append(xp);u.append(up)
    moments=deconvolve(x,u);expected=[sum(eta*q*(1-eta)**j for eta,q in cohorts) for j in range(2*Kmax)]
    assert moments==expected
    result=recover(moments,Kmax);merged={}
    for eta,q in cohorts:merged[eta]=merged.get(eta,0)+q
    merged={eta:q for eta,q in merged.items() if q!=0};decoded=dict(zip(result['rates'],result['weights']))
    assert decoded==merged
    return {'cohorts':[(str(eta),str(q)) for eta,q in cohorts],'Kmax':Kmax,'moments':list(map(str,moments)),'recovered':{k:[str(v) for v in val] if isinstance(val,list) else val for k,val in result.items()}}

def run():
    R=sp.Rational
    cases=[([(R(1,5),R(2,5)),(R(3,5),R(1,10))],2),([(R(1,5),R(1)),(R(2,5),R(-1,2))],3),([(R(1,5),R(1)),(R(1,5),R(-1)),(R(3,5),R(1,4))],3),([(R(1,5),R(1)),(R(1,5),R(-1))],2)]
    rows=[witness(*c) for c in cases]
    (HERE/'multicohort_exact_witnesses.json').write_text(json.dumps({'scope':'Symbolic witnesses: distinct rates, signed weights with zero immediate response, merged cancellation, and no-feedback case; exact information contract only','rows':rows},indent=2)+'\n')
    print('Four exact multicohort witnesses passed; deconvolution, rank, roots and merged weights verified')
if __name__=='__main__':run()

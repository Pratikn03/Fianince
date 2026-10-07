"""Exact algebraic witness for the distinction between observation contracts.
Fraction arithmetic is illustrative; it is not a floating-point market certifier.
"""
from fractions import Fraction
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def decode_exact(x1,u1,x2,u2,a,kappa):
    if not all(isinstance(v,Fraction) for v in [x1,u1,x2,u2,a,kappa]):raise TypeError('Exact rational inputs required for this witness')
    if x1==0:raise ValueError('Degenerate witness; under continuous innovations this is a probability-zero event')
    if u1==0:return {'q':Fraction(0),'eta':None,'stable':True,'reason':'q=0 and maintained a in [0,1), eta in (0,1)'}
    theta=u1/x1
    memory=(u2-theta*x2)/u1
    eta=1-memory
    if not 0<eta<1:raise ValueError('Outside assumed update class')
    q=theta/eta;Q=kappa*q
    stable=-(2-eta)*(1+a)/eta<Q<1-a
    return {'q':q,'eta':eta,'stable':stable,'Q':Q}

def path(a,kappa,eta,q,w1,w2):
    x1=w1;u1=eta*q*x1;x2=a*x1+kappa*u1+w2;u2=(1-eta)*u1+eta*q*x2
    return x1,u1,x2,u2

def run():
    rows=[]
    for a,kappa,eta,q in [(Fraction(1,2),Fraction(1),Fraction(1,5),Fraction(2,5)),(Fraction(1,2),Fraction(1),Fraction(1,5),Fraction(1,2)),(Fraction(1,2),Fraction(1),Fraction(1,5),Fraction(3,5)),(Fraction(1,2),Fraction(1),Fraction(1,5),Fraction(-14)),(Fraction(1,2),Fraction(1),Fraction(1,5),Fraction(0))]:
        obs=path(a,kappa,eta,q,Fraction(2,3),Fraction(-1,7));decoded=decode_exact(*obs,a,kappa)
        assert decoded['q']==q
        if q:assert decoded['eta']==eta
        rows.append({'parameters':{k:str(v) for k,v in zip(['a','kappa','eta','q'],[a,kappa,eta,q])},'observations':list(map(str,obs)),'decoded':{k:str(v) for k,v in decoded.items()}})
    (HERE/'full_observation_witness.json').write_text(json.dumps({'scope':'Exact rational witnesses for a proved noiseless (x,u) single-cohort contract; does not apply to anonymous price proxies or noisy disclosed states','rows':rows},indent=2)+'\n')
    print('Five exact witnesses passed: stable, unit boundary, explosive, signed oscillatory, zero feedback')
if __name__=='__main__':run()

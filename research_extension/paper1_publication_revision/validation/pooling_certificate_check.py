"""Exact rational checks of the block-Hankel certificate; no optimizer or live data."""
from pathlib import Path
import json, math
import sympy as sp

rows=[]
for K in range(2,9):
    for D in range(1,K+1):
        q=math.ceil(K/D);L=K-1+q
        s=[sp.Rational(2*i-K+1,K+1) for i in range(K)]
        W=[[sp.Rational(1,100)+(1 if i%D==d else 0) for i in range(K)] for d in range(D)]
        moments=[[sum(W[d][i]*s[i]**m for i in range(K)) for m in range(L+1)] for d in range(D)]
        H=sp.Matrix([[moments[d][j+l] for l in range(K)] for d in range(D) for j in range(q)])
        b=sp.Matrix([-moments[d][j+K] for d in range(D) for j in range(q)])
        assert H.rank()==K
        c=(H.T*H).inv()*H.T*b
        z=sp.Symbol('z');poly=sp.Poly(sp.prod(z-node for node in s),z)
        assert all(c[j]==poly.nth(j) for j in range(K))
        V=sp.Matrix([[node**j for node in s] for j in range(K)])
        assert all(V.inv()*sp.Matrix(moments[d][:K])==sp.Matrix(W[d]) for d in range(D))
        rows.append(dict(K=K,D=D,moment_order=L,rank=K,annihilator_exact=True,weights_exact=True))
# A positive-weight rank-deficient case: identical market allocations need more moments.
K,D,L=4,2,5
s=[sp.Rational(i,5) for i in range(1,5)]
m=[sum(x**j for x in s) for j in range(L+1)]
H=sp.Matrix([[m[j+l] for l in range(K)] for _ in range(D) for j in range(2)])
assert H.rank()==2<K
out={'passed':True,'exact_reconstructions':len(rows),'rows':rows,
     'rank_deficient_positive_example':{'K':K,'D':D,'L':L,'rank':int(H.rank())},
     'scope':'Exact algebraic checks; proof of genericity and compact inverse is in the manuscript.'}
path=Path(__file__).with_name('pooling_certificate_results.json')
path.write_text(json.dumps(out,indent=2)+'\n')
print('PASS:',len(rows),'exact pooled reconstructions; positive rank-deficient control.')

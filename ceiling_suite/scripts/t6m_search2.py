import numpy as np, sys
exec(open('t6m_search.py').read().split('rng=np.random')[0])
rng=np.random.default_rng(1); found=[]; n=0
for i in range(300000):
    a=rng.uniform(0.0,0.999); kappa=1.0; r=rng.uniform(0.001,1); eta=10**rng.uniform(-3,0)
    phi=rng.uniform(-3,3)*rng.choice([0,1]); eps=rng.uniform(-0.5,0.5)
    q=10**rng.uniform(-3,2)          # momentum only
    C3=phi*eps+kappa**2*eta*q-(1-a)*kappa
    if C3>0: continue
    if max(abs(np.linalg.eigvals(J(a,phi,kappa,r,eps,eta,q))))>=0.9999: continue
    n+=1
    h=imp(a,phi,kappa,r,eps,eta,q,L=2000)
    if np.nanmax(h)>h[0]*(1+1e-9):
        found.append((h.max()/h[0],a,phi,r,eps,eta,q,C3,phi*eps,int(np.argmax(h))))
print("stable C3<=0 draws:",n,"counterexamples:",len(found))
for f in sorted(found,reverse=True)[:12]: print(np.round(f,5))

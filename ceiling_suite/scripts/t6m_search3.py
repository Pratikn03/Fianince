import numpy as np
exec(open('t6m_search.py').read().split('rng=np.random')[0])
rng=np.random.default_rng(2); found=[]; n=0; near=[]
for i in range(400000):
    a=rng.uniform(0.0,0.999); kappa=1.0; r=10**rng.uniform(-3,0); eta=10**rng.uniform(-3,0)
    s=rng.choice([-1,1]); phi=s*10**rng.uniform(-3,0.7); eps=s*10**rng.uniform(-3,0)   # phi*eps >= 0
    if rng.random()<0.2: phi=0.0
    q=10**rng.uniform(-3,2)
    C3=phi*eps+kappa**2*eta*q-(1-a)*kappa
    if C3>0 or C3<-0.05*rng.random(): continue          # concentrate near the boundary
    if max(abs(np.linalg.eigvals(J(a,phi,kappa,r,eps,eta,q))))>=0.99999: continue
    n+=1
    h=imp(a,phi,kappa,r,eps,eta,q,L=4000)
    if np.nanmax(h)>h[0]*(1+1e-10):
        found.append((h.max()/h[0],a,phi,r,eps,eta,q,C3,int(np.argmax(h))))
print("stable C3<=0, phi*eps>=0, q>0 draws:",n,"counterexamples:",len(found))
for f in sorted(found,reverse=True)[:12]: print(np.round(f,6))

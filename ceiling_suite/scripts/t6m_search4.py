import numpy as np
exec(open('t6m_search.py').read().split('rng=np.random')[0])
rng=np.random.default_rng(3); found=[]; n=0; viol_bound=0; nb=0
for i in range(400000):
    a=rng.uniform(0.0,0.999); kappa=10**rng.uniform(-1,1); r=10**rng.uniform(-3,0); eta=10**rng.uniform(-3,0)
    q=rng.choice([-1,1])*10**rng.uniform(-3,2); phi=rng.uniform(-3,3); eps=rng.uniform(-0.5,0.5)
    depthfree = rng.random()<0.5
    if depthfree: phi=eps=0.0
    if max(abs(np.linalg.eigvals(J(a,phi,kappa,r,eps,eta,q))))>=0.99999: continue
    C3=phi*eps+kappa**2*eta*q-(1-a)*kappa
    Cbar=abs(phi*eps)*(1+kappa*abs(q)/r)+kappa**2*abs(q)-(1-a)*kappa
    h=imp(a,phi,kappa,r,eps,eta,q,L=3000)
    if not np.all(np.isfinite(h)): continue
    if Cbar<=0:
        nb+=1
        if np.max(np.abs(h))>kappa*(1+1e-9): viol_bound+=1
    if depthfree and q>0 and C3<=0:
        n+=1
        if h.max()>h[0]*(1+1e-10): found.append((h.max()/h[0],a,kappa,eta,q,C3))
print("bound check: draws with Cbar<=0:",nb,"violations of sup|h|<=kappa:",viol_bound)
print("depth-free, q>0, C3<=0 draws:",n,"overshoots:",len(found))
for f in sorted(found,reverse=True)[:8]: print(np.round(f,6))

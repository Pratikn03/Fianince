import numpy as np
exec(open('t6m_search.py').read().split('rng=np.random')[0])
rng=np.random.default_rng(7); n=0; viol=0; c3pos=0; worst=0
for i in range(60000):
    a=rng.uniform(0,0.999); kappa=10**rng.uniform(-1,1); eta=10**rng.uniform(-3,0); q=10**rng.uniform(-3,2)
    if max(abs(np.linalg.eigvals(J(a,0,kappa,0.5,0,eta,q))))>=0.99999: continue
    n+=1; h=imp(a,0,kappa,0.5,0,eta,q,L=800)
    rho=max(abs(np.linalg.eigvals(J(a,0,kappa,0.5,0,eta,q))))
    if kappa**2*eta*q-(1-a)*kappa>0: c3pos+=1
    ratio=np.max(h[1:]/(kappa*rho**np.arange(1,800)))
    worst=max(worst,ratio)
    if np.max(h[1:])>kappa: viol+=1
print("stable depth-free momentum draws:",n,"overshoots:",viol,"C3>0:",c3pos,"max h_k/(kappa rho^k):",worst)

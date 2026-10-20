import numpy as np
import numpy as np
def imp(a,phi,kappa,r,eps,eta,q,L=3000):
    x=np.zeros(L); d=np.zeros(L); f=np.zeros(L)
    for t in range(L):
        if t>0: f[t]=(1-eta)*f[t-1]+eta*q*x[t-1]
        tot=(1.0 if t==0 else 0.0)+f[t]
        x[t]=(a*x[t-1]+phi*d[t-1] if t else 0)+kappa*tot
        d[t]=((1-r)*d[t-1] if t else 0)+eps*tot
    return x
def J(a,phi,kappa,r,eps,eta,q):
    # state (x,d,f): f_t=(1-eta)f+eta q x ; x_t = a x + phi d + kappa f_t ; d_t=(1-r)d+eps f_t
    F=np.array([[0,0,0],[0,0,0],[eta*q,0,1-eta]],float)
    M=np.zeros((3,3)); M[2]=[eta*q,0,1-eta]
    M[0]=[a+kappa*eta*q, phi, kappa*(1-eta)]
    M[1]=[eps*eta*q, 1-r, eps*(1-eta)]
    return M
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

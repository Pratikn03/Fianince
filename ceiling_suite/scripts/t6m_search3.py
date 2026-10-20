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

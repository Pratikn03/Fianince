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
rng=np.random.default_rng(0); found=[]
for i in range(200000):
    a=rng.uniform(0.5,0.999); kappa=1.0; r=rng.uniform(0.001,1); eta=10**rng.uniform(-3,0)
    phi=rng.uniform(-1,1)*rng.choice([0,1]); eps=rng.uniform(-0.3,0.3)
    q=rng.uniform(-1,1)*10**rng.uniform(-2,2)
    C3=phi*eps+kappa**2*eta*q-(1-a)*kappa
    if C3>0: continue
    if max(abs(np.linalg.eigvals(J(a,phi,kappa,r,eps,eta,q))))>=0.9999: continue
    h=imp(a,phi,kappa,r,eps,eta,q,L=1500)
    if np.nanmax(h)>h[0]*(1+1e-9):
        found.append((h.max()/h[0],a,phi,r,eps,eta,q,C3,int(np.argmax(h))))
print(len(found))
for f in sorted(found,reverse=True)[:10]: print(np.round(f,5))

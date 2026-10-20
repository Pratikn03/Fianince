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

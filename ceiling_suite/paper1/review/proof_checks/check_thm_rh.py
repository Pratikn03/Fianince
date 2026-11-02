import numpy as np, scipy.linalg as sl, json
rng=np.random.default_rng(7); viol=0; worst=np.inf; trials=0
for inst in range(60):
    L=rng.integers(5,12); n=L-1
    E=np.zeros((L,n)); 
    for j in range(n): E[j,j]=1; E[j+1,j]=-1
    A=rng.normal(size=(n,n)); G=A@A.T+0.5*np.eye(n)
    B=rng.normal(size=(n,rng.integers(2,n+1))); M=B@B.T
    lam,V=sl.eigh(M,G)  # G-orthonormal
    if lam[-3]>=lam[-2]-1e-9: continue
    creq=rng.uniform(0.5,5); cfee=rng.uniform(0.01,2)
    def bound():
        best=np.inf
        for th in np.linspace(0,np.pi,721,endpoint=False):
            d=np.cos(th)*V[:,-2]+np.sin(th)*V[:,-1]; lt=lam[-2]*np.cos(th)**2+lam[-1]*np.sin(th)**2
            s=np.sign(E@d); F=cfee*np.sqrt(creq/lt)*np.abs(E@d).sum()
            W=cfee**2*sum((s@E@V[:,j])**2/(1-lam[j]/lt) for j in range(n-2))
            g=lt*lam[-3]/((lt-lam[-3])*creq)
            xs=np.linspace(0,10,4001); psi=np.min(xs**2+np.maximum(F*np.maximum(1-g*xs**2,0)-np.sqrt(W)*xs,0))
            best=min(best,creq/lt+psi)
        return best
    C=bound()
    for _ in range(300):
        c=rng.normal(size=n); q=c@np.diag(lam)@c
        if q<=1e-12: continue
        c*=np.sqrt(creq/q)*rng.uniform(1,1.5)   # feasible: sum lam c^2 >= creq
        u=V@c; v=E@u; Lv=u@G@u
        val=Lv+cfee*np.abs(v).sum(); trials+=1
        worst=min(worst,val/C)
        if val < C*(1-1e-6): viol+=1
json.dump(dict(trials=trials,violations=viol,min_ratio=worst),open('/tmp/claude-0/rh/rh_check.json','w'))
print(trials,viol,worst)

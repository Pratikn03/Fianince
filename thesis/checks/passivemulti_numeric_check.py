import numpy as np
rng=np.random.default_rng(1)
def check(rho, groots, T=200000):
    g=np.poly1d([1.0])
    for r in groots: g=g*np.poly1d([-1/r,1.0])   # (1 - z/r)
    f=g*np.poly1d([-rho,1.0])
    c=f.coeffs[::-1]          # c[0]=1, c[k] coefficient of z^k
    phi=np.real(-c[1:])       # x_{t+1}=sum phi_i x_{t-i}
    p=len(groots); L=p+1
    # exact tau^2 via spectral integral minimisation (numerical)
    lam=np.linspace(-np.pi,np.pi,200001); z=np.exp(-1j*lam)
    s=1/(2*np.pi*np.abs(np.polyval(f.coeffs, z))**2)
    # regressors x_t, dx_t..dx_{t-p+1}: build Gamma via spectral integration
    fil=[np.ones_like(z)]+[z**(i-1)-z**i for i in range(1,p+1)]
    G=np.array([[np.trapezoid((a*np.conj(b)*s).real,lam) for b in fil] for a in fil])
    V=np.linalg.inv(G)[0,0]
    M=f(1.0); Gm=np.max(np.abs(np.polyval(g.coeffs,z))); gam=min(abs(r) for r in groots)-1
    C=4*p*p*(p+1)*(1+np.pi**2)*Gm**2/g(1.0)
    Cbig=4*p*p*(p+1)*(1+np.pi**2)*4**p*((1+gam)/gam)**p
    # simulation
    e=rng.normal(size=T); x=np.zeros(T)
    for t in range(L,T-1): x[t+1]=phi@x[t-np.arange(L)]+e[t+1]
    X=np.column_stack([x[L+p:-1]]+[x[L+p+1-i:len(x)-i]-x[L+p-i:len(x)-i-1] for i in range(1,p+1)])
    y=x[L+p+1:]-x[L+p:-1]
    b,res,*_=np.linalg.lstsq(X,y,rcond=None); r=y-X@b; s2=r.var()
    Vhat=s2*np.linalg.inv(X.T@X/len(y))[0,0]
    print(f"rho={rho} M={M:.4f} Mhat={-b[0]:.4f} V_exact={V:.4f} V_sim={Vhat:.4f} V/M={V/M:.2f} bound(G)={C:.0f} bound(gamma)={Cbig:.0f}")
for rho in (0.9,0.97,0.99):
    check(rho,[2.0,-3.0]); check(rho,[1.5+1j,1.5-1j])

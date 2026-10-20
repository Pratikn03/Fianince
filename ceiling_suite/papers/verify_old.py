import numpy as np
from scipy.stats import norm
a,k,q,eta,sig=0.5,0.8,0.2,0.4,0.01
def imp(ws,rs,L=4000):
    # price-first: x_t = a x_{t-1} + k*sum q_i y_{i,t-1} + k v_t ; y_i,t=(1-eta_i)y+eta_i x_t
    K=len(ws); x=np.zeros(L); y=np.zeros(K); h=[]
    xp=0
    for t in range(L):
        xt=a*xp+k*np.dot(ws,y)+(k if t==0 else 0)
        y=(1-rs)*y+rs*xt  # rs here = eta
        h.append(xt); xp=xt
    return np.array(h)
d=0.05
h0=imp(np.array([q]),np.array([eta])); h1=imp(np.array([q/2,q/2]),np.array([eta-d,eta+d]))
print("h0[:4]",h0[:4],"d2",h1[2]-h0[2],"-k2 q d2",-k*k*q*d*d)
om=np.linspace(0,np.pi,200001)
E=np.exp(-1j*np.outer(om,np.arange(len(h0))))
H0=E@h0; H1=E@h1
for name,H in [("H0",H0),("H1",H1)]:
    g=H.real-k/2
    ratio=g/np.abs(H1-H0)**2
    i=np.argmin(ratio[1:])+1
    z=norm.ppf(0.95)
    print(name,"min g",g.min(),"C*=",4*sig**2*z**2*ratio[i],"omega",om[i])

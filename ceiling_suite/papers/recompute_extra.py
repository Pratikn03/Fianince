import numpy as np, json
from scipy.stats import norm
from numpy.polynomial.legendre import leggauss
a,k,q,eta,sig=0.5,0.8,0.2,0.4,0.01; z=norm.ppf(0.95); out={}
def imp(ws,rs,L=400):
    y=np.zeros(len(ws)); h=[]; xp=0.0
    for t in range(L):
        xt=a*xp+k*np.dot(ws,y)+(k if t==0 else 0.0); y=(1-rs)*y+rs*xt; h.append(xt); xp=xt
    return np.array(h)
R=np.random.default_rng(20261019)
# (1) Monte Carlo check of exact error formula Phi(-V||d_T||/(2 sigma)) for a pulse
d=0.05; h0=imp(np.array([q]),np.array([eta])); h1=imp(np.array([q/2,q/2]),np.array([eta-d,eta+d]))
mc={}
for V,T in [(20,3),(40,3),(40,10),(80,20)]:
    m0,m1=V*h0[:T],V*h1[:T]; n=np.linalg.norm(m1-m0); thr=(m1-m0)@(m0+m1)/2
    X0=m0+sig*R.standard_normal((200000,T)); X1=m1+sig*R.standard_normal((200000,T))
    e0=np.mean(X0@(m1-m0)>thr); e1=np.mean(X1@(m1-m0)<=thr)
    mc[f"V{V}_T{T}"]={"theory":float(norm.cdf(-n/(2*sig))),"mc_err_H0":float(e0),"mc_err_H1":float(e1)}
out["exact_error_mc"]=mc
# (2) Passive zero-quantity test (Prop passive0): Monte Carlo error vs blocks
b=0.03; sw2=b*b/3; sv=0.01; d=0.10
b1=a+k*q*eta; b20=b1**2+k*q*eta*(1-eta); b2d=b20-k*q*d*d; Delta=k*q*sw2*d*d
Rv=max((sw2+sv**2)*(sw2*(1+b1**2+br**2)+sv**2)+sw2**2*br**2 for br in (b20,b2d))
def block(hyp,n):
    ws=np.array([q]) if hyp==0 else np.array([q/2,q/2]); rs=np.array([eta]) if hyp==0 else np.array([eta-d,eta+d])
    w=R.uniform(-b,b,(n,3)); hh=imp(ws,rs,3)/k   # process impulse coefficients
    x1=w[:,0]; x2=hh[1]*w[:,0]+w[:,1]; x3=hh[2]*w[:,0]+hh[1]*w[:,1]+w[:,2]
    return np.mean((x1+sv*R.standard_normal(n))*(x3+sv*R.standard_normal(n)))
pas={"Delta":Delta,"R":Rv,"n_bound_alpha_0.1":4*Rv/(0.1*Delta**2)}
mid=sw2*(b20+b2d)/2; errs={}
for n in [2000,20000,200000]:
    e0=np.mean([block(0,n)<mid for _ in range(200)]); e1=np.mean([block(1,n)>mid for _ in range(200)])
    errs[str(n)]=[float(e0),float(e1)]
pas["mc_error_by_blocks"]=errs; out["passive_zero_quantity"]=pas
# (3) Gauss vs Gauss-Radau moment gaps g_K
gk={}
for K in [2,3,4]:
    xg,wg=leggauss(K); wg=wg/2
    # Gauss-Radau with fixed node at -1: nodes = -1 and roots of (P_{K-1}+P_K)/(1+x)
    from numpy.polynomial import legendre as L
    c=np.zeros(K+1); c[K-1]=1; c[K]=1; roots=np.sort(np.real(L.legroots(c)))
    xr=roots  # includes -1
    V=np.vander(xr,K,increasing=True).T; mom=[ (1-(-1)**(j+1))/(2*(j+1)) for j in range(K)]
    wr=np.linalg.solve(V,mom)
    gk[str(K)]={"gauss_nodes":xg.tolist(),"radau_nodes":xr.tolist(),"radau_weights_positive":bool(np.all(wr>0)),
                "max_moment_gap_below_2K-1":float(max(abs((wg*xg**m).sum()-(wr*xr**m).sum()) for m in range(2*K-1))),
                "gap_2K-1":float((wg*xg**(2*K-1)).sum()-(wr*xr**(2*K-1)).sum())}
out["gauss_radau"]=gk
# (4) worked example: two Kalman desks
def kgain(s2z,s2v): return (-s2z+np.sqrt(s2z**2+4*s2z*s2v))/(2*s2v)
e1,e2=kgain(0.09,1.0),kgain(0.16,1.0); de=(e2-e1)/2; eb=(e1+e2)/2
h0=imp(np.array([q]),np.array([eb])); h1=imp(np.array([q/2,q/2]),np.array([eb-de,eb+de]))
A=2*sig*norm.ppf(0.95)/(k*k*q*de*de); mu,c,P=0.005,0.0004*100,100.0
BA=k/2*A**2+(c+mu*P)*A
out["worked_example"]={"eta1":e1,"eta2":e2,"eta_bar":eb,"delta":de,"d2_check":float(h1[2]-h0[2]),"pulse_A":A,
   "capital_par":BA,"capital_usdt_roll":BA*(0.4019/0.01)**2,"note":"capital in USDT scales sigma^2; par sigma=0.01"}
json.dump(out,open("recomputed/R_P1_extra.json","w"),indent=1); print(json.dumps(out,indent=1)[:3000])

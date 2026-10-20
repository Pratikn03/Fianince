# Recomputes the theory numbers of the earlier Paper 1 that can be checked from closed forms.
import numpy as np, json
from scipy.stats import norm
a,k,q,eta,sig=0.5,0.8,0.2,0.4,0.01
def imp(ws,rs,L=400):
    K=len(ws); y=np.zeros(K); h=[]; xp=0.0
    for t in range(L):
        xt=a*xp+k*np.dot(ws,y)+(k if t==0 else 0.0); y=(1-rs)*y+rs*xt; h.append(xt); xp=xt
    return np.array(h)
def Hhat(h,om): return np.exp(-1j*np.outer(om,np.arange(len(h))))@h
z=norm.ppf(0.95); kl=0.05*np.log(0.05/0.95)+0.95*np.log(0.95/0.05)
out={"params":{"a":a,"kappa":k,"q":q,"eta":eta,"sigma":sig,"alpha":0.05},"spectral":{}}
for d in [0.02,0.03,0.05,0.08,0.10,0.15]:
    h0=imp(np.array([q]),np.array([eta])); h1=imp(np.array([q/2,q/2]),np.array([eta-d,eta+d]))
    om=np.linspace(1e-4,np.pi,20001); r=(Hhat(h0,om).real-k/2)/np.abs(Hhat(h1,om)-Hhat(h0,om))**2
    i=np.argmin(r); om2=np.linspace(max(om[i]-2e-3,1e-6),om[i]+2e-3,4001)
    r2=(Hhat(h0,om2).real-k/2)/np.abs(Hhat(h1,om2)-Hhat(h0,om2))**2; j=np.argmin(r2)
    C=4*sig**2*z**2*r2[j]
    out["spectral"][str(d)]={"C_det_quad":C,"omega_star":om2[j],"delta4_C":d**4*C,
                             "adaptive_quad":2*sig**2*kl*r2[j],"d2":float(h1[2]-h0[2])}
out["kl_ratio"]=kl/(2*z**2)
# Prop 3.1 single-pulse floor
Veff=6.25
out["delta_min_T3"]=float(np.sqrt(2*sig*z/(Veff*k**2*q)))
# Theorem 3.6 two-point pair (tau=0.01, q=0.2, eta_bar=0.4, sigma_h=1.6e-3, T=120 taps)
qq,eb,tau=0.20,0.40,0.01; pm,pp=0.5-tau/qq,0.5+tau/qq; lc={}
for de in [0.30,0.20,0.14,0.10,0.08,0.06,0.05,0.04]:
    w0=np.array([qq*pm,qq*pp]); r0=np.array([eb-pp*de,eb+pm*de]); w1=np.array([qq*pp,qq*pm]); r1=np.array([eb-pm*de,eb+pp*de])
    dh=imp(w1,r1,121)-imp(w0,r0,121); n=float(np.linalg.norm(dh))
    lc[str(de)]={"dM3":float((w1*r1**3).sum()-(w0*r0**3).sum()),"norm_dh":n,"N_LeCam_95":4*(1.6e-3)**2*z**2/n**2}
out["lecam_pair"]=lc
json.dump(out,open("recomputed/R_P1_theory_constants.json","w"),indent=1)
print(json.dumps({k_:v for k_,v in out["spectral"]["0.05"].items()},indent=1)); print(out["delta_min_T3"])

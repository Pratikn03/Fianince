import numpy as np, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import norm
plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False})
C=["#1f4e79","#c0504d","#4f8a3c","#7f6000"]
a,k,q,eta,sig=0.5,0.8,0.2,0.4,0.01; z=norm.ppf(0.95)
def imp(ws,rs,L=400):
    y=np.zeros(len(ws)); h=[]; xp=0.0
    for t in range(L):
        xt=a*xp+k*np.dot(ws,y)+(k if t==0 else 0.0); y=(1-rs)*y+rs*xt; h.append(xt); xp=xt
    return np.array(h)
def pair(d): return imp(np.array([q]),np.array([eta])), imp(np.array([q/2,q/2]),np.array([eta-d,eta+d]))
# Fig A: impulse responses and difference
h0,h1=pair(0.05)
fig,ax=plt.subplots(1,2,figsize=(6.6,2.4))
ax[0].plot(h0[:25],"o-",ms=2,color=C[0],label="single cohort"); ax[0].plot(h1[:25],"s--",ms=2,color=C[1],label=r"split pair, $\delta=0.05$")
ax[0].set_xlabel("lag j"); ax[0].set_ylabel(r"$h_j$"); ax[0].legend(frameon=False)
for i,d in enumerate([0.02,0.05,0.10]):
    a0,a1=pair(d); ax[1].plot((a1-a0)[:25]/d**2,color=C[i],label=f"δ={d}")
ax[1].axhline(-k*k*q,ls=":",color="0.5"); ax[1].set_xlabel("lag j"); ax[1].set_ylabel(r"$d_j/\delta^2$"); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig("paper1/figs/fig_impulse.pdf")
# Fig B: dissipation kernel and ratio
om=np.linspace(1e-3,np.pi,3000); E=lambda h:np.exp(-1j*np.outer(om,np.arange(len(h))))@h
fig,ax=plt.subplots(1,2,figsize=(6.6,2.4))
g=E(h0).real-k/2; ax[0].plot(om,g,color=C[0]); ax[0].set_xlabel(r"$\omega$"); ax[0].set_ylabel(r"$g_0(\omega)$")
for i,d in enumerate([0.03,0.05,0.10]):
    a0,a1=pair(d); r=4*sig**2*z**2*(E(a0).real-k/2)/np.abs(E(a1)-E(a0))**2
    ax[1].semilogy(om,r,color=C[i],label=f"δ={d}"); j=np.argmin(r); ax[1].plot(om[j],r[j],"k.",ms=4)
ax[1].set_xlabel(r"$\omega$"); ax[1].set_ylabel(r"$4\sigma^2z^2 g_0/|\Delta\hat H|^2$"); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig("paper1/figs/fig_dissipation.pdf")
# Fig C: phase diagram and pulse benchmarks
Veff=6.25; cost=0.5*k*Veff**2+0.0004*100*Veff; marg=0.005*100*Veff
ds=np.linspace(0.01,0.25,120); out={}
def bench(d,T):
    a0,a1=pair(d); n=np.linalg.norm((a1-a0)[:T]); N=int(np.ceil(4*sig**2*z**2/(Veff**2*n**2))); return N, N*cost+marg
fig,ax=plt.subplots(figsize=(4.8,3.0))
for T,col in [(3,C[1]),(20,C[0])]:
    ax.semilogy(ds,[bench(d,T)[1] for d in ds],color=col,label=f"isolated-pulse benchmark, T={T}")
cq=[]
for d in ds:
    a0,a1=pair(d); r=(E(a0).real-k/2)/np.abs(E(a1)-E(a0))**2; cq.append(4*sig**2*z**2*r.min())
ax.semilogy(ds,cq,color=C[2],label=r"spectral lower bound $C^*_{\rm det,quad}$")
ax.axvline(np.sqrt(2*sig*z/(Veff*k**2*q)),ls=":",color=C[1]); ax.text(0.205,2e4,r"$\delta_{\min}(3)$",fontsize=7)
ax.set_xlabel(r"memory separation $\delta$"); ax.set_ylabel("capital (par units)"); ax.legend(frameon=False,fontsize=6.5)
fig.tight_layout(); fig.savefig("paper1/figs/fig_phase.pdf")
for d in [0.05]:
    for T in [3,4,10,20,100]: out[f"T{T}"]=bench(d,T)
out["cost_per_pulse"]=cost; out["margin"]=marg
json.dump(out,open("recomputed/R_P1_pulse_benchmarks.json","w"),indent=1); print(out)

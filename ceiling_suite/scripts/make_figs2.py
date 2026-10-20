import numpy as np, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import norm
plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False})
C=["#1f4e79","#c0504d","#4f8a3c","#7f6000"]
a,k,q,eta=0.5,0.8,0.2,0.4; sig,P,mu,c=0.003,100.0,0.25,0.02
def imp(ws,rs,L=400):
    y=np.zeros(len(ws)); h=[]; xp=0.0
    for t in range(L):
        xt=a*xp+k*np.dot(ws,y)+(k if t==0 else 0.0); y=(1-rs)*y+rs*xt; h.append(xt); xp=xt
    return np.array(h)
def VB(B): beta=c+mu*P; return 2*B/(beta+np.sqrt(beta**2+4*(mu+0.5)*k*B))
def dT(d,T): return np.linalg.norm((imp(np.array([q/2,q/2]),np.array([eta-d,eta+d]))-imp(np.array([q]),np.array([eta])))[:T])
fig,ax=plt.subplots(1,3,figsize=(7.2,2.4))
Ts=np.arange(1,201)
for i,B in enumerate([100,1000]):
    ax[0].plot(Ts,[norm.cdf(-VB(B)*dT(0.05,T)/(2*sig)) for T in Ts],color=C[i],label=f"capital {B}")
ax[0].set_xlabel("model observations T"); ax[0].set_ylabel("exact known-pair error"); ax[0].legend(frameon=False)
Bs=np.logspace(-1,6,200); ax[1].loglog(Bs,VB(Bs),color=C[0]); ax[1].set_xlabel("counterparty capital B"); ax[1].set_ylabel("robust quantity allowance $V_B$")
ds=np.logspace(-2,-0.7,30); need=[]
for d in ds:
    Vreq=2*sig*norm.ppf(0.9)/dT(d,200); beta=c+mu*P; need.append((mu+0.5)*k*Vreq**2+beta*Vreq)
ax[2].loglog(ds,need,color=C[1]); ax[2].set_xlabel(r"rate separation $\delta$"); ax[2].set_ylabel("capital for error 0.1")
fig.tight_layout(); fig.savefig("paper1/figs/fig_knownpair.pdf")
# Paper 2: pseudospectra of a constructed stable non-normal matrix
J=np.array([[0.5,5.0],[0.0,0.4]])
xs=np.linspace(-1.6,1.6,321); X,Y=np.meshgrid(xs,xs); S=np.zeros_like(X)
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        z=X[i,j]+1j*Y[i,j]; S[i,j]=np.linalg.svd(z*np.eye(2)-J,compute_uv=False)[-1]
fig,ax=plt.subplots(1,2,figsize=(6.6,2.8))
cs=ax[0].contour(X,Y,np.log10(S),levels=[-2,-1.5,-1,-0.5],colors=C[:4],linewidths=0.8)
ax[0].clabel(cs,fmt=lambda v:f"ε=1e{v:.1f}",fontsize=6)
t=np.linspace(0,2*np.pi,400); ax[0].plot(np.cos(t),np.sin(t),"k:",lw=0.7); ax[0].plot([0.5,0.4],[0,0],"k.",ms=5)
ax[0].set_aspect("equal"); ax[0].set_title("ε-pseudospectra, ρ(J)=0.5",fontsize=8)
for th,col in zip([1,5,20],C):
    Jt=np.array([[0.5,th],[0,0.4]]); g=[np.linalg.norm(np.array([1,0])@np.linalg.matrix_power(Jt,n)) for n in range(40)]
    ax[1].plot(g,color=col,label=f"coupling {th}")
ax[1].set_yscale("log"); ax[1].set_xlabel("step k"); ax[1].set_ylabel(r"$\|e_1^\top J^k\|$"); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig("paper2/figs/fig_pseudo.pdf"); print("ok")

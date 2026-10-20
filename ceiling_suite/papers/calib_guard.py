import numpy as np, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False})
C=["#1f4e79","#c0504d","#4f8a3c","#7f6000"]
def imp(a,phi,kap,r,eps,eta,q,L=240):
    x=np.zeros(L); d=np.zeros(L); f=np.zeros(L)
    for t in range(L):
        if t>0: f[t]=(1-eta)*f[t-1]+eta*q*x[t-1]
        tot=(1.0 if t==0 else 0.0)+f[t]
        x[t]=(a*x[t-1]+phi*d[t-1] if t else 0)+kap*tot; d[t]=((1-r)*d[t-1] if t else 0)+eps*tot
    return x
cases={"All training days (medians)":dict(a=0.970,phi=-0.051,kap=0.729,r=0.059,eps=-0.0018,eta=0.878,q=0.018),
       "High-volatility days (medians)":dict(a=0.980,phi=2.586,kap=0.890,r=0.122,eps=-0.0017,eta=0.863,q=0.0115),
       "Hypothetical depleting book (eps=+0.02)":dict(a=0.980,phi=2.586,kap=0.890,r=0.122,eps=0.02,eta=0.863,q=0.0115)}
out={}; fig,ax=plt.subplots(figsize=(4.8,2.9))
for i,(k,p) in enumerate(cases.items()):
    h=imp(p["a"],p["phi"],p["kap"],p["r"],p["eps"],p["eta"],p["q"])
    C3=p["phi"]*p["eps"]+p["kap"]**2*p["eta"]*p["q"]-(1-p["a"])*p["kap"]
    row={"C3":C3,"peak":float(np.max(np.abs(h))),"peak_minute":int(np.argmax(np.abs(h)))}
    for H in [1,5,15,60]:
        row[f"sum_{H}"]=float(np.abs(h[:H]).sum()); row[f"ratio_{H}"]=float(np.abs(h[:H]).sum()/np.max(np.abs(h[:H])))
    # admissible inventory (USD) for budget 1e5 USD, shock bound 5 ($M per minute), horizon 15 min
    row["inv_usd_budget1e5_u5_H15"]=1e5/((row["sum_15"]/1e4)*5)
    row["inv_usd_peakguard_H15"]=1e5/((row["peak"]/1e4)*5)
    out[k]=row; ax.plot(h[:60],color=C[i],label=k)
ax.set_xlabel("minutes after a \\$1M flow shock"); ax.set_ylabel("price response (bp)"); ax.legend(frameon=False,fontsize=6.5)
fig.tight_layout(); fig.savefig("paper2/figs/fig_calib.pdf")
json.dump(out,open("recomputed/R_P2_calibrated_guard.json","w"),indent=1); print(json.dumps(out,indent=1))

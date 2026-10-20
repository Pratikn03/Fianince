import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os as _os; _A=_os.environ.get("RESULTS_ARCHIVE", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "results_archive")); R1=_os.path.join(_A, "realres", "results") + "/"; R2=_os.path.join(_A, "depthres", "results") + "/"
m=lambda p: json.load(open(p))["metrics"]
plt.rcParams.update({"font.size":9,"font.family":"serif","axes.spines.top":False,"axes.spines.right":False,
                     "figure.dpi":150,"savefig.bbox":"tight"})
C=["#1f4e79","#c0504d","#4f8a3c","#7f6000"]
# ---- Paper 1 Fig 1: K-cohort lower bound
t1=m(R1+"T1_K_cohort_rate.json")
fig,ax=plt.subplots(figsize=(4.6,3.0))
for i,(K,v) in enumerate(sorted(t1.items())):
    ax.loglog(v["delta_grid"],v["N_star_lower"],"o-",ms=3,color=C[i],label=f"K = {K}: slope {v['slope_N']:.2f} (theory {v['target']})")
ax.set_xlabel(r"rate spacing $\Delta\eta$"); ax.set_ylabel(r"Le Cam lower bound on resets $N^*$")
ax.legend(frameon=False,fontsize=7.5); fig.savefig("paper1/figs/fig_kcohort.pdf")
# ---- Paper 1 Fig 2: capital grid
p13=m(R1+"P1.3-T1_sigma_obs.json"); d=np.geomspace(0.02,0.2,60)
fig,ax=plt.subplots(figsize=(4.6,3.0))
lab={"roll_median":"Roll noise, median (0.40 USDT)","sd_1s_change_median":"1-s price change s.d. (1.98 USDT)","paper_assumption":"previous assumption (4 USDT)"}
for i,(k,s) in enumerate(p13["sigma_choices"].items()):
    ax.loglog(d,61.44*(s/0.01)**2*(0.05/d)**4,color=C[i],ls="-" if i<2 else "--",label=lab[k])
ax.set_xlabel(r"memory separation $\delta$"); ax.set_ylabel("capital lower bound (USDT)")
ax.legend(frameon=False,fontsize=7.5); fig.savefig("paper1/figs/fig_capital.pdf")
# ---- Paper 2 Fig 1: T6 illustration
def h2(a,phi,k,r,e,L=60):
    x=np.zeros(L); dd=np.zeros(L)
    for t in range(L):
        u=1.0 if t==0 else 0.0
        x[t]=(a*x[t-1]+phi*dd[t-1] if t else 0)+k*u; dd[t]=((1-r)*dd[t-1] if t else 0)+e*u
    return x
fig,ax=plt.subplots(figsize=(4.6,3.0))
for i,(phi,lab_) in enumerate([(0.0,r"$\varphi\varepsilon=0$"),(0.3,r"$\varphi\varepsilon<(1-a)\kappa$"),(3.0,r"$\varphi\varepsilon>(1-a)\kappa$, $r=0.15$"),(3.0,r"$\varphi\varepsilon>(1-a)\kappa$, $r=0.40$")]):
    r=0.4 if i==3 else 0.15
    ax.plot(h2(0.9,phi,1.0,r,0.1),color=C[i],label=lab_)
ax.axhline(1.0,color="0.6",lw=0.6,ls=":"); ax.set_xlabel("minutes after a unit flow shock"); ax.set_ylabel(r"price response $h_k$ (bp)")
ax.legend(frameon=False,fontsize=7.5); fig.savefig("paper2/figs/fig_t6.pdf")
# ---- Paper 2 Fig 2: depth mediation LP
d4=m(R2+"D4_depth_mediation_train.json"); H=d4["horizons_min"]
fig,ax=plt.subplots(figsize=(4.6,3.0))
names={"A":"(A) total","B":"(B) future flow held fixed","C":"(C) future flow and depth held fixed"}
for i,k in enumerate("ABC"):
    ax.plot(H,d4["versions"][k]["beta_bp_per_musd"],"o-",ms=3,color=C[i],label=names[k])
ax.set_xlabel("horizon (minutes)"); ax.set_ylabel(r"price response (bp per \$1M signed flow)")
ax.legend(frameon=False,fontsize=7.5); fig.savefig("paper2/figs/fig_mediation.pdf")
# ---- Paper 2 Fig 3: event C3 paths
d9=m(R2+"D9_event_studies.json")
fig,ax=plt.subplots(figsize=(4.6,3.0))
for i,(k,v) in enumerate([(k,v) for k,v in d9.items() if isinstance(v,dict)]):
    hrs=sorted(int(h) for h in v["C3_hat_by_hour"]); vals=[v["C3_hat_by_hour"][str(h)] for h in hrs]
    ax.plot(hrs,vals,"o-",ms=3,color=C[i],label=f"{v['date']} (worst hour {v['worst_hour_utc']}:00 UTC)")
    ax.axvline(v["worst_hour_utc"],color=C[i],lw=0.6,ls=":")
ax.axhline(0,color="k",lw=0.6); ax.set_xlabel("hour (UTC)"); ax.set_ylabel(r"$\hat C_3$ (bp per \$1M)")
ax.legend(frameon=False,fontsize=7); fig.savefig("paper2/figs/fig_events.pdf")
print("figs ok")

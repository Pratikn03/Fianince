import numpy as np, json
a,k=0.5,0.8
def imp(w,eta,L=121):
    y=np.zeros(len(w)); h=[]; xp=0.0
    for t in range(L):
        xt=a*xp+k*np.dot(w,y)+(k if t==0 else 0.0); y=(1-eta)*y+eta*xt; h.append(xt); xp=xt
    return np.array(h)
def jac(w,eta,e=1e-6):
    th=np.concatenate([w,eta]); K=len(w); cols=[]
    for j in range(2*K):
        tp=th.copy(); tm=th.copy(); tp[j]+=e; tm[j]-=e
        cols.append((imp(tp[:K],tp[K:])-imp(tm[:K],tm[K:]))/(2*e))
    return np.array(cols).T
sh1=0.01/6.25; out={}
cases={"K1_eta0.30":([0.2],[0.30]),"K2_d0.30":([0.1,0.1],[0.25,0.55]),"K2_d0.20":([0.1,0.1],[0.30,0.50]),
       "K2_d0.10":([0.1,0.1],[0.35,0.45]),"K2_d0.05":([0.1,0.1],[0.375,0.425]),
       "K3_s0.10":([0.2/3]*3,[0.30,0.40,0.50]),"K3_s0.20":([0.2/3]*3,[0.20,0.40,0.60])}
for nm,(w,e) in cases.items():
    J=jac(np.array(w,float),np.array(e,float)); Finv=np.linalg.inv(J.T@J); K=len(w)
    worst=max(Finv[i,i] for i in range(K))
    N=(1.96/0.01)**2*sh1**2*worst; scrit=(0.01/1.96)/np.sqrt(worst)
    out[nm]={"N_star":float(N),"sigma_crit":float(scrit),"ratio_sigma_h1_over_crit":float(sh1/scrit)}
    print(nm, round(N,1), "%.3g"%scrit, round(sh1/scrit,1))
json.dump(out,open("recomputed/R_P1_crb.json","w"),indent=1)

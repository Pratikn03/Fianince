import numpy as np, json
def MC(J,C,K=400): return max(np.linalg.norm(C@np.linalg.matrix_power(J,k)) for k in range(K))
def kreiss(J):
    best=0
    for r in np.concatenate([1+np.logspace(-4,3,400)]):
        for th in np.linspace(0,2*np.pi,181):
            z=r*np.exp(1j*th); best=max(best,(r-1)*np.linalg.norm(np.linalg.inv(z*np.eye(len(J))-J),2))
    return best
out={}
for th in [0,1,5,20,100]:
    J=np.array([[0.8,th],[0,0.4]]); m=MC(J,np.array([1.0,0])); mi=max(np.linalg.norm(np.linalg.matrix_power(J,k),2) for k in range(400)); kc=kreiss(J)
    out[f"theta{th}"]={"rho":0.8,"MC_price":m,"sup_norm":mi,"kreiss":kc,"e_n_kreiss":np.e*2*kc,"r_exact_B1":1/m}
a=2.8135; Jb=np.array([[0.72,a,0],[0,0.78,a],[0,0,0.76]]); c=np.array([1.0,0,0])
g=[np.linalg.norm(c@np.linalg.matrix_power(Jb,k)) for k in range(60)]
q=np.linalg.norm(np.linalg.matrix_power(Jb,42),2); Mbar=max(g[:42])
out["burst"]={"rho":float(max(abs(np.linalg.eigvals(Jb)))),"peak":float(max(g)),"peak_lag":int(np.argmax(g)),"q42":float(q),"Mbar42_q":float(Mbar*q)}
json.dump(out,open("recomputed/R_P2_kreiss.json","w"),indent=1); print(json.dumps(out,indent=1))

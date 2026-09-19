#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.finance import feasible_orders
from src.linear import simulate_linear

rng=np.random.default_rng(31022026);n=500
P=rng.uniform(50,200,n);E=rng.uniform(100,1000,n);I=rng.uniform(-.5,.5,n)*E/P;C=E-I*P;D=rng.normal(0,20,n)
q,f,d=feasible_orders(C,I,P,D,E,2.,10.,1.,.01)
np.savez_compressed(ROOT/'replication/constraint_inputs.npz',cash=C,inventory=I,price=P,desired=D,equity0=E)
np.savez_compressed(ROOT/'replication/constraint_reference.npz',fill=q)
challenges=[]
for i,(g,s) in enumerate([( .7,.02),(1.3,.02),(.95,.1),(1.05,.1),(.7,.002),(1.3,.002)]):
    sim=simulate_linear(.4,.6*g*np.array([.6,.4]),[.5,s],.02,128,64,3200000+i,'impulse')
    np.savez_compressed(ROOT/f'replication/price_challenge_{i}.npz',prices=sim['prices'],probes=sim['probes'],rates=np.array([.5,s]))
    challenges.append({'challenge':i,'true_a_plus_Q':.4+.6*g})
(ROOT/'replication/reference_truth.json').write_text(json.dumps(challenges,indent=2))

"""Fixed misspecification checks for the tagged-flow decision contract.

These falsify an application of the assumptions; they are not new market data.
"""
from pathlib import Path
import json
import numpy as np


def decide(obs, e, a=.5, k=.8, cap=.55, allowance=.005):
    lo=np.maximum(0,obs[:,:,:2]-e);hi=np.maximum(0,obs[:,:,:2]+e)
    f1lo=np.maximum(0,obs[:,:,2:4]-e);f1hi=np.maximum(0,obs[:,:,2:4]+e)
    valid=np.all(lo>0,axis=2)
    rlo=np.clip(f1lo/np.maximum(hi,1e-300)-(obs[:,:,4:5]+e)/k,0,.95)
    rhi=np.clip(f1hi/np.maximum(lo,1e-300)-(obs[:,:,4:5]-e)/k,0,.95)
    valid &= np.all(rlo<=rhi,axis=2)
    qhi=hi/k/(1-rhi)
    upper=a+k*(qhi.sum(axis=2,keepdims=True)-qhi)+allowance
    return valid & (upper.min(axis=2)<=cap),np.argmin(upper,axis=2)


def main():
    rng=np.random.default_rng(20261107)
    w=np.array([[.04,.04],[.02,.06]])
    r=.6+.1*np.array([[-1/np.sqrt(3),1/np.sqrt(3)],[-1,1/3]])
    q=w/(1-r);S=.5+.8*q.sum(axis=1);post=S[:,None]-.8*q
    h=.8*.5+.8**2*.08
    mu=np.concatenate([.8*w,w*(.8*r+h),np.full((2,1),h)],axis=1)
    reps,N,sigma=20000,128,.0005
    obs=mu[:,None,:]+rng.normal(size=(2,reps,5))*sigma/np.sqrt(N)
    e=sigma*np.sqrt(5/(N*.05))
    cases=[]
    for name,bias,drift,swap in [
        ('valid_reset_contract',0,.005,False),
        ('second_flow_downward_bias_003',-.003,.005,False),
        ('second_flow_downward_bias_006',-.006,.005,False),
        ('second_flow_downward_bias_010',-.01,.005,False),
        ('response_allowance_underestimated',0,.03,False),
        ('second_flow_labels_swapped',0,.005,True),
    ]:
        x=obs.copy();x[:,:,2:4]+=bias
        if swap:x[:,:,2:4]=x[:,:,2:4][:,:,::-1]
        halt,selected=decide(x,e)
        unsafe=halt & (np.take_along_axis(post,selected,axis=1)+drift>.55)
        cases.append(dict(name=name,halt_probability=halt.mean(axis=1).tolist(),
          unsafe_halt_probability=unsafe.mean(axis=1).tolist(),
          mean_contract_coverage=np.all(abs(x-mu[:,None,:])<=e,axis=2).mean(axis=1).tolist(),
          response_contract_valid=drift<=.005))
    assert cases[0]['unsafe_halt_probability']==[0.,0.]
    assert any(c['unsafe_halt_probability'][0]>.05 for c in cases if 'bias' in c['name'])
    assert next(c for c in cases if c['name']=='response_allowance_underestimated')['unsafe_halt_probability'][1]>.05
    result=dict(seed=20261107,replications_per_world=reps,cases=cases,
      limit='Synthetic failures under a declared fixed menu; no guarantee applies after its observation/response assumptions fail.')
    (Path(__file__).parent/'flow_falsification_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

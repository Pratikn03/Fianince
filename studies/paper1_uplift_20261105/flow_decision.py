"""Exploratory known-mechanism test using tagged flows and prices, not direct R readings."""
from pathlib import Path
import json
import numpy as np


def main():
    rng = np.random.default_rng(20261106)
    a, k, W, c, spacing, cap, allowance = .5, .8, .08, .6, .1, .55, .005
    weights = np.array([[W/2,W/2],[W/4,3*W/4]])
    rates = c + spacing*np.array([[-1/np.sqrt(3),1/np.sqrt(3)],[-1,1/3]])
    q = weights/(1-rates)
    S = a+k*q.sum(axis=1)
    post = S[:,None]-k*q
    h1 = k*a+k*k*W
    means = np.concatenate([k*weights, weights*(k*rates+h1), np.full((2,1),h1)],axis=1)
    theta = (cap-allowance-a)/(max(S)-a)
    rows = []
    reps = 20000
    for N in [32,128,512,2048,8192]:
      for sigma in [.0005,.002,.005]:
       for H in [1,10]:
        for fee in [.05,.25]:
         e = sigma*np.sqrt(5/(N*.05))
         observations = means[:,None,:]+rng.normal(size=(2,reps,5))*sigma/np.sqrt(N)
         lo = np.maximum(0, observations[:,:,:2]-e)
         hi = np.maximum(0, observations[:,:,:2]+e)
         f1lo = np.maximum(0,observations[:,:,2:4]-e)
         f1hi = np.maximum(0,observations[:,:,2:4]+e)
         hlo = observations[:,:,4:5]-e
         hhi = observations[:,:,4:5]+e
         valid = np.all(lo>0,axis=2)
         safe_lo = np.maximum(lo,1e-300)
         safe_hi = np.maximum(hi,1e-300)
         rlo = np.clip(f1lo/safe_hi-hhi/k,0,.95)
         rhi = np.clip(f1hi/safe_lo-hlo/k,0,.95)
         valid &= np.all(rlo<=rhi,axis=2)
         qlo, qhi = lo/k/(1-rlo),hi/k/(1-rhi)
         upper = a+k*(qhi.sum(axis=2,keepdims=True)-qhi)+allowance
         selected = np.argmin(upper,axis=2)
         halt = valid & (np.min(upper,axis=2)<=cap)
         actual_post = np.take_along_axis(post,selected,axis=1)+allowance
         unsafe = halt & (actual_post>cap)
         joint_covered = np.all(np.abs(observations-means[:,None,:])<=e,axis=2)
         interval_covered = np.all((qlo<=q[:,None,:]) & (q[:,None,:]<=qhi),axis=2)
         assert not np.any(unsafe & joint_covered)
         assert not np.any(valid & joint_covered & ~interval_covered)
         fallback = H*2*(1-theta)
         halt_loss = H+.02+10*H*(actual_post>cap)
         bill = fee+.0005*N
         loss = bill+np.where(halt,halt_loss,fallback)
         # Ex ante no-data lottery over the same action menu, with each class
         # considered separately and per-world error budget .05.
         no_data = fallback
         for i in range(2):
          harms = post[:,i]+allowance>cap
          lh = H+.02+10*H*harms
          pmax = .05 if np.any(harms) else 1
          no_data = min(no_data, fallback+pmax*(float(lh.mean())-fallback))
         mean_loss = float(loss.mean())
         loss_range = abs((11*H+.02)-min(H+.02,fallback))
         hoeffding = loss_range*np.sqrt(np.log(40)/(4*reps))
         se = float(np.sqrt(np.sum(np.var(loss,axis=1,ddof=1)/reps)/4))
         rows.append(dict(N=N,sigma=sigma,H=H,fixed_fee=fee,information_bill=bill,
          loss_no_data=float(no_data),loss_disclosure=mean_loss,net_advantage=float(no_data-mean_loss),
          net_advantage_hoeffding_interval=[float(no_data-mean_loss-hoeffding),float(no_data-mean_loss+hoeffding)],
          net_advantage_mc_interval=[float(no_data-mean_loss-1.96*se),float(no_data-mean_loss+1.96*se)],
          halt_probability=halt.mean(axis=1).tolist(),unsafe_halt_probability=unsafe.mean(axis=1).tolist(),
          joint_mean_coverage=joint_covered.mean(axis=1).tolist(),radius=e))
    out=Path(__file__).parent/'flow_results.json'
    result=dict(status='COMPLETED_SYNTHETIC_EXPLORATORY',seed=20261106,replications_per_world=reps,
      observation_channels=['class0 flow0','class1 flow0','class0 flow1','class1 flow1','price response1'],
      rule_information='Only observed sample means, known impact, aggregate envelope and declared rate class; no true R, w or r supplied to rule.',
      rows=rows,limits=['Independent reset Gaussian channels are assumed, not validated from public positions.',
      'Synthetic fees, surplus and response allowance; no real-market welfare result.',
      'Same paired alternatives and fixed action menu; no optimal experiment design claim.',
      'MC intervals describe simulation error of mean loss, not uncertainty in model assumptions.'])
    out.write_text(json.dumps(result,indent=2)+'\n')
    best=max(rows,key=lambda r:r['net_advantage'])
    print(json.dumps({'rows':len(rows),'positive_rows':sum(r['net_advantage']>0 for r in rows),'best':best},indent=2))


if __name__=='__main__':
    main()

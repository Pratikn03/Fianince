"""Illustrative decision example and exact Gaussian testing experiment."""
from pathlib import Path
import json
import numpy as np
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
def populations(d):
    return ((.5+d*np.array([-1/np.sqrt(3),1/np.sqrt(3)]),np.array([.1,.1])),
            (.5+d*np.array([-1,1/3]),np.array([.05,.15])))
def response(r,w,T=30):
    k=np.array([np.dot(w,r**j) for j in range(T)])
    h=np.zeros(T);h[0]=.5
    for t in range(1,T):h[t]=.3*h[t-1]+.5*np.dot(k[:t],h[t-1::-1])
    return h

def main():
    ds=np.linspace(.001,.1,200);halt=[[],[]];common=[[],[]]
    for d in ds:
        for i,(r,w) in enumerate(populations(d)):
            q=w/(1-r)
            halt[i].append(.3+.5*(q.sum()-q.max()))
            common[i].append(.3+.5*q.sum()/3)
    (r0,w0),(r1,w1)=populations(.05)
    distance=np.linalg.norm(response(r0,w0)-response(r1,w1))/.01
    tag_distance=.5*abs(w0[0]-w1[0])/.01
    ns=np.logspace(0,8,250)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,ax=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
    colors=['#176b87','#b35d25']
    for i in range(2):
        ax[0].plot(ds,halt[i],color=colors[i],label=f'Halt largest, economy {i}')
        ax[0].plot(ds,common[i],color=colors[i],ls='--',alpha=.8,label=f'Common scaling, economy {i}')
    ax[0].axhline(.375,color='#444444',ls=':',label='Prudential ceiling')
    ax[0].set(xlabel='Type radius Δ',ylabel='Feedback budget after action',title='A. Different effects of the same halt')
    ax[0].legend(fontsize=7.5,loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2,frameon=False)
    ax[1].semilogx(ns,norm.cdf(-np.sqrt(ns)*distance/2),color=colors[0],label='Noisy public response')
    ax[1].semilogx(ns,norm.cdf(-np.sqrt(ns)*tag_distance/2),color=colors[1],label='One verified class report')
    ax[1].set(xlabel='Independent repetitions N',ylabel='Error probability per hypothesis',ylim=(-.01,.51),title='B. Public responses and class reports')
    ax[1].legend(fontsize=8)
    fig.savefig(HERE/'intervention_example.pdf')
    fig.savefig(HERE/'intervention_example.png',dpi=160)
    meta={'public_mean_distance_over_noise':float(distance),'tag_mean_distance_over_noise':float(tag_distance),
          'public_N_for_5pct_error':float((2*norm.ppf(.95)/distance)**2),
          'tag_N_for_5pct_error':float((2*norm.ppf(.95)/tag_distance)**2),
          'contract':'30 deterministic impulse-response coordinates with independent N(0,.01^2) measurement errors; tag mean kappa*w1 with same reporting variance; known simple hypotheses; illustrative, not market calibration'}
    (HERE/'intervention_example.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))

if __name__=='__main__':main()

"""Exploratory finite-class tests. All repetitions and all outcomes are retained."""
import numpy as np
import pandas as pd
from scipy.stats import norm
from model import (Economy,response,candidates,cost,account,confidence_mask,
                   safe_mask,log_scores,choose,summarize_account)


def shock_sample(rng,n,H,bias=.15):
    # Uniform bounded flow with a declared positive mean; synthetic opportunity.
    # U in [-.04,.04] at every minute, including its deterministic drift.
    z=rng.uniform(-1,1,(n,H))
    return .04*((1-abs(bias))*z+bias)


def information_frontier():
    rows=[]
    for delta in [.20,.10,.05,.025,.0125]:
        one=Economy('one',(.4,),(.5,))
        two=Economy('split',(.2,.2),(.5-delta,.5+delta))
        d=np.linalg.norm(response(one,24)-response(two,24))
        for N in [8,32,128,512,2048,8192]:
            rows.append(dict(delta=delta,N=N,known_pair_optimal_error=norm.cdf(-np.sqrt(N)*d/(2*.02)),
                response_l2_gap=d,infinite_gain_one=5.,infinite_gain_split=5.,
                finite_gain_one=response(one,60).sum(),finite_gain_split=response(two,60).sum(),
                scope='known alternatives; iid Gaussian reset readings; not a uniform minimax theorem'))
    return pd.DataFrame(rows)


def run(profile,seed=20261029):
    full=profile=='full'
    ntrain,nval,ntest=(768,384,512) if full else (96,64,96)
    reps=20 if full else 2
    Ns=[8,32,128] if full else [16]
    budgets=[.5,1.,2.,4.] if full else [1.,2.]
    H,L,sigma=60,12,.02
    grid=np.linspace(0.,9.9,100)
    es=candidates();h=np.array([response(e,H) for e in es]);gains=abs(h).sum(1)
    scenarios=[
        ('no_feedback',Economy('truth',(0.,),(.5,)),True,'iid'),
        ('moderate_feedback',Economy('truth',(.4,),(.2,)),True,'iid'),
        ('near_boundary',Economy('truth',(.56,),(.5,)),True,'iid'),
        ('hidden_slow_memory',Economy('truth',(.56,),(.002,)),False,'iid'),
        ('correlated_readings',Economy('truth',(.4,),(.2,)),False,'correlated'),
        ('biased_readings',Economy('truth',(.4,),(.2,)),False,'biased'),
        ('behavior_change',Economy('truth',(.4,),(.2,)),False,'change'),
    ]
    rows=[]; decisions=[]; intervals=[]; contrasts=[]
    for si,(regime,truth,contract,noise_kind) in enumerate(scenarios):
        eval_e=Economy('changed',(.56,),(.5,)) if noise_kind=='change' else truth
        for rep in range(reps):
            rng=np.random.default_rng(np.random.SeedSequence([seed,si,rep]))
            # Same train/validation/test external tapes for all policies and budgets.
            train=account(truth,shock_sample(rng,ntrain,H),1.)
            val=account(truth,shock_sample(rng,nval,H),1.)
            test_u=shock_sample(rng,ntest,H)
            # For behavior_change, past information describes truth; future is eval_e.
            train_dp=train['price_delta'];val_dp=val['price_delta']
            score=log_scores(grid,train_dp[:,-1])
            unit_test=account(eval_e,test_u,1.)
            unit_delta=unit_test['price_delta']
            true_h=response(truth,H)
            val_cash=1000+val_dp[:,-1,None]*grid-cost(grid)
            hist_adverse=np.maximum(0.,-train_dp.min(1))
            # Strong benchmark: volatility AND price-level persistence, estimated on training only.
            x=train_dp[:,:-1].ravel();y=train_dp[:,1:].ravel()
            ar=float(np.clip(np.dot(x,y)/max(np.dot(x,x),1e-12),0,.995))
            vol=float(np.std(np.diff(train_dp,axis=1)))
            vp_unit=3*vol*np.sqrt(sum(ar**(2*j) for j in range(H)))
            # Robust-return objective: empirical returns and a fixed, adverse shifted law.
            robust_score=np.minimum(score,log_scores(grid,train_dp[:,-1]-np.std(train_dp[:,-1])))
            for N in Ns:
                readings=true_h[:L]+rng.normal(0,sigma/np.sqrt(N),L)
                if noise_kind=='correlated':
                    readings=true_h[:L]+rng.normal(0,sigma/np.sqrt(N))+.15*rng.normal(0,sigma/np.sqrt(N),L)
                if noise_kind=='biased':readings=readings-np.linspace(0,.12,L)
                mask,radius=confidence_mask(h,readings,sigma,N)
                # Verified envelope: a narrow band around actual minimum memory.
                # This is an exact audited disclosure assumption, not inferred identities.
                true_floor=min(truth.eta);low=max(0,true_floor-.025);high=true_floor+.025
                disclose=np.array([low<=min(e.eta)<=high for e in es])
                dm=mask&disclose
                point=int(np.argmin(((h[:,:L]-readings)**2).sum(1)))
                observed_true=bool(np.max(abs(true_h[:L]-readings))<=radius)
                member=any(e.q==truth.q and e.eta==truth.eta for e in es)
                identified=len({(es[i].q,es[i].eta) for i in np.flatnonzero(mask)})==1
                for B in budgets:
                    allowed=safe_mask(grid,gains[mask],B)
                    da=safe_mask(grid,gains[dm],B)
                    oa=safe_mask(grid,[abs(response(eval_e,H)).sum()],B)
                    pa=safe_mask(grid,[gains[point]],B)
                    empirical_losses=hist_adverse[:,None]*grid+cost(grid)
                    empirical_cap=np.quantile(empirical_losses,.99,axis=0)<=B
                    robust_cap=empirical_losses.max(0)<=B
                    vp_cap=grid*vp_unit+cost(grid)<=B
                    kelly=choose(grid,score,np.ones(len(grid),bool))
                    # Fractional-log benchmark tunes on independent validation, not test.
                    fractions=np.array([0,.125,.25,.5,.75,1.])
                    frac_inv=kelly*fractions
                    vl=np.maximum(0.,-val_dp.min(1))[:,None]*frac_inv+cost(frac_inv)
                    eligible=(vl>B).mean(0)<=.05
                    vscore=log_scores(frac_inv,val_dp[:,-1])
                    fractional=choose(frac_inv,vscore,eligible)
                    actions={
                        'log_utility':kelly,
                        'fractional_log_validation':fractional,
                        'empirical_loss_constrained_log':choose(grid,score,empirical_cap),
                        'robust_empirical_log':choose(grid,robust_score,robust_cap),
                        'volatility_persistence':choose(grid,score,vp_cap),
                        'point_response':choose(grid,score,pa),
                        'aggregate_certificate':choose(grid,score,allowed),
                        'disclosure_certificate':choose(grid,score,da),
                        'oracle_response':choose(grid,score,oa),
                    }
                    # Cost of disclosure is paid before trading. Re-optimize under the SAME B.
                    disclosure_fee=.01
                    paid_score=np.full(len(grid),-np.inf)
                    pw=1000+train_dp[:,-1,None]*grid-cost(grid)-disclosure_fee
                    paid_score=np.log(pw/1000).mean(0)
                    paid_allowed=safe_mask(grid,gains[dm],B-disclosure_fee)
                    # If no positive action can be certified, cash remains an explicit fallback.
                    paid_i=choose(grid,paid_score,paid_allowed)
                    actions['paid_disclosure_certificate']=paid_i
                    policy_values={}
                    for pol,I in actions.items():
                        # Price path computed once, since this is a price-taking account.
                        charge=float(cost(I));fee=disclosure_fee if pol=='paid_disclosure_certificate' else 0.
                        cash=1000-100*I-charge/2-fee
                        marked=cash+I*(100+unit_delta)
                        close_cash=cash+I*(100+unit_delta[:,-1])-charge/2
                        w=np.column_stack([np.full(ntest,1000-charge/2-fee),marked,close_cash])
                        independent_terminal=1000+I*unit_delta[:,-1]-charge-fee
                        accounting_error=float(np.max(abs(close_cash-independent_terminal)))
                        acct=dict(terminal=w[:,-1],loss_from_initial=np.maximum(0,1000-w.min(1)),
                                  peak_drawdown=(np.maximum.accumulate(w,axis=1)-w).max(1),accounting_error=accounting_error)
                        s=summarize_account(acct,I,B)
                        rows.append(dict(regime=regime,rep=rep,N=N,budget=B,policy=pol,
                                         guarantee_applicable=contract,true_in_candidate_class=member,
                                         disclosure_fee=fee,**s))
                        logs=np.log(w[:,-1]/1000)
                        policy_values[pol]=(logs,acct['loss_from_initial'],I)
                    base=policy_values['aggregate_certificate']
                    for other in ['paid_disclosure_certificate','volatility_persistence','robust_empirical_log','oracle_response']:
                        alt=policy_values[other]
                        contrasts.append(dict(regime=regime,rep=rep,N=N,budget=B,contrast=other+' minus aggregate',
                            paired_mean_log_difference=float((alt[0]-base[0]).mean()),
                            paired_mean_loss_difference=float((alt[1]-base[1]).mean()),
                            inventory_difference=alt[2]-base[2]))
                    decisions.append(dict(regime=regime,rep=rep,N=N,budget=B,
                        candidate_count=int(mask.sum()),disclosed_count=int(dm.sum()),
                        empty_set=not mask.any(),cohort_identified=identified,
                        true_response_in_band=observed_true,true_in_candidate_class=member,
                        certified_capacity=float(grid[allowed].max()),disclosed_capacity=float(grid[da].max()),
                        oracle_capacity=float(grid[oa].max()),guarantee_applicable=contract,
                        memory_floor_low=low,memory_floor_high=high,band_radius=radius))
    return pd.DataFrame(rows),pd.DataFrame(decisions),pd.DataFrame(contrasts)


def paired_intervals(contrasts,seed=99):
    rng=np.random.default_rng(seed);out=[]
    for key,d in contrasts.groupby(['regime','N','budget','contrast']):
        for metric in ['paired_mean_log_difference','paired_mean_loss_difference','inventory_difference']:
            x=d[metric].to_numpy();n=len(x)
            bs=x[rng.integers(0,n,(2000,n))].mean(1)
            lo,hi=np.quantile(bs,[.025,.975])
            out.append(dict(regime=key[0],N=key[1],budget=key[2],contrast=key[3],metric=metric,
                            mean=x.mean(),ci_low=lo,ci_high=hi,n_independent_repetitions=n,
                            interval_scope='exploratory percentile bootstrap over independent repetitions; not simultaneous'))
    return pd.DataFrame(out)

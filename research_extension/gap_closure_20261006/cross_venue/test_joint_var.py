import numpy as np
import pandas as pd
from joint_var import fit_joint,generalized_fevd,orthogonal_fevd,aligned_segments

def test_diagonal_independent_system_has_no_cross_fevd():
    J=np.diag([.7,.4,.2,.8]);sigma=np.diag([1.,2.,3.,4.])
    for h in [1,6,30]:
        raw,norm=generalized_fevd(J,sigma,h)
        np.testing.assert_allclose(raw,np.eye(4),atol=1e-14)
        np.testing.assert_allclose(norm,np.eye(4),atol=1e-14)
        np.testing.assert_allclose(orthogonal_fevd(J,sigma,h,[3,2,1,0]),np.eye(4),atol=1e-14)

def test_correlated_innovations_show_why_raw_generalized_shares_need_normalization():
    J=np.zeros((2,2));sigma=np.array([[1.,.6],[.6,1.]])
    raw,norm=generalized_fevd(J,sigma,1)
    np.testing.assert_allclose(raw,[[1,.36],[.36,1]])
    np.testing.assert_allclose(norm,raw/1.36)
    first=orthogonal_fevd(J,sigma,1,[0,1]);reverse=orthogonal_fevd(J,sigma,1,[1,0])
    np.testing.assert_allclose(first,[[1,0],[.36,.64]])
    np.testing.assert_allclose(reverse,[[.64,.36],[0,1]])

def test_generalized_fevd_is_invariant_to_physical_unit_rescaling():
    J=np.array([[.7,.2,.1,0],[0,.4,.2,.1],[0,0,.6,.2],[0,0,0,.3]])
    L=np.array([[1,0,0,0],[.3,1,0,0],[.2,.1,1,0],[.4,.2,.1,1]])
    sigma=L@L.T;scale=np.diag([100.,.01,20.,.2])
    transformedJ=scale@J@np.linalg.inv(scale);transformedSigma=scale@sigma@scale
    for h in [1,6,30]:
        for a,b in zip(generalized_fevd(J,sigma,h),generalized_fevd(transformedJ,transformedSigma,h)):
            np.testing.assert_allclose(a,b,atol=1e-13)

def test_known_multivariate_process_recovers_joint_dynamics_and_covariance():
    rng=np.random.default_rng(7119);J=np.array([[.6,.1,.08,0],[0,.3,.1,0],[.05,0,.5,.1],[0,.1,0,.4]])
    sigma=np.array([[1,.3,0,0],[.3,1,.2,0],[0,.2,1,.1],[0,0,.1,1]])
    z=np.zeros((100001,4));errors=rng.multivariate_normal(np.zeros(4),sigma,size=100000)
    for t in range(100000):z[t+1]=J@z[t]+errors[t]
    chunks=[{'date':'test','segment':0,'z':z[1000:]}]
    fit,_=fit_joint(chunks)
    np.testing.assert_allclose(fit['J_raw'],J,atol=.015)
    np.testing.assert_allclose(fit['covariance_raw'],sigma,atol=.02)
    assert fit['Schur_stable']

def test_incomplete_bins_and_date_boundaries_do_not_create_joint_transitions():
    rng=np.random.default_rng(7120);seconds=np.r_[np.arange(16000),np.arange(86400,102400)]
    cb=pd.DataFrame({'sec':seconds,'mid':100*np.exp(rng.normal(0,.001,len(seconds))),'flow':rng.normal(size=len(seconds))})
    bn=cb.copy();bn['mid']*=1.01
    cb=cb[cb.sec!=4001]
    chunks,audit=aligned_segments(cb,bn)
    assert not any(400 in c['bins'] for c in chunks)
    assert len({c['date'] for c in chunks})==2
    for c in chunks:assert np.all(np.diff(c['bins'])==1)
    assert audit['n_transitions']==sum(len(c['z'])-1 for c in chunks)

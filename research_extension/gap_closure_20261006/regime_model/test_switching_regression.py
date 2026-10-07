import itertools
import numpy as np
from switching_regression import forward_backward,expectation,fit


def test_forward_backward_matches_exhaustive_hidden_paths():
    e=np.log(np.array([[.2,.8],[.7,.3],[.4,.6],[.9,.1]]));P=np.array([[.8,.2],[.3,.7]]);pi=np.array([.4,.6])
    paths=list(itertools.product(range(2),repeat=4));weights=[]
    for z in paths:
        w=pi[z[0]]*np.exp(e[0,z[0]])
        for t in range(1,4):w*=P[z[t-1],z[t]]*np.exp(e[t,z[t]])
        weights.append(w)
    weights=np.array(weights);total=weights.sum();gamma=np.zeros((4,2));xi=np.zeros((3,2,2))
    for z,w in zip(paths,weights/total):
        for t in range(4):gamma[t,z[t]]+=w
        for t in range(3):xi[t,z[t],z[t+1]]+=w
    result=forward_backward(e,P,pi)
    assert np.isclose(result['log_likelihood'],np.log(total))
    np.testing.assert_allclose(result['posterior'],gamma,rtol=1e-12)
    np.testing.assert_allclose(result['pair_posterior'],xi,rtol=1e-12)
    assert not np.allclose(xi,gamma[:-1,:,None]*gamma[1:,None,:])


def test_segment_likelihood_excludes_boundary_transition():
    X=np.ones((6,1));y=np.array([0.,.1,-.1,3.,3.1,2.9]);beta=np.array([[0.],[3.]]);v=np.array([.1,.1]);P=np.array([[.99,.01],[.01,.99]]);pi=np.array([.5,.5])
    separate,_=expectation([(X[:3],y[:3]),(X[3:],y[3:])],beta,v,P,pi)
    joined,_=expectation([(X,y)],beta,v,P,pi)
    assert separate>joined+2


def test_em_monotonicity_final_parameters_and_shared_mean():
    rng=np.random.default_rng(59);X=np.column_stack([np.ones(600),rng.normal(size=600)])
    state=np.zeros(600,dtype=int)
    for t in range(1,600):state[t]=state[t-1] if rng.random()<.95 else 1-state[t-1]
    y=X@np.array([.2,.4])+rng.normal(size=600)*np.where(state==0,.2,1.3)
    segments=[(X[:300],y[:300]),(X[300:],y[300:])]
    for shared in [False,True]:
        result=fit(segments,shared_beta=shared,max_iter=400)
        assert result['status']=='CONVERGED'
        assert np.min(np.diff(result['history']))>=-1e-7
        ll,_=expectation(segments,result['beta'],result['variance'],result['transition'],result['initial'])
        assert np.isclose(ll,result['log_likelihood'])
        np.testing.assert_allclose(result['transition'].sum(1),1)
        if shared:np.testing.assert_allclose(result['beta'][0],result['beta'][1])


def test_compiled_backend_matches_log_domain_reference_with_tail_observations():
    from switching_regression import forward_backward_python
    rng=np.random.default_rng(22);e=-rng.exponential(200,size=(200,2));P=np.array([[.97,.03],[.04,.96]]);pi=np.array([.7,.3])
    a=forward_backward(e,P,pi);b=forward_backward_python(e,P,pi)
    for key in a:np.testing.assert_allclose(a[key],b[key],rtol=1e-8,atol=1e-10)

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


def test_predictive_score_reduces_to_independent_single_gaussian_formula():
    from run_market_study import score
    X=np.array([[1.,-1.],[1.,.5],[1.,2.]]);y=np.array([.1,-.3,1.2]);b=np.array([.2,.4]);v=.7;ys=3.5
    model={'initial':np.array([.9,.1]),'beta':np.tile(b,(2,1)),'variance':np.array([v,v]),'transition':np.array([[.93,.07],[.23,.77]])}
    actual=score([(X,y)],model,ys);res=y-X@b
    assert np.isclose(actual['mse'],np.mean(res**2)*ys**2)
    assert np.isclose(actual['negative_log_score'],np.mean(.5*np.log(2*np.pi*v)+res**2/(2*v))+np.log(ys))


def test_validation_scaling_uses_fixed_training_parameters():
    from run_market_study import prepare
    train=[{'state':'x','z':np.array([[1.,2.],[2.,1.],[4.,3.],[3.,5.]])}]
    _,sc=prepare(train);a=[{'state':'x','z':np.array([[3.,1.],[4.,2.],[5.,3.]])}]
    b=[{'state':'x','z':a[0]['z'].copy()}];b[0]['z'][-1]*=1000
    sa,_=prepare(a,**sc);sb,_=prepare(b,**sc)
    np.testing.assert_allclose(sa[0][0],sb[0][0])
    assert sa[0][1][0]==sb[0][1][0]
    assert sa[0][1][-1]!=sb[0][1][-1]

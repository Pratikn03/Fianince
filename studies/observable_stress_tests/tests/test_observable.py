import numpy as np
import pytest
from src import observable


def test_regression_recovers_slope_without_noise():
    x=np.tile([-2.,2.],8); b=np.array([.02,.01,.008])
    y=.15+np.outer(x,b)
    out=observable.response_intervals(x,y,alpha=.05)
    np.testing.assert_allclose(out['estimate'],b,atol=1e-14)
    assert np.all(out['lower']<=b+1e-14)
    assert np.all(out['upper']>=b-1e-14)


def test_response_regression_rejects_constant_input():
    with pytest.raises(ValueError):
        observable.response_intervals(np.ones(8),np.ones((8,5)))


def test_exact_deconvolution_recovers_kernel():
    from src.market import impulse
    rates=np.array([.5,.03]); q=np.array([.24,.15]); a=.4
    beta=impulse(a,q,rates,.02,20)
    recovered=observable.deconvolve(beta)
    expected=np.array([np.sum(q*rates*(1-rates)**j) for j in range(18)])
    np.testing.assert_allclose(recovered['kernel'],expected,atol=1e-12)
    assert recovered['a']==pytest.approx(a)


def test_exact_response_interval_contains_off_grid_gain():
    from src.market import impulse
    rates=np.array([.43,.037]); q=np.array([.28,.18]); a=.4
    beta=impulse(a,q,rates,.02,26)
    out=observable.recurrence_interval(beta-1e-12,beta+1e-12,.02,bins=64)
    assert out['lower']<=a+sum(q)<=out['upper']
    assert out['label']=='stable'


def test_no_impact_evidence_remains_inconclusive():
    out=observable.recurrence_interval(-np.ones(10),np.ones(10),.01)
    assert out['label']=='inconclusive'


def test_interval_deconvolution_is_conservative():
    from src.market import impulse
    q=np.array([.3,.2]);rates=np.array([.5,.05]);a=.4
    b=impulse(a,q,rates,.02,15)
    out=observable.deconvolution_interval(b-1e-6,b+1e-6,.05)
    assert out['lower']<=a+sum(q)<=out['upper']


def test_public_inference_has_no_hidden_parameter_input():
    import inspect
    for f in [observable.response_intervals,observable.recurrence_interval]:
        args=inspect.signature(f).parameters
        assert not any(k in args for k in ('q','rates','true_a','states','noise_sd','true_gain'))

@pytest.mark.parametrize('slow,G',[ (.002,.7),(.02,.95),(.1,1.05),(.1,1.3)])
def test_exact_loop_stability_and_joint_spectrum(slow,G):
    from src.market import joint_matrix
    q=.6*G*np.array([.6,.4]);J=joint_matrix(.4,q,np.array([.5,slow]))
    assert (max(abs(np.linalg.eigvals(J)))<1)==(G<1)


def test_off_grid_true_measures_satisfy_all_outer_constraints():
    from src.market import impulse
    rng=np.random.default_rng(905)
    for _ in range(100):
        floor=.003;rates=np.exp(rng.uniform(np.log(floor),0,4));q=rng.uniform(0,.3,4);a=float(rng.uniform(.1,.8))
        b=impulse(a,q,rates,.02,20);eps=1e-7
        data,status=observable.recurrence_constraints(b-eps,b+eps,floor,64)
        A,rhs,_=data;edges=np.geomspace(floor,1,65);w=np.zeros(64)
        for eta,v in zip(rates,q):w[min(63,np.searchsorted(edges,eta,side='right')-1)]+=v
        vector=np.r_[a,w]
        assert np.max(A@vector-rhs)<1e-9


def test_interval_widening_does_not_destroy_true_coverage():
    from src.market import impulse
    b=impulse(.4,np.array([.3,.45]),np.array([.5,.1]),.02,33)
    for eps in [1e-8,1e-6,1e-4]:
        out=observable.recurrence_interval(b-eps,b+eps,.1)
        assert out['lower']<=1.15<=out['upper']


def test_negative_response_contradicts_positive_class():
    L=np.array([.1,.03,-.03]);U=L+.001
    assert observable.recurrence_interval(L,U,.05)['label']=='model_conflict'


def test_rate_one_special_case_contains_true_total():
    from src.market import impulse
    b=impulse(.2,np.array([.4]),np.array([1.]),.03,16)
    ans=observable.recurrence_interval(b-1e-8,b+1e-8,1.)
    assert ans['lower']<=.6<=ans['upper']


def test_response_standard_error_increases_when_input_shrinks():
    u=np.tile([-2.,2.],16);rng=np.random.default_rng(31)
    y=rng.normal(size=(32,5))+u[:,None]*np.arange(1,6)
    a=observable.response_intervals(u,y);b=observable.response_intervals(u/2,y)
    np.testing.assert_allclose(b['estimate'],2*a['estimate'])
    np.testing.assert_allclose(b['se'],2*a['se'])


def test_point_fit_has_no_stability_constraint():
    from src.market import impulse
    b=impulse(.4,np.array([.6,.3]),np.array([.5,.1]),.02,40)
    ans=observable.recurrence_point(b,.1)
    assert ans['gain']>1

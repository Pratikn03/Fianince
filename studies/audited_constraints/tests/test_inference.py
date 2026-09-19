import numpy as np
import pytest
from src.inference import reconstruct_terminal, terminal_interval, binomial_interval, label_probability

def test_public_filter_timing():
    p=np.array([[2.,3.,4.],[4.,6.,8.]])
    X,y=reconstruct_terminal(p,[.5])
    assert np.allclose(X,[[1,3,1],[1,6,2]])
    assert np.array_equal(y,[4,8])

def test_terminal_regression_known_linear_data():
    rng=np.random.default_rng(7);X=np.column_stack([np.ones(100),rng.normal(size=(100,3))])
    b=np.array([.1,.4,.2,.3]);y=X@b
    result=terminal_interval(X,y)
    assert result['estimate']==pytest.approx(.9)
    assert result['label']=='stable'

def test_singular_is_not_confident():
    X=np.ones((20,4));y=np.ones(20)
    assert terminal_interval(X,y)['label']=='inconclusive'

def test_binomial_edges_exact():
    lo,hi=binomial_interval(0,128,.05)
    assert lo==0 and hi==pytest.approx(1-(.05/2)**(1/128))
    lo,hi=binomial_interval(128,128,.05)
    assert hi==1 and lo==pytest.approx((.05/2)**(1/128))

def test_probability_label():
    assert label_probability(0,.03,.05)=='below_threshold'
    assert label_probability(.06,.12,.05)=='above_threshold'
    assert label_probability(.02,.1,.05)=='inconclusive'

def test_public_single_roundtrip_has_no_residual_inventory():
    from src.linear import probe_orders
    u=probe_orders(np.random.default_rng(1),20,64,'single_roundtrip')
    assert np.allclose(u.sum(axis=1),0)
    assert np.allclose(np.abs(u).sum(axis=1),4)
    assert np.all(u[:,-1]==0)

def test_variable_endpoint_cannot_see_future_prices():
    from src.inference import variable_terminal
    rng=np.random.default_rng(71);p=rng.normal(size=(32,64));T=np.tile([8,16,32,64],8)
    X,y=variable_terminal(p,T,[.5,.1]);q=p.copy()
    for i,t in enumerate(T):q[i,t:]+=1e9
    XX,yy=variable_terminal(q,T,[.5,.1])
    assert np.array_equal(X,XX) and np.array_equal(y,yy)

def test_observable_rows_obey_audited_equation_without_noise():
    from src.linear import simulate_linear
    q=np.array([.3,.2]);eta=[.5,.03]
    p=simulate_linear(.4,q,eta,.02,128,64,7,'impulse',noise_sd=0)['prices']
    X,y=reconstruct_terminal(p,eta)
    assert np.allclose(X@np.r_[0.,.4,q],y,rtol=1e-12,atol=1e-14)

def test_binomial_invalid_counts_rejected():
    with pytest.raises(ValueError):binomial_interval(2,1)
    with pytest.raises(ValueError):binomial_interval(-1,20)

def test_general_contrast_recovers_tail():
    from src.inference import contrast_interval
    rng=np.random.default_rng(18);X=np.column_stack([np.ones(100),rng.normal(size=(100,3))]);b=np.array([0,.4,.3,.2]);c=np.array([0,0,.5**64,.9**64])
    z=contrast_interval(X,X@b,c,.025)
    assert z['estimate']==pytest.approx(.3*.5**64+.2*.9**64)

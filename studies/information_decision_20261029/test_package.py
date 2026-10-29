import itertools
import numpy as np
import pandas as pd
import pytest
from model import (Economy,response,account,cost,candidates,confidence_mask,safe_mask,log_scores,choose)
from market import features


def test_account_entry_mark_and_exit_reconcile():
    e=Economy('no feedback',(0.,),(.5,));u=np.array([[.01,-.02,.03]])
    a=account(e,u,3.)
    expected_x=.4*(.4*.01-.02)+.03
    assert a['terminal'][0]==pytest.approx(1000+3*expected_x-cost(3))
    assert a['terminal_inventory']==0
    assert a['entry_cash']==pytest.approx(1000-300-cost(3)/2)
    assert a['accounting_error']<1e-10


def test_impulse_convolution_matches_direct_dynamics():
    e=Economy('two',(.1,.3),(.05,.8));u=np.array([[.02,-.04,.01,.03]])
    expected=np.convolve(u[0],response(e,4))[:4]
    np.testing.assert_allclose(account(e,u,1)['price_delta'][0],expected,atol=1e-12)


def test_finite_path_bound_against_every_corner_shock():
    e=Economy('two',(.2,.2),(.1,.7));H=5;u=np.array(list(itertools.product([-.04,.04],repeat=H)))
    I=3.;a=account(e,u,I);bound=I*.04*abs(response(e,H)).sum()+cost(I)
    assert a['loss_from_initial'].max()==pytest.approx(bound)


def test_disclosure_never_reduces_certified_capacity_before_fee():
    h=np.array([response(e,60) for e in candidates()]);g=abs(h).sum(1);grid=np.linspace(0,9.9,100)
    coarse=safe_mask(grid,g,2);fine=safe_mask(grid,g[:5],2)
    assert np.all(~coarse|fine)


def test_empty_class_abstains_despite_logical_vacuity():
    grid=np.array([0.,1.,2.]);np.testing.assert_array_equal(safe_mask(grid,[],1),[True,False,False])


def test_cash_and_initial_account_not_leveraged():
    e=Economy('e',(.4,),(.2,));u=np.zeros((3,60))
    a=account(e,u,0);assert np.all(a['wealth']==1000)
    with pytest.raises(ValueError):account(e,u,11)


def test_equal_risk_need_not_imply_equal_preferred_position():
    grid=np.array([0.,1.,2.]);allowed=np.ones(3,bool)
    a=choose(grid,log_scores(grid,np.array([-10.,10.])),allowed)
    b=choose(grid,log_scores(grid,np.array([1.,2.])),allowed)
    assert a==0 and b==2


def test_known_pair_infinite_gain_equal_and_quadratic_response_gap():
    one=Economy('one',(.4,),(.5,));gaps=[]
    for delta in [.1,.05]:
        two=Economy('two',(.2,.2),(.5-delta,.5+delta))
        assert response(two,10000).sum()==pytest.approx(5)
        gaps.append(np.linalg.norm(response(one,24)-response(two,24)))
    assert 3.8<gaps[0]/gaps[1]<4.2


def test_gaussian_band_has_declared_familywise_coverage_simulation():
    rng=np.random.default_rng(11);h=response(Economy('x',(.4,),(.2,)),12)[None,:]
    # Distribution of N-sample means; all taps are independent in this test.
    accepted=[confidence_mask(h,h[0]+rng.normal(0,.02/8,12),.02,64)[0][0] for _ in range(3000)]
    assert np.mean(accepted)>.93


def fixture():
    r=np.random.default_rng(1);n=1200
    return pd.DataFrame(dict(timestamp=pd.date_range('2025-01-01',periods=n,freq='min',tz='UTC'),
      price=np.exp(4+np.cumsum(r.normal(0,.001,n))),signed_flow=r.normal(size=n)))


def test_observational_features_do_not_use_future_outcomes():
    f=fixture();g=f.copy();g.loc[721:,'price']*=1.2
    a,b=features(f),features(g)
    cols=['vol_hour','vol_six_hour','abs_return_hour','flow_imbalance','persistence_proxy','impact_proxy']
    np.testing.assert_allclose(a.loc[a.row<=720,cols],b.loc[b.row<=720,cols])


def test_irregular_market_data_rejected():
    f=fixture().drop(index=50)
    with pytest.raises(ValueError,match='regular'):features(f)


def test_fee_reduces_cash_and_cannot_be_called_a_free_benefit():
    grid=np.linspace(0,9.9,100);g=[10.]
    free=safe_mask(grid,g,1.);paid=safe_mask(grid,g,.5)
    assert np.all(~paid|free)

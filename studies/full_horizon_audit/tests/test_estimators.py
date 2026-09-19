import numpy as np
import pytest
from mmfh import estimators as e


def test_bin_envelopes_cover_continuous_rates():
    lo,hi=e.feature_envelopes(np.array([.002,.02,.3,1.]), [0,1,7,255], 'tap')
    assert lo.shape==(4,3)
    for b,(a,z) in enumerate(zip([.002,.02,.3],[.02,.3,1.])):
        rr=np.linspace(a,z,501)
        vv=rr[None,:]*(1-rr[None,:])**np.array([0,1,7,255])[:,None]
        assert np.all(lo[:,b]<=vv.min(axis=1)+1e-13)
        assert np.all(hi[:,b]>=vv.max(axis=1)-1e-13)


def test_sum_envelopes():
    lo,hi=e.feature_envelopes(np.array([.01,.1,1.]),[4,16,256],'sum')
    assert np.allclose(lo[:,0],1-.99**np.array([4,16,256]),atol=1e-10)
    assert np.allclose(hi[:,1],1,atol=1e-10)


def test_nnls_uses_late_observations():
    floor=.01;H=128;grid=e.rate_grid(floor,129)
    k=.7*grid[80]*(1-grid[80])**np.arange(H)
    fit=e.fit_nnls(k,0.0,floor)
    assert abs(fit['gain']-.7)<2e-5
    k2=k.copy();k2[64:]+=0.002
    fit2=e.fit_nnls(k2,0.0,floor)
    assert abs(fit2['gain']-fit['gain'])>1e-3


@pytest.mark.parametrize('floor',[.002,.02,.1])
@pytest.mark.parametrize('H',[4,16,64,256])
def test_outer_interval_covers_offgrid_truth(floor,H):
    rates=np.array([floor*1.23,.317,.817]);weights=np.array([.3,.2,.7])
    k=(weights*rates)@((1-rates)[:,None]**np.arange(H))
    result=e.moment_interval(k,0.0001,floor,bins=64)
    assert result['status']=='ok'
    assert result['raw_lower']<=weights.sum()+1e-8
    assert result['raw_upper']>=weights.sum()-1e-8
    assert result['dual_violation']<=1e-9


def test_unstable_gain_not_constrained_away():
    r=.2;H=64;k=1.5*r*(1-r)**np.arange(H)
    out=e.fit_nnls(k,0.0,.02)
    assert out['gain']>1.45
    ci=e.moment_interval(k,1e-5,.02)
    assert ci['raw_lower']>1


def test_exact_ambiguous_pair_not_separated():
    # v1 witness has k0=6/65, k1=3/65 and gain on opposite sides of 0.6.
    k=np.array([6/65,3/65])/.6
    out=e.moment_interval(k,0.0,.05,bins=64,horizons=(2,),max_horizon=2)
    assert out['raw_lower']<1<out['raw_upper']


def test_false_floor_control_and_summary():
    H=16;eta=.0001;k=2*eta*(1-eta)**np.arange(H)
    o=e.summary_interval(k,1e-6,.2,horizons=(16,))
    assert o['upper']<1 # deliberately false contract; retained as a negative control.


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):e.fit_nnls(np.array([1.,np.nan]),.1,.01)
    with pytest.raises(ValueError):e.moment_interval(np.ones(4),.1,0.)
    with pytest.raises(ValueError):e.feature_envelopes(np.array([.1,.01]),[1],'tap')

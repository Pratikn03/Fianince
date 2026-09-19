import numpy as np
from src import market


def test_market_exact_impulse_matches_joint_dynamics():
    cfg=market.MarketConfig(a=.4,impact=.02,rates=(.5,.1),q=(.3,.2),
            noise_flow_sd=0.,quote_noise_sd=0.,initial_memory_sd=0.)
    out=market.simulate(cfg,episodes=8,amplitude=2.,steps=20,seed=17,audit=True)
    expected=market.impulse(.4,np.array(cfg.q),np.array(cfg.rates),.02,20)
    np.testing.assert_allclose(out['prices'],out['probes'][:,None]*expected,atol=1e-11)


def test_market_cash_and_share_conservation():
    cfg=market.MarketConfig(a=.4,impact=.02,rates=(.5,.02),q=(.3,.2))
    out=market.simulate(cfg,episodes=128,amplitude=4.,steps=66,seed=119,audit=True)
    assert out['audit']['max_cash_error']<1e-7
    assert out['audit']['max_share_error']<1e-9
    assert set(out['public'])=={'probes','prices'}


def test_probe_assignment_is_balanced():
    cfg=market.MarketConfig(a=.4,impact=.02,rates=(.5,.02),q=(.3,.2))
    out=market.simulate(cfg,128,4.,20,13)
    assert out['probes'].sum()==0


def test_mismatched_rate_and_weight_vectors_rejected():
    import pytest
    with pytest.raises(ValueError):
        market.MarketConfig(.4,.02,(.5,),(.3,.2)).validate()


def test_exact_nonlinear_amplitude_scaling_is_not_linear():
    cfg=market.MarketConfig(.4,.02,(.5,.1),(.3,.2),noise_flow_sd=0.,quote_noise_sd=0.,initial_memory_sd=0.,nonlinear_capacity=1.)
    a=market.simulate(cfg,8,1.,4,29);b=market.simulate(cfg,8,4.,4,29)
    k1=np.mean(a['prices'][:,0]/a['probes']);k4=np.mean(b['prices'][:,0]/b['probes'])
    assert k4<k1
    np.testing.assert_allclose(k1,.02*np.tanh(1.))
    np.testing.assert_allclose(k4,.02*np.tanh(4.)/4.)

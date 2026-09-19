from fractions import Fraction as F
import importlib.util
import numpy as np
import pytest


def modules():
    assert importlib.util.find_spec('machine_markets.model') is not None, 'model implementation missing'
    assert importlib.util.find_spec('machine_markets.construction') is not None, 'construction implementation missing'
    assert importlib.util.find_spec('machine_markets.inference') is not None, 'inference implementation missing'
    from machine_markets import model, construction, inference
    return model, construction, inference


def test_single_mode_agent_loop_equals_matrix_powers():
    m, _, _ = modules()
    market = m.Market(0.4, np.array([0.3]), np.array([0.2]))
    assert np.allclose(market.impulse(25), market.impulse_matrix(25), atol=1e-14)
    assert market.impulse(3)[1] == pytest.approx(.4)
    assert market.impulse(3)[2] == pytest.approx(.16+.06)


def test_kernel_deconvolution_has_correct_lag():
    m, _, _ = modules()
    market = m.Market(.3, np.array([.2,.4]), np.array([.7,.03]))
    recovered = m.recover_kernel(market.impulse(13), market.a)
    assert np.allclose(recovered, market.kernel(12), atol=2e-13)


def test_exact_matched_pair_has_opposite_stability():
    _, c, _ = modules()
    pair = c.construct_pair(F(2,5), [F(0),F(1,2),F(19,20)])
    assert pair['moment_residuals'] == ['0','0']
    assert F(pair['Q_minus']) + F(2,5) < 1
    assert F(pair['Q_plus']) + F(2,5) > 1
    minus, plus = c.to_markets(pair)
    assert len(minus.q) == len(plus.q) == 3
    assert np.allclose(minus.impulse(3), plus.impulse(3), atol=1e-14)
    assert not np.isclose(minus.impulse(4)[4], plus.impulse(4)[4])


def test_noiseless_bounds_cover_feedback():
    m, _, inf = modules()
    rng = np.random.default_rng(301)
    for _ in range(50):
        eta = rng.uniform(.02,.9,8)
        q = rng.uniform(.001,.2,8)
        market = m.Market(.4,q,eta)
        for H in [1,4,32,128]:
            k = market.kernel(H)
            L,U = inf.feedback_bounds(float(k.sum()),float(k.sum()),float(k[-1]),H,.02)
            assert L <= q.sum()+1e-12 <= U+1e-12


def test_no_rate_floor_does_not_certify_safety():
    _, _, inf = modules()
    L,U=inf.feedback_bounds(.1,.1,.01,4,0.0)
    assert np.isinf(U)
    assert inf.classify(.4,L,U) == 'inconclusive'


def test_wrong_rate_floor_can_be_unsafe():
    m, _, inf = modules()
    market=m.Market(.4,np.array([.8]),np.array([.001]))
    k=market.kernel(4)
    L,U=inf.feedback_bounds(k.sum(),k.sum(),k[-1],4,.2)
    assert inf.classify(.4,L,U)=='stable'
    assert market.spectral_radius()>1


def test_one_rate_baseline_exact_recovery():
    m, _, inf=modules()
    k=m.Market(.4,np.array([.3]),np.array([.2])).kernel(16)
    assert inf.single_rate(k) == pytest.approx(.3,abs=1e-12)
    assert inf.matrix_pencil(k,0.0,.01) == pytest.approx(.3,abs=1e-9)


def test_invalid_parameter_inputs_rejected():
    m,_,inf=modules()
    with pytest.raises(ValueError):m.Market(.4,np.array([-.1]),np.array([.2]))
    with pytest.raises(ValueError):m.Market(.4,np.array([.1]),np.array([0.0]))
    with pytest.raises(ValueError):inf.feedback_bounds(.2,.1,.01,4,.02)

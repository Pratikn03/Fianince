import numpy as np
import pytest
from src.audit import tail_envelope, norm_tail, validate_contract, make_contract

def test_geometric_tail_and_zero_horizon():
    assert tail_envelope(.8,.2,0)==.8
    assert tail_envelope(.8,1,8)==0
    assert tail_envelope(.8,.2,3)==pytest.approx(.8*.8**3)

def test_random_mixture_tail_contained():
    rng=np.random.default_rng(4)
    for h in (1,8,64,256):
        for _ in range(50):
            eta=rng.uniform(.02,1,5);q=rng.dirichlet(np.ones(5))*.7
            assert np.sum(q*(1-eta)**h)<=tail_envelope(.7,.02,h)+1e-14

def test_noncontractive_state_cannot_have_norm_tail():
    with pytest.raises(ValueError): norm_tail(1.,1.,1.,8)

def test_contract_mutations_fail():
    c=make_contract([.5,.02], 'abc')
    assert validate_contract(c,'abc')['eligible']
    for key,val in [('reset','unknown'),('other_feedback_channels',['inventory']),('source_sha256','forged')]:
        d=dict(c);d[key]=val
        assert not validate_contract(d,'abc')['eligible']

def test_invalid_floor_rejected():
    with pytest.raises(ValueError):tail_envelope(.8,0,10)

def test_source_rejects_illegal_gain():
    from src.linear import simulate_linear
    with pytest.raises(ValueError):simulate_linear(.4,[-1,.1],[.5,.1],.02,10,16,1,'impulse')

def test_noisy_observation_and_binding_contract_rejected():
    c=make_contract([.5,.02],'abc')
    assert not validate_contract(dict(c,observation='noisy_quote'),'abc')['eligible']
    assert not validate_contract(dict(c,execution_regime='constrained'),'abc')['eligible']

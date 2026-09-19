import numpy as np
from scipy.stats import norm
from mmfh import testing_limits as t

def test_energy_matches_explicit_kernel():
    for eta in [1e-6,.001,.1,1.]:
        for H in [4,256,4096]:
            vector=.2*eta*(1-eta)**np.arange(H)
            assert np.isclose(t.squared_distance(.2,eta,H,.001),float(vector@vector)/.001**2,rtol=1e-9)

def test_indistinguishability_limit():
    d=t.squared_distance(.2,1e-10,256,.001)
    assert abs(t.oracle_error(d)-.5)<1e-6

def test_two_simple_hypotheses_oracle():
    assert np.isclose(t.oracle_error(4.),norm.cdf(-1))
    assert np.isclose(t.total_variation(4.),2*norm.cdf(1)-1)
    assert t.coverage_upper_bound(0.,.05)==.1

def test_infinite_energy():
    assert np.isclose(t.squared_distance(.2,.1,None,.01),.04*.1/(.01**2*1.9))

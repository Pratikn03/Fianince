"""Small independent fixtures for the corrected proof qualifications."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import pytest


@pytest.mark.parametrize('impact',[.02,.5,2.])
def test_resolvent_coefficients_include_impact_exactly_once(impact):
    from research_extension.mm_revision.states import compute_impulse_response
    a,eta,Q=.4,.2,.42
    J=np.array([[a,1],[eta*Q,1-eta]])
    state=np.array([impact,0.])
    actual=[]
    for _ in range(13):
        actual.append(state[0]); state=J@state
    h,beta=compute_impulse_response(a,eta,Q,kappa=impact,H=12)
    np.testing.assert_allclose(beta,actual,rtol=1e-13,atol=1e-14)
    np.testing.assert_allclose(beta,impact*h,rtol=1e-13,atol=1e-14)
    assert beta[0]==impact and h[0]==1


def test_rank_deficient_total_probe_identifies_rate_not_allocation():
    Q,b=F(2,5),F(2,25)
    eta=b/Q
    assert eta==F(1,5)
    # Same one-row U=(1,1), n-1=1 measurement, but distinct allocations.
    for q in [(F(3,10),F(1,10)),(F(1,5),F(1,5))]:
        assert sum(q)==Q and eta*sum(q)==b


def test_nonnegative_boundary_uniqueness_does_not_need_uniform_rank():
    U=np.array([[1.,0.,0.]])
    assert np.linalg.matrix_rank(np.vstack([np.ones(3),U]))==2
    # b/eta fixes q1=Q=1, and q2,q3>=0 with zero remaining sum forces both zero.
    b,eta,Q=F(1,2),F(1,2),F(1)
    q1=b/eta
    assert q1==Q and Q-q1==0


def test_paper_records_corrected_normalization_and_joint_scope():
    source=(Path(__file__).resolve().parents[1]/'paper/Machine_Markets_Final_Integrated_Paper.tex').read_text()
    assert r'H_{xu}(z)=\sum_{j\ge0}\beta_jz^{-(j+1)}' in source
    assert r'joint identification of $(\eta,\mathbf q)$' in source
    assert 'common disturbance law' in source

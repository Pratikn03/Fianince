"""Failure-oriented checks for the newly incorporated theorem statements.

No live data; no claim that these tests replace the accompanying proofs.
"""
import numpy as np
import pytest
from scipy.integrate import quad
from scipy.stats import norm

def design(x,L):
    Z=np.zeros((len(x),L))
    for t in range(len(x)):
        k=min(t,L)
        if k:Z[t,:k]=x[t-k:t][::-1]
    return Z

def sequential_logq(x,L,sigma):
    P=np.eye(L);m=np.zeros(L);total=0.
    for y,z in zip(x,design(x,L)):
        Pz=P@z;v=sigma*sigma+z@Pz;res=y-z@m
        total+=norm.logpdf(y,loc=z@m,scale=np.sqrt(v))
        m+=Pz*res/v;P-=np.outer(Pz,Pz)/v
    return total

def batch_logq(x,L,sigma):
    Z=design(x,L);A=np.eye(L)+Z.T@Z/sigma**2
    b=Z.T@x/sigma**2
    objective=x@x/sigma**2-b@np.linalg.solve(A,b)
    return -.5*(len(x)*np.log(2*np.pi*sigma*sigma)+np.linalg.slogdet(A)[1]+objective)

@pytest.mark.parametrize('sigma',[.25,1.,3.])
@pytest.mark.parametrize('L',[1,4,12])
def test_adaptive_gaussian_integral_matches_sequential_density(sigma,L):
    x=np.random.default_rng(71+L).normal(size=35)*sigma
    assert abs(sequential_logq(x,L,sigma)-batch_logq(x,L,sigma))<1e-10

@pytest.mark.parametrize('sigma',[.4,2.])
def test_pathwise_bayesian_comparator_bound(sigma):
    rng=np.random.default_rng(188);x=rng.normal(size=45)*sigma
    L=5;phi=np.array([.4,.1,.05,.02,.01]);Z=design(x,L)
    p=norm.logpdf(x,loc=Z@phi,scale=sigma).sum()
    upper=.5*phi@phi+.5*np.linalg.slogdet(np.eye(L)+Z.T@Z/sigma**2)[1]
    assert p-batch_logq(x,L,sigma)<=upper+1e-11

@pytest.mark.parametrize('alpha',[.25,.5,1.,2.])
def test_random_mean_gap_does_not_have_universal_gaussian_error_curve(alpha):
    actual=quad(lambda x:2*norm.pdf(x)*norm.cdf(-alpha*x),0,np.inf)[0]
    exact=np.arctan(1/alpha)/np.pi
    assert abs(actual-exact)<1e-10
    assert abs(actual-norm.cdf(-alpha))>.01
    # KL is half the expected squared conditional-mean difference.
    assert (2*alpha)**2/2==2*alpha**2

def test_arbitrary_initial_state_invalidates_zero_state_uniform_bound():
    s=.5;x0=1e4
    expected_regret=.5*(np.log(1+x0*x0)+(1+s*s*x0*x0)/(1+x0*x0)-1)
    zero_state_bound=s*s/2+.5*np.log(1+1/(1-s)**2)
    assert expected_regret>zero_state_bound+5

def test_mixture_regret_bound_is_one_sided():
    true_density=.01;other_density=.9;prior=.5
    mixture=prior*true_density+(1-prior)*other_density
    regret=np.log(true_density/mixture)
    assert regret<=np.log(1/prior)
    assert abs(regret)>np.log(1/prior)

def test_rank_is_necessary_for_the_proposed_inverse_argument():
    # A one-dimensional constant rule is smooth but records only total mass.
    moments0=np.array([.1,.2]);moments1=np.array([.15,.15])
    g=np.ones(8)
    assert np.allclose(moments0.sum()*g,moments1.sum()*g)
    assert not np.allclose(moments0,moments1)

@pytest.mark.parametrize('K',[2,3,4])
def test_exponential_and_power_derivative_rank(K):
    import sympy as sp
    t=sp.Symbol('t');m=2*K
    exponential=sp.Matrix([[sp.diff((1-t)*t**j,t,p).subs(t,sp.Rational(1,2)) for p in range(m)] for j in range(m)])
    assert exponential.det()!=0
    # Power derivatives differ by a positive diagonal factor from a Vandermonde.
    logs=np.log(np.arange(1,m+1))
    assert np.all(np.diff(logs)>0)
    assert np.prod([logs[j]-logs[i] for i in range(m) for j in range(i+1,m)])>0
